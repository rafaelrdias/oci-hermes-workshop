mock_provider "oci" {
  mock_data "oci_identity_region_subscriptions" {
    defaults = { region_subscriptions = [{ is_home_region = true, region_name = "sa-saopaulo-1", region_key = "GRU", state = "READY" }] }
  }
  mock_data "oci_identity_availability_domains" {
    defaults = { availability_domains = [{ name = "test:AD-1", id = "ad1", compartment_id = "ocid1.tenancy.oc1..test" }] }
  }
  mock_data "oci_core_images" {
    defaults = { images = [{ id = "ocid1.image.oc1.sa-saopaulo-1.test" }] }
  }
}
mock_provider "random" {}
mock_provider "oci" {
  alias = "home"
}

variables {
  tenancy_ocid                = "ocid1.tenancy.oc1..test"
  region                      = "sa-saopaulo-1"
  ssh_public_key              = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITestOnlyNotARealKey stand-test"
  ssh_allowed_cidr            = "203.0.113.7/32"
  telegram_bot_token          = "123456:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
  acknowledge_secret_in_state = true
}

run "gru" {
  command = apply
  assert {
    condition     = output.region == "sa-saopaulo-1" && output.model == "meta.llama-3.3-70b-instruct"
    error_message = "GRU deve usar o modelo on-demand local."
  }
  assert {
    condition     = length(oci_core_instance.hermes.metadata.user_data) < 30000
    error_message = "User data comprimido excede o orçamento de metadados OCI."
  }
  assert {
    condition     = strcontains(oci_identity_dynamic_group.hermes.matching_rule, oci_core_instance.hermes.id)
    error_message = "Dynamic group deve autorizar apenas esta VM."
  }
  assert {
    condition     = strcontains(oci_identity_policy.hermes.statements[0], "use generative-ai-chat") && !strcontains(oci_identity_policy.hermes.statements[0], "manage")
    error_message = "A VM não pode administrar a tenancy."
  }
  assert {
    condition     = oci_core_instance.hermes.shape_config[0].ocpus == 1 && oci_core_instance.hermes.shape_config[0].memory_in_gbs == 8
    error_message = "Tamanho padrão do stand alterado."
  }
}

run "ord" {
  command = plan
  variables { region = "us-chicago-1" }
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [{ is_home_region = true, region_name = "us-chicago-1", region_key = "ORD", state = "READY" }] }
  }
  assert {
    condition     = output.region == "us-chicago-1"
    error_message = "ORD deve permanecer em Chicago."
  }
}

run "reject_open_ssh_without_consent" {
  command = plan
  variables { ssh_allowed_cidr = "0.0.0.0/0" }
  expect_failures = [oci_core_security_list.stand]
}

run "allow_public_ssh_with_key_and_consent" {
  command = plan
  variables {
    ssh_allowed_cidr       = "0.0.0.0/0"
    acknowledge_public_ssh = true
  }
  assert {
    condition = length([for rule in oci_core_security_list.stand.ingress_security_rules : rule
      if rule.protocol == "6" && rule.source == "0.0.0.0/0" &&
      alltrue([for ports in rule.tcp_options : ports.min == 22 && ports.max == 22])
    ]) == 1
    error_message = "Aceite deve liberar somente TCP/22 para qualquer IPv4."
  }
  assert {
    condition     = oci_core_instance.hermes.metadata.ssh_authorized_keys == trimspace(var.ssh_public_key)
    error_message = "Chave pública deve ser entregue à instância."
  }
}

run "reject_public_ssh_without_key" {
  command = plan
  variables {
    ssh_public_key         = ""
    ssh_allowed_cidr       = "0.0.0.0/0"
    acknowledge_public_ssh = true
  }
  expect_failures = [oci_core_instance.hermes]
}

run "reject_invalid_ssh_cidr" {
  command = plan
  variables { ssh_allowed_cidr = "999.1.1.1/32" }
  expect_failures = [var.ssh_allowed_cidr]
}

run "reject_ipv6_ssh_cidr" {
  command = plan
  variables { ssh_allowed_cidr = "::/0" }
  expect_failures = [var.ssh_allowed_cidr]
}

run "reject_other_region" {
  command = plan
  variables { region = "us-ashburn-1" }
  expect_failures = [var.region]
}

run "no_ssh_by_default" {
  command = plan
  variables {
    ssh_public_key   = ""
    ssh_allowed_cidr = ""
  }
  assert {
    condition     = alltrue([for rule in oci_core_security_list.stand.ingress_security_rules : rule.protocol != "6"])
    error_message = "Sem chave/CIDR não deve haver entrada TCP."
  }
}

run "require_consent_for_secret" {
  command = plan
  variables { acknowledge_secret_in_state = false }
  expect_failures = [var.acknowledge_secret_in_state]
}

run "ord_with_ashburn_home" {
  command = apply
  variables { region = "us-chicago-1" }
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [
      { is_home_region = true, region_name = "us-ashburn-1", region_key = "IAD", state = "READY" },
      { is_home_region = false, region_name = "us-chicago-1", region_key = "ORD", state = "READY" }
    ] }
  }
  assert {
    condition     = output.region == "us-chicago-1" && output.iam_home_region == "us-ashburn-1"
    error_message = "VM/modelo devem ficar em ORD e IAM deve usar a home region IAD."
  }
}

run "gru_with_frankfurt_home" {
  command = plan
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [
      { is_home_region = true, region_name = "eu-frankfurt-1", region_key = "FRA", state = "READY" },
      { is_home_region = false, region_name = "sa-saopaulo-1", region_key = "GRU", state = "READY" }
    ] }
  }
  assert {
    condition     = output.region == "sa-saopaulo-1" && output.iam_home_region == "eu-frankfurt-1"
    error_message = "Home region não deve restringir a região da instalação."
  }
}

run "reject_unsubscribed_region" {
  command = plan
  variables { region = "us-chicago-1" }
  expect_failures = [oci_identity_compartment.stand]
}

run "reject_region_not_ready" {
  command = plan
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [
      { is_home_region = true, region_name = "us-ashburn-1", region_key = "IAD", state = "READY" },
      { is_home_region = false, region_name = "sa-saopaulo-1", region_key = "GRU", state = "IN_PROGRESS" }
    ] }
  }
  expect_failures = [oci_identity_compartment.stand]
}
