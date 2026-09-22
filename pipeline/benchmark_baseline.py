import json
from pathlib import Path

import mlx_whisper
from huggingface_hub import snapshot_download
from mlx_whisper.audio import load_audio


ROOT = Path("/Users/ted/Documents/Codex/2026-09-19/ca")
manifest = json.loads((ROOT / "work/tapes/inventory.json").read_text())
model = snapshot_download(
    "mlx-community/whisper-large-v3-turbo", local_files_only=True
)

# One minute from the middle of the principal track for each numbered tape.
principal = {}
for recording in manifest["recordings"]:
    tape_number = int(recording["tape_folder"].split()[2])
    if tape_number not in principal or recording["duration_seconds"] > principal[tape_number]["duration_seconds"]:
        principal[tape_number] = recording

results = []
for tape_number, recording in sorted(principal.items()):
    duration = recording["duration_seconds"]
    start = max(0.0, duration / 2 - 30.0)
    audio = load_audio(recording["source_path"])
    sample = audio[int(start * 16000) : int((start + 60) * 16000)]
    result = mlx_whisper.transcribe(
        sample,
        path_or_hf_repo=model,
        language=None,
        condition_on_previous_text=False,
        word_timestamps=True,
        temperature=(0.0, 0.2, 0.4),
    )
    item = {
        "tape": tape_number,
        "recording_id": recording["id"],
        "source_path": recording["source_path"],
        "sample_start_seconds": round(start, 3),
        "detected_language": result.get("language"),
        "text": result["text"].strip(),
        "segments": result.get("segments", []),
    }
    results.append(item)
    (ROOT / "work/tapes/baseline_samples.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2)
    )
    print(f"Tape {tape_number}: {item['detected_language']} — {item['text']}", flush=True)
