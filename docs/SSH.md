# Acesso SSH opcional

[Voltar ao passo a passo](../README.md#5-escolha-se-quer-ssh--opcional)

A instalação e o Telegram funcionam sem SSH. Use esta opção para administrar
sua VM. A chave SSH é diferente de uma API signing key cadastrada no perfil OCI:
**não precisa criar API key de usuário para este laboratório**.

## 1. Gere a chave no formulário da Stack

Em **Configure variables → Opcional — acesso SSH e chave automática**:

1. Marque **Gerar chave SSH automaticamente para esta Stack**.
2. Leia e marque **Aceito armazenar a chave SSH privada no state da Stack**.
3. Deixe **Chave pública SSH opcional** vazia.
4. Informe seu IPv4 público com `/32` em **Origem IPv4 do SSH** para conectar.
   Vazio instala a chave mas deixa TCP/22 fechado.
5. Execute Plan, revise e aplique. O Terraform gera um par RSA 4096 e instala
   somente a pública na VM.

A chave privada fica no state, acessível a quem tem permissão para lê-lo.
O aceite do token Telegram continua obrigatório e é independente deste.

## 2. Guarde a chave privada no seu computador

Abra **Resource Manager → Stacks → a Stack que acabou de executar →
Application information → SSH opcional**.

Esse caminho parte dos detalhes **da Stack**, não da instância Compute nem
do job Apply. O grupo tem o título **SSH opcional — guarde sua chave privada em segurança**.
O valor privado deve continuar oculto até você estar pronto para salvá-lo.

1. Localize **Chave PRIVADA gerada: revelar, copiar e salvar como hermes.key
   (vazio se não gerada)**, título da saída **`ssh_private_key_pem`**, e revele
   o valor. Vazio significa que não houve geração automática.
2. Copie **todo o conteúdo**, desde `-----BEGIN RSA PRIVATE KEY-----` até
   `-----END RSA PRIVATE KEY-----`, preservando as quebras de linha.
3. Em um editor de texto puro, salve como **`hermes.key`**, não `hermes.key.txt`.
   No TextEdit do macOS, use **Formatar → Converter em Texto Simples** antes de salvar.
4. Guarde em uma pasta pessoal protegida; não envie por Telegram/e-mail, não
   publique no Git e não inclua em capturas de tela.
5. Copie também **`public_ip`** ou **`ssh_connection_command`** da mesma Stack.

A extensão `.key` ou `.pem` é apenas o nome; este par usa conteúdo PEM compatível
com OpenSSH. A saída **`ssh_public_key`** não permite entrar no lugar da privada.

## 3. Conecte pelo terminal local

No macOS/Linux, dentro da pasta onde salvou o arquivo:

```bash
chmod 600 hermes.key
ssh -i hermes.key opc@IP_DA_SUA_VM
```

Substitua `IP_DA_SUA_VM` pela saída real. Na primeira conexão, confira a
identidade do host antes de aceitar; não desative a verificação de host.
No Windows, use OpenSSH no PowerShell e limite as permissões do arquivo à sua
conta pelas propriedades de Segurança. O usuário da imagem é **`opc`**.

Se usar `0.0.0.0/0`, o formulário exige outro aceite: qualquer IPv4 poderá
tentar acessar SSH. A chave continua obrigatória. **Não há expiração automática**:
ao terminar, altere o CIDR para seu `/32` ou vazio, revise Plan e aplique.

## Alternativa: sua própria chave

Desmarque a geração e cole **apenas a pública**, começando com `ssh-ed25519` ou
`ssh-rsa`, no campo `ssh_public_key`. A privada correspondente permanece
no seu computador. Pode gerar o par localmente, por exemplo:

```bash
ssh-keygen -t ed25519 -f ./hermes-evento
```

Escolha um nome ainda não usado, não sobrescreva uma chave existente e proteja
com passphrase. Cole o conteúdo de `hermes-evento.pub` no formulário; para acessar,
use `ssh -i ./hermes-evento opc@IP_DA_SUA_VM`.

## Ajustes do Hermes na VM

O serviço roda como usuário **`hermes`**, não como `opc` ou `root`.
O diretório de configuração é **`/var/lib/hermes/.hermes`** e o workspace é
**`/var/lib/hermes/workspace`**.

Para alterar preferências de comportamento, primeiro copie `SOUL.md` para um
arquivo de backup com nome exclusivo e então edite-o como `hermes`. Para opções
do agente, faça o mesmo com `config.yaml`. Preserve proprietário e permissões.

Não publique `.env`, `bridge.key`, state ou arquivos de credenciais. Não execute
o setup como root: isso configuraria outro perfil, não o usado pelo Telegram.

Após uma alteração planejada, fora de uma conversa ativa:

```bash
sudo systemctl restart hermes-gateway
sudo systemctl is-active hermes-gateway
```

Envie `/new` e repita o teste de arquivo. O modelo exibido como `hermes-oci`
é um alias; a integração OCI inclui um bridge e não deve ser trocada apenas
renomeando o modelo em `config.yaml`. Para mudar o LLM pelo formulário, revise
o Plan: mudanças no bootstrap podem **substituir a VM e apagar dados locais**.

Alterar a pública nos metadados de uma VM existente não garante atualizar ou
revogar entradas em `authorized_keys`. Não use essa mudança como mecanismo de
rotação. Guarde backup antes de substituir ou destruir a VM.

## Se não conectar

Confira CIDR, pública/privada correspondentes, IP de saída da Stack e usuário
`opc`. Se a rede do evento bloquear TCP/22, teste outra rede autorizada.
Um timeout não significa necessariamente que a chave esteja errada.
Veja [diagnóstico](OPERACAO.md).
