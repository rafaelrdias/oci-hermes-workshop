# Hermes Agent na OCI — Terraform para eventos

**Versão 1.5.0.** Execute pela Console OCI, sem Terraform local ou Cloud Shell.

[Guia ilustrado completo](https://github.com/rafaelrdias/oci-hermes-workshop#hermes-agent-na-oci-pelo-telegram)

[Baixar pasta Terraform](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager.zip)
— extraia uma vez antes de escolher Folder na Console.

Esta pasta é publicada isoladamente na branch `resource-manager`, sem imagens,
PDFs, binários de providers ou state.

1. Na Console, selecione **Chicago (`us-chicago-1`)**.
2. Abra **Resource Manager → Stacks → Create Stack → My configuration → Folder**.
3. Selecione a pasta que contém `main.tf` e `schema.yaml`.
4. Escolha GPT-OSS 120B, informe o token BotFather e leia/marque o aceite do token.
5. Opcionalmente, gere SSH com seu aceite separado e configure CIDR. Sem CIDR, a porta fica fechada.
6. Execute **Plan → revisar → Apply**.
7. Abra **a Stack recém-executada → Application information**, revele
   `telegram_pairing_command` e envie o comando completo em DM ao seu bot.
8. Aguarde a configuração e teste `/new`, uma tarefa e um áudio.

IAM é automático: DG de uma única VM, chat no compartment da aplicação e todos
os modelos de chat em ORD. GRU exige Llama explícito e mantém a inferência em GRU.
IAM usa a home region; a instalação pode usar outra região subscrita. Não há
fallback, upgrade ou aumento de quota automático. VM/disco/modelo podem gerar cobrança.

**Segredos:** token Telegram persiste em variáveis/state/metadados. A chave
SSH privada gerada fica no state/saída sensível, nunca na VM ou no Telegram.
Recupere `ssh_private_key_pem` em Application information e guarde com segurança.
`sensitive` mascara a interface; leitores de state podem obter os valores.

**Ciclo de vida:** mudanças de modelo/token/bootstrap podem substituir a VM.
Revise Plan e faça backup. Editar metadata não garante instalar/revogar SSH em
um SO inicializado. Para fechar a porta, esvazie CIDR e mantenha a chave.
Para remover recursos, execute **Destroy antes de excluir a Stack**.
