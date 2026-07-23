# Pós-deploy

```bash
terraform output ssh_config_entry
ssh hermes-oci 'cloud-init status --wait'
ssh hermes-oci 'hermes-worker-ready'
ssh hermes-oci 'sudo tail -n 80 /var/log/hermes-bootstrap.log'
ssh -t hermes-oci 'hermes-workshop-configure'
```

Validação:

```bash
ssh hermes-oci 'hermes --version'
ssh hermes-oci 'hermes doctor'
ssh hermes-oci 'sudo systemctl is-enabled hermes-gateway'
ssh hermes-oci 'sudo systemctl is-active hermes-gateway'
ssh hermes-oci 'sudo journalctl -u hermes-gateway -n 100 --no-pager'
```

Pairing, se não foi usada allowlist:

```bash
ssh hermes-oci 'hermes pairing approve telegram CODIGO'
```

Nunca cole segredos em comandos SSH, pois eles podem ficar no histórico ou na lista de processos. Use o prompt interativo de `hermes-workshop-configure`.
