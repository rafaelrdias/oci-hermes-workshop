# Validação e manutenção

[Voltar ao guia](../README.md)

## Estrutura

| Diretório | Conteúdo |
|---|---|
| `terraform/` | Módulo completo para Resource Manager, schema e bootstrap |
| `terraform/tests/` | Testes de infraestrutura com providers simulados |
| `tests/` | Testes Python, contrato Hermes e consistência do guia |
| `docs/` | Operação, SSH, arquitetura e documentação das capturas |
| `docs/images/console/` | Capturas reais da Console OCI, fora do pacote Terraform |

A branch **`resource-manager`** contém somente o conteúdo de `terraform/`.
O download dessa branch é o pacote leve usado na Console. Não inclua binários,
`.terraform`, state, variáveis pessoais, imagens ou credenciais nesse pacote.

## Executar os testes localmente

Estes comandos são para **mantenedores**. Participantes executam pela Console,
conforme o guia principal. Use ambiente virtual Python 3.11; dependências do
bridge estão fixadas em `terraform/files/requirements.lock`.

```bash
python3.11 -m venv .test-data/venv
.test-data/venv/bin/pip install -r terraform/files/requirements.lock
.test-data/venv/bin/python -m unittest discover -s tests -v
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
terraform -chdir=terraform test
```

`terraform test` usa providers simulados e requer Terraform **1.7+**; não cria
recursos OCI. A implantação permite Terraform >= 1.5 e < 2.0.
Os testes Python não fazem inferência real ou publicam mensagens Telegram.

O teste `tests/check_hermes_contract.py` exige o checkout e o ambiente da versão
Hermes fixada em `bootstrap.sh`. Execute com o Python desse ambiente e
`PYTHONPATH` apontando ao checkout para validar resolução do provider,
ferramentas Telegram e política de respostas em texto.

## Antes de publicar

1. Execute testes Python, contrato Hermes, `fmt`, `validate` e `terraform test`.
2. Confira screenshots/ilustrações e todos os links relativos no guia. Siga
   [a origem e os critérios das capturas](TELAS.md): não desenhe uma tela OCI
   e a apresente como screenshot. O botão Deploy deve existir uma única vez
   no README, depois dos pré-requisitos, acompanhado da orientação de nova aba.
3. Verifique que não há credenciais, state, IPs de participantes ou arquivos
   privados preparados para commit.
4. Sincronize versão do `schema.yaml` e documentação.
5. Revise tamanho e conteúdo do pacote: deve ficar muito abaixo de 11 MB.
6. Faça commit em `main`, derive a branch do pacote e publique ambas.
   Em um clone onde não exista branch local `resource-manager`:

```bash
git subtree split --prefix=terraform -b resource-manager
git push --atomic origin main resource-manager
```

Se a branch local já existir, crie uma branch temporária com outro nome a partir
do subtree e confira ancestralidade antes de atualizar o destino. Não use
force-push para resolver divergência sem inspecioná-la. Nunca coloque PAT na URL
do remote ou em arquivos do repositório.

7. Baixe o pacote publicado e confira `main.tf`/`schema.yaml` na pasta raiz.
8. Teste uma Stack **nova** em uma conta de teste autorizada: Plan, Apply, vínculo
   privado, `/new`, criação/leitura de arquivo e áudio com resposta em texto.
   Esse aceite ponta a ponta é separado dos testes locais.

## Cuidados com mudanças

Os scripts de bootstrap são comprimidos individualmente e o user-data completo
tem uma precondição de tamanho. Mantenha as versões fixadas e os testes de
streaming, ferramentas, autenticação, áudio e pareamento ao atualizar dependências.

Alterar modelo, token ou bootstrap pode provocar substituição da VM por
`terraform_data.bootstrap_revision`. Informe o impacto, confira Plan e faça
backup antes de aplicar a um ambiente com dados.
