output "public_ip" { value = oci_core_instance.hermes.public_ip }
output "instance_id" { value = oci_core_instance.hermes.id }
output "compartment_id" { value = oci_identity_compartment.stand.id }
output "image_id" { value = oci_core_instance.hermes.source_details[0].source_id }
output "region" { value = var.region }
output "model" { value = local.model }
output "next_step" {
  value = "Copie telegram_pairing_command e envie em mensagem privada ao seu bot. Ele avisará quando inferência, ferramentas e gateway estiverem prontos. Apply não comprova a conversa final."
}
output "telegram_pairing_command" {
  value       = "/start ${local.pairing_code}"
  description = "Código temporário de vínculo. Não compartilhe: o primeiro usuário que o enviar em DM será o dono autorizado."
  sensitive   = true
}
