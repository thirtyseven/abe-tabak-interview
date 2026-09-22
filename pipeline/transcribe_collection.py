import json
from pathlib import Path

import mlx_whisper
from huggingface_hub import snapshot_download


ROOT = Path("/Users/ted/Documents/Codex/2026-09-19/ca")
WORK = ROOT / "work/tapes/transcripts-turbo"
WORK.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT / "work/tapes/inventory.json").read_text())
model = snapshot_download(
    "mlx-community/whisper-large-v3-turbo", local_files_only=True
)

for recording in manifest["recordings"]:
    destination = WORK / f"{recording['id']}.json"
    if destination.exists():
        print(f"Skipping {recording['id']}: already complete", flush=True)
        continue
    print(f"Transcribing {recording['id']}: {recording['track']}", flush=True)
    result = mlx_whisper.transcribe(
        recording["source_path"],
        path_or_hf_repo=model,
        language=None,
        condition_on_previous_text=True,
        word_timestamps=True,
        temperature=(0.0, 0.2, 0.4),
    )
    payload = {
        "recording": recording,
        "model": "mlx-community/whisper-large-v3-turbo",
        "detected_language": result.get("language"),
        "text": result["text"].strip(),
        "segments": result.get("segments", []),
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(
        f"Completed {recording['id']}: {payload['detected_language']}, "
        f"{len(payload['segments'])} segments",
        flush=True,
    )
