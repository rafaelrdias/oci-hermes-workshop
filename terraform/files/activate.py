"""Runs on the VM after Resource Manager Apply; no Cloud Shell or SSH needed."""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from configure import activate, validate_binding

STATE = Path("/var/lib/hermes-stand")


class ActivationError(Exception):
    pass


def save_json(path, data):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with temp.open("w") as stream:
        json.dump(data, stream)
    temp.chmod(0o600)
    temp.replace(path)


def telegram(token, method, payload=None):
    request = urllib.request.Request("https://api.telegram.org/bot" + token + "/" + method,
            data=json.dumps(payload or {}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            data = json.load(response)
        if not data.get("ok"):
            raise ActivationError("Telegram recusou a operação. Confira o bot e o token.")
        return data["result"]
    except urllib.error.HTTPError as exc:
        # URLs contain the token: never print urllib exceptions or response body.
        if exc.code == 409:
            raise ActivationError("Bot em uso por outro processo. Use um bot exclusivo; integração existente preservada.") from None
        raise ActivationError("Telegram HTTP " + str(exc.code) + "; confira token/rede.") from None
    except (urllib.error.URLError, TimeoutError):
        raise ActivationError("Telegram sem conexão; nova tentativa automática posteriormente.") from None


def owner_from_update(update, challenge, since):
    message = update.get("message", {})
    user = message.get("from", {})
    chat = message.get("chat", {})
    if (chat.get("type") == "private" and not user.get("is_bot", True)
            and message.get("text", "").strip() in (challenge, "/start " + challenge)
            and message.get("date", 0) >= since
            and isinstance(user.get("id"), int) and user["id"] > 0
            and chat.get("id") == user["id"]):
        return str(user["id"])
    return None


def pair(token, challenge, identity):
    binding_file = STATE / "binding.json"
    if binding_file.exists():
        binding = json.loads(binding_file.read_text())
        if binding.get("identity") == identity:
            validate_binding({"token": token, "owner_id": binding.get("owner_id")})
            return binding["owner_id"]
    # Accept a valid command sent while cloud-init was still installing.
    since = int(time.time()) - 86400
    offset = 0
    print("Aguardando o comando privado de pareamento dos Outputs da Stack.", flush=True)
    while True:
        updates = telegram(token, "getUpdates", {"offset": offset, "timeout": 20, "allowed_updates": ["message"]})
        for update in updates:
            offset = max(offset, update["update_id"] + 1)
            owner = owner_from_update(update, challenge, since)
            if owner:
                save_json(binding_file, {"identity": identity, "owner_id": owner})
                telegram(token, "getUpdates", {"offset": offset, "timeout": 0})
                telegram(token, "sendMessage", {"chat_id": owner, "text":
                    "Conta vinculada! Estou validando acesso OCI e ferramentas. Avisarei quando o Hermes estiver pronto."})
                return owner
        time.sleep(1)


def test_inference(token, owner):
    deadline = time.monotonic() + 1200
    while time.monotonic() < deadline:
        result = subprocess.run(["runuser", "-u", "hermes", "--", "/opt/hermes-stand/agent/.venv/bin/python",
                                 "/opt/hermes-stand/smoke.py"], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("OCI: inferência, tool call e tool result verificados.", flush=True)
            return
        if result.returncode != 4:
            telegram(token, "sendMessage", {"chat_id": owner, "text":
                "Teste de ferramenta falhou; o agente não foi liberado. Consulte a documentação de diagnóstico com o facilitador."})
            raise ActivationError("Tool calling ou execução do smoke test falhou; gateway não ativado.")
        print("OCI ainda não pronta; verifique propagação IAM, acesso e limites. Nova tentativa em 30 s.", flush=True)
        time.sleep(30)
    # Send once; service will retry automatically using the persisted binding.
    notice = STATE / "iam-notice.json"
    if not notice.exists():
        telegram(token, "sendMessage", {"chat_id": owner, "text":
            "OCI ainda indisponível. IAM pode levar até uma hora; acesso ao modelo e limites também precisam estar liberados. "
            "Continuarei tentando. Se persistir, consulte o facilitador ou remova a Stack com Destroy para encerrar o consumo."})
        save_json(notice, {"sent": True})
    raise ActivationError("OCI indisponível após 20 min; tentativa será retomada pelo serviço.")


def main():
    os.umask(0o077)
    secrets_config = json.loads(Path("/etc/hermes-stand-secrets.json").read_text())
    token, challenge = secrets_config["token"], secrets_config["pairing_code"]
    validate_binding({"token": token, "owner_id": "1"})
    identity = hashlib.sha256((token + challenge).encode()).hexdigest()
    ready_file = STATE / "ready.json"
    if ready_file.exists() and json.loads(ready_file.read_text()).get("identity") == identity:
        print("Ativação já concluída; serviços do Hermes gerenciados por systemd.")
        return
    telegram(token, "getMe")
    if telegram(token, "getWebhookInfo").get("url"):
        raise ActivationError("Webhook existente detectado. Não foi removido; use um bot exclusivo.")
    owner = pair(token, challenge, identity)
    test_inference(token, owner)
    activate({"token": token, "owner_id": owner})
    time.sleep(10)
    subprocess.run(["systemctl", "is-active", "--quiet", "hermes-gateway"], check=True)
    telegram(token, "sendMessage", {"chat_id": owner, "text":
        "Configuração concluída! Envie /new e depois: Crie boas-vindas.txt no seu workspace com uma saudação e leia o arquivo. "
        "Sua próxima mensagem fará o teste final do Hermes pelo Telegram."})
    save_json(ready_file, {"identity": identity, "inference_and_tools": "passed"})
    print("Ativação concluída. Confirme a resposta final do Hermes no Telegram.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc) if isinstance(exc, ActivationError) else "Ativação não concluída; veja diagnóstico, sem compartilhar segredos.", file=sys.stderr)
        sys.exit(1)
