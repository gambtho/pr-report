# Project Config — kubernetes-sigs/headlamp

This file is **human-authored** review guidance. The daily review prompt
reads it but never modifies it. Anything you write here overrides anything
the AI has inferred in `learnings.md`.

Use this file for:

- Hard project conventions that should never be flagged
- Commit message / DCO / license header requirements specific to headlamp
- Patterns the AI keeps incorrectly flagging — promote them here from
  `learnings.md` once you're sure they're really conventions and not bugs
- Extra checklist items beyond what the universal/stack-specific checklist
  covers

## Project conventions (do not flag)

<!-- Example entries — delete or replace once real ones land:
- The `backend/` directory uses `slog` for structured logging; do not
  suggest switching to `log/slog` or `logrus`.
- The frontend uses Material-UI v5 patterns; do not suggest migrating
  to a different component library.
- Helm chart values use camelCase by project convention even where
  Kubernetes itself uses kebab-case.
-->

## Commit / PR conventions

<!-- Example:
- Commit subject format: `area: component: description` (e.g.
  `backend: oidc: add characterization tests`).
- DCO sign-off required (`Signed-off-by:` trailer).
- PR description must reference an issue or explain the standalone change.
-->

## Extra checklist items

<!-- Example:
- For any backend change touching auth, verify there is a corresponding
  characterization test.
- Frontend PRs touching component props should include a Storybook update.
-->

## Known false positives

<!-- Things the AI has flagged that are actually intentional. Format:
- {pattern}: {why it's intentional}
-->
