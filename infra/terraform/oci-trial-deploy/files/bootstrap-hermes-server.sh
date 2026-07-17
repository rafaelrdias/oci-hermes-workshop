#!/usr/bin/env bash
set -euo pipefail

HERMES_GIT_REF="${HERMES_GIT_REF:-v2026.7.7.2}"
HERMES_INSTALL_BROWSER_TOOLS="${HERMES_INSTALL_BROWSER_TOOLS:-false}"
OCI_GENAI_REGION="${OCI_GENAI_REGION:-us-chicago-1}"
OCI_GENAI_MODEL="${OCI_GENAI_MODEL:-openai.gpt-oss-120b}"
OCI_GENAI_BASE_URL="${OCI_GENAI_BASE_URL:-https://inference.generativeai.${OCI_GENAI_REGION}.oci.oraclecloud.com/20231130/actions/v1}"

if [[ "$(id -u)" -eq 0 ]]; then
  printf 'Run this script as the unprivileged opc user, not root.\n' >&2
  exit 1
fi

export PATH="$HOME/.local/bin:$HOME/.hermes/bin:$PATH"

if ! command -v hermes >/dev/null 2>&1; then
  installer_url="https://raw.githubusercontent.com/NousResearch/hermes-agent/${HERMES_GIT_REF}/scripts/install.sh"
  installer_args=(--branch "$HERMES_GIT_REF" --skip-setup)
  if [[ "$HERMES_INSTALL_BROWSER_TOOLS" != "true" ]]; then
    installer_args+=(--skip-browser)
  fi
  curl -fsSL "$installer_url" | bash -s -- "${installer_args[@]}"
  export PATH="$HOME/.local/bin:$HOME/.hermes/bin:$PATH"
else
  printf 'Hermes already installed; preserving the existing installation.\n'
fi

# Telegram is the only messaging extra required by this workshop.
"$HOME/.hermes/bin/uv" pip install \
  --python "$HOME/.hermes/hermes-agent/venv/bin/python" \
  "python-telegram-bot[webhooks]==22.6"

hermes doctor --fix || true
hermes config set model.provider custom
hermes config set model.default "$OCI_GENAI_MODEL"
hermes config set model.base_url "$OCI_GENAI_BASE_URL"
hermes config set model.api_mode chat_completions
hermes config set model.context_length 128000

# Install the gateway at system scope but do not start it before secrets exist.
if ! sudo test -f /etc/systemd/system/hermes-gateway.service; then
  sudo env \
    HOME="$HOME" USER="$(id -un)" LOGNAME="$(id -un)" HERMES_HOME="$HOME/.hermes" PATH="$PATH" \
    "$HOME/.local/bin/hermes" gateway install \
    --system --run-as-user "$(id -un)" --no-start-now --start-on-login
fi

# On SELinux-enforcing Oracle Linux, systemd cannot directly execute a Python
# interpreter stored below /home. Starting through the system bash binary keeps
# the service unprivileged while allowing the normal SELinux domain transition.
if command -v getenforce >/dev/null 2>&1 && [[ "$(getenforce)" == "Enforcing" ]]; then
  systemd_override="$(mktemp)"
  {
    printf '%s\n' '[Service]'
    printf '%s\n' 'ExecStart='
    printf "ExecStart=/usr/bin/bash -lc 'exec %s/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run'\n" "$HOME"
    printf '%s\n' 'ExecStopPost='
    printf "ExecStopPost=-/usr/bin/bash -lc 'exec %s/.hermes/hermes-agent/venv/bin/python -m gateway.cgroup_cleanup'\n" "$HOME"
  } > "$systemd_override"
  sudo install -d -o root -g root -m 0755 /etc/systemd/system/hermes-gateway.service.d
  sudo install -o root -g root -m 0644 \
    "$systemd_override" /etc/systemd/system/hermes-gateway.service.d/selinux.conf
  rm -f "$systemd_override"
  sudo restorecon -RF /etc/systemd/system/hermes-gateway.service.d
  sudo systemctl daemon-reload
fi

printf 'Hermes bootstrap complete. Run: hermes-workshop-configure\n'
