# The Abe Tabak family oral-history archive

This repository preserves, transcribes, and annotates two related collections:

- the July 1988 family-reunion video in which Abraham “Abe” Tabak discusses his early life in Krasnobród, Poland; and
- nine later audio tapes of conversations among Abe, Bella (Rita), Nina, Len, and occasionally Dan.

The public reader combines synchronized media and transcripts with a deliberately simple family-correction interface. The transcripts are working historical documents: machine output is published as a draft, family corrections are incorporated incrementally, and uncertain language remains marked for review.

## Read and review

- [Collection homepage](https://thirtyseven.github.io/abe-tabak-interview/)
- [Original July 1988 family video](https://thirtyseven.github.io/abe-tabak-interview/Abe_Tabak_interview.html)
- [Tape 1 working transcript](https://thirtyseven.github.io/abe-tabak-interview/tapes/tape-1/)
- [Open work and feature requests](https://github.com/thirtyseven/abe-tabak-interview/issues)

## Current status

The [collection homepage](https://thirtyseven.github.io/abe-tabak-interview/) lists
the ASR, speaker, reader, and family-review status of each recording. Its source
is [`site/collection.json`](site/collection.json). Tape 1 remains a working draft
under family review; a published reader does not mean that review is complete.

The source collection contains 14 audio files because some numbered tapes have multiple tracks. Together they contain about 7.8 hours of audio.

## How family review works

1. Open a tape reader and choose **Correct or annotate** beside a passage.
2. Correct the speaker or transcript and add an optional family note. The text editor includes clickable Polish place names that insert at the cursor. Changes remain in that browser's local storage.
3. Use **Export transcript for Word (.rtf)** to download the latest transcript, including corrections saved in that browser, for reading or editing in Microsoft Word. Use **Export corrections (.json)** periodically and keep the downloaded file to share corrections with the repository maintainer.
4. Send the correction export (.json) to the repository maintainer. The import script validates it, merges it into the canonical transcript, rebuilds the page, and publishes the result.

Exports are cumulative, so review can happen across many short sessions. Importing and publishing one batch does not mean that a tape is fully reviewed.

## Project organization

- `index.html` is the generated collection homepage. `Abe_Tabak_interview.html`
  preserves the original 1988 video reader; the root transcript files accompany it.
- `site/` contains the homepage source data, template, stylesheet, and existing
  interview still used on the homepage.
- `tapes/` contains the published readers and downloadable draft transcripts.
- `transcripts/` contains canonical structured transcript data.
- `recordings/` contains per-recording reader configuration, including media IDs,
  chapters, speaker choices, and browser storage keys.
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

See [`pipeline/README.md`](pipeline/README.md) for processing stages and the
recording-driven reader build.
