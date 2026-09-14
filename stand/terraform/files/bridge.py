"""Loopback-only OpenAI chat facade. LiteLLM handles OCI messages/tools/SSE.

No provider selection, endpoints or credentials are accepted from the caller.
This is a personal demo bridge, not a public multi-tenant API gateway.
"""
import json
import logging
import secrets
import threading
import time
import math
from email.utils import parsedate_to_datetime
from functools import lru_cache
from pathlib import Path

import litellm
from litellm.llms.oci.chat import transformation as oci_chat
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner

litellm.telemetry = False
litellm.suppress_debug_info = True
for name in ("LiteLLM", "httpx", "httpcore", "oci"):
    logging.getLogger(name).setLevel(logging.CRITICAL)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
slots = threading.BoundedSemaphore(2)
rate_lock = threading.Lock()
request_times = []
upstream_lock = threading.Lock()
cooldown_until = 0.0
RATE_RETRY_SECONDS = 65
REQUEST_BUDGET_SECONDS = 100


def retry_delay(exc):
    """Respect Retry-After, including HTTP dates. Never expose provider headers."""
    response = getattr(exc, 'response', None)
    headers = getattr(response, 'headers', {}) or {}
    value = headers.get('retry-after')
    try:
        delay = float(value)
    except (ValueError, TypeError):
        try:
            delay = parsedate_to_datetime(value).timestamp() - time.time()
        except (ValueError, TypeError, AttributeError, OverflowError):
            delay = RATE_RETRY_SECONDS
    return max(1, delay) if math.isfinite(delay) else RATE_RETRY_SECONDS


def rate_error(delay):
    return HTTPException(429, 'Limite temporário OCI/Grok. Aguarde a janela de uso; não é erro de autenticação.',
                         headers={'Retry-After': str(max(1, math.ceil(delay))),
                                  'X-Hermes-Limit-Source': 'oci'})


def completion_with_backoff(args):
    """One bounded retry of rejected inference, never replay a delivered stream.

    Share cooldown across foreground and auxiliary requests. Serialize opening
    upstream calls, but do not hold the lock for the entire SSE response.
    This does not change OCI quotas, models, accounts or the hourly ceiling.
    """
    global cooldown_until
    deadline = time.monotonic() + REQUEST_BUDGET_SECONDS
    if not upstream_lock.acquire(timeout=REQUEST_BUDGET_SECONDS):
        raise HTTPException(429, 'Fila local ocupada; aguarde a tarefa anterior.',
                            headers={'Retry-After': '10', 'X-Hermes-Limit-Source': 'local'})
    try:
        for attempt in range(2):
            delay = max(0, cooldown_until - time.monotonic())
            if delay >= deadline - time.monotonic():
                raise rate_error(delay)
            if delay:
                time.sleep(delay)
            if attempt:
                with rate_lock:
                    now = time.monotonic()
                    request_times[:] = [t for t in request_times if now - t < 3600]
                    if len(request_times) >= 120:
                        raise HTTPException(429, 'Limite local: 120 chamadas/hora.',
                                            headers={'X-Hermes-Limit-Source': 'local'})
                    request_times.append(now)
            try:
                remaining = max(1, deadline - time.monotonic())
                return litellm.completion(**dict(args, timeout=min(args['timeout'], remaining)), oci_signer=signer())
            except Exception as exc:
                if getattr(exc, 'status_code', None) != 429:
                    raise
                delay = retry_delay(exc)
                cooldown_until = max(cooldown_until, time.monotonic() + delay)
                logging.getLogger('hermes.bridge').warning('OCI HTTP 429; cooldown %.0fs; attempt %s/2', delay, attempt + 1)
                if attempt or delay >= deadline - time.monotonic():
                    raise rate_error(delay) from None
        raise RuntimeError('Unreachable retry state')
    finally:
        upstream_lock.release()


def iter_oci_sse_events(stream, _parse=oci_chat._iter_sse_events):
    """Compatibility fix for pinned LiteLLM: [DONE] is not an OCI JSON chunk.

    Keep upstream framing (including split HTTP reads), stopping only at the
    exact SSE terminal marker. Malformed payloads still reach its error path.
    """
    for event in _parse(stream):
        if event.partition(':')[2].strip() == '[DONE]':
            return
        yield event


# This bridge uses only synchronous completion; async OCI calls are not used.
# Local to this process, with LiteLLM pinned and regression tests below.
oci_chat._iter_sse_events = iter_oci_sse_events


@lru_cache(maxsize=1)
def settings():
    return json.loads(Path("/etc/hermes-stand.json").read_text())


class RefreshingOCISigner:
    """Adapt LiteLLM's low-level signing hook to the SDK's refresh-aware API.

    LiteLLM 1.100.1 calls do_request_sign directly, bypassing the OCI SDK
    __call__ path that renews the federation token and resets signing keys.
    Serialize refresh + signing so concurrent requests cannot mix key pairs.
    """

    def __init__(self, sdk_signer):
        self._sdk_signer = sdk_signer
        self._lock = threading.Lock()

    def do_request_sign(self, request, enforce_content_headers=True):
        with self._lock:
            return self._sdk_signer(request, enforce_content_headers=enforce_content_headers)


@lru_cache(maxsize=1)
def signer():
    return RefreshingOCISigner(InstancePrincipalsSecurityTokenSigner())


def authorize(authorization):
    key = Path("/var/lib/hermes/.hermes/bridge.key").read_text().strip()
    if not secrets.compare_digest(authorization or "", "Bearer " + key):
        raise HTTPException(401, "Credencial local inválida")


def completion_args(body):
    config = settings()
    if body.get("model") not in ("hermes-oci", config["model"]):
        raise HTTPException(400, "Modelo não permitido nesta demonstração")
    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        raise HTTPException(400, "messages deve ser uma lista não vazia")
    if len(json.dumps(body).encode()) > 512_000:
        raise HTTPException(413, "Conversa grande demais; envie /new")
    if any(isinstance(m.get("content"), list) and
           any(p.get("type") != "text" for p in m["content"])
           for m in messages if isinstance(m, dict)):
        raise HTTPException(400, "Esta edição usa apenas texto, não imagens/áudio")
    # Forward only OpenAI conversation parameters, never arbitrary LiteLLM kwargs.
    allowed = ("messages", "tools", "tool_choice", "temperature", "top_p", "stop",
               "frequency_penalty", "presence_penalty", "stream")
    result = {k: body[k] for k in allowed if k in body}
    try:
        requested = int(body.get("max_completion_tokens") or body.get("max_tokens") or 2048)
    except (ValueError, TypeError):
        raise HTTPException(400, "max_tokens inválido") from None
    ceiling = 8192 if config['model'] == 'xai.grok-4.6' else 4000
    result.update(model="oci/" + config["model"], max_tokens=max(1, min(requested, ceiling)),
                  oci_region=config["region"], oci_compartment_id=config["compartment_id"],
                  oci_serving_mode="ON_DEMAND", timeout=120, num_retries=0, drop_params=True)
    return result


def normalized_stream(result):
    """Keep each tool call's identity stable across pinned OCI adapter deltas.

    LiteLLM 1.100.1 synthesizes a different id from each argument fragment
    when OCI omits the id on continuation chunks. Hermes then sees separate,
    invalid tool calls. Indices are scoped to one choice and one response.
    Never concatenate/repair arguments here, or hide a real length cutoff.
    """
    calls = {}
    for chunk in result:
        payload = chunk.model_dump(exclude_none=True)
        for choice in payload.get("choices", []):
            choice_index = choice.get("index", 0)
            delta = choice.get("delta", {})
            for position, call in enumerate(delta.get("tool_calls") or []):
                index = call.get("index", position)
                key = (choice_index, index)
                call["index"] = index
                function = call.setdefault("function", {})
                if key not in calls:
                    calls[key] = {"id": call.get("id") or "call_" + secrets.token_hex(12), "name": ""}
                state = calls[key]
                name = function.get("name") or ""
                if state["name"] and name and name != state["name"]:
                    raise ValueError("OCI reused a tool index for a different function")
                if state["name"] or not name:
                    # Function name is metadata, not a repeated argument delta.
                    function.pop("name", None)
                else:
                    state["name"] = name
                call["id"] = state["id"]
            if choice.get("finish_reason") == "stop" and any(k[0] == choice_index for k in calls):
                choice["finish_reason"] = "tool_calls"
        yield payload


@app.get("/healthz")
def health():
    # Process readiness only; smoke.py checks actual inference and tool calling.
    return {"status": "process-ready", "inference_tested": False}


@app.get("/v1/models")
def models(authorization: str = Header(default="")):
    authorize(authorization)
    return {"object": "list", "data": [{"id": "hermes-oci", "object": "model", "owned_by": "oci"}]}


@app.post("/v1/chat/completions")
def chat(body: dict, authorization: str = Header(default="")):
    authorize(authorization)
    args = completion_args(body)
    if not slots.acquire(blocking=False):
        raise HTTPException(429, "Aguarde a resposta anterior")
    with rate_lock:
        now = time.monotonic()
        request_times[:] = [t for t in request_times if now - t < 3600]
        if len(request_times) >= 120:
            slots.release()
            raise HTTPException(429, "Limite local: 120 chamadas/hora; não é um teto financeiro")
        request_times.append(now)
    try:
        result = completion_with_backoff(args)
    except HTTPException:
        slots.release()
        raise
    except Exception as exc:
        slots.release()
        status = getattr(exc, "status_code", 502)
        status = status if isinstance(status, int) and 400 <= status <= 599 else 502
        # Never serialize provider exceptions: they may contain request bodies/headers.
        raise HTTPException(status, "OCI indisponível: verifique IAM, modelo, limites e créditos") from None
    if not args.get("stream"):
        try:
            return result.model_dump(exclude_none=True)
        finally:
            slots.release()

    def events():
        try:
            for payload in normalized_stream(result):
                yield "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"
            yield "data: [DONE]\n\n"
        except Exception:
            yield 'data: {"error":{"message":"Streaming OCI interrompido","type":"upstream_error"}}\n\n'
        finally:
            if hasattr(result, "close"):
                result.close()
            slots.release()
    return StreamingResponse(events(), media_type="text/event-stream")
