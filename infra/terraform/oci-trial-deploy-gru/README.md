# Terraform alternativo — OCI Trial em São Paulo (GRU)

Use esta variante somente quando a tenancy Trial foi criada em **Brazil East
(São Paulo)**: `sa-saopaulo-1`, region key `GRU`.

Todos os recursos regionais permanecem em GRU:

- Stack do OCI Resource Manager;
- VCN, subnet pública, Internet Gateway e regras de rede;
- VM Oracle Linux do Hermes;
- OCI Generative AI Project;
- OCI Generative AI API key criada manualmente;
- endpoint OpenAI-compatible e inferência do modelo.

IAM policies pertencem à tenancy e não são recursos regionais.

## Escolha rápida

| Home region do Trial | Use esta configuração |
|---|---|
| São Paulo — `sa-saopaulo-1` / GRU | **Esta pasta** |
| Chicago — `us-chicago-1` / ORD | [`../oci-trial-deploy`](../oci-trial-deploy) |

Para usar a Console sem instalar Terraform, baixe a branch leve:

**[Baixar a pasta Terraform GRU](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder-gru.zip)**

Extraia uma vez e selecione esta pasta no Resource Manager:

```text
oci-hermes-workshop-resource-manager-folder-gru
```

## Arquitetura

```text
Telegram
   ↓ HTTPS long polling
Hermes Agent na VM — sa-saopaulo-1
   ↓ OpenAI-compatible Chat Completions
OCI Generative AI Project — sa-saopaulo-1
   ↓
openai.gpt-oss-120b — GRU
```

O stack cria um `oci_generative_ai_project` e configura:

```text
https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com/openai/v1
```

O OCID do Project é enviado pelo header `OpenAI-Project`. A versão do Hermes
fixada pelo workshop suporta `extra_headers` em providers customizados.

## Modelo

O modelo padrão é:

```text
openai.gpt-oss-120b
```

Se a tenancy não oferecer esse modelo no momento do laboratório, tente o
modelo menor da mesma família:

```text
openai.gpt-oss-20b
```

Altere somente a variável `genai_model` antes do Plan. Não use um modelo de
outra região ou um modelo marcado apenas para Dedicated AI Cluster em um Trial.
Confira o catálogo na Console antes do workshop, pois disponibilidade e
capacidade podem mudar.

## Recursos criados

- OCI Generative AI Project;
- VCN e subnet pública;
- Internet Gateway e route table;
- security list com somente SSH de entrada;
- VM Oracle Linux;
- policy para API keys chamarem somente Chat Completions no modelo escolhido;
- cloud-init que instala Hermes Agent e gateway do Telegram.

Segredos não são criados pelo Terraform e não entram no state.

## Variáveis principais

Na Console do Resource Manager, mantenha:

```text
region       = sa-saopaulo-1
genai_region = sa-saopaulo-1
genai_model  = openai.gpt-oss-120b
prefix       = hermes-gru
```

Preencha:

- `tenancy_ocid`;
- `compartment_ocid`;
- `ssh_public_key`;
- `ssh_allowed_cidr`, preferencialmente seu IP público com `/32`.

Não cole API key, token do Telegram ou chave SSH privada nas variáveis.

## Execução pelo OCI Resource Manager

1. selecione **Brazil East (São Paulo)** na barra superior da Console;
2. abra **Developer Services → Resource Manager → Stacks**;
3. clique em **Create stack**;
4. escolha **My configuration → Folder**;
5. selecione `oci-hermes-workshop-resource-manager-folder-gru`;
6. preencha as variáveis;
7. crie a Stack com **Run apply** desmarcado;
8. execute **Plan** e revise os Logs;
9. execute **Apply** usando o último Plan;
10. em **Outputs**, confirme `deployment_region = sa-saopaulo-1 (GRU)`.

Guia específico:

https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/GRU_RESOURCE_MANAGER.md

## API key e Telegram

Depois do Apply:

1. mantenha a Console em **Brazil East (São Paulo)**;
2. abra **Analytics & AI → AI Services → Generative AI → API keys**;
3. crie a key no mesmo compartment;
4. copie imediatamente um secret `sk-...`;
5. crie o bot com `/newbot` no `@BotFather`;
6. guarde o token e o link do bot.

O Project já foi criado pelo Terraform. Copie seu OCID em `genai_project_ocid`
apenas para diagnóstico; o cloud-init já o entregou ao Hermes.

## Configurar a VM

Use o `public_ip` dos Outputs:

```bash
ssh -i <chave-privada> opc@<public_ip> 'cloud-init status --wait'
ssh -t -i <chave-privada> opc@<public_ip> 'hermes-workshop-configure'
```

O configurador:

1. lê o Project OCID criado pelo Terraform;
2. solicita a OCI Generative AI API key com entrada oculta;
3. testa o modelo em GRU;
4. solicita o token do BotFather;
5. inicia o gateway do Telegram.

## Pairing e primeiro teste

Abra o link do bot, toque em **Start** e copie o código de pairing:

```bash
ssh -i <chave-privada> opc@<public_ip> \
  'hermes pairing approve telegram CODIGO'
```

Depois envie `/new`.

## Execução local opcional

```bash
cd infra/terraform/oci-trial-deploy-gru
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
terraform plan -out workshop-gru.tfplan
terraform apply workshop-gru.tfplan
```

## Destruir ao final

No Resource Manager:

1. abra a Stack;
2. execute **Destroy**;
3. aguarde `SUCCEEDED`;
4. confirme que **Stack resources** está vazia;
5. somente então exclua a Stack.

## Referências oficiais

- [Regiões do OCI Generative AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/regions.htm)
- [Modelos e regiões para endpoints OpenAI-compatible](https://docs.oracle.com/en-us/iaas/Content/generative-ai/agentic-regions.htm)
- [OpenAI gpt-oss por região](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm)
- [QuickStart da OCI Responses API e Projects](https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started-agents.htm)
- [Criar um Project](https://docs.oracle.com/en-us/iaas/Content/generative-ai/create-project.htm)
- [Hermes — providers customizados](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/integrations/providers.md)
