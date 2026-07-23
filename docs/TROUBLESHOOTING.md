# Troubleshooting rápido

## Resource Manager: pasta excede 11 MB após compressão

Mensagem:

```text
After compression, this folder exceeds the maximum size (11 MB).
Reduce the size of the folder and try again.
```

Foi selecionado o repositório completo ou uma pasta de desenvolvimento com o diretório oculto `.terraform`, que pode conter centenas de megabytes de providers.

Use a pasta limpa:

1. baixe **[a pasta Terraform leve](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip)**;
2. extraia o download uma vez;
3. escolha **My configuration → Folder**;
4. selecione somente `oci-hermes-workshop-resource-manager-folder`.

Essa pasta contém cerca de 60 KB. Não selecione `oci-hermes-workshop-main`, `.terraform` ou o repositório de desenvolvimento.

## Terraform: `NotAuthorizedOrNotFound` ao criar policy

O usuário não pode criar policies no root compartment. Defina:

```hcl
create_genai_policy = false
```

Peça a um administrador para criar a statement descrita em [ENTERPRISE_AI.md](ENTERPRISE_AI.md).

## Terraform: `Out of host capacity`

Ocorre com frequência em A1 Always Free. Permaneça em Chicago e tente outro Availability Domain de `us-chicago-1`, ou use o preset E5 com créditos Trial. Não troque a Stack para outra região durante o workshop.

## SSH não conecta

```bash
terraform output public_ip
terraform output ssh_config_entry
ssh -vvv hermes-oci
```

Confira `ssh_allowed_cidr`, o caminho da chave privada e permissões `chmod 600`.

## Cloud-init ainda está rodando

```bash
ssh hermes-oci 'cloud-init status --wait'
ssh hermes-oci 'sudo tail -f /var/log/cloud-init-output.log'
ssh hermes-oci 'sudo tail -f /var/log/hermes-bootstrap.log'
```

## OCI retorna 401

- o segredo copiado não é uma OCI Generative AI API key;
- foi copiado o OCID da API key em vez do secret `sk-...`;
- a key não foi criada em US Midwest (Chicago);
- ela expirou, foi desativada ou revogada;
- `OPENAI_API_KEY` não foi gravada corretamente.

Reexecute `hermes-workshop-configure`; ele substitui os valores sem mostrá-los.
Consulte também o [guia visual de criação da API key](OCI_API_KEY_TELEGRAM.md#parte-1--criar-a-api-key-openai-compatible-na-oci).

## OCI retorna 403/404

- policy ainda não propagou;
- model ID ou region estão errados;
- o modelo não está on-demand naquela região;
- a API key pertence a outro compartment/escopo.

Padrão testado:

```text
region: us-chicago-1
model: openai.gpt-oss-120b
base URL: https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1
```

Se `terraform plan` rejeitar `region` ou `genai_region`, use `us-chicago-1` nos dois campos. A validação impede a criação de recursos regionais fora de ORD.

## Bot não responde

Confirme primeiro que você abriu o link `https://t.me/<username>` entregue pelo
BotFather e tocou em **Start**. Bots não podem iniciar a conversa com usuários.

```bash
ssh hermes-oci 'sudo systemctl status hermes-gateway --no-pager'
ssh hermes-oci 'sudo journalctl -u hermes-gateway -n 100 --no-pager'
```

Confira token, allowlist e se outro processo usa o mesmo bot token. Um token não deve operar em dois gateways ao mesmo tempo.
Veja o [fluxo completo de BotFather, pairing e primeira conversa](OCI_API_KEY_TELEGRAM.md#parte-2--criar-o-bot-com-o-botfather).

### `status=203/EXEC` no Oracle Linux com SELinux

O bootstrap instala automaticamente um override quando o SELinux está em modo
`Enforcing`. Ele inicia o Python do Hermes por `/usr/bin/bash`, mantendo o
serviço como usuário `opc` e permitindo a transição SELinux adequada.

Confirme que o drop-in foi carregado:

```bash
sudo systemctl cat hermes-gateway
sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway
```

O status deve listar
`/etc/systemd/system/hermes-gateway.service.d/selinux.conf`.

## Bot retorna código de pairing

Comportamento esperado quando não há allowlist:

```bash
ssh hermes-oci 'hermes pairing approve telegram CODIGO'
```

## Alterei a configuração

```bash
ssh hermes-oci 'sudo systemctl restart hermes-gateway'
```

## Diagnóstico geral

```bash
ssh hermes-oci 'hermes doctor'
ssh hermes-oci 'hermes gateway status --system --deep'
```
