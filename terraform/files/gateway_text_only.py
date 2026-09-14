"""Entrypoint for the pinned Hermes: local CPU STT, no automatic voice replies.

Keep changes out of the upstream checkout. Guards also override /voice on
and old per-chat voice preferences; STT remains independent of outgoing TTS.
"""
import sys


def load_cpu_whisper(model_name):
    from faster_whisper import WhisperModel
    return WhisperModel(model_name, device='cpu', compute_type='int8',
                        cpu_threads=2, local_files_only=True)


def disable_voice_reply(*args, **kwargs):
    return False


def apply_policy():
    from gateway.platforms.base import BasePlatformAdapter
    from gateway.run import GatewayRunner
    from tools import transcription_tools
    # Fail on incompatible upstream API rather than silently enable voice.
    assert callable(BasePlatformAdapter._should_auto_tts_for_chat)
    assert callable(GatewayRunner._should_send_voice_reply)
    BasePlatformAdapter._should_auto_tts_for_chat = disable_voice_reply
    GatewayRunner._should_send_voice_reply = disable_voice_reply
    transcription_tools._load_local_whisper_model = load_cpu_whisper


def main():
    sys.path.insert(0, '/opt/hermes-stand/agent')
    apply_policy()
    from hermes_cli.main import main as hermes_main
    sys.argv = ['hermes', 'gateway', 'run']
    hermes_main()


if __name__ == '__main__':
    main()
