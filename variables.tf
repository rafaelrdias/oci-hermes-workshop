variable "tenancy_ocid" {
  type = string
  validation {
    condition     = can(regex("^ocid1.tenancy\\.", var.tenancy_ocid))
    error_message = "Informe um tenancy OCID válido."
  }
}

variable "region" {
  type        = string
  description = "Região da instalação (ORD ou GRU), subscrita nesta tenancy. Pode ser diferente da home region."
  validation {
    condition     = contains(["us-chicago-1", "sa-saopaulo-1"], var.region)
    error_message = "Esta edição suporta apenas ORD ou GRU, sem fallback entre regiões."
  }
}

variable "telegram_bot_token" {
  type        = string
  sensitive   = true
  description = "Token exclusivo do BotFather. Persiste no state e nos metadados da VM; restrinja acesso."
  validation {
    condition     = can(regex("^[0-9]{5,15}:[A-Za-z0-9_-]{30,100}$", var.telegram_bot_token))
    error_message = "Informe um token válido do BotFather, sem espaços ou quebras de linha."
  }
}

variable "acknowledge_secret_in_state" {
  type        = bool
  default     = false
  description = "Aceito que o token, embora mascarado, persista na Stack/state/metadados; uso bot exclusivo e conta pessoal."
  validation {
    condition     = var.acknowledge_secret_in_state
    error_message = "É necessário aceitar explicitamente a persistência do token antes do Plan/Apply."
  }
}

variable "prefix" {
  type    = string
  default = "hermes-stand"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,29}$", var.prefix))
    error_message = "Use 3–30 caracteres: letras minúsculas, números e hífen."
  }
}

variable "ssh_public_key" {
  type    = string
  default = ""
  validation {
    condition     = var.ssh_public_key == "" || can(regex("^ssh-(ed25519|rsa) ", trimspace(var.ssh_public_key)))
    error_message = "Opcional: informe somente a chave PÚBLICA SSH."
  }
}

variable "ssh_allowed_cidr" {
  type        = string
  default     = ""
  description = "Opcional: IPv4 do administrador /32. Vazio mantém TCP/22 fechado."
  validation {
    condition     = var.ssh_allowed_cidr == "" || (can(cidrnetmask(var.ssh_allowed_cidr)) && can(regex("/32$", var.ssh_allowed_cidr)))
    error_message = "SSH deve ficar restrito a um único IPv4 (/32)."
  }
}

variable "instance_shape" {
  type    = string
  default = "VM.Standard.E5.Flex"
  validation {
    condition     = contains(["VM.Standard.E5.Flex", "VM.Standard.E4.Flex", "VM.Standard.A1.Flex"], var.instance_shape)
    error_message = "Use E5.Flex, E4.Flex ou A1.Flex; não há troca automática com aumento de custo."
  }
}

variable "availability_domain_index" {
  type    = number
  default = 0
  validation {
    condition     = var.availability_domain_index >= 0 && floor(var.availability_domain_index) == var.availability_domain_index
    error_message = "O índice do AD deve ser inteiro >= 0."
  }
}

variable "image_ocid" {
  type        = string
  default     = ""
  description = "Vazio: imagem Oracle Linux 9 mais recente. A imagem de uma VM existente não muda automaticamente."
}
