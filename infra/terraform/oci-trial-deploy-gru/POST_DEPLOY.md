# Pós-deploy — GRU

Confirme os Outputs:

```bash
terraform output deployment_region
terraform output genai_project_ocid
terraform output genai_base_url
terraform output public_ip
```

Valores esperados:

```text
deployment_region = sa-saopaulo-1 (GRU)
genai_base_url     = https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com/openai/v1
```

Depois:

```bash
ssh hermes-oci-gru 'cloud-init status --wait'
ssh hermes-oci-gru 'hermes-worker-ready'
ssh hermes-oci-gru 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
ssh -t hermes-oci-gru 'hermes-workshop-configure'
```

Validação:

```bash
ssh hermes-oci-gru 'hermes --version'
ssh hermes-oci-gru 'hermes doctor'
ssh hermes-oci-gru 'sudo systemctl is-active hermes-gateway'
ssh hermes-oci-gru 'sudo journalctl -u hermes-gateway -n 100 --no-pager'
```

Pairing, se não foi usada allowlist:

```bash
ssh hermes-oci-gru 'hermes pairing approve telegram CODIGO'
```

Guia completo:

https://github.com/rafaelrdias/oci-hermes-workshop/blob/main/docs/GRU_RESOURCE_MANAGER.md

Nunca cole segredos em comandos SSH. Use o prompt interativo de
`hermes-workshop-configure`.
