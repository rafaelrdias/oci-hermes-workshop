# Terraform — ambiente OCI Trial para Hermes

Todos os recursos regionais do laboratório ficam em **US Midwest (Chicago)**: identificador `us-chicago-1`, region key `ORD`. Isso inclui a Stack do Resource Manager, rede, VM, API key do OCI Generative AI e endpoint do modelo. IAM policies são globais na tenancy.

## Arquitetura criada

```text
Telegram Bot API
       ^ HTTPS long polling (saída)
       |
Internet Gateway -- subnet pública -- VM Oracle Linux / Hermes
                                      |
                                      +-- OCI Generative AI, gpt-oss-120b

Entrada na VM: somente TCP/22 a partir de ssh_allowed_cidr.
```

Não é necessário abrir a porta 8642: o laboratório usa Telegram por long polling e não publica a API HTTP do Hermes.

## 1. Pré-requisitos

- Terraform `>= 1.5`;
- credenciais do provider OCI, normalmente em `~/.oci/config`;
- tenancy OCID e compartment OCID;
- chave pública SSH;
- permissão para criar Compute, Networking e IAM policy.

Antes de criar a Stack, confirme que a Console está em **US Midwest (Chicago)** e que a tenancy está inscrita nessa região.

Descubra seu IP público e use `/32` sempre que possível:

```bash
curl -4 https://ifconfig.me
```

## 2. Variáveis

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edite pelo menos:

```hcl
region           = "us-chicago-1" # US Midwest (Chicago), region key ORD
tenancy_ocid     = "ocid1.tenancy.oc1..aaaa..."
compartment_ocid = "ocid1.compartment.oc1..aaaa..."
ssh_public_key   = "ssh-ed25519 AAAA..."
ssh_allowed_cidr = "203.0.113.10/32"
genai_region     = "us-chicago-1" # mesma região da VM e da rede
```

O workshop valida tanto `region` quanto `genai_region` como `us-chicago-1`. Chicago suporta `openai.gpt-oss-120b` on-demand e o uso de API key com o SDK OpenAI.

## 3. Provisionar

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out workshop.tfplan
terraform apply workshop.tfplan
```

O `apply` termina antes do cloud-init. Espere a instalação:

```bash
terraform output deployment_region # deve mostrar us-chicago-1 (ORD)
terraform output ssh_config_entry
# copie o bloco para ~/.ssh/config e ajuste IdentityFile
ssh hermes-oci 'cloud-init status --wait'
ssh hermes-oci 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
```

## 4. Criar os dois segredos fora do Terraform

### OCI Generative AI API key

Mantenha a Console na região **US Midwest (Chicago)**:

1. Analytics & AI → Generative AI → API keys;
2. Create API key no compartment do laboratório;
3. copie imediatamente um dos segredos `sk-...` — ele aparece uma vez;
4. não coloque o segredo em `terraform.tfvars`.

O Terraform já cria a policy que permite somente `generative-ai-chat` para `openai.gpt-oss-120b`. Se sua conta não puder criar policy, defina `create_genai_policy = false` e peça ao administrador para aplicar a statement mostrada em `terraform plan`/documentação.

### Telegram

1. abra `@BotFather`;
2. execute `/newbot`;
3. escolha nome e username;
4. copie o token;
5. opcionalmente obtenha seu ID numérico com `@userinfobot`.

## 5. Configurar a VM

```bash
ssh -t hermes-oci 'hermes-workshop-configure'
```

O comando testa o OCI Generative AI antes de iniciar o gateway. Se não informar user ID, o bot emitirá um código de pairing:

```bash
ssh hermes-oci 'hermes pairing approve telegram CODIGO'
```

Também é possível executar por etapas:

```bash
ssh -t hermes-oci 'hermes-workshop-configure --oci-only'
ssh -t hermes-oci 'hermes-workshop-configure --allowlist-only'
ssh -t hermes-oci 'hermes-workshop-configure --telegram-only'
```

## 6. Diagnóstico

```bash
ssh hermes-oci 'hermes doctor'
ssh hermes-oci 'sudo systemctl status hermes-gateway --no-pager'
ssh hermes-oci 'sudo journalctl -u hermes-gateway -n 100 --no-pager'
```

## 7. OCI Resource Manager

Baixe o pacote pronto:

[Download direto de `oci-hermes-resource-manager.zip`](https://raw.githubusercontent.com/rafaelrdias/oci-hermes-workshop/refs/heads/main/infra/terraform/oci-trial-deploy/dist/oci-hermes-resource-manager.zip)

Ou gere o pacote a partir do código atual:

```bash
./build-resource-manager-zip.sh
```

Depois, siga o [passo a passo com telas da Console OCI](https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/OCI_RESOURCE_MANAGER_CONSOLE.md) para:

1. criar a Stack em **Developer Services → Resource Manager → Stacks**;
2. enviar `dist/oci-hermes-resource-manager.zip`;
3. configurar as variáveis sem incluir segredos;
4. executar e revisar **Plan**;
5. executar **Apply** e consultar **Outputs**;
6. executar **Destroy** antes de excluir a Stack.

## 8. Custo e destruição

O preset E5 usa créditos do Trial. A alternativa A1 está comentada no exemplo e cabe no limite Always Free de 2 OCPUs/12 GB, mas pode falhar por falta de capacidade. Ao terminar:

```bash
terraform destroy
```
