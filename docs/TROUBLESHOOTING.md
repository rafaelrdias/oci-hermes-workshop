# Troubleshooting rápido

## Terraform: `NotAuthorizedOrNotFound` ao criar policy

O usuário não pode criar policies no root compartment. Defina:

```hcl
create_genai_policy = false
```

Peça a um administrador para criar a statement descrita em [ENTERPRISE_AI.md](ENTERPRISE_AI.md).

## Terraform: `Out of host capacity`

Ocorre com frequência em A1 Always Free. Tente outro Availability Domain ou use o preset E5 com créditos Trial.

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
- a key foi criada em outra região;
- ela expirou, foi desativada ou revogada;
- `OPENAI_API_KEY` não foi gravada corretamente.

Reexecute `hermes-workshop-configure`; ele substitui os valores sem mostrá-los.

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

## Bot não responde

```bash
ssh hermes-oci 'sudo systemctl status hermes-gateway --no-pager'
ssh hermes-oci 'sudo journalctl -u hermes-gateway -n 100 --no-pager'
```

Confira token, allowlist e se outro processo usa o mesmo bot token. Um token não deve operar em dois gateways ao mesmo tempo.

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
