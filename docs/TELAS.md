# Capturas da Console OCI e do Telegram

[Voltar ao guia](../README.md)

## Origem e fidelidade

As 12 imagens PNG abaixo foram capturadas na **Console OCI autenticada**, em
**21/09/2026**, com região **US Midwest (Chicago)**, interface em inglês, tema
escuro e o formulário Redwood exibido pela conta. O pacote do laboratório
usado no formulário é a versão **1.5.0** da branch `resource-manager`.

São recortes de screenshots, **não reconstruções, mockups ou imagens geradas
por IA**. Não foram substituídos rótulos, opções ou resultados da interface.
Os recortes retiram dados da conta e áreas que não ajudam naquele passo.
O nome `hermes-evento` foi digitado no próprio formulário, ainda não enviado.

Na imagem de revisão, um texto de demonstração **sem validade como token**
foi usado apenas para avançar no rascunho; a Console o mascara. O rascunho foi
cancelado e os valores de demonstração não foram usados em uma implantação.
Nas imagens dos campos de token, os campos estão vazios.

Não foram criados recursos, executados jobs Plan/Apply/Destroy ou revelados
segredos para produzir estas capturas. Elas comprovam a aparência do formulário,
não uma execução bem-sucedida do laboratório.

## Catálogo

| Captura real | Onde ajuda |
|---|---|
| [01 — Seletor de região](images/console/01-regiao-chicago.png) | Identificar Chicago e diferenciar região ativa de home region |
| [02 — Menu Resource Manager](images/console/02-menu-resource-manager.png) | Encontrar Stacks em Developer Services |
| [03 — Welcome e pacote do Deploy](images/console/03-deploy-pacote.png) | Reconhecer o destino do botão e conferir Package URL |
| [04 — Alternativa Folder](images/console/04-alternativa-folder.png) | Usar upload manual quando necessário |
| [05 — Nome da Stack](images/console/05-nome-stack.png) | Trocar o nome automático por um nome fácil de localizar |
| [06 — Versão do Terraform](images/console/06-versao-terraform.png) | Encontrar a opção 1.5.x oferecida pela Console |
| [07 — Região, modelo e áudio](images/console/07-variaveis-regiao-modelo.png) | Conferir GPT-OSS em ORD e transcrição local |
| [08 — Token e seu aceite](images/console/08-token-e-aceite.png) | Localizar os dois campos de senha e o consentimento independente |
| [09 — Compute](images/console/09-compute.png) | Conferir shape e índice de availability domain |
| [10 — Sem SSH](images/console/10-ssh-fechado.png) | Reconhecer o padrão, suficiente para usar Telegram |
| [11 — Gerar chave SSH](images/console/11-ssh-gerar-chave.png) | Distinguir geração da chave de abertura da porta |
| [12 — Review sem Apply automático](images/console/12-review-sem-apply.png) | Desmarcar Run apply antes de criar a Stack |

## Cobertura e limites

Não havia uma Stack Hermes implantada disponível na sessão utilizada para
esta revisão. Por isso, **não há capturas próprias dos resultados de Plan/Apply,
Application information, recuperação da chave privada ou Destroy** nesta série.
Essas etapas continuam descritas no guia e nas instruções de SSH; não foram
substituídas por telas desenhadas. As orientações de Plan e Apply foram
conferidas com a documentação oficial da Oracle.

As quatro imagens do Telegram também são recortes reais, fornecidos pelo
mantenedor e documentados abaixo. Elas registram as conversas das capturas;
não representam uma nova implantação realizada durante esta revisão do guia.

A interface OCI pode variar conforme idioma, tema e atualizações. Use os nomes
dos controles, o contexto da página e os pontos de conferência do roteiro;
a posição exata de um botão não deve ser o único critério.

## Telegram e BotFather

O mantenedor forneceu uma captura do BotFather em **21/09/2026**, mostrando
a sequência `/newbot`, nome de exibição, tentativa de username sem o sufixo
`bot`, correção e confirmação da criação. A data da conversa exibida no original
é diferente da data de recebimento da captura.

Foram autorizados **somente recortes e tarjas opacas**, sem geração de imagem
por IA. A conversa e os rótulos foram preservados. A mensagem de uma criação
anterior, visível na parte superior do original, não foi incluída nos recortes.
O token da confirmação foi substituído por pixels pretos opacos antes de
exportar o PNG. O original não foi alterado nem adicionado ao repositório.

| Recorte real | Onde ajuda |
|---|---|
| [BotFather — nome e username](images/telegram/01-botfather-nome-username.png) | Distinguir nome de exibição de username e reconhecer o erro do sufixo |
| [BotFather — link e token ocultado](images/telegram/02-botfather-token-link.png) | Localizar as duas informações necessárias para continuar na OCI e no Telegram |

A tarja é uma edição de segurança, **não um elemento da interface Telegram**.
Ela não revoga credenciais. Se os tokens do original ainda estiverem ativos,
o proprietário deve substituí-los pelo BotFather. Não foi feito acesso à API
do Telegram nem alteração de bots para produzir estas imagens.

## Telegram e pareamento com o Hermes

Uma segunda captura, também recebida em **21/09/2026**, mostra a conversa com
o bot criado: comando de vínculo, confirmações do instalador, `/new` e resposta
do teste de arquivo.

| Recorte real | Onde ajuda |
|---|---|
| [Telegram — vínculo com o Hermes](images/telegram/03-telegram-vinculo.png) | Diferenciar Conta vinculada de Configuração concluída e identificar quando enviar `/new` |
| [Telegram — resposta do teste de arquivo](images/telegram/04-telegram-teste-arquivo.png) | Reconhecer o resultado esperado após pedir criação e leitura do arquivo |

O código privado enviado após `/start` foi coberto por uma tarja opaca antes
de exportar. O recorte do resultado inclui somente a resposta do bot, sem
os nomes de participantes e as mensagens citadas da conversa. Os textos da
interface não foram reescritos e os horários não foram alterados.

A imagem original não foi adicionada ao repositório. Nenhum código de vínculo
foi utilizado e nenhum bot foi acionado para produzir os recortes. A captura
do teste é de uma tarefa de texto/arquivo; não demonstra a transcrição de áudio.

## Atualizar as capturas

1. Abra uma sessão autorizada na Console e confira o pacote atual do laboratório.
2. Capture o controle real, com contexto suficiente para identificar a etapa.
3. Não inclua tokens, comandos de pareamento, chaves privadas, OCIDs, IPs de
   participantes ou dados de conta. Prefira recortes; não revele segredos.
4. Não altere o DOM para inventar valores, estados Succeeded ou rótulos.
5. Para documentar etapas posteriores, use uma Stack de teste autorizada já
   existente. A necessidade de um screenshot não autoriza provisionar ou destruir.
6. Confira cada PNG em tamanho legível, a legenda e os links. Atualize este
   catálogo com a data e as condições observadas.
7. Mantenha imagens em `docs/images/console/` ou `docs/images/telegram/`, nunca
   em `terraform/` ou no pacote da branch `resource-manager`.

## Referências oficiais

- [Botão Deploy to Oracle Cloud](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/deploybutton.htm)
- [Criar um job Plan](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/create-job-plan.htm)
- [Criar um job Apply](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/create-job-apply.htm)
- [Schema e Application information](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/terraformconfigresourcemanager_topic-schema.htm)
- [BotFather e criação de bots](https://core.telegram.org/bots/features#botfather)
