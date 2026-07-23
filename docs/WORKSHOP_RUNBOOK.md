# Roteiro do participante — 60 minutos de atividade

O evento dura 90 minutos. A atividade foi desenhada para caber em 60; os 30 restantes protegem contra dúvidas, problemas de capacity, permissões IAM e digitação de credenciais.

## Resultado esperado

Ao final, uma mensagem enviada ao seu bot do Telegram chega ao Hermes na VM, o Hermes chama `openai.gpt-oss-120b` no OCI Generative AI e devolve a resposta pelo Telegram.

## Antes de começar

Tenha:

- acesso à OCI Console e à região **US Midwest (Chicago)** habilitada na tenancy Trial;
- acesso ao OCI Resource Manager;
- tenancy OCID e compartment OCID;
- uma chave pública SSH;
- seu IP público no formato `/32`;
- a pasta `oci-hermes-workshop-resource-manager-folder` obtida pelo [download leve do Terraform](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip);
- Telegram instalado.

Se faltar algum desses itens, conclua a seção de [preparação pela Console](OCI_RESOURCE_MANAGER_CONSOLE.md#preparação-pela-console--sem-instalar-ferramentas) antes de iniciar o cronômetro de 60 minutos.

## 0–10 min — entender o fluxo

```text
Pessoa → Telegram → Hermes Gateway → Hermes Agent → OCI Generative AI
                                             ↘ ferramentas na VM

                           VM, rede e modelo: us-chicago-1 / ORD
```

O Telegram usa long polling. A VM não recebe conexões do Telegram e não precisa expor webhook nem porta do Hermes.

## 10–20 min — preparar e aplicar o Terraform

Antes do primeiro passo, selecione **US Midwest (Chicago)** no canto superior da Console. A Stack, rede, VM e OCI Generative AI permanecerão nessa região.

Use o [guia visual da Console OCI](OCI_RESOURCE_MANAGER_CONSOLE.md):

1. se necessário, use a preparação visual do guia para obter Tenancy OCID, Compartment OCID e chaves SSH;
2. abra **Developer Services → Resource Manager → Stacks**;
3. extraia o download e localize `oci-hermes-workshop-resource-manager-folder`;
4. clique em **Create stack**, escolha **My configuration → Folder** e selecione essa pasta;
5. preencha tenancy, compartment, chave SSH pública e seu IP `/32`;
6. crie a Stack com **Run apply** desmarcado;
7. execute **Plan**, revise os Logs e aguarde **SUCCEEDED**;
8. execute **Apply** usando o último Plan e aguarde **SUCCEEDED**.

Enquanto o cloud-init instala o Hermes, avance para as duas credenciais.

## 20–35 min — criar OCI Generative AI API key e bot

### OCI

Mantenha a Console em **US Midwest (Chicago)** e abra Analytics & AI → Generative AI → API keys. Crie uma chave no compartment do laboratório e copie o segredo `sk-...`.

### Telegram

No `@BotFather`:

1. `/newbot`;
2. escolha nome;
3. escolha username terminado em `bot`;
4. guarde o token.

Opcional: consulte seu ID numérico em `@userinfobot`. Sem ele, o pairing será feito depois.

## 35–45 min — acessar e configurar

No job `apply-...` do Resource Manager, abra **Outputs**, confirme `deployment_region = us-chicago-1 (ORD)` e copie `public_ip`. Depois substitua os valores entre `<...>`:

```bash
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'cloud-init status --wait'
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
```

Configure os segredos de forma interativa:

```bash
ssh -t -i <caminho-da-chave-privada> opc@<public_ip> 'hermes-workshop-configure'
```

## 45–55 min — testar no Telegram

Com allowlist, envie `/new` ao bot. Com pairing, envie uma mensagem, copie o código e aprove:

```bash
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'hermes pairing approve telegram CODIGO'
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
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'sed -n "1,120p" ~/hermes-tasks/resultado.md'
```

## Encerramento

No Resource Manager, abra a Stack e execute **Destroy**. Aguarde **SUCCEEDED**, confirme que **Stack resources** está vazia e somente então use **Delete stack**. Veja a [tela e a ordem correta](OCI_RESOURCE_MANAGER_CONSOLE.md#9-destruir-os-recursos-ao-final).

Se precisar apenas parar temporariamente o gateway:

```bash
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'sudo systemctl stop hermes-gateway'
```

## Alternativa — Terraform no computador

Use este caminho somente se o facilitador optar pela execução local:

```bash
git clone https://github.com/rafaelrdias/oci-hermes-workshop.git
cd oci-hermes-workshop/infra/terraform/oci-trial-deploy
cp terraform.tfvars.example terraform.tfvars
# edite terraform.tfvars e mantenha region/genai_region = "us-chicago-1"
terraform init
terraform validate
terraform plan -out workshop.tfplan
terraform apply workshop.tfplan
```
