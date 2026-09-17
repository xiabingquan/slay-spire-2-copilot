# doctor.md — Documentation Health Check

A checklist for keeping this repository's documentation where it belongs. The
agent executes it against the working tree: walk every section, report
violations with file paths, then fix what the rules settle unambiguously.

## How to run

Ask the agent in the current session to execute this checklist, e.g.:

    run doctor.md

The agent goes through each check below and, for every violation:

- **relocates or deletes** content that clearly breaks a rule — e.g. run
  residue inside `references/game/` is deleted, run memory found outside
  `memory/runs/` is moved into the matching runs note;
- **reports, without touching**, anything ambiguous (frozen-file edits,
  borderline README wording) so the user decides.

## When to run

- **After a run ends**, once the run's memory note has been written — catches
  notes that landed outside `memory/runs/` and overview drift.
- **Before committing any documentation change.**
- **Whenever the layout looks off** — a markdown file appeared in a code
  directory, a reference doc mentions a date, etc.

Do not run it mid-run for reorganization; mid-run the only applicable check is
that additions to `references/game/` stay static (check 4).

## Checks

### 1. README is a project overview only

Files: `README.md`, `README_EN.md`

Rule: the READMEs describe what the project is, how the repository is laid
out, and how to load the skill. They must not contain skill-run content — no
play narratives, run dates, per-run outcomes, lessons learned, or experience
notes. That material belongs in the skill's `memory/` (check 3) or, if static,
in `references/`.

Violation → move the material into the appropriate `memory/runs/` note (or
drop it if it duplicates one) and restore overview-only wording.

### 2. mod/ and bridge/ are code-only

Paths: `slay-spire-2-copilot/mod/`, `slay-spire-2-copilot/bridge/`

Rule: these are code directories — the in-game communication mod and the
`spirectl` CLI. They must not hold documentation or any other non-code
content: no stray `.md` notes, design write-ups, or run logs.

Violation → delete if redundant; otherwise relocate: bridge/mod development
notes → `references/bridge/` or `proposal.md`; run narratives →
`memory/runs/`.

### 3. memory/ and references/ have separate duties

`memory/` records what happened in runs; `references/` holds material the
agent consults while playing. Content never crosses between them.

#### 3a. Per-run memory lives only in memory/runs/

All run memory is written to the run's own markdown file(s) under
`slay-spire-2-copilot/memory/runs/` — and nowhere else. Not in
`references/`, not in `SKILL.md`, not in the READMEs, not in `mod/`,
`bridge/`, or `scripts/`.

Violation → move the content into the matching `memory/runs/` note, then
remove it from the wrong location.

#### 3b. template.md and user guide.md are frozen mid-run

`memory/template.md` and `memory/user guide.md` define how run notes are
recorded. They must not be modified while a run is in progress.

Violation → revert the mid-run edit; surface the proposed change to the user
instead of keeping it.

#### 3c. overview.md is post-run and meta-only

`memory/overview.md` is updated only after a run ends, and records only the
run's meta information (the overview table — character, outcome, scoring).
No narrative, no lessons.

Violation → move narrative content into that run's `memory/runs/` note; keep
`overview.md` down to the meta table.

### 4. references/game/ is static reference material

Files: `slay-spire-2-copilot/references/game/*.md` — EN and `_zh` pairs for
cards, relics, powers, potions, afflictions, monsters, events, intents, and
characters.

Rule: these are static reference docs consulted mid-run. They may be edited
during a run, but only with static descriptive content (a relic's effect, a
monster's behavior, a card's wording). They must not contain run records,
dates, or session notes.

Violation → delete the run-specific content; it belongs in `memory/runs/`,
not here.
