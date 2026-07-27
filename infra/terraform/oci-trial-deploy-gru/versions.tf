terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 8.21.0, < 9.0.0"
    }
  }
}

provider "oci" {
  region = var.region
}
