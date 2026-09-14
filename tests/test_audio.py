"""Local audio policy tests without API calls, downloads or recordings."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

FILES = Path(__file__).resolve().parents[1] / 'terraform/files'


def load(name):
    spec = importlib.util.spec_from_file_location(name, FILES / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gateway = load('gateway_text_only')
prepare = load('prepare_audio')
configure = load('configure')


class AudioTests(unittest.TestCase):
    def test_cpu_model_has_no_network_or_gpu_fallback(self):
        model = Mock()
        with patch.dict(sys.modules, {'faster_whisper': SimpleNamespace(WhisperModel=model)}):
            gateway.load_cpu_whisper('/local/model')
        model.assert_called_once_with('/local/model', device='cpu', compute_type='int8',
                                      cpu_threads=2, local_files_only=True)

    def test_voice_policy_blocks_even_explicit_opt_in(self):
        self.assertFalse(gateway.disable_voice_reply(SimpleNamespace(_voice_mode={'telegram:1': 'all'}), '1'))

    def test_stt_opt_out_skips_download(self):
        with patch.object(Path, 'read_text', return_value='{"stt_enabled": false}'):
            # Dependency import itself must not happen in opt-out path.
            with patch.dict(sys.modules, {'huggingface_hub': None}):
                prepare.main()

    def test_generated_config_respects_stt_opt_out(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            original_read, original_exists = Path.read_text, Path.exists
            def read(path, *args, **kwargs):
                if str(path) == '/etc/hermes-stand.json':
                    return '{"stt_enabled": false}'
                return original_read(path, *args, **kwargs)
            def exists(path):
                return str(path) == '/etc/hermes-stand.json' or original_exists(path)
            with patch.object(configure, 'STATE', state), patch.object(configure, 'write_private', side_effect=lambda p,s: p.write_text(s)), patch.object(Path, 'read_text', read), patch.object(Path, 'exists', exists):
                configure.initialize()
            cfg = configure.yaml.safe_load((state / 'config.yaml').read_text())
            self.assertFalse(cfg['stt']['enabled'])
            self.assertEqual(cfg['stt']['provider'], 'local')
            self.assertFalse(cfg['voice']['auto_tts'])

    def test_bootstrap_preloads_before_services(self):
        script = (FILES / 'bootstrap.sh').read_text()
        self.assertIn('--extra voice', script)
        self.assertLess(script.index('"$root/prepare_audio.py"'), script.index('systemctl enable --now'))
        service = (FILES / 'hermes-gateway.service').read_text()
        self.assertIn('gateway_text_only.py', service)

    def test_model_weights_are_pinned_and_not_in_terraform_folder(self):
        self.assertRegex(prepare.MODEL_REVISION, r'^[a-f0-9]{40}$')
        self.assertFalse(list(FILES.rglob('model.bin')))


if __name__ == '__main__':
    unittest.main()
