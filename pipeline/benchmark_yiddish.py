import json
import subprocess
from pathlib import Path

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


ROOT = Path("/Users/ted/Documents/Codex/2026-09-19/ca")
manifest = json.loads((ROOT / "work/tapes/inventory.json").read_text())
recording = next(r for r in manifest["recordings"] if r["id"] == "R14")
sample_start = max(0.0, recording["duration_seconds"] / 2 - 30.0)
sample_path = ROOT / "work/tapes/tape9-yiddish-sample.wav"
subprocess.run(
    [
        "ffmpeg", "-y", "-v", "error", "-ss", str(sample_start),
        "-t", "60", "-i", recording["source_path"], "-ac", "1", "-ar", "16000",
        str(sample_path),
    ],
    check=True,
)

model_path = Path(
    "/Users/ted/Documents/Codex/2026-09-19/ca/work/hf-cache/hub/"
    "models--ivrit-ai--yi-whisper-large-v3/snapshots/"
    "eea1f9c368ec355e2c4189c561f211cc7d34d09c"
)
device = "mps" if torch.backends.mps.is_available() else "cpu"
dtype = torch.float16 if device == "mps" else torch.float32
processor = AutoProcessor.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_path, local_files_only=True, torch_dtype=dtype, low_cpu_mem_usage=True
).to(device)
transcriber = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    device=device,
    torch_dtype=dtype,
)
result = transcriber(
    str(sample_path),
    return_timestamps=True,
    chunk_length_s=30,
    generate_kwargs={"language": "yiddish", "task": "transcribe"},
)
payload = {
    "recording_id": recording["id"],
    "source_path": recording["source_path"],
    "sample_start_seconds": round(sample_start, 3),
    "model": "ivrit-ai/yi-whisper-large-v3",
    "language_forced": "yiddish",
    "text": result["text"],
    "chunks": result.get("chunks", []),
}
(ROOT / "work/tapes/yiddish_sample.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2)
)
print(result["text"])
