"""Merge a browser correction export into the reviewed transcript JSON."""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corrections", type=Path)
    parser.add_argument("transcript", type=Path)
    args = parser.parse_args()

    export = json.loads(args.corrections.read_text())
    transcript = json.loads(args.transcript.read_text())
    if export.get("format") != "abe-tabak-family-corrections-v1":
        raise SystemExit("Unrecognized correction-export format")
    edits = export.get("corrections")
    if not isinstance(edits, list):
        raise SystemExit("Correction export has no corrections list")

    rows = {round(float(row["start"]), 3): row for row in transcript["segments"]}
    applied = []
    for edit in edits:
        key = round(float(edit["start"]), 3)
        if key not in rows:
            raise SystemExit(f"No transcript passage starts at {key:.3f}")
        row = rows[key]
        if abs(float(row["end"]) - float(edit["end"])) > 0.01:
            raise SystemExit(f"End time differs for passage at {key:.3f}")
        row["speaker"] = edit["speaker"].strip()
        row["text"] = edit["text"].strip()
        note = edit.get("note", "").strip()
        if note:
            row["family_note"] = note
        else:
            row.pop("family_note", None)
        row["family_reviewed"] = True
        row["family_reviewed_at"] = edit.get("updated_at") or export.get("exported_at")
        applied.append(key)

    transcript["family_corrections_format"] = export["format"]
    transcript["family_corrections_last_imported"] = export.get("exported_at")
    args.transcript.write_text(json.dumps(transcript, ensure_ascii=False, indent=2) + "\n")
    print(f"Applied {len(applied)} corrections to {args.transcript}")


if __name__ == "__main__":
    main()
