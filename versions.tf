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
  }
}

# Resource Manager injects authentication. No user API key is needed.
provider "oci" {
  region       = var.region
  tenancy_ocid = var.tenancy_ocid
}
