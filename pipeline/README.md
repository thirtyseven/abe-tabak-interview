# Transcription pipeline

This directory versions the scripts used to inventory, transcribe, diarize, align,
render, and upload the Abe Tabak recordings. GitHub Pages serves the generated
reader from `tapes/`.

## Main stages

1. `transcribe_collection.py` runs Whisper large-v3-turbo with word timestamps.
2. `benchmark_yiddish.py` compares a Yiddish-focused Whisper model on a sample.
3. `diarize_tape1.py` runs Pyannote Community-1 speaker diarization.
4. `tag_tape1_segments.py` aligns diarization with transcript passages.
5. `import_family_corrections.py` validates and merges an exported family-review
   batch into the canonical transcript.
6. `build_reader.py` builds a reader from recording configuration and canonical
   transcript data. `build_tape1_reader.py` remains a compatible Tape 1 command.
7. `upload_private_youtube.py` uploads an archival video as private through the
   YouTube Data API.

## Rebuild readers

From the repository root:

```sh
python3 pipeline/build_reader.py recordings/tape-1.json
python3 pipeline/build_reader.py pipeline/fixtures/recording.json --output work/reader-fixture/index.html
```

The first command reads `transcripts/tape-1.json` and writes the published
`tapes/tape-1/index.html`. The second builds a small synthetic recording in an
ignored working directory, proving that the same template and assets accept a
different media ID, speaker list, chapters, transcript, and storage key. The
fixture media ID is deliberately not a real video. To add another recording,
create a config following `recordings/tape-1.json`, point `transcript` at its
canonical JSON, and set its published `output` path. Paths in a config are
relative to that config file. `--output` overrides the configured output.

`pipeline/reader_template.html`, `tapes/assets/reader.css`, and
`tapes/assets/reader.js` are the shared interface source. Each generated page
contains recording-specific HTML and a small JSON configuration for the shared
JavaScript. Build and commit source files and generated HTML together. Tape 1's
storage key (`abe-tabak-tape1-corrections-v1`), export format
(`abe-tabak-family-corrections-v1`), filename, and media ID are retained so
existing browser corrections and export files continue to work.

## Rebuild the collection homepage

From the repository root, run `python3 pipeline/build_collection_homepage.py`.
It reads `site/collection.json` and `site/collection_template.html`, then writes
the published root `index.html`. The homepage stylesheet and the original
interview still are in `site/`. The original video reader remains unchanged at
`Abe_Tabak_interview.html`.

Collection status labels live only in `site/collection.json`. Published audio
reader links are derived from each recording's config `output` path, so a live
card cannot point to a missing reader. Move a tape number from `upcoming.numbers`
to `featured` only when its reader is ready to publish; then rebuild and commit
the homepage and source data together. The builder checks that the original
video and every numbered tape appear exactly once.

Reviewed transcript data is committed under `transcripts/`. Original browser
exports remain in local archival storage because they may contain private family
notes; Git history records the resulting published changes. Recordings, working
transcripts, model caches, OAuth secrets, and refresh tokens stay outside Git.
Python dependencies are recorded in `requirements.txt`; FFmpeg is also required.
