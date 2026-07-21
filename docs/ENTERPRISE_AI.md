# OCI Enterprise AI no workshop

## Por que esta integração funciona

O Hermes aceita endpoints OpenAI-compatible. O OCI Generative AI fornece Chat Completions e Responses API, com modelos hospedados na OCI e autenticação por OCI Generative AI API key ou IAM. Para este laboratório usamos a API key específica do serviço, porque o SDK OpenAI a envia diretamente como Bearer token e o Hermes não precisa de um adaptador de assinatura OCI.

Configuração aplicada:

```yaml
model:
  provider: custom:oci-genai
  default: openai.gpt-oss-120b
  base_url: https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1
  api_mode: chat_completions
  context_length: 128000

custom_providers:
  - name: oci-genai
    base_url: https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1
    key_env: OPENAI_API_KEY
    model: openai.gpt-oss-120b
    api_mode: chat_completions
```

O provider nomeado e `key_env` são importantes nas versões recentes do Hermes:
por segurança, o runtime não encaminha automaticamente `OPENAI_API_KEY` para
hosts diferentes de `openai.com` sem essa associação explícita.

O segredo fica em `~/.hermes/.env`:

```dotenv
OPENAI_API_KEY=sk-...
```

## Região única: Chicago (ORD)

Em julho de 2026, a documentação OCI identifica **US Midwest (Chicago)** como `us-chicago-1`, region key `ORD`. A região oferece `openai.gpt-oss-120b` on-demand e suporta API keys com SDKs OpenAI. Para simplificar o Trial e evitar troca de contexto regional, a Stack do Resource Manager, VCN, subnet, VM, API key do OCI Generative AI e endpoint do modelo ficam todos em Chicago.

IAM policies não pertencem a uma região: elas são recursos da tenancy. Esta é a única exceção ao princípio de região única do laboratório.

## Policy criada pelo Terraform

```text
allow any-user to use generative-ai-chat
in compartment id <COMPARTMENT_OCID>
where ALL {
  request.principal.type='generativeaiapikey',
  target.model.id='openai.gpt-oss-120b'
}
```

Ela não libera usuários anônimos: `any-user` é restringido pelo `where` ao principal autenticado do tipo `generativeaiapikey`. A policy também limita a operação a chat e ao modelo do workshop.

## Por que a chave não é criada pelo Terraform

O segredo é exibido apenas no momento da criação/rotação. Se passasse pelo Terraform, poderia persistir no state, no plano, em logs ou no OCI Resource Manager. O roteiro cria a policy pelo Terraform, mas insere o segredo diretamente na VM por prompt oculto.

## Próximo passo para produção

Para produção em recursos OCI gerenciados, a Oracle recomenda IAM-based authentication. A documentação atual fornece o pacote `oci-genai-auth` para integrar assinatura IAM ao SDK OpenAI. O Hermes não oferece esse provider OCI de primeira classe nesta versão; adotar IAM exigiria um pequeno adaptador/proxy ou contribuição upstream. Isso é um bom tópico avançado, mas não cabe no caminho crítico de 60 minutos.

## Fontes oficiais

- [OCI OpenAI-compatible endpoints](https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-compatible-api.htm)
- [OCI Generative AI API keys e exemplo com SDK OpenAI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/api-keys.htm)
- [Policies para Generative AI API keys](https://docs.oracle.com/en-us/iaas/Content/generative-ai/add-api-permission.htm)
- [OpenAI gpt-oss-120b na OCI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-gpt-oss-120b.htm)
- [Modelos por região](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm)
- [Regiões e Availability Domains da OCI](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)
- [Hermes — providers customizados](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/integrations/providers.md)
