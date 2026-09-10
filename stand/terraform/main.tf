locals {
  home_region  = one([for r in data.oci_identity_region_subscriptions.tenancy.region_subscriptions : r.region_name if r.is_home_region])
  model        = "meta.llama-3.3-70b-instruct"
  tags         = { purpose = "hermes-oracle-stand", managed_by = "terraform" }
  image        = var.image_ocid != "" ? var.image_ocid : data.oci_core_images.ol9[0].images[0].id
  vm_config    = jsonencode({ region = var.region, compartment_id = oci_identity_compartment.stand.id, model = local.model })
  payloads     = { for name in ["bootstrap.sh", "configure.py", "bridge.py", "smoke.py", "activate.py", "requirements.txt", "requirements.lock", "hermes-gateway.service", "hermes-oci-bridge.service", "hermes-stand-activate.service"] : name => filebase64("${path.module}/files/${name}") }
  pairing_code = "stand_${random_id.pairing.hex}"
  user_data = base64gzip(templatefile("${path.module}/cloud-init.yaml.tftpl", {
    payloads = local.payloads
    config   = base64encode(local.vm_config)
    secrets  = base64encode(jsonencode({ token = var.telegram_bot_token, pairing_code = local.pairing_code }))
  }))
}

data "oci_identity_region_subscriptions" "tenancy" {
  tenancy_id = var.tenancy_ocid
}

resource "random_id" "pairing" {
  byte_length = 24
  keepers     = { bot = sha256(var.telegram_bot_token) }
}

resource "terraform_data" "bootstrap_revision" {
  triggers_replace = [sha256(local.user_data)]
}

resource "oci_identity_compartment" "stand" {
  provider       = oci.home
  compartment_id = var.tenancy_ocid
  name           = var.prefix
  description    = "Ambiente pessoal Hermes — demonstração Oracle, gerenciado por Terraform"
  enable_delete  = true
  freeform_tags  = local.tags
  lifecycle {
    precondition {
      condition     = contains([for r in data.oci_identity_region_subscriptions.tenancy.region_subscriptions : r.region_name if r.state == "READY"], var.region)
      error_message = "A região da instalação deve estar subscrita e READY nesta tenancy. Confira Manage Regions na Console. Ela não precisa ser a home region."
    }
  }
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_images" "ol9" {
  count                    = var.image_ocid == "" ? 1 : 0
  compartment_id           = var.tenancy_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "9"
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "stand" {
  compartment_id = oci_identity_compartment.stand.id
  display_name   = "${var.prefix}-vcn"
  cidr_blocks    = ["10.42.0.0/16"]
  dns_label      = "hermes"
  freeform_tags  = local.tags
}

resource "oci_core_internet_gateway" "stand" {
  compartment_id = oci_identity_compartment.stand.id
  vcn_id         = oci_core_vcn.stand.id
  display_name   = "${var.prefix}-internet"
  enabled        = true
}

resource "oci_core_route_table" "stand" {
  compartment_id = oci_identity_compartment.stand.id
  vcn_id         = oci_core_vcn.stand.id
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.stand.id
  }
}

resource "oci_core_security_list" "stand" {
  compartment_id = oci_identity_compartment.stand.id
  vcn_id         = oci_core_vcn.stand.id
  display_name   = "${var.prefix}-ssh-restrito"
  lifecycle {
    precondition {
      condition     = var.ssh_allowed_cidr != "0.0.0.0/0" || var.acknowledge_public_ssh
      error_message = "Para liberar SSH a qualquer IPv4 (0.0.0.0/0), marque o aceite de exposição pública. Prefira /32 quando possível e restrinja novamente após o evento."
    }
  }
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  dynamic "ingress_security_rules" {
    for_each = var.ssh_allowed_cidr != "" && var.ssh_public_key != "" ? [var.ssh_allowed_cidr] : []
    content {
      source   = ingress_security_rules.value
      protocol = "6"
      tcp_options {
        min = 22
        max = 22
      }
    }
  }
  ingress_security_rules {
    source   = "0.0.0.0/0"
    protocol = "1"
    icmp_options {
      type = 3
      code = 4
    }
  }
}

resource "oci_core_subnet" "stand" {
  compartment_id             = oci_identity_compartment.stand.id
  vcn_id                     = oci_core_vcn.stand.id
  cidr_block                 = "10.42.1.0/24"
  dns_label                  = "stand"
  route_table_id             = oci_core_route_table.stand.id
  security_list_ids          = [oci_core_security_list.stand.id]
  prohibit_public_ip_on_vnic = false
}

resource "oci_core_instance" "hermes" {
  compartment_id      = oci_identity_compartment.stand.id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[var.availability_domain_index].name
  display_name        = var.prefix
  shape               = var.instance_shape
  freeform_tags       = local.tags
  shape_config {
    ocpus         = 1
    memory_in_gbs = 8
  }
  create_vnic_details {
    subnet_id        = oci_core_subnet.stand.id
    assign_public_ip = true
    hostname_label   = "hermes"
  }
  source_details {
    source_type             = "image"
    source_id               = local.image
    boot_volume_size_in_gbs = 50
  }
  metadata = merge(
    { user_data = local.user_data },
    var.ssh_public_key != "" ? { ssh_authorized_keys = trimspace(var.ssh_public_key) } : {}
  )
  lifecycle {
    ignore_changes       = [source_details[0].source_id]
    replace_triggered_by = [terraform_data.bootstrap_revision]
    precondition {
      condition     = (var.ssh_allowed_cidr == "") == (var.ssh_public_key == "")
      error_message = "Para habilitar SSH, preencha chave pública E CIDR (/32 ou 0.0.0.0/0 com aceite), ou deixe ambos vazios."
    }
    precondition {
      condition     = length(local.user_data) < 30000
      error_message = "O pacote de bootstrap excede o limite seguro de metadados da VM."
    }
    precondition {
      condition     = var.availability_domain_index < length(data.oci_identity_availability_domains.ads.availability_domains)
      error_message = "AD não disponível nesta tenancy/região. Use índice 0 ou outro AD listado na Console."
    }
  }
}

# Only THIS VM, not every instance in the tenancy or compartment.
resource "oci_identity_dynamic_group" "hermes" {
  provider       = oci.home
  compartment_id = var.tenancy_ocid
  name           = "${var.prefix}-vm"
  description    = "Identidade da única VM Hermes deste stand"
  matching_rule  = "ALL {instance.id = '${oci_core_instance.hermes.id}'}"
}

resource "oci_identity_policy" "hermes" {
  provider       = oci.home
  compartment_id = var.tenancy_ocid
  name           = "${var.prefix}-inference"
  description    = "Somente inferência Chat no modelo do stand, sem chaves de API"
  statements = [
    "Allow dynamic-group id ${oci_identity_dynamic_group.hermes.id} to use generative-ai-chat in compartment id ${oci_identity_compartment.stand.id} where target.model.id = '${local.model}'"
  ]
}
