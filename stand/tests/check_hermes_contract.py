"""Run with the pinned Hermes venv; verifies actual upstream config resolution."""
import importlib.util
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

source = Path(__file__).resolve().parents[1] / "terraform/files/configure.py"
spec = importlib.util.spec_from_file_location("stand_config", source)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

with tempfile.TemporaryDirectory() as temp:
    state = Path(temp)
    with patch.object(config, "STATE", state), patch.object(config, "write_private", side_effect=lambda p, s: p.write_text(s)):
        config.initialize()
    with patch.dict(os.environ, {"HERMES_HOME": temp, "OPENAI_API_KEY": "test-local-key", "OPENAI_BASE_URL": config.BASE_URL}):
        from hermes_cli.config import load_config
        from hermes_cli.runtime_provider import resolve_runtime_provider
        from hermes_cli.tools_config import _get_platform_tools
        cfg = load_config()
        runtime = resolve_runtime_provider(requested="custom:oci-stand", target_model="hermes-oci")
        assert runtime["base_url"] == config.BASE_URL, runtime["base_url"]
        assert runtime["api_mode"] == "chat_completions", runtime["api_mode"]
        assert runtime["api_key"] == "test-local-key"
        active_tools = _get_platform_tools(cfg, "telegram", include_default_mcp_servers=False)
        assert active_tools == {"terminal", "file", "memory", "skills"}, active_tools
        import gateway.run  # Validate minimal installation imports gateway runtime.
        import sys
        sys.path.insert(0, str(source.parent))
        import gateway_text_only
        gateway_text_only.apply_policy()
        from gateway.platforms.base import BasePlatformAdapter
        from gateway.run import GatewayRunner
        from tools import transcription_tools
        assert not BasePlatformAdapter._should_auto_tts_for_chat(None, '123')
        assert not GatewayRunner._should_send_voice_reply(None, None, 'response', [])
        assert transcription_tools._get_provider({'enabled': True, 'provider': 'local'}) == 'local'
        assert cfg['stt']['local']['language'] == 'pt'
        assert not cfg['voice']['auto_tts']
    print("Pinned Hermes: provider, credentials, Telegram toolsets and gateway imports OK (no live inference).")
