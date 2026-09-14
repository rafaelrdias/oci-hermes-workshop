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

variable "llm_model" {
  type        = string
  default     = "openai.gpt-oss-120b"
  description = "GPT-OSS 120B em ORD (padrão). Grok é opcional; Llama é alternativa explícita para GRU; sem fallback automático."
  validation {
    condition     = contains(["openai.gpt-oss-120b", "xai.grok-4.3", "xai.grok-4.6", "meta.llama-3.3-70b-instruct"], var.llm_model)
    error_message = "Selecione GPT-OSS 120B, Grok 4.3, Grok 4.6 ou Llama 3.3 70B."
  }
}

variable "stt_enabled" {
  type        = bool
  default     = true
  description = "Transcrição local gratuita de API, Whisper base em CPU. Consome CPU/RAM da VM; respostas somente texto."
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
  default = "hermes-evento"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,29}$", var.prefix))
    error_message = "Use 3–30 caracteres: letras minúsculas, números e hífen."
  }
}

variable "generate_ssh_key" {
  type        = bool
  default     = false
  description = "Gerar par RSA 4096 exclusivo desta Stack. A chave privada persiste no state e fica em uma saída sensível. Não abre SSH sem CIDR."
}

variable "acknowledge_ssh_private_key_in_state" {
  type        = bool
  default     = false
  description = "Aceito que a chave SSH privada gerada fique no state e nas saídas da Stack; restrinjo acesso e guardarei uma cópia pessoal segura."
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
  description = "Opcional: IPv4 /32 recomendado, ou 0.0.0.0/0 com aceite explícito para acesso de qualquer IPv4. Vazio mantém TCP/22 fechado."
  validation {
    condition     = var.ssh_allowed_cidr == "" || var.ssh_allowed_cidr == "0.0.0.0/0" || (can(cidrnetmask(var.ssh_allowed_cidr)) && can(regex("/32$", var.ssh_allowed_cidr)))
    error_message = "Use um IPv4 /32, ou 0.0.0.0/0 com aceite de exposição pública, ou deixe vazio para desabilitar SSH."
  }
}

variable "acknowledge_public_ssh" {
  type        = bool
  default     = false
  description = "Aceito expor TCP/22 a qualquer IPv4 com 0.0.0.0/0 temporariamente. Uma chave gerada ou fornecida continua obrigatória; restringirei o acesso após o evento."
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
