# Checklist do facilitador

## Uma semana antes

- [ ] Confirmar o tipo e os limites das contas Trial dos participantes.
- [ ] Confirmar que todos podem criar policy na tenancy ou preparar a policy centralmente.
- [ ] Confirmar subscription da região `us-chicago-1`.
- [ ] Testar disponibilidade on-demand de `openai.gpt-oss-120b`.
- [ ] Gerar novamente o ZIP do Resource Manager.
- [ ] Executar um ensaio do zero com uma conta limpa.
- [ ] Validar a tag do Hermes fixada em `hermes_git_ref`.

## Um dia antes

- [ ] Testar a VM de demonstração e `hermes doctor`.
- [ ] Inserir uma OCI Generative AI API key válida na VM de demonstração.
- [ ] Criar um bot exclusivo para a demonstração e configurar allowlist.
- [ ] Validar um turno completo no Telegram.
- [ ] Separar uma VM pronta como plano B.
- [ ] Disponibilizar o repositório/ZIP e um QR code para o link.

## Antes da sala abrir

```bash
ssh -i /caminho/chave opc@147.224.210.244 'hermes --version'
ssh -i /caminho/chave opc@147.224.210.244 'sudo systemctl status hermes-gateway --no-pager'
ssh -i /caminho/chave opc@147.224.210.244 'sudo journalctl -u hermes-gateway -n 50 --no-pager'
```

- [ ] Deixar a OCI Console já na região Chicago.
- [ ] Abrir `@BotFather` e `@userinfobot` no celular de demonstração.
- [ ] Ter tenancy OCID, compartment OCID e chave pública em um bloco local.
- [ ] Cronometrar a atividade em 60 minutos.

## Estratégia de facilitação

- O Terraform começa primeiro; API key e bot são criados enquanto cloud-init roda.
- Participante que travar por mais de 3 minutos recebe o checkpoint/VM pronta.
- Erros comuns são tratados coletivamente; erros específicos recebem ajuda individual durante o próximo bloco.
- Aos 55 minutos, interromper novas configurações e demonstrar o resultado na VM de backup.

## Não fazer

- não pedir que participantes colem tokens no chat da sala;
- não usar `GATEWAY_ALLOW_ALL_USERS=true`;
- não abrir 8642 ou portas de webhook;
- não demonstrar comandos destrutivos pelo Telegram;
- não deixar recursos Trial rodando sem combinar a destruição.
