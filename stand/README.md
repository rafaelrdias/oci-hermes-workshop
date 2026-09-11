# Hermes no Telegram — stand Oracle, pela Console OCI

**Trial pessoal → BotFather → Create Stack → Plan → Apply → Telegram.**

**Versão 1.2.3:** corrige chamadas de ferramentas fragmentadas no streaming
que apareciam como `Response truncated due to output length limit`.
A ativação agora testa chamada e retorno de ferramenta também com streaming.
Não é necessário aumentar o limite de tokens. Em VM já instalada, consulte
[o diagnóstico e a correção](TROUBLESHOOTING.md#ferramentas-truncadas-no-streaming--versão-123).

**Versão 1.2.2:** verifica DNS antes de instalar pacotes e reaplica a
configuração DNS do NetworkManager quando necessário. Se os nomes não
resolverem após tentativas limitadas, interrompe com diagnóstico; não troca
o resolvedor por um serviço público nem reinicia a rede.

**Versão 1.2.1:** corrige a renovação automática da credencial OCI após a
instalação. Para uma VM já existente, consulte a
[correção sem recriar o ambiente](TROUBLESHOOTING.md#correção-121-renovação-da-credencial-oci)
antes de atualizar a Stack e aplicar um Plan que possa substituir a VM.

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
| Chave pública SSH / origem IPv4 | Por padrão, **deixe ambos vazios**. Para diagnóstico, informe a chave `.pub` e um IPv4 `/32`, ou `0.0.0.0/0` com o aceite abaixo |
| Aceito expor a porta SSH à internet temporariamente | Marque somente se usar `0.0.0.0/0`. Não há fechamento automático após o evento |

Tenancy OCID é preenchido pela Console. O Terraform cria o compartment,
rede, VM, dynamic group e policy. Você não precisa copiar compartment OCID,
gerar chaves SSH ou criar API key de modelo manualmente.

Clique **Next**. Em **Review**, desmarque **Run apply**, revise e clique **Create**.

### SSH opcional no evento: IPs variáveis

Ainda não tem uma chave? Para **SSH**, use o
[guia de geração de chaves no assistente Compute da Console](../docs/OCI_RESOURCE_MANAGER_CONSOLE.md#d-gerar-e-baixar-as-chaves-ssh-pela-console)
(mantenha a região escolhida para sua instalação; cancele sem criar outra VM).
Para quem procura **Perfil → Configurações do usuário → API keys**, há um
[passo a passo separado de chaves de assinatura OCI](../docs/OCI_USER_API_KEYS.md).
São credenciais diferentes: a chave do perfil não deve ser colada no campo SSH.

Na versão **1.2.0**, é possível liberar SSH temporariamente para qualquer
**IPv4**, sem precisar conhecer o IP do hotel. Isso expõe TCP/22 à internet:
qualquer pessoa poderá tentar conectar, mas ainda precisará se autenticar.
O Terraform exige a chave pública e não habilita autenticação por senha.

No grupo **4. Opcional — diagnóstico por SSH** do formulário:

1. Em **Chave pública SSH opcional**, cole o conteúdo do arquivo `.pub`
   (começando por `ssh-ed25519` ou `ssh-rsa`). Nunca envie a chave privada à Stack.
2. Em **Origem IPv4 do SSH**, informe `0.0.0.0/0`.
3. Marque **Aceito expor a porta SSH à internet temporariamente**.
4. Salve, execute **Plan**, revise a regra **TCP/22** e depois **Apply**.

O acesso à imagem Oracle Linux usa o usuário `opc` e a chave privada
correspondente. O token Telegram não é uma credencial SSH. Não compartilhe
chaves privadas entre participantes e não habilite login por senha.

**Stack já criada:** primeiro baixe o pacote atualizado e substitua a
configuração por **Edit Stack → Folder**, depois preencha os campos acima.
Repetir Plan com os arquivos antigos mantém a restrição `/32`.
Se a VM já foi criada sem chave, editar seus metadados não garante que a chave
seja instalada no sistema operacional; veja [diagnóstico SSH](TROUBLESHOOTING.md).
Esse ajuste de rede não reinstala o Hermes nem força a substituição da VM;
confira sempre o Plan antes de aplicar.

**Após o evento**, use **Edit Stack** para trocar `0.0.0.0/0` pelo seu IPv4
atual com `/32` e desmarque o aceite. Para fechar SSH completamente, deixe
chave pública e origem IPv4 vazias e desmarque o aceite. Em ambos os casos,
execute novo **Plan → revisar → Apply**. A liberação pública não expira sozinha.

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
Nesta edição, rede/VM/inferência permanecem na região selecionada (ORD ou GRU).
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
