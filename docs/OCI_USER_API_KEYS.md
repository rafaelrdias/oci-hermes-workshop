# Criar chaves pela Console OCI — configurações do usuário

Este é um procedimento **opcional**, para quem deseja uma chave de assinatura
da API OCI para usar SDKs, CLI ou outras integrações em nome do seu usuário.
Não é necessário para executar o Terraform pelo Resource Manager nem para
o Hermes da [edição stand](../stand/README.md), que usa Instance Principals.

## Antes de começar: qual chave você precisa?

| Objetivo | Onde obter | O que usar |
|---|---|---|
| Acessar a VM por SSH/VS Code | Compute → Create instance → Add SSH keys | Chave pública `.pub` na Stack; privada no seu computador |
| Assinar requisições à API OCI como usuário | Perfil → User settings / My Profile → API keys | Par de assinatura e configuração OCI — procedimento abaixo |
| Usar o endpoint OpenAI-compatible do workshop tradicional | Generative AI → API keys | Secret do serviço, não a chave do perfil |

**Não cole a chave de assinatura do perfil em `ssh_public_key` ou no campo
de token Telegram.** Se o objetivo é SSH, siga o
[passo a passo de chaves SSH pela Console](OCI_RESOURCE_MANAGER_CONSOLE.md#d-gerar-e-baixar-as-chaves-ssh-pela-console).
Para a credencial do modelo no workshop tradicional, veja o
[guia OpenAI-compatible](OCI_API_KEY_TELEGRAM.md#parte-1--criar-a-api-key-openai-compatible-na-oci).

## 1. Abrir as configurações do seu usuário

1. Entre na [Console OCI](https://cloud.oracle.com/) com sua própria conta.
2. Abra o ícone de **Perfil**, no topo da Console.
3. Selecione **User settings / Configurações do usuário**. Em outra versão
   da interface, a opção aparece como **My Profile / Meu perfil**.
4. Confirme que a página mostra o usuário correto.
5. Em **Resources / Recursos**, abra **API keys / Chaves de API**.

Se precisar localizar o usuário pelo menu de administração, o caminho é
**Identity & Security → Domains → seu domínio → Users → seu usuário**.
Não selecione outro participante para gerar suas credenciais.

## 2. Gerar e baixar o par

1. Clique em **Add API key / Adicionar chave de API**.
2. Selecione **Generate API key pair / Gerar par de chaves de API**.
3. Clique em **Download private key / Baixar chave privada**.
4. Confirme o download e guarde o arquivo `.pem` em local privado no seu
   computador, preferencialmente na pasta `.oci` do seu usuário.
5. Clique em **Add / Adicionar**. A chave pública fica registrada no perfil;
   não é preciso baixá-la para esse fluxo.

Os rótulos e a sequência seguem a
[documentação oficial de criação de chaves de assinatura](https://docs.oracle.com/en-us/iaas/Content/Identity/access/to_upload_an_API_signing_key.htm).

## 3. Guardar a configuração — somente para uso posterior de SDK/CLI

Após adicionar, a Console mostra **Configuration file preview**. Guarde o
trecho em um arquivo local; para SDK/CLI, o caminho padrão é `~/.oci/config`.
Não é o arquivo de configuração SSH usado pelo VS Code.

Confira os campos `user`, `fingerprint`, `tenancy` e `region`. Ajuste
`key_file` para o caminho real da chave privada baixada. Se já existe um
perfil `[DEFAULT]`, preserve-o e dê um nome diferente ao perfil novo.
Não substitua configurações de outras tenancies sem conferir.

Para recuperar o trecho posteriormente: volte a **API keys**, abra o menu
**⋮** da chave correspondente e selecione **View configuration file**.
Isso reabre a configuração, não recupera sua chave privada.
[Documentação Oracle](https://docs.oracle.com/en-us/iaas/Content/Identity/access/to_get_the_config_file_snippet_for_an_API_signing_key.htm).

## 4. Cuidados finais

- Mantenha a chave privada acessível somente ao seu usuário no computador.
- Nunca publique o `.pem`, nem o envie em chat, formulário da Stack ou ao bot.
- Criar a chave não concede novas permissões: as operações continuam sujeitas
  às políticas IAM do usuário.
- Para voltar ao laboratório, retorne ao [guia do stand](../stand/README.md).
  **Não há nenhum campo dessa chave para preencher na instalação automatizada.**
