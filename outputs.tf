output "instance_id" {
  description = "OCI instance OCID."
  value       = oci_core_instance.hermes.id
}

output "public_ip" {
  description = "Public IP assigned to the Hermes worker."
  value       = oci_core_instance.hermes.public_ip
}

output "deployment_region" {
  description = "OCI region used for all regional workshop resources."
  value       = "${var.region} (ORD)"
}

output "remote_workdir" {
  description = "Directory used for remote Hermes tasks."
  value       = var.remote_workdir
}

output "genai_base_url" {
  description = "OCI Generative AI OpenAI SDK base URL configured in Hermes."
  value       = local.hermes_base_url
}

output "genai_model" {
  description = "OCI Generative AI model configured in Hermes."
  value       = var.genai_model
}

output "ssh_command" {
  description = "SSH command template for the opc user."
  value       = "ssh -i <private-key-file> opc@${oci_core_instance.hermes.public_ip}"
}

output "ssh_config_alias" {
  description = "Suggested local SSH host alias."
  value       = local.ssh_config_alias
}

output "ssh_config_entry" {
  description = "Suggested ~/.ssh/config entry."
  value       = <<-EOT
Host ${local.ssh_config_alias}
  HostName ${oci_core_instance.hermes.public_ip}
  User opc
  IdentityFile <private-key-file>
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
  UpdateHostKeys no
EOT
}

output "validation_commands" {
  description = "Commands to validate the worker."
  value = [
    "ssh ${local.ssh_config_alias} 'cloud-init status --wait'",
    "ssh ${local.ssh_config_alias} 'sudo tail -n 80 /var/log/hermes-bootstrap.log'",
    "ssh ${local.ssh_config_alias} 'hermes-worker-ready'",
    "ssh -t ${local.ssh_config_alias} 'hermes-workshop-configure'",
  ]
}

output "next_steps" {
  description = "Commands to finish the secret configuration without putting secrets in Terraform state."
  value       = <<-EOT
1. Wait: ssh ${local.ssh_config_alias} 'cloud-init status --wait'
2. Configure secrets: ssh -t ${local.ssh_config_alias} 'hermes-workshop-configure'
3. Verify: ssh ${local.ssh_config_alias} 'sudo systemctl status hermes-gateway --no-pager'
EOT
}
