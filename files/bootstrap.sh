#!/usr/bin/env bash
set -euo pipefail
umask 022
root=/opt/hermes-stand
trap 'printf "Bootstrap interrompido na linha %s. Consulte o log sem compartilhar segredos ou user-data.\n" "$LINENO" >&2' ERR

source "$root/network-preflight.sh"
stand_install_packages

id hermes >/dev/null 2>&1 || useradd --create-home --home-dir /var/lib/hermes --shell /bin/bash hermes
install -d -o hermes -g hermes -m 0700 /var/lib/hermes/.hermes /var/lib/hermes/workspace
install -d -m 0755 "$root/bin" "$root/python"
export UV_INSTALL_DIR="$root/bin" UV_PYTHON_INSTALL_DIR="$root/python" UV_NO_MODIFY_PATH=1
curl --fail --silent --show-error --location --retry 3 https://astral.sh/uv/0.12.12/install.sh -o "$root/uv-install.sh"
bash "$root/uv-install.sh"
export PATH="$root/bin:$PATH"
uv python install 3.11

# Same release used in the workshop, minimal core + Telegram (no browser,
# Discord, Slack, database, GPU or interactive installer).
if [[ ! -d "$root/agent/.git" ]]; then
  git clone --depth 1 --branch v2026.7.7.2 https://github.com/NousResearch/hermes-agent.git "$root/agent"
fi
[[ "$(git -C "$root/agent" rev-parse HEAD)" == "9de9c25f620ff7f1ce0fd5457d596052d5159596" ]] || {
  printf 'A referência Hermes mudou; interrompendo para revisão.\n' >&2
  exit 1
}
(
  cd "$root/agent"
  uv sync --frozen --no-dev --python 3.11
  uv pip install --python .venv/bin/python 'python-telegram-bot[webhooks]==22.6'
)
uv venv --python 3.11 "$root/bridge-venv"
uv pip sync --python "$root/bridge-venv/bin/python" "$root/requirements.lock"

"$root/agent/.venv/bin/python" "$root/configure.py" --initialize
install -m 0644 "$root/hermes-oci-bridge.service" /etc/systemd/system/hermes-oci-bridge.service
install -m 0644 "$root/hermes-gateway.service" /etc/systemd/system/hermes-gateway.service
install -m 0644 "$root/hermes-stand-activate.service" /etc/systemd/system/hermes-stand-activate.service
restorecon -RF /etc/systemd/system/hermes-*.service "$root" /var/lib/hermes || true
systemctl daemon-reload
systemctl enable --now hermes-oci-bridge.service
# Never start an unpaired gateway. configure.py starts it AFTER secrets and tests.
systemctl enable hermes-gateway.service
systemctl enable --now hermes-stand-activate.service
touch "$root/bootstrap.done"
printf 'Instalação concluída. Ativação e testes continuam em hermes-stand-activate.service.\n'
