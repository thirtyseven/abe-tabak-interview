import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TAPES = ROOT / "work" / "tapes"
SOURCE = TAPES / "transcripts-turbo"
OUT = TAPES / "pilot-tape1"
OUT.mkdir(parents=True, exist_ok=True)


def stamp(seconds: float, millis: bool = False) -> str:
    total = round(seconds * 1000)
    hours, rem = divmod(total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    base = f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{base},{ms:03}" if millis else base


inventory = json.loads((TAPES / "inventory.json").read_text())
recordings = {item["id"]: item for item in inventory["recordings"]}
track_ids = ["R01", "R02"]

rows = []
offset = 0.0
for track_id in track_ids:
    source = json.loads((SOURCE / f"{track_id}.json").read_text())
    for segment in source["segments"]:
        text = segment["text"].strip()
        if not text:
            continue
        row = {
            "start": round(offset + segment["start"], 3),
            "end": round(offset + segment["end"], 3),
            "text": text,
            "speaker": None,
            "source_track": track_id,
            "source_start": round(segment["start"], 3),
            "confidence": round(float(segment.get("avg_logprob", 0)), 4),
            "needs_review": bool(segment.get("avg_logprob", 0) < -0.65),
        }
        rows.append(row)
    offset += float(recordings[track_id]["duration_seconds"])

payload = {
    "title": "Abe Tabak tapes — Tape 1",
    "duration_seconds": round(offset, 3),
    "sources": [recordings[key] for key in track_ids],
    "method": (
        "Continuous Tape 1 timeline assembled from the two supplied audio tracks. "
        "Draft recognition uses Whisper large-v3-turbo; speaker labels and close-listening "
        "corrections are editorial work in progress."
    ),
    "segments": rows,
}
(OUT / "transcript.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
)

plain = [
    "ABE TABAK TAPES — TAPE 1",
    "",
    payload["method"],
    "",
]
for row in rows:
    marker = " [check audio]" if row["needs_review"] else ""
    plain.append(f"[{stamp(row['start'])}]{marker} {row['text']}")
(OUT / "transcript-draft.txt").write_text("\n".join(plain) + "\n")

srt = []
for number, row in enumerate(rows, 1):
    srt.extend(
        [
            str(number),
            f"{stamp(row['start'], True)} --> {stamp(row['end'], True)}",
            row["text"],
            "",
        ]
    )
(OUT / "subtitles-draft.srt").write_text("\n".join(srt))

timeline = [
    {
        "id": item["id"],
        "file": item["source_path"],
        "duration": item["duration_seconds"],
    }
    for item in (recordings[key] for key in track_ids)
]
(OUT / "source-timeline.json").write_text(
    json.dumps(timeline, ensure_ascii=False, indent=2) + "\n"
)

print(f"Wrote {len(rows)} segments over {stamp(offset)} to {OUT}")
