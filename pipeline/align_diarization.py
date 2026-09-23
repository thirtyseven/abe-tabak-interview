"""Align an ASR draft with Pyannote turns and emit canonical reader data.

The input transcript is expected to contain continuous-time ``segments``. Speaker
cluster identities are supplied explicitly; unmapped clusters remain unidentified.
Obvious high-compression repetition is collapsed into a review marker rather than
published as though it were spoken testimony.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def overlap(left, right):
    return max(0.0, min(left["end"], right["end"]) - max(left["start"], right["start"]))


def normalized(text):
    return re.sub(r"[^a-z0-9']+", " ", text.lower()).strip()


def align_segment(segment, turns, names):
    scores = Counter()
    for turn in turns:
        amount = overlap(segment, turn)
        if amount:
            scores[turn["speaker"]] += amount
    if not scores:
        return "Unclear speaker", 0.0
    ranked = scores.most_common()
    total = sum(scores.values())
    cluster, best = ranked[0]
    confidence = best / total if total else 0.0
    second = ranked[1][1] / total if len(ranked) > 1 and total else 0.0
    if confidence < 0.6 or second >= 0.35:
        return "Multiple speakers", confidence
    return names.get(cluster, f"Unidentified {cluster.replace('_', ' ').title()}"), confidence


def collapse_hallucinations(rows):
    output = []
    index = 0
    while index < len(rows):
        row = rows[index]
        reasons = set(row.get("review_reasons", []))
        text_key = normalized(row["text"])
        run = [row]
        cursor = index + 1
        while cursor < len(rows):
            candidate = rows[cursor]
            if (
                normalized(candidate["text"]) == text_key
                and candidate["start"] - run[-1]["end"] < 3
                and "high_compression" in candidate.get("review_reasons", [])
            ):
                run.append(candidate)
                cursor += 1
            else:
                break
        obvious = "high_compression" in reasons and "repetitive_text" in reasons
        if obvious or len(run) >= 3:
            output.append(
                {
                    **row,
                    "end": run[-1]["end"],
                    "text": "[Automatic transcript unreliable; check audio.]",
                    "needs_review": True,
                    "review_reasons": sorted(reasons | {"probable_asr_hallucination"}),
                }
            )
            index = cursor
        else:
            output.append(row)
            index += 1
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path)
    parser.add_argument("diarization", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--speaker-map", action="append", default=[], metavar="CLUSTER=NAME")
    args = parser.parse_args()

    names = dict(item.split("=", 1) for item in args.speaker_map)
    transcript = json.loads(args.transcript.read_text())
    diarization = json.loads(args.diarization.read_text())
    rows = []
    for source in transcript["segments"]:
        speaker, speaker_confidence = align_segment(source, diarization["turns"], names)
        reasons = list(source.get("review_reasons", []))
        rows.append(
            {
                "start": source["start"],
                "end": source["end"],
                "text": source["text"],
                "speaker": speaker,
                "source_track": source.get("source_recording") or source.get("source_track"),
                "source_start": source.get("source_start"),
                "confidence": source.get("asr", {}).get("avg_logprob"),
                "needs_review": bool(reasons) or speaker.startswith("Unidentified") or speaker == "Multiple speakers",
                "speaker_confidence": round(speaker_confidence, 4),
                "review_reasons": reasons,
            }
        )
    rows = collapse_hallucinations(rows)

    sources = [
        {
            "track_number": item["track_number"],
            "track": item["source_name"],
            "start": item["start"],
            "end": item["end"],
            "duration_seconds": item["duration"],
        }
        for item in transcript.get("source_timeline", [])
    ]
    payload = {
        "title": args.title,
        "duration_seconds": transcript["duration"],
        "sources": sources,
        "method": "Continuous timeline assembled from supplied tracks. Draft recognition uses Whisper large-v3-turbo; obvious repetitive recognition failures are replaced with review markers.",
        "speaker_method": "Provisional Pyannote Community-1 labels using automatic speaker counting. Only the stable Abe cluster is identified; other clusters remain unidentified pending family review.",
        "segments": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {args.output}: {len(rows)} passages")


if __name__ == "__main__":
    main()
