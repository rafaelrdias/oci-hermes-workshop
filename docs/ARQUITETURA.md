# Arquitetura e segurança

[Voltar ao guia](../README.md)

## Como a conversa funciona

1. O participante envia texto ou áudio em DM ao seu bot Telegram.
2. O gateway na VM recebe mensagens por polling HTTPS de saída; não há webhook
   nem interface web pública.
3. Áudio é transcrito localmente por Whisper base na CPU. O texto resultante
   segue ao agente.
4. Hermes envia a conversa ao bridge em `127.0.0.1:4000`. O bridge autentica na
   OCI usando **Instance Principals** e chama o modelo selecionado.
5. Quando necessário, Hermes executa ferramentas como criar/ler arquivos no
   workspace, retorna o resultado ao LLM e responde ao Telegram **por texto**.

O modelo decide ações; Hermes organiza ferramentas, memória, sessão e canal.
Foi escolhido para a atividade por combinar essas funções em uma experiência
prática auto-hospedada. Não é uma alegação de superioridade universal nem um
sandbox multiusuário.

## Recursos gerenciados pelo Terraform

| Recurso | Escopo |
|---|---|
| Compartment próprio | Criado sob a tenancy; nome exclusivo por ambiente |
| VCN, subnet pública, rota e Internet Gateway | Região selecionada; saída necessária para instalação, OCI e Telegram |
| Security List | ICMP de diagnóstico e TCP/22 apenas se configurado; nenhum serviço web público |
| VM Oracle Linux 9 | 1 OCPU, 8 GB RAM, disco de boot 50 GB; IPv4 público |
| Dynamic Group | Somente o OCID da VM criada, não todas as VMs da tenancy |
| Policy | Inferência chat no compartment criado; restrição regional |
| Par SSH opcional | Pública na VM; privada sensível no state/outputs, nunca no user-data |
| Código de vínculo | Aleatório, sensível; primeiro usuário válido em DM vira dono |

VM, rede e endpoint OCI de inferência ficam em **Chicago (ORD)** ou **São Paulo (GRU)**,
conforme a escolha. GPT-OSS/Llama usam o modelo OCI regional; a opção Grok é
hospedada externamente pela xAI, conforme as notas da matriz regional abaixo.
IAM é global e o provider usa o endpoint da **home region**,
mesmo quando diferente. O executor precisa de permissões para criar esses
recursos; a policy do agente não concede permissões ao executor do Terraform.

### Acesso a modelos

Em Chicago, a policy criada permite todos os modelos de **chat** naquele
compartment e região. “Todos” não inclui automaticamente embeddings, clusters
dedicados, quotas, créditos ou qualquer produto Marketplace.

```text
Allow dynamic-group id <DG_OCID> to use generative-ai-chat in compartment id <COMPARTMENT_OCID> where request.region = 'ORD'
```

Em GRU, o pacote usa Llama explicitamente e restringe a policy também ao modelo:

```text
Allow dynamic-group id <DG_OCID> to use generative-ai-chat in compartment id <COMPARTMENT_OCID> where ALL {request.region = 'GRU', target.model.id = 'meta.llama-3.3-70b-instruct'}
```

O Terraform preenche esses identificadores; não cole os placeholders na Console.
O padrão é **`openai.gpt-oss-120b` em ORD**. Acesso e disponibilidade devem ser
confirmados na [matriz regional OCI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm).
Não há cluster dedicado, contratação Marketplace ou fallback criado automaticamente.

## Limites de segurança desta demonstração

- Cada participante deve ter seu próprio bot e conta OCI. O vínculo aceita
  somente uma DM privada com código válido, restringindo o gateway ao dono.
- Não há API key OCI do usuário no agente. Uma chave local protege o bridge,
  que escuta apenas em loopback.
- Token Telegram e código de pareamento persistem na Stack/state e no material
  de bootstrap. Chave SSH gerada também persiste no state. Mascarar não criptografa
  o dado para quem já tem permissão de ler o state.
- O usuário do serviço não é root. Mesmo assim, ferramentas locais e rede podem
  executar ações reais e consumir os créditos disponíveis à identidade da VM.
  Instruções em prompts não constituem uma barreira de isolamento.
- Transcrição não usa API paga, mas consome CPU/RAM. O texto transcrito vai ao
  modelo OCI, e a mensagem de voz transita pelo Telegram.
- TTS fica desabilitado. A integração não oferece visão, navegação web ou
  instalação automática de ferramentas externas.
- Não há Vault, backup, monitoramento gerenciado ou limpeza programada. Planeje
  essas camadas antes de reutilizar como serviço de produção.
- SSH é opt-in. `0.0.0.0/0` exige aceite separado e não se fecha sozinho.

Leia [operação](OPERACAO.md) e [SSH](SSH.md) antes de alterar o ambiente.
