# The Abe Tabak family oral-history archive

This repository preserves, transcribes, and annotates two related collections:

- the July 1988 family-reunion video in which Abraham “Abe” Tabak discusses his early life in Krasnobród, Poland; and
- nine later audio tapes of conversations among Abe, Bella (Rita), Nina, Len, and occasionally Dan.

The public reader combines synchronized media and transcripts with a deliberately simple family-correction interface. The transcripts are working historical documents: machine output is published as a draft, family corrections are incorporated incrementally, and uncertain language remains marked for review.

## Read and review

- [Original July 1988 family video](https://thirtyseven.github.io/abe-tabak-interview/)
- [Tape 1 working transcript](https://thirtyseven.github.io/abe-tabak-interview/tapes/tape-1/)
- [Open work and feature requests](https://github.com/thirtyseven/abe-tabak-interview/issues)

## Current status

| Recording | ASR | Speakers | Web reader | Family review |
| --- | --- | --- | --- | --- |
| Original 1988 video | Published | Partially identified | Published | Ongoing |
| Tape 1 | Generated | Abe and Bella detected | Published | **In progress; many corrections remain** |
| Tapes 2–9 | Baseline generated | Not yet processed | Not yet published | Not started |

The source collection contains 14 audio files because some numbered tapes have multiple tracks. Together they contain about 7.8 hours of audio.

## How family review works

1. Open a tape reader and choose **Correct or annotate** beside a passage.
2. Correct the speaker or transcript and add an optional family note. Changes remain in that browser's local storage.
3. Use **Export corrections (.json)** periodically and keep the downloaded file.
4. Send the export to the repository maintainer. The import script validates it, merges it into the canonical transcript, rebuilds the page, and publishes the result.

Exports are cumulative, so review can happen across many short sessions. Importing and publishing one batch does not mean that a tape is fully reviewed.

## Project organization

- `index.html` and the root transcript files contain the original 1988 video edition.
- `tapes/` contains the published readers and downloadable draft transcripts.
- `transcripts/` contains canonical structured transcript data.
- `review-batches/` contains correction batches that were intentionally retained as project records.
- `pipeline/` contains the reproducible transcription, diarization, import, build, and upload tools.
- [`PROJECT.md`](PROJECT.md) defines scope, statuses, priorities, and the lightweight issue workflow.
- [`AGENTS.md`](AGENTS.md) tells Codex and other coding agents how to coordinate safely in this repository.

## Managing the work

GitHub Issues is the task list. You do not need to maintain a separate product-management system:

- create an issue for a bug, feature, pipeline change, or tape-processing pass;
- use the issue checklist as the acceptance criteria;
- an agent claims an issue before changing code and links the resulting commit or pull request;
- close the issue only after the published result is verified, when publishing is part of the task.

The recording table above is the human-readable overview. Issues contain the implementation detail. Git commit history is the changelog.

## Local development

Python dependencies are listed in `pipeline/requirements.txt`; FFmpeg is also required. Original recordings, model caches, generated working files, OAuth credentials, and browser correction exports remain outside the repository unless deliberately incorporated into the public archive.

See [`pipeline/README.md`](pipeline/README.md) for the current processing stages and known Tape 1-specific code that still needs to be generalized.
