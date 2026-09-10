# Hermes no Telegram — stand Oracle, pela Console OCI

**Trial pessoal → BotFather → Create Stack → Plan → Apply → Telegram.**

Esta edição não exige terminal, Cloud Shell, Terraform local, OCI CLI, API key
OCI ou conexão SSH para instalar. O **OCI Resource Manager executa o Terraform
pela Console**. A VM instala o Hermes, autentica no modelo com sua identidade
OCI, identifica o dono do bot e inicia o Telegram automaticamente.

> **Segurança:** para permitir o fluxo sem comandos, o token do BotFather é
> informado em um campo sensível da Stack. Ele é mascarado, mas **persiste nas
> variáveis, planos/state e metadados cloud-init da VM**. A opção `sensitive`
> não criptografa o valor dentro do state nem remove essa persistência. Use
> conta pessoal e bot exclusivo; restrinja acesso à Stack/state/VM. Há aceite
> obrigatório no formulário. Para produção, adote secret management apropriado.

## 1. Ative o Trial

1. Cadastre-se no [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) e
   conclua as verificações. Escolha **US Midwest (Chicago)** — ORD,
   `us-chicago-1` — ou **Brazil East (São Paulo)** — GRU, `sa-saopaulo-1`,
   como home region desta demonstração.
2. Aguarde a ativação e entre na [Console OCI](https://cloud.oracle.com/) com a
   conta do próprio visitante, com permissão administrativa.
3. No seletor superior, escolha a **home region do Trial**. O Terraform valida
   essa escolha: não muda de região nem contrata serviço dedicado como fallback.
4. Confirme créditos, limites de Compute e acesso a OCI Generative AI on-demand.

Cadastro, validação cadastral, liberação da conta, capacidade e eventuais
permissões/quota do serviço não podem ser garantidos pelo Terraform. O material
não faz upgrade da conta para uma modalidade paga.

## 2. Crie seu bot no Telegram

1. Abra o **[@BotFather oficial](https://t.me/BotFather)** e toque **Start/Iniciar**.
2. Envie `/newbot`.
3. Escolha um nome, como `Meu Hermes OCI`.
4. Escolha um username único terminado em `bot`, por exemplo
   `meu_nome_hermes_oci_bot`.
5. Guarde o **token** retornado e o link `https://t.me/SEU_BOT`.

Use um **bot novo e exclusivo**. Não envie o token ao atendente, não o coloque
em GitHub, mensagens, fotos ou apresentações. O instalador não remove webhooks
nem assume o controle de bots usados por outra integração.

O [guia ilustrado de Telegram do workshop](https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/OCI_API_KEY_TELEGRAM.md)
também mostra o BotFather. **A etapa de API key OCI daquele guia não se aplica
a esta edição**: aqui a VM usa Instance Principals, sem chave OCI persistente.

## 3. Abra a Stack diretamente pela Console

Com a Console já na home region, clique:

[![Deploy to Oracle Cloud](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https%3A%2F%2Fgithub.com%2Frafaelrdias%2Foci-hermes-workshop%2Farchive%2Frefs%2Fheads%2Fstand-resource-manager.zip)

**[Criar Stack do stand na Console OCI](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https%3A%2F%2Fgithub.com%2Frafaelrdias%2Foci-hermes-workshop%2Farchive%2Frefs%2Fheads%2Fstand-resource-manager.zip)**

O botão seleciona o pacote Terraform automaticamente. Não é necessário
baixá-lo, extrair uma pasta ou executar comandos. O pacote contém apenas esta
edição, sem apresentações, PDFs ou binários de providers.

### Se preferir selecionar a pasta manualmente

1. [Baixe a pasta leve do stand](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/stand-resource-manager.zip).
2. Extraia uma vez. A pasta resultante é `oci-hermes-workshop-stand-resource-manager`.
3. Na Console: **Developer Services → Resource Manager → Stacks → Create Stack**.
4. Em **My configuration → Folder**, selecione essa pasta, onde estão `main.tf`
   e `schema.yaml`. Não selecione o repositório inteiro, `stand/` do repositório
   principal nem uma pasta contendo `.terraform`.

O ZIP é apenas o transporte da pasta pelo GitHub. O visitante não executa
nenhum comando para preparar o pacote. As telas gerais de Folder/Stack/Plan
estão no [guia visual da Console](https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/OCI_RESOURCE_MANAGER_CONSOLE.md);
para os campos desta edição, siga a tabela abaixo, não os campos da versão antiga.

## 4. Preencha o formulário

Na tela **Stack information**:

1. Nome: `hermes-stand`.
2. Compartment da Stack: use o **root compartment** do seu Trial, ou outro
   compartment administrativo já existente. A Stack não deve ficar dentro do
   compartment que ela própria criará e removerá.
3. Terraform: escolha uma versão oferecida **>= 1.5 e < 2.0**.
4. Clique **Next**.

Na tela **Configure variables**:

| Campo | O que fazer |
|---|---|
| Home region do Trial | Confira `us-chicago-1` ou `sa-saopaulo-1`, igual ao seletor superior |
| Nome do ambiente | Mantenha `hermes-stand`; se já houver outro, use um nome diferente e outro bot |
| Token do BotFather | Cole o token no campo mascarado e na confirmação |
| Aceite de persistência | Leia e marque somente se concordar com o token em state/metadados |
| Shape | Padrão E5.Flex: 1 OCPU, 8 GB RAM, 50 GB de boot; usa créditos |
| Availability domain | Mantenha `0` (primeiro AD) |
| Chave SSH / IPv4 `/32` | **Deixe ambos vazios**. Não são necessários para instalar/conversar |

Tenancy OCID é preenchido pela Console. O Terraform cria o compartment,
rede, VM, dynamic group e policy. Você não precisa copiar compartment OCID,
gerar chaves SSH ou criar API key de modelo manualmente.

Clique **Next**. Em **Review**, desmarque **Run apply**, revise e clique **Create**.

## 5. Execute Plan e Apply — sem sair da Console

1. Na Stack, clique **Plan** e confirme. Aguarde o job ficar **Succeeded**.
2. Abra os **Logs** do Plan e confira: uma VM 1 OCPU/8 GB, disco de 50 GB,
   rede e IAM. **Não** deve haver GPU, cluster dedicado, banco ou load balancer.
   O token deve aparecer mascarado, nunca como texto legível.
3. Volte à Stack e clique **Apply**.
4. Escolha o **Plan mais recente que você revisou** e confirme o Apply.
5. Aguarde **Succeeded** e abra **Application information** ou **Outputs**.

**Succeeded no Apply significa infraestrutura criada.** A instalação do
software e os testes do modelo continuam na VM. Não crie outra Stack porque
o bot ainda não respondeu.

## 6. Vincule o bot à sua conta

1. Em **Application information**, localize `telegram_pairing_command`.
2. Clique **Unlock/Desbloquear** e copie o comando completo, começando por
   `/start stand_...`. Se estiver em Outputs, use a opção de revelar/copiar o
   valor sensível; a aba Application information foi preparada para isso.
3. Abra o bot pelo link recebido do BotFather e toque **Start/Iniciar**.
4. Cole o comando de pareamento **em mensagem privada para seu bot**.
   Um `/start` simples não basta: envie também o código mostrado na Stack.
5. Aguarde: o bot confirma o vínculo, testa acesso OCI e ferramentas e envia
   a mensagem **“Configuração concluída!”** quando o gateway está ativo.

O ID numérico da sua conta é identificado automaticamente. Não é necessário
`@userinfobot`, aprovação por SSH ou criação de uma allowlist manual.

**Não compartilhe esse comando:** o primeiro usuário que o enviar em DM será
o dono autorizado. Use um bot por visitante. Não adicione o bot a grupos
durante a demonstração.

## 7. Faça o teste real

Depois da mensagem de configuração concluída, envie `/new` e:

> Crie o arquivo boas-vindas.txt no seu workspace com uma saudação para quem
> está visitando o stand Oracle. Depois leia o arquivo e mostre o conteúdo.

Esse teste percorre **Telegram → Hermes → OCI → ferramenta → Telegram**.
A mensagem enviada pelo instalador não substitui a resposta real do Hermes.

Também experimente pedir um roteiro de estudo de OCI salvo em Markdown ou
guardar sua preferência por respostas curtas. Esta edição habilita texto,
terminal, arquivos, memória e skills; navegador, pesquisa web, imagens,
áudio, outros canais e GPUs estão fora do fluxo rápido.

## O que está automatizado

| Camada | Configuração |
|---|---|
| Infraestrutura | Compartment, VCN, subnet, internet gateway, rotas, regras e VM Oracle Linux 9 |
| Identidade OCI | Dynamic group de uma única VM e policy apenas para chat no modelo do stand |
| Instalação | Python 3.11, Hermes oficial, Telegram, ponte local OCI e serviços systemd |
| Modelo | Llama 3.3 70B on-demand na mesma região da VM, sem API key OCI/Project/cluster dedicado |
| Pareamento | Código privado da Stack, identificação automática do dono e allowlist |
| Aceitação | Teste real de inferência, chamada de ferramenta e retorno ao modelo |
| Operação | Reinício dos serviços no boot e novas tentativas quando IAM ainda propaga |

Reserve **15–30 minutos após o Trial ativado** como estimativa inicial de
planejamento, **não como tempo medido ou garantido**. Cadastro, downloads,
capacidade e IAM podem demorar mais; alterações de dynamic groups podem levar
até uma hora para surtir efeito. Combine cadastro antecipado quando possível.

## Encerrar: Destroy na Console

1. Guarde os arquivos que desejar preservar; a remoção é destrutiva.
2. Abra **Resource Manager → Stacks → sua Stack → Terraform actions → Destroy**.
3. Revise e confirme. Aguarde **Succeeded** e confira os logs.
4. Só depois exclua a Stack, se desejar.
5. No BotFather, use `/deletebot` para remover o bot ou `/revoke` se seu token
   foi exposto. O Terraform não exclui o bot do Telegram.

Destroy remove VM, disco, histórico/memória/arquivos locais, rede, policy,
dynamic group e compartment criados. Não coloque outros recursos dentro do
compartment da demonstração. Fechar a aba, parar o chat ou excluir a Stack
**sem Destroy** não garante a remoção dos recursos.

## Custos e limites de segurança

- E5/E4.Flex e inferência **consomem créditos do Trial**; não anuncie tudo como
  Always Free. A1 é uma opção explícita no formulário, sujeita a quota,
  capacidade e elegibilidade da conta. Não há troca automática de shape/região.
- Configure acompanhamento de custos na Console. Limites locais de 8
  iterações/tarefa, até 4.000 tokens de saída/chamada e 120 chamadas/hora na
  ponte **não são teto de gastos** e não cobrem outros usos da tenancy.
- Telegram usa polling de saída. Não é necessário domínio, TLS, webhook,
  porta de aplicação pública ou SSH. A ponte escuta apenas em `127.0.0.1:4000`.
- Hermes roda como usuário dedicado, sem sudo e com restrições de escrita.
  Ainda possui terminal/rede e acesso aos próprios segredos: é demonstração
  pessoal, não sandbox multiusuário ou ambiente para informações confidenciais.
  A allowlist não impede prompt injection.
- **Não publique state, planos, variáveis, metadados, arquivos `.env`, dumps de
  cloud-init ou logs com dados pessoais.** Administradores e leitores desses
  recursos podem obter o token. `sensitive` apenas mascara a apresentação.
- Alterar token ou arquivos do bootstrap exige nova instalação. Esta Stack
  marca a VM para **substituição** nesses casos; revise Plan e faça backup.
  Não confirme um Plan de substituição achando que é apenas atualização de texto.

## Modelo e documentação

A [matriz regional da Oracle](https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm)
lista `meta.llama-3.3-70b-instruct` on-demand em ORD e GRU; GPT-OSS em GRU está
listado somente como dedicado. Criar um Project não muda essa modalidade.
Nesta edição, rede/VM/inferência permanecem na home region; IAM é global.

- [Arquitetura e componentes](ARCHITECTURE.md)
- [Problemas, rotação e recuperação](TROUBLESHOOTING.md)
- [Validação e homologação antes do evento](VALIDATION.md)
- [Arquivos Terraform](terraform/)

**Estado da entrega:** testes locais/simulados documentados. A execução
completa em Trial ORD/GRU e a resposta final no Telegram ainda precisam de
homologação antes da oferta ao público.
