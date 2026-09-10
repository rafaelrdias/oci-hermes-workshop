mock_provider "oci" {
  mock_data "oci_identity_region_subscriptions" {
    defaults = { region_subscriptions = [{ is_home_region = true, region_name = "sa-saopaulo-1", region_key = "GRU", state = "READY", tenancy_id = "ocid1.tenancy.oc1..test" }] }
  }
  mock_data "oci_identity_availability_domains" {
    defaults = { availability_domains = [{ name = "test:AD-1", id = "ad1", compartment_id = "ocid1.tenancy.oc1..test" }] }
  }
  mock_data "oci_core_images" {
    defaults = { images = [{ id = "ocid1.image.oc1.sa-saopaulo-1.test" }] }
  }
}
mock_provider "random" {}

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
    values = { region_subscriptions = [{ is_home_region = true, region_name = "us-chicago-1", region_key = "ORD", state = "READY", tenancy_id = "ocid1.tenancy.oc1..test" }] }
  }
  assert {
    condition     = output.region == "us-chicago-1"
    error_message = "ORD deve permanecer em Chicago."
  }
}

run "reject_open_ssh" {
  command = plan
  variables { ssh_allowed_cidr = "0.0.0.0/0" }
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

run "reject_wrong_home_region" {
  command = plan
  variables { region = "us-chicago-1" }
  expect_failures = [oci_identity_compartment.stand]
}
