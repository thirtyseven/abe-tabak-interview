import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TAPES = ROOT / "work" / "tapes"
PILOT = TAPES / "pilot-tape1"
inventory = json.loads((TAPES / "inventory.json").read_text())
recordings = {item["id"]: item for item in inventory["recordings"]}
turns = json.loads((PILOT / "diarization.json").read_text())["turns"]

# The forced four-cluster pass split Abe as recording conditions changed.
# Listening/context checks show SPEAKER_02 contains the short questions and
# interjections; the other three clusters contain Abe's continuous narrative.
names = {
    "SPEAKER_00": "Abe",
    "SPEAKER_01": "Abe",
    "SPEAKER_02": "Family interviewer",
    "SPEAKER_03": "Abe",
}


def speaker_at(start, end):
    scores = {}
    for turn in turns:
        overlap = max(0.0, min(end, turn["end"]) - max(start, turn["start"]))
        if overlap:
            scores[turn["speaker"]] = scores.get(turn["speaker"], 0.0) + overlap
    if not scores:
        midpoint = (start + end) / 2
        nearest = min(turns, key=lambda turn: min(abs(midpoint - turn["start"]), abs(midpoint - turn["end"])))
        return names[nearest["speaker"]]
    return names[max(scores, key=scores.get)]


words = []
offset = 0.0
for recording_id in ("R01", "R02"):
    source = json.loads((TAPES / "transcripts-turbo" / f"{recording_id}.json").read_text())
    for segment in source["segments"]:
        for word in segment.get("words", []):
            start = offset + float(word["start"])
            end = offset + float(word["end"])
            words.append(
                {
                    "start": start,
                    "end": end,
                    "word": word["word"],
                    "probability": float(word.get("probability", 1.0)),
                    "speaker": speaker_at(start, end),
                }
            )
    offset += float(recordings[recording_id]["duration_seconds"])

rows = []
current = None
for word in words:
    boundary = current is None or word["speaker"] != current["speaker"]
    if current and word["start"] - current["end"] > 1.2:
        boundary = True
    if current and len(current["text"]) > 260 and re.search(r"[.!?][\"']?$", current["text"].strip()):
        boundary = True
    if boundary:
        if current:
            current["text"] = current["text"].strip()
            current["needs_review"] = current["mean_word_probability"] < 0.72
            del current["word_count"]
            rows.append(current)
        current = {
            "start": round(word["start"], 3),
            "end": round(word["end"], 3),
            "text": word["word"],
            "speaker": word["speaker"],
            "mean_word_probability": word["probability"],
            "word_count": 1,
        }
    else:
        current["text"] += word["word"]
        current["end"] = round(word["end"], 3)
        count = current["word_count"] + 1
        current["mean_word_probability"] = (
            current["mean_word_probability"] * current["word_count"] + word["probability"]
        ) / count
        current["word_count"] = count
if current:
    current["text"] = current["text"].strip()
    current["needs_review"] = current["mean_word_probability"] < 0.72
    del current["word_count"]
    rows.append(current)

payload = {
    "title": "Abe Tabak tapes — Tape 1",
    "duration_seconds": round(offset, 3),
    "speaker_method": (
        "Pyannote Community-1 turn boundaries. Abe's three acoustic clusters were "
        "merged; the remaining cluster is provisionally labeled Family interviewer."
    ),
    "segments": rows,
}
(PILOT / "transcript-speakers.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(f"Wrote {len(rows)} speaker-aligned passages")
