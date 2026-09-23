# Project guide

## Goal

Create a durable, family-usable oral-history archive in which each recording has synchronized media, a readable transcript, conservative speaker labels, and a low-stress way for relatives to submit corrections.

## Product principles

1. **Family evidence wins over confident automation.** ASR and diarization create drafts; they do not settle names, words, or history.
2. **Uncertainty stays visible.** Mark uncertain speakers, wording, translations, and inferred context rather than silently inventing precision.
3. **Review remains simple.** A reviewer should be able to listen, correct, annotate, save locally, and export without an account or backend.
4. **One shared reader.** All numbered tapes should use the same UI and shared assets. Recording-specific data belongs in configuration and transcript files.
5. **Raw material stays private by default.** Publish media only through the agreed hosting workflow. Never commit credentials or local source recordings.
6. **A published draft is still a draft.** “Published” and “family reviewed” are independent statuses.

## Scope

### In scope

- the original July 1988 family video;
- numbered audio Tapes 1–9, including their split source tracks;
- ASR, speaker diarization, transcript alignment, chaptering, and subtitles;
- the static GitHub Pages reader and local-storage correction workflow;
- incremental incorporation of family corrections;
- provenance notes needed to distinguish spoken testimony, family notes, and editorial context.

### Deferred unless requested

- a login system or correction backend;
- training a custom ASR model for only these nine tapes;
- public release of source files or private family notes;
- a large project-management platform or elaborate release process.

## Recording status vocabulary

- **Inventoried:** source tracks and durations are known.
- **ASR generated:** an automatic transcript exists; it may be rough.
- **Speakers added:** diarization has been aligned and obvious identities mapped conservatively.
- **Published draft:** a reader is live and usable for correction.
- **Family review in progress:** at least one relative is reviewing; substantial errors may remain.
- **Family reviewed:** the family explicitly considers a full listening pass complete.
- **Needs follow-up:** unresolved identities, language, timing, or technical problems remain.

Only a family member can move a recording to **Family reviewed**.

## Priority order

1. Keep Tape 1 review reliable and prevent correction loss.
2. Extract the Tape 1 reader into shared assets and a recording-driven build.
3. Build a collection homepage containing the original video and Tapes 1–9 with honest statuses.
4. Process and publish Tape 2 as the first test of the generalized pipeline.
5. Process Tapes 3–9, improving the shared pipeline instead of copying tape-specific code.
6. Continue importing family-review batches throughout the project.

## Issue workflow

GitHub Issues is the source of truth for unfinished work.

1. Use one issue for one independently verifiable result.
2. Put the observable outcome and acceptance checklist in the issue, rather than prescribing every implementation detail.
3. Use title prefixes: `[Site]`, `[Pipeline]`, `[Tape 1]` through `[Tape 9]`, or `[Original video]`.
4. Before starting, an agent comments that it is claiming the issue and states the files or subsystem it expects to touch.
5. Parallel agents should work in separate branches or worktrees and avoid claiming issues that edit the same generated page or shared asset.
6. Link commits or pull requests to the issue. Record durable decisions in this file, the README, code, or the issue—not only in chat.
7. For deployed changes, verify the live GitHub Pages result before closing the issue.

Open means work remains. Closed means its acceptance criteria were met. Labels help filtering but are not a second status system.

## Definition of done

A code or site issue is done when:

- its acceptance criteria are satisfied;
- generated output and source code agree;
- relevant syntax, validation, or pipeline checks pass;
- privacy rules remain intact;
- documentation changes when behavior or workflow changes;
- and the live page is checked when the issue includes deployment.

A tape is not “done” merely because its page is live. Technical publication and family review are tracked separately.

## Decisions already made

- GitHub Pages hosts the static archive.
- YouTube hosts review media; uploads begin private, and Ted changes visibility to unlisted manually.
- Browser corrections use local storage and JSON export rather than a backend.
- Yiddish within English is retained and may be marked typographically; translations and uncertainty belong in notes.
- Speaker labels are conservative. Expected voices include Abe, Bella, Nina, Len, and possibly Dan, but presence varies by tape.
- Git commits and issues record implementation changes; public annotations should discuss the history, not previous transcript editions.
- Numbered tape readers are built from canonical transcript JSON and per-recording
  configuration with shared CSS and JavaScript under `tapes/assets/`. Tape 1 keeps
  its original browser storage key and correction export format.
