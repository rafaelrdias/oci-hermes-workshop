# Hermes no Telegram Utilizando Soluções OCI

Esta solução não exige terminal, Cloud Shell, Terraform local, OCI CLI, API key
OCI ou conexão SSH para instalar. O **OCI Resource Manager executa o Terraform
pela Console**. A VM instala o Hermes, autentica no modelo com sua identidade
OCI, identifica o dono do bot e inicia o Telegram automaticamente.

## 1. Ative o Trial

1. Cadastre-se no [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) e
   conclua as verificações. Escolha **US Midwest (Chicago)** — ORD,
   `us-chicago-1` — ou **Brazil East (São Paulo)** — GRU, `sa-saopaulo-1`,
   como home region se estiver criando um Trial para esta demonstração.
   **Se já possui uma tenancy com outras regiões, não precisa mudar a home
   region:** a instalação pode usar Chicago ou São Paulo desde que a região
   esteja subscrita e pronta (`READY`).
2. Aguarde a ativação e entre na [Console OCI](https://cloud.oracle.com/) com a
   conta do próprio visitante, com permissão administrativa.
3. No seletor superior, escolha a **região da instalação: Chicago ou São Paulo**.
   VM, rede e inferência ficam nessa região. O Terraform detecta a home region
   e usa seu endpoint apenas para criar compartment, dynamic group e policy
   (IAM global). Não muda a região da VM nem contrata modelo dedicado como fallback.
   Para **GPT-OSS 120B**, escolha Chicago. No grupo **1. Região da instalação**,
   mantenha **LLM = openai.gpt-oss-120b** e **Transcrever áudios localmente** marcado.
   Para um Trial somente em GRU, selecione **meta.llama-3.3-70b-instruct**.
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

Com a Console já na região da instalação (Chicago ou São Paulo), clique:

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
| Região da instalação | Confira `us-chicago-1` ou `sa-saopaulo-1`, igual ao seletor superior; não precisa ser a home region |
| Nome do ambiente | Mantenha `hermes-stand`; se já houver outro, use um nome diferente e outro bot |
| Token do BotFather | Cole o token no campo mascarado e na confirmação |
| Aceite de persistência | Leia e marque somente se concordar com o token em state/metadados |
| Shape | Padrão E5.Flex: 1 OCPU, 8 GB RAM, 50 GB de boot; usa créditos |
| Availability domain | Mantenha `0` (primeiro AD) |
| Gerar chave SSH automaticamente | Marque se quiser uma chave exclusiva para acessar a VM depois; deixe a chave pública manual vazia |
| Aceito armazenar a chave SSH privada no state | Obrigatório somente ao gerar a chave. Quem acessa o state pode obter a privada; guarde uma cópia segura |
| Chave pública SSH opcional | Alternativa à geração: cole sua `.pub`. Não preencha se marcou gerar automaticamente |
| Origem IPv4 do SSH | Vazio mantém a porta fechada, mesmo com chave instalada. Para conectar: seu IPv4 `/32`, ou `0.0.0.0/0` com aceite abaixo |
| Aceito expor a porta SSH à internet temporariamente | Marque somente se usar `0.0.0.0/0`. Não há fechamento automático após o evento |

Tenancy OCID é preenchido pela Console. O Terraform cria o compartment,
rede, VM, dynamic group e policy. Você não precisa copiar compartment OCID,
gerar chaves SSH ou criar API key de modelo manualmente.

Clique **Next**. Em **Review**, desmarque **Run apply**, revise e clique **Create**.

### SSH opcional: chave automática e acesso à VM

SSH é opcional: instalar e usar o Hermes pelo Telegram não exige terminal.
Esta opção serve para quem quiser administrar a própria VM posteriormente.

**Durante Create Stack → Configure variables**, no grupo
**4. Opcional — acesso SSH e chave automática**:

1. Marque **Gerar chave SSH automaticamente para esta Stack**.
2. Leia e marque **Aceito armazenar a chave SSH privada no state da Stack**.
   A chave fica legível dentro do state; `sensitive` mascara sua exibição,
   não impede que leitores do state a obtenham. Use apenas no laboratório.
3. Deixe **Chave pública SSH opcional** vazia. Não é preciso ir a Compute
   nem a Configurações do usuário para gerar outra chave.
4. Para guardar a chave e acessar depois, deixe **Origem IPv4 do SSH** vazia.
   Para acessar já, informe seu IPv4 público com `/32`. No evento, se precisar
   de qualquer IPv4, informe `0.0.0.0/0` e marque também **Aceito expor a porta
   SSH à internet temporariamente**. Esse aceite é separado do aceite da chave.
5. Execute **Plan → revisar → Apply**. O plano deve incluir um
   `tls_private_key.ssh[0]`; somente sua chave pública vai para a VM.

**Depois do Apply — na Stack que acabou de executar**:

1. Abra **Resource Manager → Stacks → sua Stack → Application information**.
2. Localize o grupo **SSH opcional — guarde sua chave privada em segurança**.
3. Revele e copie **`ssh_private_key_pem`**. Se a geração não foi selecionada,
   essa saída estará vazia. **Não copie `ssh_public_key` para acessar por SSH.**
4. Salve todo o conteúdo em um arquivo de **texto puro** chamado `hermes.key`
   (ou `hermes.pem`), incluindo as linhas `-----BEGIN RSA PRIVATE KEY-----`
   e `-----END RSA PRIVATE KEY-----`, mantendo as quebras de linha.
   Não inclua aspas, crases ou formatação Markdown. Evite extensão `.txt` oculta.
5. Guarde no computador pessoal ou gerenciador de senhas seguro. Não envie ao
   facilitador, Telegram, GitHub, e-mail ou computador compartilhado.
   A cópia não é baixada automaticamente para seu computador.

No macOS/Linux, abra um terminal **na pasta onde salvou o arquivo**:

```bash
chmod 600 hermes.key
ssh -i hermes.key opc@IP_DA_VM
```

Substitua `IP_DA_VM` pela saída `public_ip`, ou copie `ssh_connection_command`.
No Windows, use OpenSSH do PowerShell, proteja o arquivo para acesso exclusivo
do seu usuário e use o mesmo comando `ssh -i`; `chmod` é para macOS/Linux.
A primeira conexão pede confirmação da identidade do servidor: confira o
fingerprint por um canal confiável; não desabilite essa verificação.
Esses comandos são para acesso opcional depois do laboratório, **não para
executar o Terraform**, que continua sendo feito pela Console.

**Liberar/restringir a rede depois:** em **Edit Stack**, mantenha a geração e
o aceite da chave como estavam; altere somente `ssh_allowed_cidr` e, quando
necessário, `acknowledge_public_ssh`. Execute Plan/Apply e revise: mudar apenas
o CIDR não deve recriar a VM nem a chave. CIDR vazio fecha SSH; não desmarque
a geração apenas para fechar a porta. A liberação pública não expira sozinha.

**Já tem sua chave?** Não marque geração automática; cole a chave pública
`.pub` existente (`ssh-rsa` ou `ssh-ed25519`). Guarde a privada original no
seu computador. Também pode usar o
[assistente Compute para gerar um par manual](../docs/OCI_RESOURCE_MANAGER_CONSOLE.md#d-gerar-e-baixar-as-chaves-ssh-pela-console).
As [API keys do perfil OCI](../docs/OCI_USER_API_KEYS.md) são outras credenciais;
não são necessárias para esta etapa.

**Cuidados com ciclo de vida:** uma nova Stack/novo state gera outra chave;
repetir Apply preserva a existente. Faça backup antes de Destroy. Não trate o
state como guarda permanente: históricos de jobs/state e cópias podem manter
segredos mesmo após Destroy. Uma cópia privada baixada não é apagada pelo Terraform.
Em uma VM já instalada, mudar/remover a chave dos metadados **não garante**
atualizar/revogar `authorized_keys` no SO. Use esta opção na instalação nova;
para rotação em VM existente, mantenha acesso de recuperação e atualize o SO.
Nunca compartilhe a mesma chave entre participantes nem habilite senha SSH.

Referência: [tls_private_key e risco de persistência no state](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key).

## 5. Execute Plan e Apply — sem sair da Console

1. Na Stack, clique **Plan** e confirme. Aguarde o job ficar **Succeeded**.
2. Abra os **Logs** do Plan e confira: uma VM 1 OCPU/8 GB, disco de 50 GB,
   rede e IAM. **Não** deve haver GPU, cluster dedicado, banco ou load balancer.
   O token deve aparecer mascarado, nunca como texto legível.
3. Volte à Stack e clique **Apply**.
4. Escolha o **Plan mais recente que você revisou** e confirme o Apply.
5. Aguarde o **Apply** ficar **Succeeded**. Volte aos detalhes **da mesma Stack
   cujo Apply você acabou de executar** e abra **Application information /
   Informações da aplicação**. Essa aba fica na Stack, não na VM nem nos logs
   do job. Siga o passo 6 abaixo para copiar o comando do Telegram.

**Succeeded no Apply significa infraestrutura criada.** A instalação do
software e os testes do modelo continuam na VM. Não crie outra Stack porque
o bot ainda não respondeu.

## 6. Vincule o bot à sua conta

**Acesse a informação na própria Stack cujo Apply acabou de concluir com
Succeeded. Não procure na página da VM, em outra Stack ou nos logs do Plan.**

1. Na Console OCI, mantenha a região em que fez a instalação e acesse
   **☰ → Developer Services → Resource Manager → Stacks**.
2. Selecione o **compartment onde você criou a Stack** (não necessariamente
   o compartment criado pelo Terraform para a VM) e clique no **nome da
   mesma Stack que acabou de executar**. Se estiver nos logs do Apply,
   volte aos detalhes dela pelo nome da Stack no caminho de navegação.
3. Nos detalhes dessa Stack, abra **Application information / Informações
   da aplicação**. No grupo **Próximo passo no Telegram**, localize o campo
   **Desbloqueie, copie e envie este comando em DM ao seu bot**. Esse é o
   nome exibido para a saída Terraform `telegram_pairing_command`.
4. Clique **Unlock/Desbloquear** e copie o comando completo, começando por
   `/start stand_` e incluindo todo o código que vem depois. Não copie
   apenas `/start`, o nome da variável ou o texto `<sensitive>`.
5. Abra o bot pelo link recebido do BotFather e toque **Start/Iniciar**.
6. Cole o comando de pareamento **em mensagem privada para seu próprio bot,
   não para o @BotFather nem em um grupo**.
   Um `/start` simples não basta: envie também o código mostrado na Stack.
7. Aguarde: o bot confirma o vínculo, testa acesso OCI e ferramentas e envia
   a mensagem **“Configuração concluída!”** quando o gateway está ativo.

Se não encontrar a aba, nessa **mesma Stack** abra **Jobs → Apply concluído
com Succeeded → Outputs** e procure `telegram_pairing_command`. Se o valor
estiver mascarado e não houver opção de revelar, não envie `<sensitive>`
ao bot; peça ajuda ao facilitador, sem compartilhar tokens ou códigos.

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
outros canais e GPUs estão fora do fluxo rápido. Áudios recebidos são
transcritos localmente quando STT está habilitado; respostas continuam em texto.

### Testar mensagens de voz

1. Após **Configuração concluída**, envie `/new` ao seu bot.
2. Grave pelo microfone do Telegram um áudio curto (10–30 segundos), em português:
   “Crie o arquivo lembrete.txt com o texto Bem-vindo ao stand Oracle e leia o arquivo.”
3. Aguarde a transcrição e a resposta escrita. Confirme que ele entendeu o pedido
   e executou as ferramentas. O bot não deve enviar voz, mesmo após `/voice on`.
4. Em local barulhento, fale perto do microfone. Se houver erro, repita ou envie texto.

Whisper **base multilíngue**, CPU/int8, sem GPU ou chave STT. Os pesos (~150 MB)
são baixados durante o bootstrap, não fazem parte da pasta enviada à Console.
O áudio é processado na VM; a transcrição segue para o LLM como texto.
Grok é acessado e cobrado via OCI, mas **hospedado externamente pela xAI**;
não há garantia de que o processamento do LLM permaneça em Chicago.
Não envie dados sensíveis no teste. A transcrição usa CPU/RAM; áudios longos
podem ser lentos em 1 OCPU. Não há garantia de latência nem de acerto em ruído.
Para dispensar STT, desmarque a opção ao criar a Stack; o bot continua textual.

## O que está automatizado

| Camada | Configuração |
|---|---|
| Infraestrutura | Compartment, VCN, subnet, internet gateway, rotas, regras e VM Oracle Linux 9 |
| Identidade OCI | Terraform cria DG de uma única VM e policy apenas para chat no compartment do stand: todos os modelos em ORD; Llama em GRU; condição de região em ambos |
| Instalação | Python 3.11, Hermes oficial, Telegram, ponte local OCI e serviços systemd |
| Modelo | GPT-OSS 120B via OCI ORD (padrão); Grok opcional; Llama 3.3 como opção explícita ORD/GRU. Instance Principal, sem API key/cluster dedicado |
| Áudio recebido | Whisper base local em CPU, sem cobrança de API STT; pode ser desabilitado no formulário |
| Resposta | Sempre texto; TTS automático bloqueado no gateway e ferramenta TTS desabilitada |
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
  iterações/tarefa, até 8.192 tokens de saída/chamada para Grok (4.000 para Llama)
  e 120 chamadas/hora na
  ponte **não são teto de gastos** e não cobrem outros usos da tenancy.
  Grok usa orçamento inicial de 4.096 tokens e cada chamada do smoke test
  também permite até 4.096, para não limitar raciocínio ao antigo teste de
  128 tokens do Llama. O limite não implica consumo integral, mas não é gratuito.
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
lista GPT-OSS 120B e Grok on-demand em ORD. O pacote não oferece GPT-OSS
on-demand em GRU nem cria cluster dedicado para contornar isso (consulta em 14/09/2026).
Identificador: [openai.gpt-oss-120b na OCI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-gpt-oss-120b.htm).
Llama 3.3 permanece disponível como escolha explícita em ORD/GRU.
Nesta edição, rede/VM e endpoint OCI permanecem na região selecionada.
**Grok é hospedado externamente pela xAI**, conforme as notas da mesma matriz;
usar endpoint OCI não significa residência do processamento LLM na VM/região.
A home region pode ser outra: IAM é global e é criado pelo endpoint da home
region detectada automaticamente. Veja a saída `iam_home_region` na Stack.
Outras regiões de VM/LLM ainda não estão habilitadas neste pacote: o modelo
e a modalidade on-demand precisam estar disponíveis na região escolhida.

## Atualizar uma Stack que bloqueou por home region

O erro antigo **“Selecione a HOME REGION do Trial”** foi removido na versão 1.1.0.
Uma Stack criada por Folder/ZIP ou pelo botão de deploy mantém uma cópia do
Terraform; **somente executar outro Plan não baixa a atualização do GitHub**.

1. Baixe novamente o [pacote leve atualizado](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/stand-resource-manager.zip)
   e extraia a pasta `oci-hermes-workshop-stand-resource-manager`.
2. Na Console, abra **Resource Manager → Stacks → a mesma Stack que falhou**.
3. Clique **Edit / Edit Stack** e, na configuração Terraform, selecione
   **Folder** e carregue a pasta extraída atualizada. Não use o repositório inteiro.
4. Avance, confira as variáveis preservadas (região, token e aceite) e salve.
   O formulário atualizado mostra **Região da instalação**, não “Home region do Trial”.
5. Execute um **novo Plan**, revise e depois **Apply** usando esse novo Plan.
   O erro relatado ocorreu no Plan; não é necessário Destroy para corrigi-lo.
   Se esta Stack já tiver recursos de outras execuções, revise qualquer
   substituição/destruição antes de aprovar.

A Stack e sua VM podem ficar em Chicago com home region em Ashburn, por exemplo.
Não remova manualmente as validações nem altere o tenancy OCID para contornar erros.

- [Arquitetura e componentes](ARCHITECTURE.md)
- [Problemas, rotação e recuperação](TROUBLESHOOTING.md)
- [Validação e homologação antes do evento](VALIDATION.md)
- [Arquivos Terraform](terraform/)

**Estado da entrega:** testes locais/simulados documentados. A execução
completa em Trial ORD/GRU e a resposta final no Telegram ainda precisam de
homologação antes da oferta ao público.
