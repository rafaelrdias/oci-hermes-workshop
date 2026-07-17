# Roteiro do participante — 60 minutos de atividade

O evento dura 90 minutos. A atividade foi desenhada para caber em 60; os 30 restantes protegem contra dúvidas, problemas de capacity, permissões IAM e digitação de credenciais.

## Resultado esperado

Ao final, uma mensagem enviada ao seu bot do Telegram chega ao Hermes na VM, o Hermes chama `openai.gpt-oss-120b` no OCI Generative AI e devolve a resposta pelo Telegram.

## Antes de começar

Tenha:

- acesso à OCI Console e à região home do Trial;
- Terraform ou acesso ao OCI Resource Manager;
- tenancy OCID e compartment OCID;
- uma chave pública SSH;
- Telegram instalado.

## 0–10 min — entender o fluxo

```text
Pessoa → Telegram → Hermes Gateway → Hermes Agent → OCI Generative AI
                                             ↘ ferramentas na VM
```

O Telegram usa long polling. A VM não recebe conexões do Telegram e não precisa expor webhook nem porta do Hermes.

## 10–20 min — preparar e aplicar o Terraform

```bash
git clone https://github.com/rafaelrdias/oci-hermes-workshop.git
cd oci-hermes-workshop/infra/terraform/oci-trial-deploy
cp terraform.tfvars.example terraform.tfvars
```

Edite `terraform.tfvars`, depois:

```bash
terraform init
terraform validate
terraform plan -out workshop.tfplan
terraform apply workshop.tfplan
```

Enquanto o cloud-init instala o Hermes, avance para as duas credenciais.

## 20–35 min — criar OCI Generative AI API key e bot

### OCI

Mude a Console para **US Midwest (Chicago)** e abra Analytics & AI → Generative AI → API keys. Crie uma chave no compartment do laboratório e copie o segredo `sk-...`.

### Telegram

No `@BotFather`:

1. `/newbot`;
2. escolha nome;
3. escolha username terminado em `bot`;
4. guarde o token.

Opcional: consulte seu ID numérico em `@userinfobot`. Sem ele, o pairing será feito depois.

## 35–45 min — acessar e configurar

Copie a saída abaixo para seu `~/.ssh/config` e ajuste o caminho da chave privada:

```bash
terraform output ssh_config_entry
```

Espere a conclusão:

```bash
ssh hermes-oci 'cloud-init status --wait'
ssh hermes-oci 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
```

Configure os segredos de forma interativa:

```bash
ssh -t hermes-oci 'hermes-workshop-configure'
```

## 45–55 min — testar no Telegram

Com allowlist, envie `/new` ao bot. Com pairing, envie uma mensagem, copie o código e aprove:

```bash
ssh hermes-oci 'hermes pairing approve telegram CODIGO'
```

Prompts de teste:

```text
Explique em três bullets quais componentes OCI sustentam você.
```

```text
Use uma ferramenta local para informar hostname, sistema operacional e espaço livre, sem modificar arquivos.
```

## 55–60 min — mini desafio

Peça ao Hermes para criar um arquivo `~/hermes-tasks/resultado.md` contendo:

- data e hostname;
- uma explicação curta da arquitetura;
- três cuidados de segurança.

Depois valide por SSH:

```bash
ssh hermes-oci 'sed -n "1,120p" ~/hermes-tasks/resultado.md'
```

## Encerramento

Pare o gateway ou destrua tudo:

```bash
ssh hermes-oci 'sudo systemctl stop hermes-gateway'
terraform destroy
```
