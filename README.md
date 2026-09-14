# Terraform do stand Oracle — execução pela Console OCI

Versão **1.4.0**: SSH automático opcional. Em **Configure variables → 4. Opcional —
acesso SSH e chave automática**, marque `generate_ssh_key` e o aceite
`acknowledge_ssh_private_key_in_state`; deixe `ssh_public_key` vazio.
Terraform gera RSA 4096 e instala somente a pública. A privada fica no state
e na saída sensível `ssh_private_key_pem`. Não é recomendação para produção.

Depois do Apply, abra **a Stack recém-executada → Application information →
SSH opcional**, revele/copie `ssh_private_key_pem` e salve como `hermes.key` em
texto puro no seu computador/gerenciador seguro, preservando cabeçalho,
rodapé e quebras de linha. Não há download automático nem envio ao Telegram.
Restrinja acesso à Stack/state; nunca publique a chave ou o state.

`ssh_allowed_cidr` vazio mantém a porta fechada mesmo com a chave instalada.
Para conectar, informe IPv4 `/32`; `0.0.0.0/0` exige também o aceite separado
`acknowledge_public_ssh`. Consulte `ssh_connection_command` depois do Apply.
Para fechar/reabrir SSH, altere o CIDR sem desmarcar a geração: preserva a chave.
Sem geração, é possível continuar fornecendo a própria chave pública.
Por padrão, geração e abertura SSH permanecem desabilitadas.

Versão **1.3.3**: DG e policy são criados automaticamente pelo Terraform.
O DG inclui somente a nova VM. Em Chicago, a policy permite todos os modelos
de chat no compartment do stand com `where request.region = 'ORD'`, sem
restrição por ID de modelo. Em GRU, mantém Llama e `request.region = 'GRU'`.
Não concede administração, embeddings ou rerank; não aumenta quotas/créditos.
O Hermes continua usando Grok 4.3 por padrão, STT local e respostas textuais.

Após Destroy, baixe/extraia novamente este pacote e use a pasta atualizada
em **Create Stack → My configuration → Folder → Plan → Apply**. Não use uma
cópia antiga. O formulário deve indicar **1.4.0**. Se reutilizar a Stack,
substitua primeiro sua configuração Terraform pela pasta atualizada.
Depois abra **a Stack recém-executada → Application information** e envie
o novo `telegram_pairing_command` ao bot. Não há etapa manual de IAM.

Versão **1.3.2**: escolha Chicago e mantenha `xai.grok-4.3` como LLM.
Grok 4.6 permanece opcional. Na versão 1.3.2, a policy autorizava somente o modelo escolhido;
a versão 1.3.3 substitui essa restrição em Chicago conforme descrito acima.
STT local e respostas sempre textuais são mantidos. Trocar modelo não garante
eliminar HTTP 429. Em uma Stack existente, alterar o modelo/bootstrap pode
substituir a VM: revise o Plan e não aplique sem backup e aceite da perda de dados.

Versão **1.3.1**: espera e retry limitados para HTTP 429 da OCI. Mantém Grok,
STT local e respostas textuais; não aumenta quotas nem contrata capacidade.

Versão **1.3.0**: escolha Chicago e mantenha `xai.grok-4.6` como LLM.
STT local Whisper vem habilitado; respostas sempre em texto. Sem API paga de
transcrição, mas VM e LLM consomem créditos. Grok é hospedado pela xAI via OCI.

Versão 1.2.3: identidade estável das ferramentas no streaming e teste de
ativação com e sem streaming. Inclui as correções anteriores.

Versão 1.2.2: preflight DNS antes dos downloads, recuperação via NetworkManager
e tentativas limitadas de instalação de pacotes. Inclui as correções 1.2.1.

Versão 1.2.1: renovação da credencial OCI corrigida na ponte LiteLLM. Em VMs
existentes, atualizar o bootstrap via Apply pode substituir a VM; veja o
guia de diagnóstico antes de aplicar. Novas instalações já incluem a correção.

[Abra o guia completo, sem comandos](https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/stand/README.md).

Esta pasta é publicada sozinha na branch `stand-resource-manager`, usada pelo
botão **Deploy to Oracle Cloud**. Ela inclui `schema.yaml` para o formulário
do Resource Manager e os arquivos de instalação da VM. Não inclua `.terraform`,
state, variáveis pessoais, chaves, PDFs ou apresentações no pacote.

Fluxo: **Create Stack → token sensível + aceite → Plan → revisar → Apply →
Application information → revelar comando privado → enviar ao bot → aguardar**.

ORD usa Grok 4.3 por padrão. Para GRU selecione Llama 3.3 70B explicitamente;
Grok + GRU é rejeitado. Não há fallback automático de modelo/região.
A home region pode ser diferente: é detectada automaticamente e usada apenas
pelo provider `oci.home` para criar IAM global. A região da instalação deve
estar subscrita e `READY`. Nenhuma
API key OCI precisa ser criada. O token Telegram persiste em state/planos,
variáveis e metadados da VM; o formulário exige aceite e uso de bot exclusivo.

SSH é opcional e fechado por padrão. Para remover, use **Destroy na Console**
antes de excluir a Stack. O disco/arquivos/histórico da VM serão apagados.

Para diagnóstico com IPs variáveis: gere a chave com aceite ou informe sua pública,
`ssh_allowed_cidr = 0.0.0.0/0` e marque `acknowledge_public_ssh` no formulário.
Isso expõe somente TCP/22 a qualquer IPv4; não habilita login por senha.
Após o evento, restrinja a `/32` ou deixe somente CIDR vazio, desmarque o aceite
de SSH público e aplique novo Plan/Apply. Não desmarque geração para fechar a porta.
Não há expiração automática. Em uma VM existente
sem chave, a atualização dos metadados pode não instalar a chave no SO.
Alterar/remover metadados tampouco garante revogação no SO. Um novo state gera
outra chave; Apply normal mantém a mesma. Guarde sua cópia antes de Destroy;
jobs/state históricos podem reter segredos e o Terraform não apaga cópias baixadas.

Já criou uma Stack com o pacote antigo? Baixe novamente este pacote e use
**Edit Stack → configuração Terraform → Folder** para substituir os arquivos.
Confira as variáveis, salve e execute novo **Plan → Apply**. Apenas repetir
Plan não atualiza o código da Stack. Veja o guia completo para os detalhes.

Testes locais não substituem a homologação real em Trial:
[veja o roteiro de aceite](https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/stand/VALIDATION.md).
