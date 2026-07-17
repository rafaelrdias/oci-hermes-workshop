# Hermes Agent + OCI Enterprise AI + Telegram

Material do workshop Oracle no TDC Florianópolis. O laboratório provisiona uma VM Oracle Linux, instala o [Hermes Agent oficial da Nous Research](https://github.com/NousResearch/hermes-agent), configura o modelo `openai.gpt-oss-120b` no OCI Generative AI e publica a interação por Telegram.

## O que está automatizado

- VCN, subnet pública, Internet Gateway, route table e security list;
- VM Oracle Linux com somente SSH exposto;
- Hermes Agent `v2026.7.7.2`, Python 3.11 e gateway do Telegram;
- serviço `systemd` para iniciar o gateway no boot;
- policy de menor privilégio para Chat Completions no modelo do workshop;
- comando interativo que grava os segredos diretamente na VM, sem colocá-los no Terraform state.

## Começo rápido

Pré-requisitos: Terraform 1.5+, credenciais OCI configuradas, OCIDs da tenancy e do compartment, chave SSH e um IP/CIDR autorizado para SSH.

```bash
cd infra/terraform/oci-trial-deploy
cp terraform.tfvars.example terraform.tfvars
# edite terraform.tfvars
terraform init
terraform validate
terraform plan -out workshop.tfplan
terraform apply workshop.tfplan
```

Copie `terraform output ssh_config_entry` para `~/.ssh/config`, substitua `<private-key-file>` e execute:

```bash
ssh hermes-oci 'cloud-init status --wait'
ssh hermes-oci 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
ssh -t hermes-oci 'hermes-workshop-configure'
```

O último comando solicita, com entrada oculta:

1. o segredo da OCI Generative AI API key;
2. o token criado no `@BotFather`;
3. opcionalmente, seu Telegram user ID. Se ficar vazio, use o pairing seguro.

Depois, envie `/new` ao bot. Se optou por pairing, envie qualquer mensagem e aprove o código na VM:

```bash
ssh hermes-oci 'hermes pairing approve telegram CODIGO'
```

Para preparar as credenciais em momentos diferentes, use `--oci-only`,
`--allowlist-only` e, quando o token do BotFather estiver disponível,
`--telegram-only`. O modo padrão `--full` executa as duas configurações.

## Material do workshop

- [Roteiro completo](docs/WORKSHOP_RUNBOOK.md)
- [OCI Enterprise AI e autenticação](docs/ENTERPRISE_AI.md)
- [Checklist do facilitador](docs/FACILITATOR_CHECKLIST.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Apresentação em Markdown](PRESENTATION.md)
- [Terraform](infra/terraform/oci-trial-deploy/README.md)

## Segurança

Não grave API keys ou tokens em `terraform.tfvars`, código, prints ou chat. O Telegram dá acesso às ferramentas do agente na VM; nunca habilite `GATEWAY_ALLOW_ALL_USERS=true`. Use allowlist ou pairing e destrua os ambientes dos participantes ao final:

```bash
terraform destroy
```

## Estado da VM de demonstração

Na VM `147.224.210.244`, o Hermes oficial está instalado, a chamada ao OCI
Generative AI foi validada, a allowlist do Telegram foi registrada e o gateway
está ativo. O bot de demonstração é `@rafadias_oci_bot`.
