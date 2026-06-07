# Decisions

This file records project design decisions.

---

## 2026-06-06: Separate template content from the update engine

This repo holds the update engine.
The canonical managed files live in a separate `denisecase/templates` repository.

This keeps the responsibilities separate:

- `denisecase/templates` defines the managed baseline content.
- This repo detects repository shape, fetches template layers,
  plans changes, applies managed updates, and reports project-specific work.

This allows template content to evolve without
requiring a new `dc-up` package release for every baseline file change.

---

## 2026-06-06: Use additive template layers

Template content is organized into additive layers.
Later layers may override earlier layers.

The initial layer model is:

- `ALL`
- `ALL-PY`
- `ALL-PY-SRC`
- `ALL-PY-PYPI`
- `ALL-PY-NB`
- `ALL-PY-KAFKA`
- `ALL-TS`
- `ALL-TS-VSCODE`

This avoids course-specific template duplication
while still allowing different repository shapes
to receive appropriate managed files.

---

## 2026-06-06: Default to dry-run behavior

`dc-up` should show the planned changes by default.

Writing changes requires explicit write mode.
This is important because the tool modifies repository files
and must make managed updates reviewable before applying them.

---

## 2026-06-06: Preserve project-specific work by default

`dc-up` should not overwrite source code, tests, notebooks,
data, SQL, or project-specific documentation by default.

The tool may update known managed files and, later,
explicitly marked managed sections.
Ambiguous content should be preserved and reported as human-review work.

---

## 2026-06-06: Keep repo identity mostly convention-based

Normal repositories should not need repetitive
local configuration just to use `dc-up`.

The tool should infer common repository facts
from the current repository name and files when possible.
Local configuration should be reserved for exceptions,
overrides, or pinned baseline refs.
