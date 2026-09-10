"""Root-only configuration, invoked by activate.py; optional stdin for diagnostics."""
import argparse
import json
import os
import pwd
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

STATE = Path("/var/lib/hermes/.hermes")
BASE_URL = "http://127.0.0.1:4000/v1"
TOKEN_PATTERN = r"[0-9]{5,15}:[A-Za-z0-9_-]{30,100}"


def write_private(path, text):
    user = pwd.getpwnam("hermes")
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(text)
        os.chmod(temp, 0o600)
        os.chown(temp, user.pw_uid, user.pw_gid)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def validate_binding(data):
    if not re.fullmatch(TOKEN_PATTERN, str(data.get("token", ""))):
        raise ValueError("Token do Telegram inválido")
    owner = str(data.get("owner_id", ""))
    if not re.fullmatch(r"[1-9][0-9]{0,19}", owner):
        raise ValueError("ID do dono deve ser numérico e positivo")
    return owner


def initialize():
    key_file = STATE / "bridge.key"
    if not key_file.exists():
        write_private(key_file, secrets.token_urlsafe(48) + "\n")
    key = key_file.read_text().strip()
    if not (STATE / "config.yaml").exists():
        config = {
            "_config_version": 33,
            "model": {"provider": "custom:oci-stand", "default": "hermes-oci",
                      "base_url": BASE_URL, "api_mode": "chat_completions",
                      "context_length": 128000, "max_tokens": 2048},
            "custom_providers": [{"name": "oci-stand", "base_url": BASE_URL,
                                  "api_mode": "chat_completions", "key_env": "OPENAI_API_KEY",
                                  "model": "hermes-oci", "context_length": 128000}],
            "agent": {"max_turns": 8, "gateway_timeout": 300, "disabled_toolsets": ["kanban"]},
            "terminal": {"backend": "local", "cwd": "/var/lib/hermes/workspace", "timeout": 30},
            "auxiliary": {name: {"provider": "custom", "model": "hermes-oci", "base_url": BASE_URL}
                          for name in ("compression", "title_generation", "approval")},
            "toolsets": ["terminal", "file", "memory", "skills"],
            "platform_toolsets": {"telegram": ["terminal", "file", "memory", "skills"]},
        }
        write_private(STATE / "config.yaml", yaml.safe_dump(config, sort_keys=False))
    if not (STATE / ".env").exists():
        write_private(STATE / ".env", "OPENAI_API_KEY=" + key + "\nOPENAI_BASE_URL=" + BASE_URL + "\nGATEWAY_ALLOW_ALL_USERS=false\n")
    if not (STATE / "SOUL.md").exists():
        write_private(STATE / "SOUL.md", """# Hermes no stand Oracle
Você é o assistente pessoal deste visitante, executando em OCI. Responda em português.
Este ambiente é uma demonstração de texto. Não prometa analisar imagens ou áudio.
Use ferramentas quando necessário, confira os resultados e não invente execuções.
Trabalhe em /var/lib/hermes/workspace. Não leia nem exponha chaves ou tokens,
inclusive .env, bridge.key, metadados de identidade da VM e credenciais OCI.
Peça confirmação antes de ações destrutivas ou envio de informações a terceiros.
""")


def activate(data):
    owner = validate_binding(data)
    initialize()
    # Complete replacement of ONLY managed env keys; reruns rotate token safely.
    managed = {"TELEGRAM_BOT_TOKEN": data["token"], "TELEGRAM_ALLOWED_USERS": owner,
               "TELEGRAM_HOME_CHANNEL": owner, "GATEWAY_ALLOW_ALL_USERS": "false"}
    lines = [line for line in (STATE / ".env").read_text().splitlines()
             if line.split("=", 1)[0] not in managed]
    lines += [name + "=" + value for name, value in managed.items()]
    write_private(STATE / ".env", "\n".join(lines) + "\n")
    write_private(STATE / "telegram.ready", "Owner verified by private Telegram challenge.\n")
    subprocess.run(["systemctl", "restart", "hermes-gateway"], check=True)
    subprocess.run(["systemctl", "is-active", "--quiet", "hermes-gateway"], check=True)
    print("Telegram configurado; confirme a resposta real no aplicativo.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise RuntimeError("Execute via sudo no servidor")
    if args.initialize:
        initialize()
    elif args.activate:
        activate(json.loads(sys.stdin.read(8192)))
    else:
        parser.error("Escolha --initialize ou --activate")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # No traceback of JSON/secrets even on validation errors.
        print("Configuração não concluída. Verifique entrada, permissões e serviço.", file=sys.stderr)
        sys.exit(1)
