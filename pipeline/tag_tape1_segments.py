import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "work" / "tapes" / "pilot-tape1"
payload = json.loads((PILOT / "transcript.json").read_text())
turns = json.loads((PILOT / "diarization-auto.json").read_text())["turns"]

speaker_name = {
    "SPEAKER_00": "Bella",
    "SPEAKER_01": "Abe",
}

for row in payload["segments"]:
    overlap = Counter()
    for turn in turns:
        amount = max(0.0, min(row["end"], turn["end"]) - max(row["start"], turn["start"]))
        if amount:
            overlap[speaker_name[turn["speaker"]]] += amount
    if not overlap:
        row["speaker"] = "Unclear speaker"
        row["speaker_confidence"] = 0.0
        continue
    total = sum(overlap.values())
    speaker, amount = overlap.most_common(1)[0]
    dominance = amount / total
    row["speaker"] = speaker if dominance >= 0.68 else "Multiple speakers"
    row["speaker_confidence"] = round(dominance, 3)

payload["speaker_method"] = (
    "Provisional Pyannote Community-1 labels using automatic speaker counting. The model "
    "found one stable Abe cluster and one interviewer cluster identified by the family as "
    "Bella. Mixed passages are labeled Multiple speakers."
)
(PILOT / "transcript-speakers.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
)
print(Counter(row["speaker"] for row in payload["segments"]))
