variable "region" {
  description = "OCI region for the Resource Manager stack, network and VM. The workshop is fixed to US Midwest (Chicago), region key ORD."
  type        = string
  default     = "us-chicago-1"

  validation {
    condition     = var.region == "us-chicago-1"
    error_message = "This workshop must run in US Midwest (Chicago): region must be us-chicago-1 (ORD)."
  }
}

variable "tenancy_ocid" {
  description = "Tenancy OCID. Required only to create the least-privilege Generative AI policy."
  type        = string
}

variable "compartment_ocid" {
  description = "Compartment OCID where the worker will be created."
  type        = string
}

variable "prefix" {
  description = "Name prefix for OCI resources."
  type        = string
  default     = "hermes-worker"
}

variable "create_genai_policy" {
  description = "Create an IAM policy allowing OCI Generative AI API keys to invoke only the workshop chat model."
  type        = bool
  default     = true
}

variable "genai_region" {
  description = "OCI Generative AI region. Fixed to US Midwest (Chicago) so all regional workshop resources stay in ORD."
  type        = string
  default     = "us-chicago-1"

  validation {
    condition     = var.genai_region == "us-chicago-1"
    error_message = "OCI Generative AI must run in US Midwest (Chicago): genai_region must be us-chicago-1 (ORD)."
  }
}

variable "genai_model" {
  description = "OCI Generative AI model used by Hermes."
  type        = string
  default     = "openai.gpt-oss-120b"
}

variable "hermes_git_ref" {
  description = "Hermes Agent release tag installed by cloud-init. Pin this for a reproducible workshop."
  type        = string
  default     = "v2026.7.7.2"
}

variable "install_browser_tools" {
  description = "Install the Playwright browser runtime. Disabled by default to make workshop bootstrap faster."
  type        = bool
  default     = false
}

variable "ssh_public_key" {
  description = "Public SSH key authorized for opc."
  type        = string

  validation {
    condition     = can(regex("^(ssh-rsa|ssh-ed25519|ecdsa-sha2-[^ ]+|sk-ssh-ed25519@openssh.com|sk-ecdsa-sha2-nistp256@openssh.com) [A-Za-z0-9+/=]+", trimspace(var.ssh_public_key)))
    error_message = "ssh_public_key must be a valid OpenSSH public key."
  }
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to access SSH. Prefer your public IP with /32."
  type        = string

  validation {
    condition     = can(cidrnetmask(var.ssh_allowed_cidr))
    error_message = "ssh_allowed_cidr must be a valid IPv4 CIDR, preferably your public IP with /32."
  }
}

variable "ssh_config_alias" {
  description = "Suggested local SSH alias."
  type        = string
  default     = "hermes-oci"
}

variable "remote_workdir" {
  description = "Remote directory used by Hermes task execution."
  type        = string
  default     = "/home/opc/hermes-tasks"
}

variable "vcn_cidr" {
  description = "CIDR block for the VCN."
  type        = string
  default     = "10.20.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.20.10.0/24"
}

variable "availability_domain_index" {
  description = "Index of the availability domain returned by OCI."
  type        = number
  default     = 0
}

variable "instance_shape" {
  description = "OCI compute shape. E5 consumes trial credits; A1 can fit Always Free limits but may lack capacity."
  type        = string
  default     = "VM.Standard.E5.Flex"
}

variable "instance_ocpus" {
  description = "OCPUs for flexible shapes."
  type        = number
  default     = 2
}

variable "instance_memory_in_gbs" {
  description = "Memory in GB for flexible shapes."
  type        = number
  default     = 16
}

variable "boot_volume_size_gbs" {
  description = "Boot volume size."
  type        = number
  default     = 80
}

variable "oracle_linux_version" {
  description = "Oracle Linux major version used to discover the image."
  type        = string
  default     = "9"
}

variable "image_ocid" {
  description = "Optional custom image OCID."
  type        = string
  default     = ""
}

variable "freeform_tags" {
  description = "Additional free-form tags applied to workshop resources."
  type        = map(string)
  default     = {}
}
