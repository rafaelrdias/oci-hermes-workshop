# Operação e diagnóstico

[Voltar ao guia](../README.md)

## Primeiro, identifique a etapa

| Etapa | O que comprova | Próxima ação |
|---|---|---|
| Plan → Succeeded | Configuração planejada; não instala a VM | Revisar e executar Apply |
| Apply → Succeeded | Recursos provisionados; bootstrap pode continuar | Abrir **a própria Stack → Application information** |
| Conta vinculada! | O comando privado identificou o participante | Aguardar testes OCI e ferramentas |
| Configuração concluída! | Testes de inferência/ferramentas e serviço concluídos | Enviar `/new` e testar pelo Telegram |
| Arquivo criado e lido | Fluxo real agente + ferramentas + Telegram funcionando | Testar áudio curto com resposta em texto |

Downloads, IAM, capacidade e limites variam. Não há tempo máximo garantido
para cadastro, provisionamento ou prontidão. Se permanecer sem evolução por
10 minutos, confira o estágio/log correspondente; não crie outra Stack para
tentar acelerar. A ativação tenta OCI por janelas de 20 minutos e o serviço
pode retomar as tentativas. Créditos/permissões ausentes exigem ação, não só espera.

## Problemas comuns

| Sintoma | Verificação / ação |
|---|---|
| `acknowledge_secret_in_state is false` | Edit Stack → Configure variables → marque o aceite **do token**, se concordar. É diferente dos dois aceites SSH. |
| Pasta excede 11 MB | Use apenas o [pacote Terraform](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager.zip), extraia e selecione a pasta com `main.tf`. Não envie imagens, providers ou `.terraform`. |
| Região inválida/não subscrita | Escolha ORD ou GRU subscrita e READY. Home region diferente é permitida; IAM usa o endpoint dela. |
| GPT-OSS/Grok escolhido em GRU | Selecione explicitamente Llama 3.3 70B, ou ORD se estiver disponível na sua conta. Não há fallback automático. |
| Falha ao criar DG/policy/compartment | Confira permissões administrativas do executor e nomes exclusivos. A VM não precisa e não recebe acesso administrador. |
| Out of capacity/quota | Confira capacidade e quota do shape/AD. Revise custo antes de trocar E5/E4/A1; não há troca automática. |
| SSH `0.0.0.0/0` recusado | Exige chave configurada **e** aceite de SSH público. Prefira `/32`; vazio deixa a porta fechada. |
| Bot não responde a `/start` | Envie o comando **completo** de `telegram_pairing_command` em DM ao seu bot, não ao BotFather. Confira bootstrap e token. |
| Telegram HTTP 409 / webhook existente | Outro processo usa esse bot. Use bot exclusivo; a instalação não remove integrações de terceiros. |
| Conta vinculada, mas não pronta | Confira créditos, propagação IAM, modelo/região e logs de ativação/bridge. |
| Provider authentication failed | Confira DG, matching rule da VM, policy e bridge. A VM usa Instance Principals, não API key OpenAI do participante. Não substitua a chave local do bridge por uma chave OCI. |
| Rate limit / HTTP 429 | Pode ser throttling de requisições, tokens, capacidade do provedor ou limite local. Leia o diagnóstico do bridge; limite de 200 mil tokens/min não comprova a causa. Aguarde antes de repetir. |
| Resposta demorando | Evite mensagens simultâneas, abra `/new` e teste algo curto. Confira retries/429. O padrão é GPT-OSS 120B em ORD; não há SLA de latência. |
| Resposta truncada | Comece nova sessão e teste saudação curta; depois arquivo. Confira o modelo e limites de saída no bridge, sem aumentar limites indiscriminadamente. |
| Áudio não entendido | Use áudio curto e claro em português. Confira STT habilitado, download do Whisper, CPU e RAM; tente texto. Não precisa API paga de voz. |

IAM pode levar tempo para propagar. Policy não cria créditos nem elimina quotas:
veja [Instance Principals](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/callingservicesfrominstances.htm)
e [limites do Generative AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/limits.htm).

## Diagnóstico pela Console, sem SSH

1. Abra **Resource Manager → Stacks → sua Stack → Jobs**. Se o Apply falhou,
   leia o erro final e o recurso correspondente, não apenas a inicialização dos providers.
2. Abra **Application information** dessa Stack para região/modelo e OCID da VM.
3. Em **Compute → Instances**, encontre essa VM na região e compartment indicados.
   Confira estado, VNIC, rota e permissões. A instalação usa conexões de saída.
4. Em **Identity & Security**, confira o DG criado para o OCID exato dessa VM
   e a policy correspondente; veja [arquitetura](ARQUITETURA.md).
5. Confira crédito, acesso ao modelo e limites antes de repetir Apply.

Os logs do job Terraform **não são** os logs do Hermes. Sem SSH, a Console
permite diagnosticar infraestrutura e IAM, mas não expõe automaticamente os
logs privados do gateway neste pacote. Para um problema dentro da VM, configure
SSH opcional com sua chave e origem autorizada ou peça apoio ao facilitador.

## Logs na VM, se SSH estiver habilitado

Execute somente na sua VM:

```bash
sudo cloud-init status --long
sudo systemctl is-active hermes-oci-bridge hermes-gateway
sudo journalctl -u hermes-stand-activate -n 60 --no-pager
sudo journalctl -u hermes-oci-bridge -n 60 --no-pager
sudo journalctl -u hermes-gateway -n 60 --no-pager
```

O bootstrap registra em `/var/log/hermes-stand-bootstrap.log`; o cloud-init
também tem seu próprio log em `/var/log/cloud-init-output.log`.
O serviço de ativação pode estar inativo após concluir normalmente; isso é
diferente de falha no gateway. Reveja logs localmente e **remova tokens, códigos,
chaves, OCIDs e dados pessoais antes de compartilhar**. Nunca publique user-data,
`.env` ou o conteúdo do state.

O bridge limita chamadas localmente e aplica espera compartilhada após 429;
mensagens repetidas durante a espera não aumentam a quota OCI. Trocar o modelo
não é um mecanismo para burlar limites.

## Atualizar ou encerrar

Antes de qualquer Apply, leia o Plan. Mudanças de token, modelo ou bootstrap
podem substituir a VM. Salve arquivos e memórias primeiro. Não mantenha duas
VMs consumindo o mesmo token de bot.

Para encerrar: **Stack → Destroy → Succeeded → excluir Stack**, nessa ordem.
Destroy remove os recursos gerenciados, inclusive o disco; não revoga o bot nem
apaga cópias de chaves/state baixadas. Gerencie o bot separadamente no BotFather.
