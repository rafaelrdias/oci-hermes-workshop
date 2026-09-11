# Terraform do stand Oracle — execução pela Console OCI

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

ORD e GRU são suportadas, com Llama 3.3 70B on-demand na região selecionada.
A home region pode ser diferente: é detectada automaticamente e usada apenas
pelo provider `oci.home` para criar IAM global. A região da instalação deve
estar subscrita e `READY`. Nenhuma
API key OCI precisa ser criada. O token Telegram persiste em state/planos,
variáveis e metadados da VM; o formulário exige aceite e uso de bot exclusivo.

SSH é opcional e fechado por padrão. Para remover, use **Destroy na Console**
antes de excluir a Stack. O disco/arquivos/histórico da VM serão apagados.

Na versão 1.2.0, para diagnóstico com IPs variáveis: informe chave pública,
`ssh_allowed_cidr = 0.0.0.0/0` e marque `acknowledge_public_ssh` no formulário.
Isso expõe somente TCP/22 a qualquer IPv4; não habilita login por senha.
Após o evento, restrinja a `/32` ou deixe chave/CIDR vazios, desmarque o aceite
e aplique novo Plan/Apply. Não há expiração automática. Em uma VM existente
sem chave, a atualização dos metadados pode não instalar a chave no SO.

Já criou uma Stack com o pacote antigo? Baixe novamente este pacote e use
**Edit Stack → configuração Terraform → Folder** para substituir os arquivos.
Confira as variáveis, salve e execute novo **Plan → Apply**. Apenas repetir
Plan não atualiza o código da Stack. Veja o guia completo para os detalhes.

Testes locais não substituem a homologação real em Trial:
[veja o roteiro de aceite](https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/stand/VALIDATION.md).
