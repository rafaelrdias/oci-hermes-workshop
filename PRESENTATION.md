# Hermes Agent na OCI pelo Telegram

## Workshop Oracle — TDC Florianópolis

**90 minutos de sala · 60 minutos de atividade · 30 minutos de segurança operacional**

Resultado: cada participante publica um agente pessoal no Telegram usando Hermes Agent e OCI Enterprise AI.

---

# O que vamos construir

```text
Você
  ↓ mensagem
Telegram Bot API
  ↓ long polling HTTPS
Hermes Gateway em Oracle Linux — Chicago (ORD)
  ↓ OpenAI-compatible Chat Completions
OCI Generative AI — Chicago (ORD) — openai.gpt-oss-120b
```

Saída: um bot capaz de conversar, manter sessões, usar memória e executar ferramentas autorizadas na VM.

---

# O que é o Hermes Agent?

Um agente open source da Nous Research que combina:

- loop de agente com uso de ferramentas;
- sessões e memória persistidas localmente;
- skills que ensinam novos fluxos;
- gateway para Telegram, Discord, Slack, WhatsApp e outros canais;
- tarefas agendadas e delegação;
- escolha de provider/modelo, inclusive endpoints OpenAI-compatible.

Fonte: [repositório e documentação oficial](https://github.com/NousResearch/hermes-agent).

---

# Chatbot × agente

Um chatbot responde texto.

Um agente pode:

1. entender um objetivo;
2. escolher ferramentas;
3. observar resultados;
4. corrigir o plano;
5. persistir contexto;
6. devolver uma conclusão verificável.

Essa capacidade aumenta o valor — e também o risco. Segurança faz parte da arquitetura.

---

# Por que Hermes neste laboratório?

- experiência pronta de terminal + gateway, sem construir uma aplicação do zero;
- modelo e infraestrutura desacoplados;
- configuração local, simples de inspecionar;
- Telegram funciona por long polling, sem domínio, TLS ou webhook;
- skills, memória, cron e ferramentas já integrados;
- cabe em uma VM pequena e pode ser reproduzido por Terraform.

O Hermes funciona com endpoints OpenAI-compatible, segundo a [documentação de providers](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/integrations/providers.md).

---

# Comparação honesta: escolha pelo problema

| Categoria | Ponto forte | Quando Hermes se destaca |
|---|---|---|
| Gateway pessoal, como OpenClaw | muitos canais, plugins e apps | experiência Python, skills e runtime do Hermes já no mesmo pacote |
| Framework, como LangGraph | controle explícito, execução durável, HITL | quando queremos um agente utilizável agora, sem programar o grafo |
| Multiagente, como CrewAI | crews, papéis e flows estruturados | interação contínua por chat, memória pessoal e ferramentas na máquina |
| Workflow visual | integrações determinísticas e auditáveis | tarefas abertas em que o agente precisa explorar e adaptar o plano |

Não existe “melhor” absoluto. LangGraph se define como runtime low-level; CrewAI enfatiza Crews e Flows; OpenClaw também é um gateway self-hosted. Fontes: [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview), [CrewAI](https://docs.crewai.com/), [OpenClaw](https://docs.openclaw.ai/).

---

# Onde está a vantagem prática

Para este workshop, o Hermes reduz cinco integrações a uma configuração:

```text
agente + ferramentas + memória + serviço + Telegram
```

O participante concentra energia em:

- infraestrutura OCI;
- policy e segredo do modelo;
- segurança do canal;
- experiência final do usuário.

---

# OCI Enterprise AI

O OCI Generative AI oferece endpoints OpenAI-compatible com autenticação OCI.

Hoje usaremos:

```text
Modelo: openai.gpt-oss-120b
Região: us-chicago-1
API: Chat Completions
Auth: OCI Generative AI API key
```

O modelo tem 128 mil tokens de contexto e function calling. Fontes: [model card](https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-gpt-oss-120b.htm) e [API keys](https://docs.oracle.com/en-us/iaas/Content/generative-ai/api-keys.htm).

---

# Uma única região para todo o laboratório

Todos os recursos regionais ficam em Chicago:

```text
US Midwest (Chicago)
Identificador: us-chicago-1
Region key: ORD

Resource Manager + rede + VM + Hermes + API key + modelo
```

Chicago combina suporte de API keys com SDK OpenAI e disponibilidade on-demand de `gpt-oss-120b`. A API key deve estar na mesma região do modelo. IAM policy é a única exceção: pertence à tenancy, não a uma região. Fontes: [Regions and Availability Domains](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm), [API keys](https://docs.oracle.com/en-us/iaas/Content/generative-ai/api-keys.htm) e [Models by Region](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm).

---

# O que o Terraform cria

- VCN e subnet pública;
- Internet Gateway e rota de saída;
- security list com apenas TCP/22 de entrada;
- VM Oracle Linux;
- bootstrap do Hermes fixado em uma release;
- serviço `systemd` do gateway;
- policy limitada a Chat Completions + modelo do lab.

Stack, jobs, rede, VM e OCI Generative AI usam `us-chicago-1`.

Ele não recebe o token do Telegram nem a API key. Segredos não devem ir para o Terraform state.

---

# Modelo de segurança

```text
Internet → VM: somente SSH do seu CIDR
VM → Telegram: HTTPS de saída
VM → OCI GenAI: HTTPS de saída
Usuário Telegram: allowlist ou pairing
```

Nunca:

- `GATEWAY_ALLOW_ALL_USERS=true`;
- porta 8642 aberta sem autenticação;
- token em Git, tfvars, print ou slide;
- um bot compartilhado entre várias VMs.

---

# Pré-lab sem terminal

Antes da atividade, pela Console e pelo navegador:

1. usar **[Baixar a pasta Terraform leve](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip)**;
2. extrair e abrir `oci-hermes-workshop-resource-manager-folder`;
3. copiar o Tenancy OCID;
4. selecionar/criar o compartment e copiar seu OCID;
5. gerar o par SSH em **Compute → Create instance → Add SSH keys**;
6. salvar as chaves privada e pública e cancelar o assistente sem criar a VM.

O [guia visual](docs/OCI_RESOURCE_MANAGER_CONSOLE.md#preparação-pela-console--sem-instalar-ferramentas) contém todas as telas.

---

# Cronograma da prática

| Tempo | Atividade |
|---:|---|
| 0–10 | arquitetura e segurança |
| 10–20 | criar Stack, revisar Plan e executar Apply na Console OCI |
| 20–35 | criar API key OCI e bot enquanto cloud-init roda |
| 35–45 | SSH e configuração interativa |
| 45–55 | Telegram, pairing e primeiro prompt |
| 55–60 | mini desafio e validação |

Os 30 minutos restantes absorvem dúvidas e recuperação.

---

# Checkpoint 1 — Terraform

```text
Console OCI
  → Region: US Midwest (Chicago)
  → Developer Services
  → Resource Manager
  → Stacks
  → Create stack
  → My configuration / Folder
```

1. selecionar a pasta `oci-hermes-workshop-resource-manager-folder`;
2. preencher as variáveis sem segredos;
3. criar com **Run apply** desmarcado;
4. executar **Plan** e revisar os Logs;
5. executar **Apply** usando o último Plan;
6. confirmar `deployment_region = us-chicago-1 (ORD)` e copiar `public_ip` em **Outputs**.

Passo a passo: [guia visual da Console OCI](docs/OCI_RESOURCE_MANAGER_CONSOLE.md).

Em paralelo: criar a OCI Generative AI API key na mesma região de Chicago e o bot no `@BotFather`.

---

# Checkpoint 2 — bootstrap e segredos

```bash
ssh -i <chave-privada> opc@<public_ip> 'cloud-init status --wait'
ssh -i <chave-privada> opc@<public_ip> 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
ssh -t -i <chave-privada> opc@<public_ip> 'hermes-workshop-configure'
```

O configurador testa o modelo antes de iniciar o gateway.

---

# Checkpoint 3 — Telegram

Allowlist: envie `/new`.

Pairing: envie uma mensagem, receba o código e execute:

```bash
hermes pairing approve telegram CODIGO
```

Primeiro prompt:

```text
Explique em três bullets quais componentes OCI sustentam você.
```

---

# Mini desafio

Pelo Telegram, peça:

```text
Crie ~/hermes-tasks/resultado.md com o hostname,
uma explicação curta da arquitetura e três cuidados de segurança.
Antes de terminar, verifique se o arquivo existe.
```

Valide por SSH:

```bash
sed -n '1,120p' ~/hermes-tasks/resultado.md
```

---

# Diagnóstico em 30 segundos

```bash
hermes doctor
sudo systemctl status hermes-gateway --no-pager
sudo journalctl -u hermes-gateway -n 100 --no-pager
```

401 → segredo/região da key.

403/404 → policy, modelo ou disponibilidade regional.

Bot silencioso → token, allowlist/pairing ou gateway parado.

---

# Para onde evoluir depois

- skills específicas da empresa;
- Object Storage e banco como ferramentas controladas;
- Vault e rotação de credenciais;
- observabilidade e avaliação;
- autenticação IAM com adaptador `oci-genai-auth`;
- múltiplos perfis/agentes com isolamento;
- pipeline de atualização e testes antes de produção.

---

# Encerramento responsável

O agente tem acesso às ferramentas do servidor. Trate o bot como uma identidade privilegiada.

Ao terminar:

1. abra a Stack em **US Midwest (Chicago)**;
2. execute **Destroy** e aguarde `SUCCEEDED`;
3. confirme que **Stack resources** está vazia;
4. somente então use **Delete stack**.

**Infraestrutura reproduzível. Modelo Enterprise AI. Agente no seu bolso.**
