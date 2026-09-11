# Validação e homologação antes do stand

## Escopo dos testes desta entrega

Validações locais em 10–11/09/2026, sem tokens reais ou criação de recursos na nuvem:

- Terraform `fmt`, `init -backend=false`, `validate`;
- **14 testes Terraform aprovados** com providers simulados: ORD/GRU, home region diferente (IAD/FRA), rejeição de região não subscrita/não READY, IAM mínimo, VM 1 OCPU/8 GB,
  tamanho do user-data, SSH fechado por padrão, acesso público somente com
  chave e aceite, rejeição de CIDR inválido/IPv6 e
  aceite obrigatório para persistência do token;
- **23 testes Python aprovados** de pareamento privado, entrada malformada,
  mascaramento de erros, configuração, permissões, streaming, tradução nativa de ferramentas OCI,
  renovação simulada de token/chave com SDK OCI real, assinatura concorrente serializada
  e marcador SSE `[DONE]` dividido entre leituras sem ocultar payloads inválidos;
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

## Repetir testes locais — somente mantenedor

O visitante usa **Plan e Apply na Console**, não estes comandos. Os testes
Terraform usam `mock_provider` e exigem Terraform >= 1.7. Não removê-lo:
testes com providers reais podem criar recursos.

```bash
cd stand
python3 -m venv /tmp/hermes-stand-test-venv
/tmp/hermes-stand-test-venv/bin/pip install -r terraform/files/requirements.lock
/tmp/hermes-stand-test-venv/bin/python -m unittest discover -s tests -v
bash -n terraform/files/bootstrap.sh
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
