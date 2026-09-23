# Agent instructions

These instructions apply to the entire repository.

## Begin every task

1. Read `README.md`, `PROJECT.md`, and the relevant GitHub issue.
2. Check `git status` and recent commits before editing.
3. If working from an issue, claim it with a brief issue comment that names the expected subsystem or files.
4. Confirm that no other active issue or agent is changing the same generated page or shared reader asset. Use a separate branch or worktree for parallel work.

## Sources of truth

- GitHub Issues: unfinished tasks and acceptance criteria.
- `PROJECT.md`: scope, status definitions, priorities, and durable product decisions.
- `transcripts/`: canonical published structured transcripts.
- `pipeline/`: reproducible tooling.
- generated HTML under `tapes/`: published output, which must be rebuilt from its source rather than hand-edited alone.

If code and generated output differ, fix the generator and rebuild the output in the same change.

## Transcript and historical-content rules

- Treat ASR and diarization as suggestions.
- Preserve meaningful uncertainty and do not guess names or translations.
- Distinguish words spoken in a recording from family notes and editorial context.
- Never mark a tape “Family reviewed” without explicit confirmation from a family member.
- Do not mention prior transcript editions in public annotations. Put implementation history in issues and commits.
- Retain mixed Yiddish/English faithfully; use notes for translation or uncertain spelling.

## Privacy and repository hygiene

- Never commit source recordings, OAuth client secrets, refresh tokens, model caches, or unreviewed private exports.
- Do not print secrets or token contents in logs, issues, or chat.
- Upload media as private through the established YouTube workflow. The owner changes visibility manually.
- Inspect family correction exports before deciding whether they belong in `review-batches/`; canonical merged data belongs in `transcripts/`.
- Keep transient files and Python caches out of commits.

## Implementation expectations

- Prefer shared reader assets and recording configuration over copied tape-specific code.
- Keep the correction interface simple and usable for a reviewer who is uncomfortable with complex software.
- Preserve correction-export compatibility or provide an explicit migration.
- Test the source generator, generated output, and important browser behavior appropriate to the change.
- For GitHub Pages changes, publish and verify the live page before reporting completion.
- Update the README or `PROJECT.md` when changing workflow, status meanings, privacy boundaries, or architecture.

## Finishing a task

1. Review the diff and run relevant checks.
2. Commit with a concrete description of the resulting behavior.
3. Link the commit or pull request in the issue.
4. Verify deployed behavior when applicable.
5. Close the issue only when every acceptance criterion is met; otherwise leave a concise status comment describing what remains.
