# Transcription pipeline

This directory versions the scripts used to inventory, transcribe, diarize, align,
render, and upload the Abe Tabak recordings. The published HTML lives elsewhere in
this repository because GitHub Pages serves the repository root.

The scripts are currently organized around the Tape 1 pilot and its working-data
layout. They document the exact process used for the published pilot; subsequent
tapes should generalize the Tape 1-specific entry points rather than duplicating
them.

## Main stages

1. `transcribe_collection.py` runs Whisper large-v3-turbo with word timestamps.
2. `benchmark_yiddish.py` compares a Yiddish-focused Whisper model on a sample.
3. `diarize_tape1.py` runs Pyannote Community-1 speaker diarization.
4. `tag_tape1_segments.py` aligns diarization with transcript passages.
5. `build_tape1_reader.py` builds the interactive transcript and correction UI.
6. `upload_private_youtube.py` uploads an archival video as private through the
   YouTube Data API.

## Local-only inputs

Recordings, extracted audio, generated transcripts, model caches, OAuth client
secrets, and refresh tokens must stay outside Git. The scripts in this snapshot
refer to the adjacent working tree used for the pilot. Before making this a
portable batch pipeline, replace the remaining Tape 1 paths with command-line
arguments and a data directory outside the repository.

Python dependencies are recorded in `requirements.txt`. FFmpeg is also required.

