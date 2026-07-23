# Pasta Terraform pronta para o OCI Resource Manager

Esta branch contém somente a configuração necessária para criar a Stack do workshop. Ela não inclui apresentações, documentação extensa, `.terraform`, providers locais, state ou segredos.

## Uso pela Console OCI

1. use **[Download da pasta Terraform](https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager-folder.zip)**;
2. extraia o download uma vez;
3. na Console OCI, selecione **US Midwest (Chicago)**;
4. abra **Developer Services → Resource Manager → Stacks → Create stack**;
5. escolha **My configuration → Folder**;
6. selecione a pasta extraída `oci-hermes-workshop-resource-manager-folder`;
7. prossiga com as variáveis, Plan e Apply.

O conteúdo desta pasta fica muito abaixo do limite de 11 MB do upload por Folder.

Guia completo com telas:

https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/OCI_RESOURCE_MANAGER_CONSOLE.md

> Nunca adicione API keys, token do BotFather, chave SSH privada, `terraform.tfvars`, state ou a pasta `.terraform`.
