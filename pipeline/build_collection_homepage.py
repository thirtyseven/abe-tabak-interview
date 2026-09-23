"""Build the collection homepage from site/collection.json.

Run from anywhere: python3 pipeline/build_collection_homepage.py
"""

import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "collection.json"
TEMPLATE = ROOT / "site" / "collection_template.html"
OUTPUT = ROOT / "index.html"
STATUS_FIELDS = ("asr", "speakers", "publication", "family_review")
STATUS_LABELS = ("ASR", "Speakers", "Reader", "Family review")


def esc(value):
    return html.escape(str(value), quote=True)


def status_grid(record):
    return "".join(
        f'<div><dt>{label}</dt><dd>{esc(record[field])}</dd></div>'
        for field, label in zip(STATUS_FIELDS, STATUS_LABELS)
    )


def card(record, image, href):
    return (
        f'<article class="feature {esc(record["art"])}">'
        f'<div class="feature-art">{image}</div>'
        '<div class="feature-content">'
        f'<p class="eyebrow">{esc(record["period"])}</p>'
        f'<h3>{esc(record["title"])}</h3>'
        f'<p class="feature-summary">{esc(record["summary"])}</p>'
        f'<dl class="status-grid">{status_grid(record)}</dl>'
        f'<a class="reader-link" href="{esc(href)}">Open {esc(record["label"])} <span aria-hidden="true">↗</span></a>'
        '</div></article>'
    )


def build():
    data = json.loads(DATA.read_text())
    featured = data["featured"]
    upcoming = data["upcoming"]
    numbers = [record["number"] for record in featured if record.get("art") == "audio"] + upcoming["numbers"]
    if sorted(numbers) != list(range(1, 10)) or sum(record.get("art") == "video" for record in featured) != 1:
        raise ValueError("Collection must include the original video and each tape exactly once")
    for record in (*featured, upcoming):
        for field in STATUS_FIELDS:
            if not record.get(field):
                raise ValueError(f"Missing {field} status")
    cards = []
    for record in featured:
        if record["art"] == "video":
            href = record["reader"]
            if not (ROOT / href).is_file():
                raise ValueError("Original interview reader is missing")
            image = '<img src="site/original-still.jpg" alt="Abe Tabak in the July 1988 interview" width="480" height="360">'
        elif record["art"] == "audio":
            recording_config = (ROOT / record["recording_config"]).resolve()
            reader_config = json.loads(recording_config.read_text())
            tape_output = (recording_config.parent / reader_config["output"]).resolve()
            if not tape_output.is_file():
                raise ValueError(f"Tape {record['number']} reader is missing")
            href = tape_output.parent.relative_to(ROOT).as_posix() + "/"
            image = (
                '<div class="audio-art" aria-hidden="true">'
                f'<span>TAPE <b>{record["number"]:02}</b></span>'
                + '<i></i>' * 12
                + f'<small>VOICE ARCHIVE{(" • " + esc(record["duration"])) if record.get("duration") else ""}</small></div>'
            )
        else:
            raise ValueError(f"Unknown feature art: {record['art']}")
        cards.append(card(record, image, href))
    rows = "".join(
        '<tr>'
        f'<th scope="row"><span class="tape-number">{number:02}</span><span>Tape {number}</span></th>'
        f'<td data-label="ASR">{esc(upcoming["asr"])}</td>'
        f'<td data-label="Speakers">{esc(upcoming["speakers"])}</td>'
        f'<td data-label="Reader">{esc(upcoming["publication"])}</td>'
        f'<td data-label="Family review">{esc(upcoming["family_review"])}</td>'
        '</tr>'
        for number in upcoming["numbers"]
    )
    upcoming_title = f'Tapes {min(upcoming["numbers"])}–{max(upcoming["numbers"])}'
    page = Template(TEMPLATE.read_text()).substitute(featured="".join(cards), upcoming_rows=rows, upcoming_title=upcoming_title)
    OUTPUT.write_text(page)
    print(f"Wrote {OUTPUT} (original interview and Tapes 1–9)")


if __name__ == "__main__":
    build()
