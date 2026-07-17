# Artefatos e validação

## Validar

```bash
terraform -chdir=infra/terraform/oci-trial-deploy fmt -check -recursive
terraform -chdir=infra/terraform/oci-trial-deploy validate
bash -n \
  infra/terraform/oci-trial-deploy/files/bootstrap-hermes-server.sh \
  infra/terraform/oci-trial-deploy/files/configure-hermes-server.sh
git diff --check
```

## Gerar Stack do OCI Resource Manager

```bash
infra/terraform/oci-trial-deploy/build-resource-manager-zip.sh
unzip -l infra/terraform/oci-trial-deploy/dist/oci-hermes-resource-manager.zip
```

Saída:

```text
infra/terraform/oci-trial-deploy/dist/oci-hermes-resource-manager.zip
```

O ZIP inclui `files/bootstrap-hermes-server.sh` e `files/configure-hermes-server.sh`. Não inclui `.terraform`, state, plano ou `terraform.tfvars`.

## Verificar a VM

```bash
ssh hermes-oci 'hermes --version'
ssh hermes-oci 'hermes doctor'
ssh hermes-oci 'sudo systemctl status hermes-gateway --no-pager'
```
