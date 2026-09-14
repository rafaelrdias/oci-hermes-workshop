# Hermes Agent + OCI Enterprise AI + Telegram

Material do workshop Oracle no TDC Florianópolis. O caminho principal usa
**US Midwest (Chicago)** — `us-chicago-1`, region key `ORD`. Para tenancies
Trial criadas em São Paulo, há uma variante completa em **Brazil East
(São Paulo)** — `sa-saopaulo-1`, region key `GRU`. As duas provisionam uma VM
Oracle Linux, instalam o
[Hermes Agent oficial da Nous Research](https://github.com/NousResearch/hermes-agent),
configuram OCI Generative AI e publicam a interação por Telegram.

## O que está automatizado

- VCN, subnet pública, Internet Gateway, route table e security list;
- VM Oracle Linux na região da variante escolhida, com somente SSH exposto;
- Hermes Agent `v2026.7.7.2`, Python 3.11 e gateway do Telegram;
- serviço `systemd` para iniciar o gateway no boot;
- policy de menor privilégio para Chat Completions no modelo do workshop;
- comando interativo que grava os segredos diretamente na VM, sem colocá-los no Terraform state.

## Começo rápido

### Edição rápida para o stand Oracle

**[Instalação automatizada: seu Hermes no Telegram](stand/README.md)** — um
formulário no **OCI Resource Manager** executa Terraform, instala o Hermes,
configura acesso OCI via identidade da VM e vincula o Telegram ao dono.
Todo o fluxo pela Console, sem Cloud Shell, API key OCI ou SSH obrigatório.
Versão **1.4.0**: **Grok 4.3 em Chicago**, entrada de voz com **Whisper local**
(sem API STT paga) e respostas **sempre em texto**. Para GRU, Llama é uma
opção explícita; VM/LLM continuam consumindo créditos.
DG e policy são criados automaticamente: somente a VM da Stack, chat no
compartimento do stand e todos os modelos de chat em Chicago. Em GRU, Llama.
Chave SSH automática opcional por Stack, com aceite de persistência no state
e recuperação pela aba Application information. Gerar a chave não abre a porta.
O token do bot é informado como variável sensível; confira o aviso de segurança.
Inclui operação, remoção e roteiro de homologação antes de oferecer ao público.

### Escolha a região do seu Trial

| Região | Download leve | Guia |
|---|---|---|
| Chicago — `us-chicago-1` / ORD | [Terraform ORD](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip) | [Console ORD](docs/OCI_RESOURCE_MANAGER_CONSOLE.md) |
| São Paulo — `sa-saopaulo-1` / GRU | [Terraform GRU](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder-gru.zip) | [Console GRU](docs/GRU_RESOURCE_MANAGER.md) |

As pastas são independentes. Não misture variáveis ou arquivos das duas
regiões.

### Caminho principal — ORD

O caminho recomendado para os participantes é executar o Terraform pelo **OCI Resource Manager**, sem instalar Terraform ou OCI CLI no computador:

1. selecione **US Midwest (Chicago)** na Console OCI antes de abrir o Resource Manager;
2. use **[Baixar a pasta Terraform leve](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip)** e extraia o download uma vez;
3. no Resource Manager, escolha **My configuration → Folder** e selecione `oci-hermes-workshop-resource-manager-folder`;
4. siga o [passo a passo visual da Console OCI](docs/OCI_RESOURCE_MANAGER_CONSOLE.md);
5. execute **Plan**, revise os Logs e somente então execute **Apply** selecionando o Plan mais recente;
6. abra o job de Apply, confirme `deployment_region = us-chicago-1 (ORD)` e copie `public_ip` em **Outputs**.

Enquanto a VM é criada, siga o
**[guia visual de credenciais OCI e Telegram](docs/OCI_API_KEY_TELEGRAM.md)**
para criar a API key OpenAI-compatible, acionar o `@BotFather`, guardar o token
e abrir a primeira conversa com o bot.

Depois, substitua os valores entre `<...>` e execute:

```bash
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'cloud-init status --wait'
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
ssh -t -i <caminho-da-chave-privada> opc@<public_ip> 'hermes-workshop-configure'
```

O último comando solicita, com entrada oculta:

1. o segredo da OCI Generative AI API key;
2. o token criado no `@BotFather`;
3. opcionalmente, seu Telegram user ID. Se ficar vazio, use o pairing seguro.

Depois, envie `/new` ao bot. Se optou por pairing, envie qualquer mensagem e aprove o código na VM:

```bash
ssh -i <caminho-da-chave-privada> opc@<public_ip> 'hermes pairing approve telegram CODIGO'
```

Para preparar as credenciais em momentos diferentes, use `--oci-only`,
`--allowlist-only` e, quando o token do BotFather estiver disponível,
`--telegram-only`. O modo padrão `--full` executa as duas configurações.

## Material do workshop

- [Roteiro completo](docs/WORKSHOP_RUNBOOK.md)
- [Guia visual — pasta Terraform, OCIDs, chaves SSH e Console OCI](docs/OCI_RESOURCE_MANAGER_CONSOLE.md)
- [Guia visual — API key OpenAI-compatible, BotFather e primeira conversa](docs/OCI_API_KEY_TELEGRAM.md)
- [Opcional — criar chaves de assinatura OCI em Configurações do usuário](docs/OCI_USER_API_KEYS.md)
- [Alternativa para OCI Trial em São Paulo — GRU](docs/GRU_RESOURCE_MANAGER.md)
- [OCI Enterprise AI e autenticação](docs/ENTERPRISE_AI.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Apresentação em Markdown](PRESENTATION.md)
- [Apresentação PDF — template Oracle](output/pdf/oci-enterprise-ai-hermes-agent-workshop-TDC_v2.pdf)
- [Terraform](infra/terraform/oci-trial-deploy/README.md)
- [Terraform alternativo GRU](infra/terraform/oci-trial-deploy-gru/README.md)

## Segurança

No workshop tradicional, não grave API keys ou tokens em variáveis da Stack,
`terraform.tfvars`, código, prints ou chat. A **[edição stand](stand/README.md)**
tem um fluxo diferente, inteiramente pela Console: recebe o token Telegram
como variável sensível, com aceite explícito de sua persistência no state e
nos metadados. Leia o aviso de segurança dessa edição antes de utilizá-la.
O Telegram dá acesso às ferramentas do agente na VM; nunca habilite
`GATEWAY_ALLOW_ALL_USERS=true`. Use allowlist ou pairing e, ao final, execute
**Destroy** no Resource Manager antes de excluir a Stack.

IAM policies pertencem à tenancy e não são recursos regionais. Dentro de cada
variante, Stack, jobs, rede, VM, API key, Project quando aplicável e endpoint
do modelo permanecem na região escolhida.
