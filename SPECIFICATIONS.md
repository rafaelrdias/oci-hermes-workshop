# Especificação do workshop

## Runtime

- Hermes Agent oficial: release `v2026.7.7.2` por padrão;
- sistema operacional: Oracle Linux 9;
- usuário do serviço: `opc`;
- serviço: `/etc/systemd/system/hermes-gateway.service`;
- configuração: `/home/opc/.hermes/config.yaml`;
- segredos: `/home/opc/.hermes/.env`, modo `0600`.

## Modelo

```text
provider: custom:oci-genai
model: openai.gpt-oss-120b
region: us-chicago-1
api_mode: chat_completions
context_length: 128000
```

## Canal

- Telegram Bot API por long polling;
- `TELEGRAM_ALLOWED_USERS` ou pairing;
- `GATEWAY_ALLOW_ALL_USERS` proibido no laboratório;
- nenhum webhook e nenhuma porta HTTP pública.

## Infraestrutura

- VCN `10.20.0.0/16`;
- subnet pública `10.20.10.0/24`;
- entrada TCP/22 restrita por variável;
- saída liberada para HTTPS do Telegram, GitHub e OCI;
- E5 Flex por padrão; A1 Flex como opção Always Free;
- policy restrita a `generative-ai-chat` e ao model ID do laboratório.

## Critérios de aceite

1. `terraform validate` retorna sucesso;
2. `cloud-init status --wait` termina com `done`;
3. `hermes doctor` reconhece `python-telegram-bot`;
4. o teste do configurador recebe resposta do OCI Generative AI;
5. `hermes-gateway` fica `active`;
6. uma mensagem autorizada no Telegram recebe resposta;
7. nenhum segredo existe no Git ou no Terraform state.
