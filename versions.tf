terraform {
  required_version = ">= 1.5.0, < 2.0.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "8.21.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.3.0"
    }
  }
}

# Resource Manager injects authentication. No user API key is needed.
provider "oci" {
  region       = var.region
  tenancy_ocid = var.tenancy_ocid
}

# IAM is global, but its write API must use the tenancy's home region.
# Authentication is also injected by Resource Manager for this provider alias.
provider "oci" {
  alias        = "home"
  region       = local.home_region
  tenancy_ocid = var.tenancy_ocid
}
