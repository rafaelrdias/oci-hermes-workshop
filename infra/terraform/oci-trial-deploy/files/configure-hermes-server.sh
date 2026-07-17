#!/usr/bin/env bash
set -euo pipefail

if [[ "$(id -u)" -eq 0 ]]; then
  printf 'Run this command as opc: hermes-workshop-configure\n' >&2
  exit 1
fi

export PATH="$HOME/.local/bin:$HOME/.hermes/bin:$PATH"
env_file="$HOME/.hermes/.env"

usage() {
  cat <<'EOF'
Usage: hermes-workshop-configure [MODE]

Modes:
  --full            Configure and test OCI, then configure Telegram (default)
  --oci-only        Configure and test only OCI Generative AI
  --telegram-only   Configure Telegram and start the gateway
  --allowlist-only  Store only the Telegram numeric user allowlist
EOF
}

mode="${1:---full}"
if [[ $# -gt 1 ]]; then
  usage >&2
  exit 2
fi
case "$mode" in
  --full|--oci-only|--telegram-only|--allowlist-only) ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

prompt_secret() {
  local variable_name="$1"
  local prompt_text="$2"
  local current_value="${!variable_name:-}"
  if [[ -z "$current_value" ]]; then
    read -r -s -p "$prompt_text" current_value
    printf '\n' >&2
  fi
  if [[ -z "$current_value" || "$current_value" == *$'\n'* ]]; then
    printf '%s is empty or invalid.\n' "$variable_name" >&2
    exit 1
  fi
  printf -v "$variable_name" '%s' "$current_value"
}

upsert_env() {
  local key="$1"
  local value="$2"
  local temp_file
  temp_file="$(mktemp "$HOME/.hermes/.env.XXXXXX")"
  if [[ -f "$env_file" ]]; then
    awk -v key="$key" 'index($0, key "=") != 1 && index($0, "# " key "=") != 1 { print }' "$env_file" > "$temp_file"
  fi
  printf '%s=%s\n' "$key" "$value" >> "$temp_file"
  chmod 600 "$temp_file"
  mv "$temp_file" "$env_file"
}

read_env() {
  local key="$1"
  [[ -f "$env_file" ]] || return 0
  awk -v key="$key" 'index($0, key "=") == 1 { print substr($0, length(key) + 2); exit }' "$env_file"
}

validate_telegram_allowlist() {
  if [[ -n "$TELEGRAM_ALLOWED_USERS" && ! "$TELEGRAM_ALLOWED_USERS" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
    printf 'Use one or more numeric Telegram user IDs separated by commas.\n' >&2
    exit 1
  fi
}

OCI_GENAI_REGION="${OCI_GENAI_REGION:-us-chicago-1}"
OCI_GENAI_MODEL="${OCI_GENAI_MODEL:-openai.gpt-oss-120b}"
OCI_GENAI_BASE_URL="${OCI_GENAI_BASE_URL:-https://inference.generativeai.${OCI_GENAI_REGION}.oci.oraclecloud.com/20231130/actions/v1}"
OCI_GENAI_API_KEY="${OCI_GENAI_API_KEY:-$(read_env OPENAI_API_KEY)}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-$(read_env TELEGRAM_BOT_TOKEN)}"
TELEGRAM_ALLOWED_USERS="${TELEGRAM_ALLOWED_USERS:-}"

if [[ "$mode" == "--full" || "$mode" == "--oci-only" ]]; then
  prompt_secret OCI_GENAI_API_KEY 'OCI Generative AI API key (input hidden): '
  upsert_env OPENAI_API_KEY "$OCI_GENAI_API_KEY"

  hermes config set model.provider custom:oci-genai
  hermes config set model.default "$OCI_GENAI_MODEL"
  hermes config set model.base_url "$OCI_GENAI_BASE_URL"
  hermes config set model.api_mode chat_completions
  hermes config set model.context_length 128000

  OCI_GENAI_MODEL="$OCI_GENAI_MODEL" \
  OCI_GENAI_BASE_URL="$OCI_GENAI_BASE_URL" \
  "$HOME/.hermes/hermes-agent/venv/bin/python" - <<'PY'
import os

from hermes_cli.config import load_config, save_config

name = "oci-genai"
base_url = os.environ["OCI_GENAI_BASE_URL"]
model = os.environ["OCI_GENAI_MODEL"]
config = load_config()
providers = config.get("custom_providers") or []
if not isinstance(providers, list):
    providers = []

entry = next(
    (
        provider
        for provider in providers
        if isinstance(provider, dict)
        and (provider.get("name") == name or provider.get("base_url") == base_url)
    ),
    None,
)
if entry is None:
    entry = {}
    providers.append(entry)

entry.update(
    {
        "name": name,
        "base_url": base_url,
        "key_env": "OPENAI_API_KEY",
        "model": model,
        "api_mode": "chat_completions",
        "models": {model: {"context_length": 128000}},
    }
)
entry.pop("api_key", None)
config["custom_providers"] = providers
save_config(config)
PY

  printf 'Testing OCI Generative AI without printing the secret...\n'
  OPENAI_API_KEY="$OCI_GENAI_API_KEY" \
  OCI_GENAI_MODEL="$OCI_GENAI_MODEL" \
  OCI_GENAI_BASE_URL="$OCI_GENAI_BASE_URL" \
  "$HOME/.hermes/hermes-agent/venv/bin/python" - <<'PY'
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OCI_GENAI_BASE_URL"],
)
response = client.chat.completions.create(
    model=os.environ["OCI_GENAI_MODEL"],
    messages=[{"role": "user", "content": "Responda apenas: OCI Enterprise AI OK"}],
    max_tokens=256,
)
text = response.choices[0].message.content or ""
if not text.strip():
    raise RuntimeError("OCI returned an empty assistant response")
print(text.strip())
PY
  printf 'OCI Generative AI configured successfully.\n'
fi

if [[ "$mode" == "--allowlist-only" ]]; then
  if [[ -z "$TELEGRAM_ALLOWED_USERS" ]]; then
    read -r -p 'Telegram numeric user ID(s), comma-separated: ' TELEGRAM_ALLOWED_USERS
  fi
  validate_telegram_allowlist
  if [[ -z "$TELEGRAM_ALLOWED_USERS" ]]; then
    printf 'Telegram allowlist cannot be empty in --allowlist-only mode.\n' >&2
    exit 1
  fi
  upsert_env TELEGRAM_ALLOWED_USERS "$TELEGRAM_ALLOWED_USERS"
  printf 'Telegram allowlist stored. The gateway was not started.\n'
fi

if [[ "$mode" == "--full" || "$mode" == "--telegram-only" ]]; then
  prompt_secret TELEGRAM_BOT_TOKEN 'Telegram bot token from @BotFather (input hidden): '
  if [[ -z "$TELEGRAM_ALLOWED_USERS" ]]; then
    TELEGRAM_ALLOWED_USERS="$(read_env TELEGRAM_ALLOWED_USERS)"
  fi
  if [[ -z "$TELEGRAM_ALLOWED_USERS" ]]; then
    read -r -p 'Telegram numeric user ID (optional; Enter enables secure pairing): ' TELEGRAM_ALLOWED_USERS
  fi
  validate_telegram_allowlist

  upsert_env TELEGRAM_BOT_TOKEN "$TELEGRAM_BOT_TOKEN"
  if [[ -n "$TELEGRAM_ALLOWED_USERS" ]]; then
    upsert_env TELEGRAM_ALLOWED_USERS "$TELEGRAM_ALLOWED_USERS"
  fi

  sudo systemctl restart hermes-gateway
  sleep 3
  sudo systemctl --no-pager --full status hermes-gateway

  if [[ -z "$TELEGRAM_ALLOWED_USERS" ]]; then
    printf '\nEnvie uma mensagem privada ao bot. Ele retornará um código. Aprove com:\n'
    printf '  hermes pairing approve telegram <CODIGO>\n'
  else
    printf '\nTelegram configurado com allowlist. Envie /new ao bot para testar.\n'
  fi
fi
