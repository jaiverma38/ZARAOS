import subprocess
import tempfile
from pathlib import Path
import soundfile as sf
import whisper

class SpeechEngine:
    def __init__(self, whisper_model: str, piper_voice: str):
        self.stt_model = whisper.load_model(whisper_model)
        self.piper_voice = piper_voice

    def transcribe(self, audio_bytes: bytes, suffix: str = ".wav") -> dict:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as handle:
            handle.write(audio_bytes)
            handle.flush()
            result = self.stt_model.transcribe(handle.name)
        return {"text": result.get("text", "").strip(), "language": result.get("language", "unknown"), "segments": result.get("segments", [])}

    def synthesize(self, text: str) -> bytes:
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "tts.wav"
            subprocess.run(["piper", "--model", self.piper_voice, "--output_file", str(wav)], input=text.encode(), check=True)
            data, sample_rate = sf.read(wav, dtype="int16")
            out = Path(tmp) / "tts_out.wav"
            sf.write(out, data, sample_rate, subtype="PCM_16")
            return out.read_bytes()
