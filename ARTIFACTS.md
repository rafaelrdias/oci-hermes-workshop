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

## Pasta do OCI Resource Manager

O download recomendado é a branch leve:

```text
https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip
```

Depois de extrair, na Console OCI use **My configuration → Folder** e selecione:

```text
oci-hermes-workshop-resource-manager-folder
```

A pasta extraída tem cerca de 60 KB e não contém `.terraform`, providers locais, apresentações, state ou segredos.

O pacote abaixo é opcional e permanece disponível somente para automação ou compatibilidade:

```bash
infra/terraform/oci-trial-deploy/build-resource-manager-zip.sh
unzip -l infra/terraform/oci-trial-deploy/dist/oci-hermes-resource-manager.zip
```

Saída:

```text
infra/terraform/oci-trial-deploy/dist/oci-hermes-resource-manager.zip
```

O ZIP inclui `files/bootstrap-hermes-server.sh` e `files/configure-hermes-server.sh`. Não inclui `.terraform`, state, plano ou `terraform.tfvars`.

## Apresentação do workshop

```text
presentation/oci-enterprise-ai-hermes-agent-workshop-TDC_v3.pptx
```

A apresentação reaproveita o template Oracle do material-base e cobre catálogo de LLMs, modalidades on-demand e Dedicated AI Cluster, Hermes Agent, arquitetura OCI + Telegram, segurança, cronograma e checkpoints da atividade.

## Verificar a VM

```bash
ssh hermes-oci 'hermes --version'
ssh hermes-oci 'hermes doctor'
ssh hermes-oci 'sudo systemctl status hermes-gateway --no-pager'
```
