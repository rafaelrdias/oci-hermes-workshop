"""Live OCI acceptance check. Executes on VM; does incur a few inference calls."""
import json
import secrets
import sys
from pathlib import Path

from openai import OpenAI


def main():
    client = OpenAI(api_key=Path("/var/lib/hermes/.hermes/bridge.key").read_text().strip(),
                    base_url="http://127.0.0.1:4000/v1", timeout=140, max_retries=0)
    nonce = "stand-" + secrets.token_hex(4)
    messages = [{"role": "user", "content": "Call stand_echo with value '" + nonce + "'."}]
    tool = {"type": "function", "function": {"name": "stand_echo", "description": "Echo a test value",
            "parameters": {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]}}}
    first = client.chat.completions.create(model="hermes-oci", messages=messages, tools=[tool],
            tool_choice={"type": "function", "function": {"name": "stand_echo"}}, max_tokens=128)
    message = first.choices[0].message
    calls = message.tool_calls or []
    if len(calls) != 1 or calls[0].function.name != "stand_echo" or json.loads(calls[0].function.arguments).get("value") != nonce:
        print("Inferência respondeu, mas o teste de tool calling falhou. Telegram não será ativado.")
        return 5
    messages += [message.model_dump(exclude_none=True), {"role": "tool", "tool_call_id": calls[0].id, "content": nonce},
                 {"role": "user", "content": "Repeat exactly the value returned by the tool."}]
    second = client.chat.completions.create(model="hermes-oci", messages=messages, tools=[tool],
                                           tool_choice="none", max_tokens=128)
    if nonce not in (second.choices[0].message.content or ""):
        print("Teste de retorno da ferramenta falhou.")
        return 5
    print("OCI OK: inferência + chamada de ferramenta + retorno da ferramenta.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        status = getattr(exc, "status_code", "network")
        print("OCI ainda não pronta (status " + str(status) + "). Verifique IAM/limites/modelo.")
        sys.exit(4)
