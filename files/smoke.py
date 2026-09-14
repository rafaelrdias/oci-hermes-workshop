"""Live OCI acceptance check. Executes on VM; does incur a few inference calls."""
import json
import secrets
import sys
from pathlib import Path

from openai import OpenAI


def collect_stream(chunks):
    """Validate the streaming contract the actual Hermes gateway consumes."""
    calls, text, finish = {}, '', None
    for chunk in chunks:
        for choice in chunk.choices:
            if choice.index != 0:
                raise ValueError('Unexpected choice')
            text += choice.delta.content or ''
            finish = choice.finish_reason or finish
            for call in choice.delta.tool_calls or []:
                state = calls.setdefault(call.index, {'id': call.id, 'name': '', 'arguments': ''})
                if call.index is None or not state['id'] or (call.id and call.id != state['id']):
                    raise ValueError('Unstable tool identity')
                if call.function:
                    state['name'] += call.function.name or ''
                    state['arguments'] += call.function.arguments or ''
    if finish not in ('stop', 'tool_calls'):
        raise ValueError('Stream incomplete or truncated')
    if calls and finish != 'tool_calls':
        raise ValueError('Incorrect tool finish reason')
    message = {'role': 'assistant', 'content': text}
    if calls:
        message['tool_calls'] = [{'id': c['id'], 'type': 'function',
            'function': {'name': c['name'], 'arguments': c['arguments']}} for c in calls.values()]
        for call in message['tool_calls']:
            if not call['function']['name'] or not isinstance(json.loads(call['function']['arguments']), dict):
                raise ValueError('Incomplete tool arguments')
    return message


def main():
    # Reasoning models need room beyond the 128-token Llama-only smoke budget.
    config = json.loads(Path('/etc/hermes-stand.json').read_text())
    budget = 4096 if config['model'] in ('openai.gpt-oss-120b', 'xai.grok-4.3', 'xai.grok-4.6') else 128
    client = OpenAI(api_key=Path("/var/lib/hermes/.hermes/bridge.key").read_text().strip(),
                    base_url="http://127.0.0.1:4000/v1", timeout=140, max_retries=0)
    nonce = "stand-" + secrets.token_hex(4)
    messages = [{"role": "user", "content": "Call stand_echo with value '" + nonce + "'."}]
    tool = {"type": "function", "function": {"name": "stand_echo", "description": "Echo a test value",
            "parameters": {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]}}}
    first = client.chat.completions.create(model="hermes-oci", messages=messages, tools=[tool],
            tool_choice={"type": "function", "function": {"name": "stand_echo"}}, max_tokens=budget)
    message = first.choices[0].message
    calls = message.tool_calls or []
    if len(calls) != 1 or calls[0].function.name != "stand_echo" or json.loads(calls[0].function.arguments).get("value") != nonce:
        print("Inferência respondeu, mas o teste de tool calling falhou. Telegram não será ativado.")
        return 5
    messages += [message.model_dump(exclude_none=True), {"role": "tool", "tool_call_id": calls[0].id, "content": nonce},
                 {"role": "user", "content": "Repeat exactly the value returned by the tool."}]
    second = client.chat.completions.create(model="hermes-oci", messages=messages, tools=[tool],
                                           tool_choice="none", max_tokens=budget)
    if nonce not in (second.choices[0].message.content or ""):
        print("Teste de retorno da ferramenta falhou.")
        return 5
    # The original check was non-streaming only and missed broken SSE tool ids.
    streamed = collect_stream(client.chat.completions.create(model='hermes-oci', messages=messages[:1],
        tools=[tool], tool_choice={'type': 'function', 'function': {'name': 'stand_echo'}},
        max_tokens=budget, stream=True))
    calls = streamed.get('tool_calls', [])
    if len(calls) != 1 or calls[0]['function']['name'] != 'stand_echo' or json.loads(calls[0]['function']['arguments']).get('value') != nonce:
        raise ValueError('Streaming tool call failed')
    followup = messages[:1] + [streamed, {'role': 'tool', 'tool_call_id': calls[0]['id'], 'content': nonce},
                              {'role': 'user', 'content': 'Repeat exactly the value returned by the tool.'}]
    answer = collect_stream(client.chat.completions.create(model='hermes-oci', messages=followup,
        tools=[tool], tool_choice='none', max_tokens=budget, stream=True))
    if nonce not in answer['content']:
        raise ValueError('Streaming tool result failed')
    print("OCI OK: inferência + chamada/retorno de ferramenta, com e sem streaming.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError:
        print("Teste de contrato de ferramenta/streaming falhou; gateway não será ativado.")
        sys.exit(5)
    except Exception as exc:
        status = getattr(exc, "status_code", "network")
        print("OCI ainda não pronta (status " + str(status) + "). Verifique IAM/limites/modelo.")
        sys.exit(4)
