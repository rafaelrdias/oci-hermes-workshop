# Pasta Terraform GRU para OCI Resource Manager

Esta branch contém somente a configuração para participantes cuja tenancy
Trial usa **Brazil East (São Paulo)**:

```text
sa-saopaulo-1 / GRU
```

Ela cria rede, VM Oracle Linux, policy e OCI Generative AI Project em GRU,
instala Hermes Agent e prepara o endpoint OpenAI-compatible do modelo.

## Download e uso

1. use **[Download da pasta Terraform GRU](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder-gru.zip)**;
2. extraia o download uma vez;
3. selecione **Brazil East (São Paulo)** na OCI Console;
4. abra **Developer Services → Resource Manager → Stacks → Create stack**;
5. escolha **My configuration → Folder**;
6. selecione `oci-hermes-workshop-resource-manager-folder-gru`;
7. mantenha `region` e `genai_region` como `sa-saopaulo-1`;
8. execute Plan e Apply.

## Modelo

Padrão:

```text
openai.gpt-oss-120b
```

Fallback para a mesma superfície em GRU:

```text
openai.gpt-oss-20b
```

Altere `genai_model` somente se o modelo maior não estiver disponível para a
tenancy.

## Guias

Resource Manager em GRU:

https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/GRU_RESOURCE_MANAGER.md

API key, BotFather e primeira conversa:

https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/OCI_API_KEY_TELEGRAM.md

> Esta pasta não contém `.terraform`, providers locais, state, apresentações
> ou segredos. Nunca adicione API keys, token do BotFather, chave SSH privada
> ou `terraform.tfvars`.
