"""Loopback-only OpenAI chat facade. LiteLLM handles OCI messages/tools/SSE.

No provider selection, endpoints or credentials are accepted from the caller.
This is a personal demo bridge, not a public multi-tenant API gateway.
"""
import json
import logging
import secrets
import threading
import time
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
    result.update(model="oci/" + config["model"], max_tokens=max(1, min(requested, 4000)),
                  oci_region=config["region"], oci_compartment_id=config["compartment_id"],
                  oci_serving_mode="ON_DEMAND", timeout=120, num_retries=0, drop_params=True)
    return result


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
        result = litellm.completion(**args, oci_signer=signer())
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
            for chunk in result:
                yield "data: " + chunk.model_dump_json(exclude_none=True) + "\n\n"
            yield "data: [DONE]\n\n"
        except Exception:
            yield 'data: {"error":{"message":"Streaming OCI interrompido","type":"upstream_error"}}\n\n'
        finally:
            if hasattr(result, "close"):
                result.close()
            slots.release()
    return StreamingResponse(events(), media_type="text/event-stream")
