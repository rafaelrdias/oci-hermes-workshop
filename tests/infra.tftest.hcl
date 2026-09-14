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
mock_provider "tls" {
  mock_resource "tls_private_key" {
    defaults = {
      public_key_openssh = "ssh-rsa TEST-ONLY-GENERATED-PUBLIC-KEY\n"
      private_key_pem    = "TEST-ONLY-PRIVATE-KEY-NOT-A-REAL-SECRET"
    }
  }
}
mock_provider "oci" {
  alias = "home"
}

variables {
  tenancy_ocid                = "ocid1.tenancy.oc1..test"
  region                      = "sa-saopaulo-1"
  llm_model                   = "meta.llama-3.3-70b-instruct"
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
    condition     = oci_identity_dynamic_group.hermes.matching_rule == "ALL {instance.id = '${oci_core_instance.hermes.id}'}" && oci_identity_dynamic_group.hermes.compartment_id == var.tenancy_ocid
    error_message = "Dynamic group deve autorizar apenas esta VM."
  }
  assert {
    condition     = strcontains(oci_identity_policy.hermes.statements[0], "use generative-ai-chat") && !strcontains(oci_identity_policy.hermes.statements[0], "manage")
    error_message = "A VM não pode administrar a tenancy."
  }
  assert {
    condition     = oci_identity_policy.hermes.statements == tolist(["Allow dynamic-group id ${oci_identity_dynamic_group.hermes.id} to use generative-ai-chat in compartment id ${oci_identity_compartment.stand.id} where ALL {request.region = 'GRU', target.model.id = 'meta.llama-3.3-70b-instruct'}"])
    error_message = "GRU deve manter chat restrito ao Llama, à região GRU e ao compartment do stand."
  }
  assert {
    condition     = oci_core_instance.hermes.shape_config[0].ocpus == 1 && oci_core_instance.hermes.shape_config[0].memory_in_gbs == 8
    error_message = "Tamanho padrão do stand alterado."
  }
}

run "ord" {
  command = plan
  variables {
    region    = "us-chicago-1"
    llm_model = "xai.grok-4.6"
  }
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [{ is_home_region = true, region_name = "us-chicago-1", region_key = "ORD", state = "READY" }] }
  }
  assert {
    condition     = output.region == "us-chicago-1" && output.model == "xai.grok-4.6" && local.chat_policy_condition == "request.region = 'ORD'"
    error_message = "ORD deve permanecer em Chicago."
  }
}

run "reject_grok_in_gru" {
  command = plan
  variables { llm_model = "xai.grok-4.6" }
  expect_failures = [oci_identity_compartment.stand]
}

run "ord_grok_43" {
  command = apply
  variables {
    region    = "us-chicago-1"
    llm_model = "xai.grok-4.3"
  }
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [{ is_home_region = true, region_name = "us-chicago-1", region_key = "ORD", state = "READY" }] }
  }
  assert {
    condition     = output.model == "xai.grok-4.3" && oci_identity_policy.hermes.statements == tolist(["Allow dynamic-group id ${oci_identity_dynamic_group.hermes.id} to use generative-ai-chat in compartment id ${oci_identity_compartment.stand.id} where request.region = 'ORD'"])
    error_message = "ORD deve autorizar todos os modelos de chat somente em Chicago e no compartment do stand."
  }
  assert {
    condition     = oci_identity_dynamic_group.hermes.matching_rule == "ALL {instance.id = '${oci_core_instance.hermes.id}'}" && oci_identity_dynamic_group.hermes.compartment_id == var.tenancy_ocid && oci_identity_policy.hermes.compartment_id == var.tenancy_ocid
    error_message = "DG/policy devem ser criados na raiz da tenancy, com DG exclusivo para a VM desta Stack."
  }
}

run "reject_grok_43_in_gru" {
  command = plan
  variables { llm_model = "xai.grok-4.3" }
  expect_failures = [oci_identity_compartment.stand]
}

run "gptoss_in_ord" {
  command = plan
  variables {
    region    = "us-chicago-1"
    llm_model = "openai.gpt-oss-120b"
  }
  override_data {
    target = data.oci_identity_region_subscriptions.tenancy
    values = { region_subscriptions = [{ is_home_region = true, region_name = "us-chicago-1", region_key = "ORD", state = "READY" }] }
  }
  assert {
    condition     = output.model == "openai.gpt-oss-120b" && local.chat_policy_condition == "request.region = 'ORD'"
    error_message = "GPT-OSS deve usar Chicago com a policy regional existente."
  }
}

run "reject_gptoss_on_demand_in_gru" {
  command = plan
  variables { llm_model = "openai.gpt-oss-120b" }
  expect_failures = [oci_identity_compartment.stand]
}

run "reject_unknown_model" {
  command = plan
  variables { llm_model = "unavailable-model" }
  expect_failures = [var.llm_model]
}

run "disable_stt_explicitly" {
  command = plan
  variables { stt_enabled = false }
  assert {
    condition     = jsondecode(local.vm_config).stt_enabled == false
    error_message = "A escolha de desabilitar STT deve chegar à VM."
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
  assert {
    condition     = length(tls_private_key.ssh) == 0 && output.ssh_private_key_pem == "" && !contains(keys(oci_core_instance.hermes.metadata), "ssh_authorized_keys")
    error_message = "Por padrão, nenhuma chave deve ser gerada, exposta ou instalada."
  }
}

run "generate_ssh_with_closed_port" {
  command = apply
  variables {
    generate_ssh_key                     = true
    acknowledge_ssh_private_key_in_state = true
    ssh_public_key                       = ""
    ssh_allowed_cidr                     = ""
  }
  assert {
    condition     = length(tls_private_key.ssh) == 1 && tls_private_key.ssh[0].algorithm == "RSA" && tls_private_key.ssh[0].rsa_bits == 4096
    error_message = "Deve gerar exatamente um par RSA 4096 exclusivo da Stack."
  }
  assert {
    condition     = oci_core_instance.hermes.metadata.ssh_authorized_keys == trimspace(tls_private_key.ssh[0].public_key_openssh) && output.ssh_public_key == oci_core_instance.hermes.metadata.ssh_authorized_keys
    error_message = "Somente a chave pública gerada deve ser instalada na VM."
  }
  assert {
    condition     = output.ssh_private_key_pem == tls_private_key.ssh[0].private_key_pem && !strcontains(jsonencode(oci_core_instance.hermes.metadata), tls_private_key.ssh[0].private_key_pem) && !strcontains(local.vm_config, tls_private_key.ssh[0].private_key_pem)
    error_message = "Privada deve ir somente para saída/state, nunca para metadata/config da VM."
  }
  assert {
    condition     = alltrue([for rule in oci_core_security_list.stand.ingress_security_rules : rule.protocol != "6"]) && startswith(output.ssh_connection_command, "SSH fechado")
    error_message = "Gerar uma chave não pode abrir SSH automaticamente."
  }
}

run "generated_ssh_key_stable_when_opening_cidr" {
  command = apply
  variables {
    generate_ssh_key                     = true
    acknowledge_ssh_private_key_in_state = true
    ssh_public_key                       = ""
    ssh_allowed_cidr                     = "203.0.113.8/32"
  }
  assert {
    condition     = output.ssh_private_key_pem == run.generate_ssh_with_closed_port.ssh_private_key_pem && output.instance_id == run.generate_ssh_with_closed_port.instance_id && startswith(output.ssh_connection_command, "ssh -i hermes.key opc@")
    error_message = "Abrir CIDR deve preservar a chave/VM existentes e fornecer comando SSH."
  }
  assert {
    condition     = length([for rule in oci_core_security_list.stand.ingress_security_rules : rule if rule.protocol == "6" && rule.source == "203.0.113.8/32" && alltrue([for ports in rule.tcp_options : ports.min == 22 && ports.max == 22])]) == 1
    error_message = "A chave gerada com /32 deve liberar somente TCP/22 nesse IP."
  }
}

run "reject_generated_key_without_state_consent" {
  command = plan
  variables {
    generate_ssh_key                     = true
    acknowledge_ssh_private_key_in_state = false
    ssh_public_key                       = ""
    ssh_allowed_cidr                     = ""
  }
  expect_failures = [tls_private_key.ssh]
}

run "reject_generated_and_supplied_key" {
  command = plan
  variables {
    generate_ssh_key                     = true
    acknowledge_ssh_private_key_in_state = true
  }
  expect_failures = [tls_private_key.ssh]
}

run "generated_key_public_ssh_requires_separate_consent" {
  command = plan
  variables {
    generate_ssh_key                     = true
    acknowledge_ssh_private_key_in_state = true
    ssh_public_key                       = ""
    ssh_allowed_cidr                     = "0.0.0.0/0"
  }
  expect_failures = [oci_core_security_list.stand]
}

run "generated_key_public_ssh_with_both_consents" {
  command = plan
  variables {
    generate_ssh_key                     = true
    acknowledge_ssh_private_key_in_state = true
    ssh_public_key                       = ""
    ssh_allowed_cidr                     = "0.0.0.0/0"
    acknowledge_public_ssh               = true
  }
  assert {
    condition     = length([for rule in oci_core_security_list.stand.ingress_security_rules : rule if rule.protocol == "6" && rule.source == "0.0.0.0/0" && alltrue([for ports in rule.tcp_options : ports.min == 22 && ports.max == 22])]) == 1
    error_message = "Com ambos os aceites, somente TCP/22 pode abrir para todos os IPv4."
  }
}

run "supplied_key_with_closed_port" {
  command = plan
  variables { ssh_allowed_cidr = "" }
  assert {
    condition     = length(tls_private_key.ssh) == 0 && output.ssh_private_key_pem == "" && oci_core_instance.hermes.metadata.ssh_authorized_keys == trimspace(var.ssh_public_key) && alltrue([for rule in oci_core_security_list.stand.ingress_security_rules : rule.protocol != "6"])
    error_message = "Chave própria pode ser instalada sem gerar outra chave nem abrir a porta."
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
