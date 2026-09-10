# Variante GRU — OCI Trial criado em São Paulo

> **Atenção — disponibilidade revisada em 10/09/2026:** GPT-OSS em GRU aparece
> como **dedicated only** na [matriz Oracle](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm).
> Criar Project não o transforma em on-demand. Não use o GPT-OSS desta variante
> histórica como promessa de implantação Trial sem cluster. Para a edição
> automatizada com modelo on-demand em GRU, use [stand/](../stand/README.md),
> que escolhe Llama 3.3 70B e não cria infraestrutura dedicada.

Este é o caminho alternativo para participantes cuja tenancy Trial usa
**Brazil East (São Paulo)** como home region:

```text
Region identifier: sa-saopaulo-1
Region key:        GRU
```

Para Chicago/ORD, continue usando o
[guia principal](OCI_RESOURCE_MANAGER_CONSOLE.md).

## 1. Baixar a pasta correta

Use somente:

**[Baixar Terraform GRU](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder-gru.zip)**

O GitHub usa ZIP apenas para transportar a pasta. Extraia uma vez e localize:

```text
oci-hermes-workshop-resource-manager-folder-gru
```

Não selecione a pasta ORD, o repositório inteiro ou uma pasta que contenha
`.terraform`.

## 2. Selecionar São Paulo

Antes de abrir o Resource Manager:

1. use o seletor de região da barra superior;
2. escolha **Brazil East (São Paulo)**;
3. confirme `sa-saopaulo-1`;
4. mantenha essa região durante todo o laboratório.

## 3. Criar a Stack

1. abra **Developer Services → Resource Manager → Stacks**;
2. clique em **Create stack**;
3. escolha **My configuration → Folder**;
4. selecione `oci-hermes-workshop-resource-manager-folder-gru`;
5. use o nome `hermes-oci-workshop-gru`;
6. escolha o compartment do laboratório;
7. confirme uma Terraform version compatível com `>= 1.5`;
8. avance para as variáveis.

## 4. Preencher as variáveis

| Variável | Valor |
|---|---|
| `region` | `sa-saopaulo-1` |
| `genai_region` | `sa-saopaulo-1` |
| `genai_model` | `openai.gpt-oss-120b` |
| `prefix` | `hermes-gru` |

Preencha `tenancy_ocid`, `compartment_ocid`, `ssh_public_key` e
`ssh_allowed_cidr`. Mantenha `create_genai_policy = true` quando sua conta
puder criar policies.

Nunca cole API key, token do Telegram ou chave SSH privada nas variáveis.

## 5. Plan e Apply

1. crie a Stack com **Run apply** desmarcado;
2. execute **Plan** e revise os Logs;
3. aguarde `SUCCEEDED`;
4. execute **Apply** selecionando o Plan mais recente;
5. aguarde `SUCCEEDED`;
6. abra **Outputs**.

Confirme:

```text
deployment_region = sa-saopaulo-1 (GRU)
genai_base_url     = https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com/openai/v1
genai_project_ocid = ocid1.generativeaiproject...
```

O Apply cria automaticamente o OCI Generative AI Project necessário para a
nova API OpenAI-compatible.

## 6. Escolher o modelo

O padrão é `openai.gpt-oss-120b`. Antes do evento, confirme sua disponibilidade
na Console do Generative AI em GRU.

Se o modelo não estiver liberado para a tenancy, altere `genai_model` para:

```text
openai.gpt-oss-20b
```

Gere um novo Plan e Apply. Não tente criar Dedicated AI Cluster no Trial.

## 7. Criar a API key em GRU

Depois do Apply:

1. mantenha a Console em **Brazil East (São Paulo)**;
2. abra **Analytics & AI → AI Services → Generative AI → API keys**;
3. escolha o mesmo compartment;
4. clique em **Create API key**;
5. crie `hermes-workshop-gru-key`;
6. copie imediatamente um secret `sk-...`.

A key precisa estar em GRU, na mesma região do Project e do modelo. Não use uma
key criada em Chicago.

## 8. Configurar Hermes e Telegram

Use `public_ip`:

```bash
ssh -i <chave-privada> opc@<public_ip> 'cloud-init status --wait'
ssh -t -i <chave-privada> opc@<public_ip> 'hermes-workshop-configure'
```

O configurador já conhece `genai_project_ocid`; você informa somente o secret
da API key, o token do `@BotFather` e, opcionalmente, o Telegram user ID.

Se deixar o user ID vazio, abra o link do bot, toque em **Start**, copie o
código e aprove:

```bash
ssh -i <chave-privada> opc@<public_ip> \
  'hermes pairing approve telegram CODIGO'
```

Depois envie `/new`.

## 9. Diagnóstico

```bash
ssh -i <chave-privada> opc@<public_ip> \
  'sudo systemctl status hermes-gateway --no-pager'

ssh -i <chave-privada> opc@<public_ip> \
  'sudo journalctl -u hermes-gateway -n 100 --no-pager'
```

| Sintoma | Verificação |
|---|---|
| `401` | API key `sk-...` ativa e criada em GRU |
| `403` | policy, compartment, Project OCID e modelo |
| `404` | base URL `/openai/v1`, região e model ID |
| Project ausente | confirme `genai_project_ocid` nos Outputs |
| Modelo indisponível | tente `openai.gpt-oss-20b` e gere novo Plan |

## 10. Destroy

Execute **Destroy**, aguarde `SUCCEEDED`, confirme que **Stack resources** está
vazia e somente então exclua a Stack. Isso remove também o OCI Generative AI
Project criado pelo Terraform.

## Referências oficiais

- [OCI Generative AI Regions](https://docs.oracle.com/en-us/iaas/Content/generative-ai/regions.htm)
- [Agentic models and regions](https://docs.oracle.com/en-us/iaas/Content/generative-ai/agentic-regions.htm)
- [Regional availability for models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm)
- [OCI OpenAI-compatible endpoints](https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-compatible-api.htm)
- [Creating a Project](https://docs.oracle.com/en-us/iaas/Content/generative-ai/create-project.htm)
