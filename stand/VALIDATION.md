# Validação e homologação antes do stand

## Escopo dos testes desta entrega

Validações locais em 10/09/2026, sem tokens reais ou criação de recursos na nuvem:

- Terraform `fmt`, `init -backend=false`, `validate`;
- **7 testes Terraform aprovados** com provider simulado: ORD/GRU, home region, IAM mínimo, VM 1 OCPU/8 GB,
  tamanho do user-data, SSH fechado por padrão, rejeição de SSH aberto e
  aceite obrigatório para persistência do token;
- **18 testes Python aprovados** de pareamento privado, entrada malformada,
  mascaramento de erros, configuração, permissões, streaming e tradução nativa de ferramentas OCI;
- `schema.yaml` validado contra o meta-schema oficial Oracle do Resource Manager;
- contrato da configuração verificado com o código/venv real do Hermes fixado:
  provider, chave local, modo Chat Completions, toolsets e importação do gateway;
- resolução/instalação local das dependências fixadas e sintaxe do bootstrap.

Isso **não comprova** disponibilidade Compute, autorização real IAM, acesso
GenAI na conta Trial, execução de cloud-init/systemd na VM ou conversa final
do Telegram. A edição precisa de homologação real antes de ser distribuída
como pronta para visitantes.

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

Nenhuma das etapas reais abaixo está declarada como aprovada nesta entrega.

1. Usar conta do visitante/admin e um bot novo, sem webhook.
2. Abrir o botão de deploy; verificar seleção automática do pacote e formulário.
3. Confirmar tenancy/região preenchidas, token mascarado/confirmado e aceite
   obrigatório. Não publicar prints contendo token ou comando de vínculo.
4. Executar Plan, revisar custo/shape/rede/IAM e Apply pela Console.
5. Confirmar que todos os recursos regionais estão na home region e que
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
