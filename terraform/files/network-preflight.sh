#!/usr/bin/env bash
# Sourced by bootstrap before package downloads. Does not restart networking,
# override DHCP servers, disable TLS validation, or use an external DNS service.
stand_dns_ready() {
  local host
  for host in astral.sh github.com pypi.org; do
    timeout 8 getent ahostsv4 "$host" >/dev/null 2>&1 || return 1
  done
}

stand_wait_for_dns() {
  local attempt
  for attempt in 1 2 3 4 5 6; do
    if stand_dns_ready; then
      printf 'DNS pronto para os downloads.\n'
      return 0
    fi
    printf 'DNS indisponível (tentativa %s/6); reaplicando DNS do NetworkManager.\n' "$attempt" >&2
    # Repair stale resolv.conf using already negotiated DNS settings. Preserve
    # the original for diagnosis; do not invent 8.8.8.8 or hard-code OCI DNS.
    if command -v nmcli >/dev/null 2>&1; then
      install -d -m 0700 /var/backups/hermes-stand
      cp -an /etc/resolv.conf /var/backups/hermes-stand/resolv.conf.before-bootstrap
      nmcli general reload dns-rc || true
    fi
    if stand_dns_ready; then
      printf 'DNS recuperado; continuando a instalação.\n'
      return 0
    fi
    [[ "$attempt" == 6 ]] || sleep 5
  done
  printf 'DNS não recuperado. Verifique DHCP/resolvedor/rotas antes de retomar o bootstrap; o Telegram ainda não foi instalado.\n' >&2
  return 1
}

stand_install_packages() {
  local attempt
  for attempt in 1 2 3; do
    stand_wait_for_dns || return 1
    if timeout 600 dnf -y install git curl tar gzip python3 unzip; then
      return 0
    fi
    printf 'Instalação de pacotes falhou (tentativa %s/3).\n' "$attempt" >&2
    [[ "$attempt" == 3 ]] || sleep 10
  done
  return 1
}
