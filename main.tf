locals {
  ssh_public_key       = trimspace(var.ssh_public_key)
  image_id             = var.image_ocid != "" ? var.image_ocid : data.oci_core_images.oracle_linux.images[0].id
  ssh_config_alias     = var.ssh_config_alias != "" ? var.ssh_config_alias : "hermes-oci"
  hermes_base_url      = "https://inference.generativeai.${var.genai_region}.oci.oraclecloud.com/20231130/actions/v1"
  bootstrap_script_b64 = base64encode(file("${path.module}/files/bootstrap-hermes-server.sh"))
  configure_script_b64 = base64encode(file("${path.module}/files/configure-hermes-server.sh"))
  common_freeform_tags = merge(var.freeform_tags, { "workshop" = "tdc-hermes-oci" })
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

data "oci_core_images" "oracle_linux" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = var.oracle_linux_version
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "this" {
  compartment_id = var.compartment_ocid
  display_name   = "${var.prefix}-vcn"
  cidr_block     = var.vcn_cidr
  dns_label      = "hermes"
  freeform_tags  = local.common_freeform_tags
}

resource "oci_core_internet_gateway" "this" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.prefix}-igw"
  enabled        = true
  freeform_tags  = local.common_freeform_tags
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.prefix}-public-rt"
  freeform_tags  = local.common_freeform_tags

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.this.id
  }
}

resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.prefix}-public-sl"
  freeform_tags  = local.common_freeform_tags

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    source   = var.ssh_allowed_cidr
    protocol = "6"

    tcp_options {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.this.id
  display_name               = "${var.prefix}-public-subnet"
  cidr_block                 = var.subnet_cidr
  dns_label                  = "public"
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic = false
  freeform_tags              = local.common_freeform_tags
}

resource "oci_core_instance" "hermes" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[var.availability_domain_index].name
  compartment_id      = var.compartment_ocid
  display_name        = "${var.prefix}-worker"
  shape               = var.instance_shape
  freeform_tags       = local.common_freeform_tags

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    display_name     = "${var.prefix}-vnic"
    hostname_label   = "hermes"
  }

  source_details {
    source_type             = "image"
    source_id               = local.image_id
    boot_volume_size_in_gbs = var.boot_volume_size_gbs
  }

  metadata = {
    ssh_authorized_keys = local.ssh_public_key
    user_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tftpl", {
      remote_workdir        = var.remote_workdir
      hermes_git_ref        = var.hermes_git_ref
      install_browser_tools = tostring(var.install_browser_tools)
      genai_region          = var.genai_region
      genai_model           = var.genai_model
      hermes_base_url       = local.hermes_base_url
      bootstrap_script_b64  = local.bootstrap_script_b64
      configure_script_b64  = local.configure_script_b64
    }))
  }
}

# Hermes authenticates to OCI Generative AI with a service-specific API key.
# This policy authorizes only Chat Completions for the selected workshop model.
# The secret itself is intentionally created after Terraform so it never enters
# Terraform state.
resource "oci_identity_policy" "hermes_genai" {
  count = var.create_genai_policy ? 1 : 0

  compartment_id = var.tenancy_ocid
  name           = "${var.prefix}-genai-chat"
  description    = "Allow OCI Generative AI API keys to call the Hermes workshop model"
  statements = [
    "allow any-user to use generative-ai-chat in compartment id ${var.compartment_ocid} where ALL {request.principal.type='generativeaiapikey', target.model.id='${var.genai_model}'}"
  ]
  freeform_tags = local.common_freeform_tags
}
