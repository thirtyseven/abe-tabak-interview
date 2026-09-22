import json
from pathlib import Path

import mlx_whisper
from huggingface_hub import snapshot_download


ROOT = Path("/Users/ted/Documents/Codex/2026-09-19/ca")
OUT = ROOT / "work/tapes/transcripts-large"
OUT.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT / "work/tapes/inventory.json").read_text())
model = snapshot_download("mlx-community/whisper-large-v3-mlx", local_files_only=True)

for recording in manifest["recordings"]:
    if recording["tape_folder"] != "Abe Tabak 1 sub":
        continue
    destination = OUT / f"{recording['id']}.json"
    if destination.exists():
        continue
    result = mlx_whisper.transcribe(
        recording["source_path"],
        path_or_hf_repo=model,
        language="en",
        condition_on_previous_text=True,
        word_timestamps=True,
        temperature=(0.0, 0.2, 0.4),
    )
    destination.write_text(json.dumps({
        "recording": recording,
        "model": "mlx-community/whisper-large-v3-mlx",
        "language": "en",
        "text": result["text"].strip(),
        "segments": result.get("segments", []),
    }, ensure_ascii=False, indent=2))
    print(f"Completed {recording['id']}: {len(result.get('segments', []))} segments", flush=True)
