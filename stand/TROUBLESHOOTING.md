# Problemas e operação pela Console

| Sintoma | O que fazer |
|---|---|
| Botão de deploy retorna 400 | Use o download leve → extraia → Resource Manager → Create Stack → My configuration → Folder |
| Folder excede 11 MB | Selecione somente a pasta da branch `stand-resource-manager`, não o repositório principal ou pasta com `.terraform` |
| Plan rejeita região | Escolha ORD/GRU subscrita e READY no topo e no formulário. A home region pode ser outra; não há fallback de VM/LLM |
| Erro antigo “Selecione a HOME REGION do Trial” | Atualize o pacote da mesma Stack por Edit Stack → Folder e execute novo Plan. Veja o guia principal; repetir Plan com arquivos antigos não resolve |
| Erro antigo “SSH deve ficar restrito a um único IPv4 (/32)” | Atualize a Stack com o pacote 1.2.0 por Edit Stack → Folder. Para qualquer IPv4, preencha chave pública + 0.0.0.0/0 e marque o aceite de exposição pública |
| Plan pede aceite | Leia o aviso: token persiste em variáveis/state/metadados. Marque apenas se concordar |
| `NotAuthorizedOrNotFound` criando IAM | Use administrador com permissão para criar IAM. O provider oci.home seleciona automaticamente o endpoint da home region |
| `Out of host capacity` | Aguarde/reexecute Plan/Apply; ou escolha outra shape/AD explicitamente em Edit Stack. Capacidade não é garantida |
| `LimitExceeded` | Confira créditos, Service Limits e recursos existentes. O template não amplia quota nem transforma conta em paga |
| Apply succeeded, bot silencioso | Bootstrap ainda pode estar em andamento. Revele/copie o comando de pareamento nos Outputs e envie em DM |
| `Could not resolve host`, pacotes falham e todos os serviços Hermes estão inativos | Instalação parou antes do Telegram. A versão 1.2.2 verifica/reaplica DNS antes dos downloads; veja recuperação abaixo |
| `/start` sem resposta | Use o comando completo `/start stand_...` da sua Stack; `/start` sozinho não autoriza a conta |
| “Conta vinculada”, sem “Configuração concluída” | Testes OCI ainda aguardam IAM/acesso/modelo/limites. Alterações de dynamic groups podem levar até uma hora |
| OCI persiste sem funcionar | Confira GenAI on-demand, policy/dynamic group, limites e crédito. Não autorize `manage all-resources` para contornar |
| Tool calling falhou | Não trate chat simples como aceite. É preciso validar ferramenta e retorno ao modelo antes de liberar ao público |
| Plan rejeita Grok em GRU | Selecione Chicago para Grok 4.3/4.6, ou Llama explicitamente para GRU. Não mude apenas o endpoint na VM |
| Áudio não foi entendido | Confira STT habilitado no formulário, use português e áudio curto. Verifique bootstrap/prepare_audio e logs do gateway, sem expor gravações ou transcrições |
| Bootstrap parou baixando Whisper | Confira DNS/HTTPS para Hugging Face e espaço em disco. Não contrate STT pago como contorno; instalação exige os pesos locais antes da ativação |
| `/voice on` não produz áudio | Comportamento intencional desta edição: entrada por voz, saída sempre textual |
| `Response truncated due to output length limit` até em tarefa curta | Versões até 1.2.2 podiam fragmentar ferramentas no streaming. A versão 1.2.3 corrige os IDs; veja abaixo antes de aumentar tokens |
| Bot já tem webhook/Telegram 409 | Use um bot novo/exclusivo. O ativador não apaga integrações externas |
| Bot respondeu ao instalador mas não ao visitante | Envie `/new` e nova tarefa. A mensagem do instalador não prova a resposta do agente |
| Funcionou inicialmente e depois retornou `Provider authentication failed` / OCI 401 | Versões até 1.2.0 tinham um defeito na renovação do token de Instance Principal na ponte LiteLLM. A versão 1.2.1 corrige esse caminho. Veja abaixo; não crie outra API key nem amplie IAM sem diagnóstico |
| Pareamento para conta errada | Destrua a instalação, revogue token e crie novo vínculo privado; não compartilhe o comando dos Outputs |

## Retomar sem criar outra Stack

### Limite do Grok (HTTP 429) — versão 1.3.1

Uma mensagem pode exigir várias inferências: decidir escrever → executar
`write_file` → decidir ler → executar `read_file` → responder. Cada chamada
inclui contexto e definições das ferramentas; o tamanho da frase digitada
não representa o total de tokens processados. Títulos auxiliares também usam
inferência. Um smoke test curto pode passar e a conversa completa atingir quota.

Na ocorrência diagnosticada, a mensagem da OCI mencionou **service limit**,
mas isso não comprova esgotamento dos 200 mil tokens/minuto. Um teste direto
na API, sem Hermes/LiteLLM, consumiu 7.800 tokens e a chamada seguinte retornou
429. A Oracle documenta [throttling dinâmico](https://docs.oracle.com/en-us/iaas/Content/generative-ai/dynamic-throttling.htm);
essa é uma hipótese, não uma causa confirmada nesta tenancy.
O arquivo foi criado antes do 429 na chamada seguinte. As
repetições antigas em 2–5 segundos ainda encontravam a mesma janela limitada.
Isso é distinto do limite local de 120 chamadas/hora e não indica falha de SSH,
Telegram, STT ou necessariamente falta de créditos.

A ponte 1.3.1 respeita `Retry-After` quando informado; sem ele, aguarda 65 s.
Compartilha a espera entre requisições, serializa a abertura de chamadas OCI e
faz **no máximo uma repetição adicional** antes de devolver o erro. O orçamento
da abertura da chamada é 100 s, incluindo fila/espera; não repete streams já
entregues nem ferramentas locais. O retry conta no limite local de 120/h.
Os logs registram apenas status, espera e tentativa, sem prompts/credenciais.
O Hermes ainda tem seu próprio limite de tentativas e timeout da tarefa:
a espera não garante conclusão se a quota continuar insuficiente.

Para testar após a correção, envie `/new`, peça criação/leitura e aguarde
sem reenviar a mensagem repetidamente. Não é necessário novo pareamento.

Para vários visitantes/mais velocidade, o administrador deve conferir na
**Console OCI → Governance & Administration → Limits, Quotas and Usage**
os limites de **Generative AI**, com região **Chicago**, e procurar
`grok-4-3-tokens-per-minute-count` para Grok 4.3, ou
`grok-4-6-tokens-per-minute-count` para Grok 4.6. Confira uso e limite efetivo;
se o 429 ocorrer abaixo do limite, forneça os request IDs ao suporte Oracle.
Não assuma que aumentar o limite resolve. Quando o esgotamento for confirmado,
o aumento depende de aprovação/elegibilidade da conta.
Mais quota não é crédito gratuito: monitore custos e não autorize upgrade
automático. A VM não possui permissão para alterar quotas.

Fonte: [Grok 4.6 e nome oficial do limite](https://docs.oracle.com/en-us/iaas/Content/generative-ai/xai-grok-4-6.htm).

### Trocar o modelo em uma VM existente

**Nova instalação 1.3.3 em Chicago:** DG e policy já são criados pelo Terraform,
com acesso a todos os modelos de chat em ORD no compartment do stand.
Não execute a edição manual abaixo ao reinstalar com o pacote atual.
Isso não altera automaticamente o modelo configurado no Hermes nem garante
disponibilidade/cota de cada modelo. Em GRU, o pacote continua restrito ao Llama.

**VM antiga, instalada até 1.3.2:** a policy restringe `target.model.id` ao
modelo selecionado. Alterar só a ponte pode retornar 404 (recurso não encontrado
ou não autorizado). Para migrar Chicago ao escopo solicitado na versão 1.3.3:

1. Na Console da **tenancy da VM**, abra **Identity & Security → Policies**
   (ou pesquise Policies) e selecione o **compartimento raiz**. Se necessário,
   selecione a home region para editar IAM; a VM/LLM continuam em Chicago.
2. Abra **hermes-stand-inference** (ou `<prefix>-inference`, se mudou o nome).
3. Em **Edit policy**, preserve a regra, os IDs e o verbo `use generative-ai-chat`;
   substitua a condição `target.model.id = 'xai.grok-4.6'` (ou o modelo atual)
   por `request.region = 'ORD'`. Salve e aguarde propagação IAM.
4. O mantenedor deve atualizar o modelo em `/etc/hermes-stand.json`, manter
   orçamento de saída de 4.096 tokens para Grok e usar os scripts da versão 1.3.3.
   Reiniciar somente a ponte aplica o modelo; não é necessário novo pareamento.
5. Validar inferência e criação/leitura de arquivo pelo Hermes. HTTP 404 não é
   HTTP 429: primeiro confirme a autorização e a disponibilidade regional.

Mantenha o escopo no compartment do stand e na região ORD; não dê administração
IAM à VM. O acesso a todos os modelos de chat em ORD pode permitir consumo de
modelos mais caros, mas não aumenta quota/crédito nem cria fallback no agente.
A atualização manual gera diferença em relação à Stack: alinhe posteriormente
a variável `llm_model` e o código da Stack, mas **revise o Plan** — este pacote
substitui a VM quando modelo/bootstrap mudam. Não aplique uma substituição
apenas para sincronizar o state sem antes preservar seus dados.

Modelo e limite: [Grok 4.3 — Oracle](https://docs.oracle.com/en-us/iaas/Content/generative-ai/xai-grok-4-3.htm).

### Ferramentas truncadas no streaming — versão 1.2.3

No defeito diagnosticado, os logs registravam `Unrepairable tool_call arguments`
para pedaços de palavras/JSON. A ponte gerava um ID diferente para cada
fragmento da mesma chamada; o Hermes recusava argumentos incompletos,
repetia a solicitação e exibia uma mensagem genérica de limite de saída.
Isso não era falta de créditos nem exigia outro modelo ou limite maior.

- Novas instalações: use o pacote **1.2.3** da branch `stand-resource-manager`.
  A ativação só libera o gateway após validar também ferramenta e retorno
  em streaming. O teste final no Telegram continua obrigatório.
- VM existente com SSH administrativo: o mantenedor pode fazer backup e
  atualizar somente `/opt/hermes-stand/bridge.py` e `smoke.py` com os arquivos
  desta versão, reiniciar `hermes-oci-bridge` e executar o teste `smoke.py`
  com `/opt/hermes-stand/bridge-venv/bin/python`. Não é preciso novo pareamento.
- Depois da correção, envie **`/new`** ao bot e teste saudação e criação/leitura
  de arquivo. Isso inicia uma sessão limpa sem apagar o workspace.
- Pela Console, atualizar arquivos da Stack não altera a VM imediatamente.
  O próximo Plan/Apply pode **substituir a VM**, pois mudou o bootstrap.
  Faça backup dos dados e revise o Plan antes de aceitar a substituição.

Uma resposta genuinamente longa ainda pode atingir o teto de saída; a
correção preserva esse sinal. Se o problema persistir após `/new`, diagnostique
os logs da nova execução, sem publicar conteúdo de conversas ou credenciais.

### Falha de DNS antes da instalação — versão 1.2.2

Em uma VM diagnosticada, o NetworkManager havia recebido `169.254.169.254`
por DHCP, mas `/etc/resolv.conf` continha `192.168.122.1`. Consultas diretas
ao resolvedor OCI funcionavam; os downloads pelo resolvedor do sistema falhavam.
Não presuma que toda falha de DNS tem essa mesma causa.

Para diagnóstico pelo atendente, compare `/etc/resolv.conf` com
`nmcli -g IP4.DNS device show`. Quando a configuração recebida está correta,
`sudo nmcli general reload dns-rc` reaplica o DNS gerenciado sem derrubar a
interface. Faça backup de `/etc/resolv.conf` antes. Valide resolução e acesso
aos repositórios antes de retomar os pacotes e o bootstrap.

O instalador 1.2.2 faz essa verificação **antes de dnf**, respeita os servidores
configurados no NetworkManager, preserva um backup e limita as tentativas.
Não desabilita NetworkManager, não altera DHCP da VCN e não fixa DNS público.
Se DNS/rotas/firewall continuarem incorretos, encerra com erro em vez de
anunciar que o Telegram está pronto.

Após recuperação manual, `cloud-init status` pode continuar registrando o
erro da execução inicial. Não execute `cloud-init clean` nem recrie a VM só
para apagar esse registro: confira o resultado da recuperação, o marcador
`/opt/hermes-stand/bootstrap.done` e o estado dos serviços.
O serviço de ativação fica aguardando o comando privado da **Stack atual**.

Novas instalações devem usar o pacote atualizado. Atualizar os arquivos de
bootstrap na Stack existente pode propor substituição da VM; revise Plan
e faça backup antes de aplicar. A recuperação direta não exige novo Apply.

Referências: [NetworkManager — reload dns-rc](https://networkmanager.dev/docs/api/latest/nmcli.html)
e [OCI — DHCP e DNS](https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/managingDHCP.htm).

### Correção 1.2.1: renovação da credencial OCI

A ponte agora chama a interface do SDK que verifica/renova o token antes de
assinar cada requisição. Um lock mantém renovação e assinatura juntas nas
chamadas simultâneas. Não é necessário trocar token Telegram, chave SSH ou
pareamento. Reiniciar a ponte antiga apenas obtém outro token temporário;
não corrige permanentemente a renovação.

A versão também trata o marcador SSE `[DONE]` antes do parser JSON do
LiteLLM 1.100.1. Isso evita erro no fim do streaming depois de receber texto.
Somente esse marcador é tratado; payloads inválidos continuam gerando erro.

Para **novas instalações**, use o pacote atualizado. Para uma **VM existente**,
o mantenedor pode fazer backup e substituir apenas `/opt/hermes-stand/bridge.py`
pelo arquivo da versão 1.2.1, preservando root:root e modo 0644, e reiniciar
somente `hermes-oci-bridge`. Valide `smoke.py` e depois a conversa no Telegram.
Não exponha `.env`, `bridge.key` ou credenciais nos logs.

**Atenção ao Terraform:** carregar o pacote novo na Stack e executar Apply
pode propor **substituir a VM**, pois esse arquivo faz parte do bootstrap.
Para preservar a VM e suas conversas, não aprove essa substituição inadvertidamente.
Uma correção direta na VM não atualiza a cópia antiga do Terraform armazenada
na Stack; planeje a atualização/recriação futura com backup e revisão do Plan.

Outros erros 401 ainda exigem diagnóstico: essa correção não substitui
verificação de IAM, limites, acesso ao modelo e disponibilidade de créditos.

Para falhas de provisionamento, na **mesma Stack**, execute novo **Plan**,
revise e depois **Apply**. O state do Resource Manager reaproveita os recursos
já criados. Não é necessário baixar o state ou copiar OCIDs entre ferramentas.

Para IAM ou conectividade temporária, a VM faz novas tentativas por systemd.
Um novo Apply sem mudanças não reinstala software. Se não deseja aguardar,
execute **Destroy** para evitar consumo contínuo.

## Falha definitiva no bootstrap / reinstalação

Primeiro confira a instância em **Compute → Instances**, na região e
compartment exibidos nos Outputs. Um Apply concluído não é evidência de que
todos os downloads e serviços terminaram com sucesso.

Sem acesso SSH configurado, a recuperação mais simples para um **ambiente
descartável ainda sem dados** é: **Destroy na Stack → aguardar sucesso → novo
Plan → Apply** na mesma Stack. Será criada outra VM, com novo código de vínculo;
revele o novo output e faça o pareamento novamente. Isso perde os dados da VM.

Para diagnóstico especializado, SSH pode ser habilitado desde a criação ou
posteriormente: **Edit Stack → chave pública SSH + IPv4 do administrador `/32`
→ Plan → revisar → Apply**. Para IPs variáveis no evento, a versão 1.2.0 aceita
**0.0.0.0/0 + aceite de exposição pública**, mantendo a chave obrigatória.
Isso abre somente TCP/22 para qualquer IPv4; não habilita senha nem libera
portas da aplicação. Restrinja a `/32` ou feche SSH após o evento por novo
Plan/Apply — não há expiração automática.
Guarde a privada fora da Stack. Se a imagem/serviço
de SSH não atualizar a chave automaticamente, use o procedimento de recuperação
da Console OCI; não presuma que editar metadados sempre atualiza `authorized_keys`.

Na VM, estes comandos são **opcionais, para o atendente técnico**, não parte do
fluxo do visitante nem da execução do Terraform:

```bash
sudo cloud-init status --long
sudo tail -n 80 /var/log/hermes-stand-bootstrap.log
sudo systemctl status hermes-oci-bridge hermes-gateway hermes-stand-activate --no-pager
sudo journalctl -u hermes-stand-activate -u hermes-gateway --since '-20 min' --no-pager
```

Não compartilhe `user-data`, `.env`, state ou conteúdo de
`/etc/hermes-stand-secrets.json`. Logs do agente podem conter conversas; revise
e anonimize antes de enviar a alguém.

## Rotação do token e atualização do bootstrap

1. No BotFather, revogue o token exposto e obtenha outro.
2. Faça backup dos arquivos/memória necessários antes de reinstalar.
3. **Edit Stack → Configure variables**: atualize o token e a confirmação.
4. Execute **Plan**. Esta configuração marca a VM para **substituição** quando
   token/bootstrap muda, porque cloud-init só executa a instalação inicial.
5. Revise os recursos a destruir/criar e só então **Apply**.
6. Use o **novo** comando privado dos Outputs e confirme o teste real.

O token antigo continua podendo existir em versões históricas do state/jobs.
**Revogá-lo no BotFather** é o que elimina sua validade; mascarar o campo ou
excluir apenas um arquivo não apaga todas as cópias.

## Trocar shape ou AD

Em **Edit Stack → Configure variables**, E4.Flex ou A1.Flex são escolhas
explícitas. E5/E4 usam créditos; A1 depende de elegibilidade/quota/capacidade.
Em Chicago, use outro índice de AD somente se esse AD existir na tenancy;
`0` é o primeiro. GRU pode oferecer apenas um.

Revise o Plan: trocar shape/AD pode substituir a VM e perder dados. Não há
retry infinito de Compute nem mudança automática para recurso mais caro.

## Encerrar

Use **Terraform actions → Destroy** na Console. Espere **Succeeded** antes de
excluir a Stack. Se houver recursos adicionais no compartment, a exclusão
pode falhar: remova/mova apenas os que você reconheça e repita. Não exclua a
Stack como solução para falha de Destroy. Exclua/revogue o bot no BotFather
se não for reutilizá-lo.
