"""Build a static reader from a recording config and canonical transcript.

Usage: python3 pipeline/build_reader.py recordings/tape-1.json
       python3 pipeline/build_reader.py pipeline/fixtures/recording.json --output work/reader-fixture/index.html
"""

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "tapes" / "assets"


def timestamp(value):
    value = int(value)
    return f"{value // 3600:02}:{value // 60 % 60:02}:{value % 60:02}"


def escaped(value):
    return html.escape(str(value), quote=True)


def inline_text(value):
    """Render the correction editor's existing *term* convention."""
    parts = escaped(value).split("*")
    return "".join(f"<em>{part}</em>" if index % 2 else part for index, part in enumerate(parts))


def render_rows(rows, chapters):
    article = []
    current = None
    for row in rows:
        start = float(row["start"])
        chapter = max((index for index, item in enumerate(chapters) if item["start"] <= start), default=0)
        if chapter != current:
            if current is not None:
                article.append("</section>")
            current = chapter
            heading = chapters[chapter]
            article.append(
                f'<section class="chapter" id="chapter-{chapter}"><h2><small>{timestamp(heading["start"])}</small>{escaped(heading["title"])}</h2>'
            )
        review = " review" if row.get("needs_review") else ""
        badge = '<span class="badge">Check audio</span>' if row.get("needs_review") else ""
        speaker = escaped(row.get("speaker") or "Unclear speaker")
        family_note = str(row.get("family_note") or "").strip()
        note = f'<span class="editorial-note">Family note: {escaped(family_note)}</span>' if family_note else ""
        article.append(
            f'<div class="utterance{review}" data-key="{start:.3f}" data-start="{start}" data-end="{float(row["end"])}">'
            f'<button class="stamp" data-seek="{start}">{timestamp(start)}</button>'
            f'<div class="utterance-main"><p>{badge}<strong class="speaker">{speaker}:</strong> '
            f'<span class="transcript-text">{inline_text(row["text"])}</span>{note}</p>'
            '<button class="edit-toggle" type="button">Correct or annotate</button></div></div>'
        )
    if current is not None:
        article.append("</section>")
    return "".join(article)


def build(config_path, output_override=None):
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text())
    for field in ("title", "eyebrow", "heading", "description", "notice", "media_title", "media_id", "speakers", "chapters", "annotations", "storage_key", "player_size_key", "export_recording", "export_filename", "transcript"):
        if field not in config:
            raise ValueError(f"Missing recording configuration: {field}")
    transcript_path = (config_path.parent / config["transcript"]).resolve()
    transcript = json.loads(transcript_path.read_text())
    rows = transcript["segments"]
    if not rows or not config["chapters"] or config["chapters"][0]["start"] != 0:
        raise ValueError("Reader needs transcript passages and chapters beginning at zero")
    if output_override:
        output = Path(output_override).resolve()
    elif config.get("output"):
        output = (config_path.parent / config["output"]).resolve()
    else:
        raise ValueError("Pass --output or set output in recording configuration")
    output.parent.mkdir(parents=True, exist_ok=True)
    asset_base = Path(os.path.relpath(ASSETS, output.parent)).as_posix()
    reader_js = ASSETS / "reader.js"
    js_url = asset_base + "/reader.js?v=" + hashlib.sha256(reader_js.read_bytes()).hexdigest()[:12]
    nav = "".join(
        f'<a href="#chapter-{index}" data-seek="{item["start"]}"><time>{timestamp(item["start"])}</time>{escaped(item["title"])}</a>'
        for index, item in enumerate(config["chapters"])
    )
    notes = "".join(f'<h3>{escaped(item["title"])}</h3><p>{escaped(item["text"])}</p>' for item in config["annotations"])
    runtime = {key: config[key] for key in ("media_id", "speakers", "storage_key", "player_size_key", "export_recording", "export_filename")}
    # Escape '<' so config text cannot terminate the JSON script element.
    runtime_json = json.dumps(runtime, ensure_ascii=False).replace("<", "\\u003c")
    page = Template((Path(__file__).parent / "reader_template.html").read_text()).substitute(
        title=escaped(config["title"]), eyebrow=escaped(config["eyebrow"]), heading=escaped(config["heading"]),
        description=escaped(config["description"]), notice=escaped(config["notice"]),
        media_title=escaped(config["media_title"]), media_id=escaped(config["media_id"]),
        css=escaped(asset_base + "/reader.css"), js=escaped(js_url),
        nav=nav, rows=render_rows(rows, config["chapters"]), notes=notes, runtime_json=runtime_json,
    )
    output.write_text(page)
    print(f"Wrote {output} ({len(rows)} passages)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, nargs="?", default=ROOT / "recordings" / "tape-1.json")
    parser.add_argument("--output", type=Path, help="Override the configured output path")
    args = parser.parse_args()
    build(args.config, args.output)
