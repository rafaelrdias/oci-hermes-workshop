output "public_ip" { value = oci_core_instance.hermes.public_ip }
output "instance_id" { value = oci_core_instance.hermes.id }
output "compartment_id" { value = oci_identity_compartment.stand.id }
output "image_id" { value = oci_core_instance.hermes.source_details[0].source_id }
output "region" { value = var.region }
output "iam_home_region" {
  value       = local.home_region
  description = "Endpoint usado para criar IAM global. VM, rede e modelo permanecem em region."
}
output "model" { value = local.model }
output "ssh_private_key_pem" {
  value       = var.generate_ssh_key ? tls_private_key.ssh[0].private_key_pem : ""
  sensitive   = true
  description = "Somente geração automática: salve o conteúdo completo como hermes.key em texto puro. Segredo persiste no state; nunca compartilhe. Vazio se não foi gerado."
}
output "ssh_public_key" {
  value       = local.effective_ssh_public_key
  description = "Chave pública instalada na criação da VM. Não é a chave privada."
}
output "ssh_connection_command" {
  value       = local.ssh_key_configured && var.ssh_allowed_cidr != "" ? "ssh -i hermes.key opc@${oci_core_instance.hermes.public_ip}" : "SSH fechado: informe um CIDR permitido e configure uma chave para conectar."
  description = "Execute no computador onde salvou a chave privada como hermes.key, ou ajuste o caminho para sua chave existente."
}
output "next_step" {
  value = "Copie telegram_pairing_command e envie em mensagem privada ao seu bot. Ele avisará quando inferência, ferramentas e gateway estiverem prontos. Apply não comprova a conversa final."
}
output "telegram_pairing_command" {
  value       = "/start ${local.pairing_code}"
  description = "Código temporário de vínculo. Não compartilhe: o primeiro usuário que o enviar em DM será o dono autorizado."
  sensitive   = true
}
