# Validação e homologação antes do stand

## Escopo dos testes desta entrega

### Versão 1.4.0 — par SSH automático opcional, 14/09/2026

- Provider TLS 4.3.0 fixado, instalado e hashes registrados no lockfile.
  Geração RSA 4096 opt-in com aceite independente de persistência da privada.
- Chave própria e geração automática são mutuamente exclusivas; a privada
  aparece somente no state/saída sensível, não no cloud-init/VM/Telegram.
- 26 testes Terraform com providers simulados aprovados: sem SSH por padrão,
  geração com porta fechada, chave pública correta na metadata, privada ausente
  da metadata/config, /32, /0 com aceite separado, falta de chave, conflito de
  modos, falta de aceite e manutenção de chave/VM quando só o CIDR muda.
- 51 testes Python aprovados, incluindo defaults seguros no schema, output
  privado sensível e ausência de entrada de chave privada fornecida pelo usuário.
- `init -backend=false`, `validate`, `fmt -check` e `git diff --check` aprovados.
- **Pendente:** nova Stack real, recuperação/cópia da chave pela Console e
  conexão SSH com OpenSSH. Testes simulados não comprovam UI, criptografia
  do par real nem conectividade; nenhum recurso OCI foi criado nesta validação.
- Mantidos Grok 4.3, STT local, respostas textuais, DG de uma VM e IAM ORD.

### Versão 1.3.3 — IAM regional automático, 14/09/2026

- DG mantido como recurso Terraform, com regra exata para o OCID da única
  VM criada na Stack; DG e policy criados na raiz pelo provider da home region.
- ORD: policy autoriza `use generative-ai-chat` somente no compartment do stand
  com `where request.region = 'ORD'`, sem restrição por modelo.
- GRU: preserva restrição ao Llama e adiciona condição de região GRU.
- 19 testes Terraform com providers simulados aprovados, incluindo comparação
  exata das regras em ORD/GRU e do vínculo do DG à VM; 50 testes Python aprovados.
  `terraform validate`, `fmt -check` e `git diff --check` aprovados.
- Grok 4.3, STT local e respostas textuais permanecem configurados. Nenhuma
  alteração de credencial, quota, crédito ou permissão administrativa da VM.
- A Stack anterior foi destruída pelo usuário. **Pendente: nova implantação
  real pela Console e teste no Telegram.** Os testes locais não comprovam
  propagação IAM, disponibilidade do modelo nem inferência ao vivo.

### Histórico inicial

Validações locais em 10–11/09/2026, sem tokens reais ou criação de recursos na nuvem:

- Terraform `fmt`, `init -backend=false`, `validate`;
- **14 testes Terraform aprovados** com providers simulados: ORD/GRU, home region diferente (IAD/FRA), rejeição de região não subscrita/não READY, IAM mínimo, VM 1 OCPU/8 GB,
  tamanho do user-data, SSH fechado por padrão, acesso público somente com
  chave e aceite, rejeição de CIDR inválido/IPv6 e
  aceite obrigatório para persistência do token;
- **36 testes Python aprovados** de pareamento privado, entrada malformada,
  mascaramento de erros, configuração, permissões, streaming, tradução nativa de ferramentas OCI,
  renovação simulada de token/chave com SDK OCI real, assinatura concorrente serializada
  marcador SSE `[DONE]` dividido entre leituras sem ocultar payloads inválidos,
  DNS saudável, recuperação DNS antes dos pacotes, falha persistente sem downloads,
  retries limitados e ordem do cloud-init (testes shell com comandos de SO simulados);
- Regressão do adaptador OCI real fixado: fragmentos com IDs diferentes,
  índices independentes, estado isolado por resposta, nome tardio/repetido,
  rejeição de mudança ambígua de função, preservação de truncamento real,
  aceite de stream completo e rejeição do stream fragmentado/incompleto;
- `schema.yaml` validado contra o meta-schema oficial Oracle do Resource Manager;
- contrato da configuração verificado com o código/venv real do Hermes fixado:
  provider, chave local, modo Chat Completions, toolsets e importação do gateway;
- resolução/instalação local das dependências fixadas e sintaxe do bootstrap.

Isso **não comprova** disponibilidade Compute, autorização real IAM, acesso
GenAI na conta Trial, execução de cloud-init/systemd na VM ou conversa final
do Telegram. A edição precisa de homologação real antes de ser distribuída
como pronta para visitantes.

## Verificação na VM existente — 11/09/2026, versão 1.2.1

- Antes da correção, a ponte em execução retornou HTTP 401; uma chamada com
  signer recém-criado respondeu usando a mesma configuração OCI.
- Após substituir somente `bridge.py` e reiniciar a ponte, `smoke.py` passou:
  inferência, chamada de ferramenta e retorno da ferramenta.
- Streaming real com texto em português passou: HTTP 200, texto recebido,
  marcador `[DONE]` e ausência de erro no stream.
- O processo do gateway foi preservado; não foi feito novo pareamento,
  alteração IAM, troca de chaves ou recriação de VM.

A renovação foi coberta por regressão local com SDK real e troca simulada de
token/chave. Ainda falta observação prolongada em produção após expiração
natural e o teste final da conversa pelo participante no Telegram. Não
generalizar esta verificação para todas as tenancies/regiões ou declarar
todo o roteiro abaixo aprovado.

## Recuperação de nova VM — 11/09/2026, versão 1.2.2

Uma nova VM chegou com resolução do sistema divergente do DNS recebido por
DHCP. A atualização do DNS gerenciado pelo NetworkManager restaurou a
resolução. Pacotes e bootstrap foram retomados sem novo Apply ou recriação.
O instalador concluiu, reconheceu o pareamento já enviado, validou inferência
e ferramentas e iniciou o gateway Telegram. Ponte e gateway ficaram ativos.
O registro de erro do cloud-init original foi preservado para diagnóstico.
O teste da conversa nessa nova VM ainda deve ser confirmado pelo participante.

## Ferramentas com streaming — 11/09/2026, versão 1.2.3

- Reprodução real: uma chamada curta de `stand_echo` funcionava sem streaming,
  mas o stream retornava vários IDs diferentes para fragmentos da mesma função.
  O Hermes registrava argumentos irrecuperáveis e recusava executar as chamadas.
- Após atualizar `bridge.py`, o mesmo teste manteve um único ID, argumentos JSON
  completos e `finish_reason=tool_calls`, sem elevar o teto de tokens.
- O `smoke.py` ampliado passou em inferência e chamada/retorno de ferramenta
  com e sem streaming na VM, usando a mesma identidade OCI e modelo.
- O próprio `AIAgent` do Hermes instalado, com streaming habilitado e toolset
  de arquivos, respondeu à saudação e executou `write_file` seguido de
  `read_file`. O arquivo de diagnóstico único foi conferido no workspace.
- Ponte reiniciada, gateway preservado e pareamento mantido. Não houve
  novo Apply, alteração IAM ou recriação da VM. Backups dos scripts preservados.

Esse teste exercitou o agente na VM, não uma nova mensagem enviada pelo usuário
no Telegram. A confirmação final deve ser feita pelo participante após `/new`.

## Grok e áudio local — 14/09/2026, versão 1.3.0

- 17 testes Terraform com providers simulados: inclui Grok em ORD, rejeição
  de Grok em GRU e modelo desconhecido, opção STT desligada e policy do modelo.
- 42 testes Python: inclui configuração local explícita, STT desligado sem
  download, carregamento CPU/local-only, TTS bloqueado e pesos fora do Terraform.
- Contrato executado contra o Hermes fixado, com o extra `voice` instalado:
  provider/STT local e guardas dos dois caminhos de TTS automático confirmados.
- Transcrição real em CPU/int8 pelo módulo do Hermes, com amostra sintética
  em português em WAV e OGG/Opus: sucesso e texto reconhecido. Houve pequena
  imprecisão na fala sintetizada; isso não mede precisão em ambiente de evento.
  Teste local no Mac, não na nova VM OCI; não foram usados áudios do usuário
  nem API paga. A amostra/pesos não foram incluídos no pacote Terraform.
- Consulta da disponibilidade oficial OCI em 14/09/2026: Grok 4.6 em ORD,
  hospedagem externa xAI; sem disponibilidade listada em GRU.

O usuário removeu a instalação anterior. **Não foi criada VM nem executada
inferência real Grok nesta entrega.** A nova Stack deverá validar IAM,
acesso/créditos, chamada/retorno de ferramentas (com e sem streaming) e a
conversa final por voz no Telegram. Não interpretar testes locais como
homologação do Grok na tenancy ou medição de latência da VM de 1 OCPU.

## HTTP 429 na nova VM — 14/09/2026, versão 1.3.1

- A OCI retornou erro de service limit do modelo Grok. Chamadas com contexto
  maior reproduziram sucesso seguido de 429, independentemente do limite local.
- O agente havia executado `write_file` antes do erro; o problema estava na
  inferência seguinte, não em Telegram, SSH ou ferramentas de arquivo.
- Ponte corrigida na VM com backup, sem alterar IAM/quota/modelo/pareamento.
- Teste real do Hermes com Grok, streaming e os toolsets do stand concluiu
  `write_file` → `read_file` → resposta textual; arquivo conferido no workspace.
  Tempo observado: **144,6 s**, incluindo espera pela janela do serviço.
- 49 testes Python aprovados: inclui retry limitado, erros não-429 sem retry,
  Retry-After numérico/data, cooldown compartilhado, teto de espera e quota local.
- 17 testes Terraform aprovados. Scripts passam a usar gzip+base64 individual
  no cloud-init para manter o user-data abaixo do limite seguro de 30.000
  caracteres. O limite não foi aumentado. A compactação não é criptografia.

Isso comprova uma execução real nesta VM/tenancy, não capacidade para vários
visitantes simultâneos. Falta confirmar a nova mensagem do usuário no Telegram.
O 429 não comprova esgotamento do limite publicado de 200 mil TPM. Um teste
posterior diretamente na API OCI, sem Hermes/LiteLLM, retornou 200 com 7.800
tokens e depois 429. Throttling dinâmico é uma hipótese documentada pela Oracle,
não a causa comprovada nesta tenancy. Aumentar quota não é solução garantida.

## Grok 4.3 — 14/09/2026, versão 1.3.2

- Modelo padrão alterado para `xai.grok-4.3` em Chicago; Grok 4.6 continua
  selecionável. Mantidos limites conservadores de contexto/saída, STT local,
  respostas textuais, retry limitado e IAM restrito ao modelo escolhido.
- 50 testes Python e 19 testes Terraform com providers simulados aprovados.
  Contrato com o Hermes fixado e sintaxe shell aprovados; user-data permanece
  abaixo de 30.000 caracteres, sem aumentar o limite.
- Pré-teste direto na VM atual: duas chamadas Grok 4.3 retornaram HTTP 404.
  A policy gerada para essa instalação restringe acesso a Grok 4.6. A identidade
  da VM não administra IAM; a credencial local pertence a outra tenancy.
- **Pendente à época da 1.3.2:** administrador alterar a condição da policy para Grok 4.3;
  depois atualizar a configuração da VM e repetir inferência e criação/leitura
  pelo Hermes. O modelo da VM não foi alterado para não interromper Grok 4.6.
  Não anunciar validação ao vivo de Grok 4.3 antes de concluir esses passos.
  A Stack foi posteriormente destruída; para a reinstalação, a versão 1.3.3
  automatiza o novo escopo IAM de Chicago e dispensa essa edição manual.

## Repetir testes locais — somente mantenedor

O visitante usa **Plan e Apply na Console**, não estes comandos. Os testes
Terraform usam `mock_provider` e exigem Terraform >= 1.7. Não removê-lo:
testes com providers reais podem criar recursos.

```bash
cd stand
python3 -m venv /tmp/hermes-stand-test-venv
/tmp/hermes-stand-test-venv/bin/pip install -r terraform/files/requirements.lock
/tmp/hermes-stand-test-venv/bin/python -m unittest discover -s tests -v
bash -n terraform/files/bootstrap.sh terraform/files/network-preflight.sh
export TF_DATA_DIR="$(mktemp -d)"
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
terraform -chdir=terraform test
terraform fmt -check -recursive terraform
```

## Homologação real — uma Trial ORD e outra GRU

O roteiro abaixo ainda não foi aprovado integralmente; os testes reais
parciais realizados estão registrados na seção anterior.

1. Usar conta do visitante/admin e um bot novo, sem webhook.
2. Abrir o botão de deploy; verificar seleção automática do pacote e formulário.
3. Confirmar tenancy/região preenchidas, token mascarado/confirmado e aceite
   obrigatório. Não publicar prints contendo token ou comando de vínculo.
4. Executar Plan, revisar custo/shape/rede/IAM e Apply pela Console.
5. Confirmar que todos os recursos regionais estão na região selecionada,
   que `iam_home_region` corresponde à home region real da tenancy e que
   somente a VM criada pertence ao dynamic group.
6. Medir separadamente: provisionamento, bootstrap, propagação IAM e pareamento.
7. Revelar comando privado na aba Application information, enviar em DM e
   conferir confirmação da conta e mensagem de configuração concluída.
8. Verificar no serviço de ativação que tool call e tool result passaram.
9. Enviar `/new` e tarefa de criar/ler arquivo; conferir execução real.
10. Testar com uma segunda conta: ela não deve conseguir executar tarefas.
11. Reiniciar a VM pela Console e confirmar nova resposta sem reconfigurar.
12. Executar novo Plan sem mudanças: não deve propor duplicação/substituição.
13. Exercitar rotação/recriação em ambiente descartável, revisando explicitamente
    perda de dados e novo código de pareamento.
14. Executar Destroy e conferir remoção de Compute, disco, rede e IAM;
    excluir a Stack só depois. Excluir/revogar bot no BotFather.

Registre tempo e resultados sem segredos/OCIDs pessoais. Se qualquer região
falhar no ciclo completo, não a anuncie como homologada até corrigir e repetir.
