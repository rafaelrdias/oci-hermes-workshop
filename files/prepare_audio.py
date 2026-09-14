"""Download a pinned local STT model before activation; never send user audio."""
import json
from pathlib import Path

MODEL_DIR = Path('/var/lib/hermes/models/whisper-base')
MODEL_REVISION = 'ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66'


def main():
    if not json.loads(Path('/etc/hermes-stand.json').read_text()).get('stt_enabled', True):
        print('STT desabilitado no formulário; respostas somente texto.')
        return
    from huggingface_hub import snapshot_download
    from faster_whisper import WhisperModel
    import numpy as np
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download('Systran/faster-whisper-base', revision=MODEL_REVISION,
                      local_dir=str(MODEL_DIR),
                      allow_patterns=['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt'])
    model = WhisperModel(str(MODEL_DIR), device='cpu', compute_type='int8',
                         cpu_threads=2, local_files_only=True)
    # Check model loading and VAD without a user recording or paid API.
    segments, _ = model.transcribe(np.zeros(16000, dtype=np.float32), language='pt', vad_filter=True)
    list(segments)
    print('STT local pronto: Whisper base, CPU, português. Respostas somente texto.')


if __name__ == '__main__':
    main()
