"""Offline safety/contract tests; no tenancy, VM or Telegram requests."""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


sys.path.insert(0, str(ROOT / "terraform/files"))
setup = module("stand_activate", ROOT / "terraform/files/activate.py")
configure = module("stand_configure", ROOT / "terraform/files/configure.py")
bridge = module("stand_bridge", ROOT / "terraform/files/bridge.py")


class PairingTests(unittest.TestCase):
    def update(self, **kwargs):
        message = {"text": "/start stand_abc", "date": 100, "from": {"id": 12345, "is_bot": False},
                   "chat": {"id": 12345, "type": "private"}}
        message.update(kwargs)
        return {"update_id": 1, "message": message}

    def test_private_owner(self):
        self.assertEqual(setup.owner_from_update(self.update(), "stand_abc", 95), "12345")

    def test_reject_wrong_challenge(self):
        self.assertIsNone(setup.owner_from_update(self.update(), "other", 95))

    def test_reject_old_message(self):
        self.assertIsNone(setup.owner_from_update(self.update(), "stand_abc", 101))

    def test_reject_group_and_bot(self):
        self.assertIsNone(setup.owner_from_update(self.update(chat={"type": "group", "id": -50}), "stand_abc", 95))
        self.assertIsNone(setup.owner_from_update(self.update(**{"from": {"id": 12345, "is_bot": True}}), "stand_abc", 95))

    def test_reject_mismatched_sender(self):
        self.assertIsNone(setup.owner_from_update(self.update(chat={"type": "private", "id": 2}), "stand_abc", 95))

    def test_binding_validation_blocks_newline_injection(self):
        valid = {"token": "123456:" + "a" * 35, "owner_id": "12345"}
        self.assertEqual(configure.validate_binding(valid), "12345")
        for field, value in [("owner_id", "12345\nGATEWAY_ALLOW_ALL_USERS=true"), ("owner_id", "-100"),
                             ("token", valid["token"] + "\nEVIL=true")]:
            with self.assertRaises(ValueError):
                configure.validate_binding(dict(valid, **{field: value}))

    def test_telegram_http_error_never_leaks_token(self):
        token = "123456:" + "a" * 35
        error = setup.urllib.error.HTTPError("https://api.telegram.org/bot" + token, 401, "bad", {}, None)
        with patch.object(setup.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(setup.ActivationError) as caught:
                setup.telegram(token, "getMe")
        self.assertNotIn(token, str(caught.exception))


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.config_patch = patch.object(bridge, "settings", return_value={"region": "sa-saopaulo-1",
              "compartment_id": "ocid1.compartment.oc1..test", "model": "meta.llama-3.3-70b-instruct"})
        self.config_patch.start()
        self.addCleanup(self.config_patch.stop)
        bridge.request_times.clear()

    def request(self, **kwargs):
        body = {"model": "hermes-oci", "messages": [{"role": "user", "content": "oi"}]}
        body.update(kwargs)
        return body

    def test_no_caller_endpoint_or_auth_override(self):
        args = bridge.completion_args(self.request(api_base="https://attacker.invalid", api_key="evil", oci_region="elsewhere"))
        self.assertNotIn("api_base", args)
        self.assertNotIn("api_key", args)
        self.assertEqual(args["oci_region"], "sa-saopaulo-1")
        self.assertEqual(args["oci_serving_mode"], "ON_DEMAND")

    def test_limit_and_tool_passthrough(self):
        tools = [{"type": "function", "function": {"name": "test"}}]
        args = bridge.completion_args(self.request(tools=tools, tool_choice="auto", max_tokens=99999, stream=True))
        self.assertEqual(args["max_tokens"], 4000)
        self.assertEqual(args["tools"], tools)
        self.assertTrue(args["stream"])

    def test_reject_model_and_images(self):
        with self.assertRaises(bridge.HTTPException):
            bridge.completion_args(self.request(model="gpt-other"))
        with self.assertRaises(bridge.HTTPException):
            bridge.completion_args(self.request(messages=[{"role": "user", "content": [{"type": "image_url"}]}]))

    def test_http_auth_and_completions(self):
        from fastapi.testclient import TestClient
        from litellm import ModelResponse
        client = TestClient(bridge.app)
        with patch.object(Path, "read_text", return_value="local-test-key"):
            self.assertEqual(client.post("/v1/chat/completions", json=self.request()).status_code, 401)
            with patch.object(bridge, "signer", return_value=object()), patch.object(bridge.litellm, "completion", return_value=ModelResponse(
                    model="oci/test", choices=[{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}])):
                response = client.post("/v1/chat/completions", json=self.request(), headers={"Authorization": "Bearer local-test-key"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["choices"][0]["message"]["content"], "ok")

    def test_errors_are_redacted(self):
        from fastapi.testclient import TestClient
        client = TestClient(bridge.app)
        with patch.object(Path, "read_text", return_value="local-test-key"), patch.object(bridge, "signer", side_effect=RuntimeError("secret-token-example")):
            response = client.post("/v1/chat/completions", json=self.request(), headers={"Authorization": "Bearer local-test-key"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("secret-token-example", response.text)

    def test_streaming_contract(self):
        from fastapi.testclient import TestClient
        from litellm import ModelResponseStream
        client = TestClient(bridge.app)
        chunks = iter([ModelResponseStream(id="stream-test", choices=[{
            "index": 0, "delta": {"role": "assistant", "content": "oi"}, "finish_reason": None}])])
        with patch.object(Path, "read_text", return_value="local-test-key"), patch.object(bridge, "signer", return_value=object()), patch.object(bridge.litellm, "completion", return_value=chunks):
            response = client.post("/v1/chat/completions", json=self.request(stream=True), headers={"Authorization": "Bearer local-test-key"})
        self.assertIn("text/event-stream", response.headers["content-type"])
        self.assertIn("data: [DONE]", response.text)
        self.assertIn('"content":"oi"', response.text)

    def test_native_oci_tool_adapter(self):
        from litellm.llms.oci.chat.generic import adapt_messages_to_generic_oci_standard
        messages = [{"role": "user", "content": "test"}, {"role": "assistant", "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "stand_echo", "arguments": '{"value":"ok"}'}}]},
            {"role": "tool", "tool_call_id": "call_1", "content": "ok"}]
        mapped = adapt_messages_to_generic_oci_standard(messages)
        self.assertEqual(mapped[1].toolCalls[0].name, "stand_echo")
        self.assertEqual(mapped[2].toolCallId, "call_1")


class FilesTests(unittest.TestCase):
    def test_state_file_permissions(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data.json"
            setup.save_json(path, {"owner_id": "12345"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(path.read_text())["owner_id"], "12345")

    def test_init_config_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            def writer(path, text):
                path.write_text(text)
            with patch.object(configure, "STATE", state), patch.object(configure, "write_private", side_effect=writer):
                configure.initialize()
                first_key = (state / "bridge.key").read_text()
                configure.initialize()
                self.assertEqual((state / "bridge.key").read_text(), first_key)
                config = configure.yaml.safe_load((state / "config.yaml").read_text())
                self.assertEqual(config["platform_toolsets"]["telegram"], ["terminal", "file", "memory", "skills"])
                self.assertEqual(config["model"]["provider"], "custom:oci-stand")
                self.assertNotIn("TELEGRAM_BOT_TOKEN", (state / ".env").read_text())
                self.assertFalse((state / "telegram.ready").exists())

    def test_secret_risk_is_explicit_and_sensitive(self):
        source = (ROOT / "terraform/variables.tf").read_text().lower()
        self.assertIn('variable "telegram_bot_token"', source)
        self.assertRegex(source, r'sensitive\s*=\s*true')
        self.assertIn('variable "acknowledge_secret_in_state"', source)
        for forbidden in ("oci_api_key", "private_key", "tls_private_key"):
            self.assertNotIn(forbidden, source)

    def test_service_security_and_no_public_bridge(self):
        gateway = (ROOT / "terraform/files/hermes-gateway.service").read_text()
        proxy = (ROOT / "terraform/files/hermes-oci-bridge.service").read_text()
        self.assertIn("User=hermes", gateway)
        self.assertIn("NoNewPrivileges=true", gateway)
        self.assertIn("ConditionPathExists=", gateway)
        self.assertIn("--host 127.0.0.1", proxy)


if __name__ == "__main__":
    unittest.main()
