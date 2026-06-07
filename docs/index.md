# dc-up

`dc-up` brings a repository up to a managed baseline.

It is designed for repositories that follow repeatable professional patterns
but still contain local, project-specific work.
The tool updates shared repository infrastructure from canonical templates
while preserving source code, tests, notebooks, data, documentation,
and other project-specific surfaces unless those areas are explicitly managed.

## Purpose

Many repositories share the same infrastructure:

* editor and Git configuration
* ignore and line-ending rules
* Markdown, YAML, and link-checking configuration
* Python tooling configuration
* documentation tooling configuration
* continuous integration workflows
* release and package validation surfaces

Keeping those files synchronized by hand is error-prone.
`dc-up` makes the shared parts explicit, repeatable, and reviewable.

## Design Model

`dc-up` separates repository maintenance into three concerns:

1. **Canonical templates** define the standard files and managed content.
2. **Repository conventions** identify the target repository shape and applicable template layers.
3. **Repository-specific surfaces** remain local to the project and require human review.

The tool is intentionally conservative.
It should update files that are known to be managed and report
the areas that require human judgment.

## Template Layers

Templates are applied as ordered layers.
Later layers may override files from earlier layers.

The standard layer model is:

* `ALL` for files shared by all repositories.
* `ALL-PY` for Python repository tooling.
* `ALL-PY-SRC` for Python repositories with a `src/` package layout.
* `ALL-PY-PYPI` for Python packages released to PyPI.
* `ALL-PY-NB` for notebook-centered Python repositories.
* `ALL-PY-KAFKA` for Kafka or streaming-data Python repositories.
* `ALL-TS` for TypeScript repositories.
* `ALL-TS-VSCODE` for VS Code extension repositories.

This keeps the baseline additive instead of duplicative.

## Managed and Preserved Surfaces

A managed surface is a file or section that can be updated from the canonical baseline.

A preserved surface is project-specific and
should not be overwritten automatically.
Examples include source code, tests, notebooks, data files,
SQL files, and module-specific documentation.

When a file contains both repeated and project-specific material,
the long-term model is to manage only marked sections and
leave the rest under local ownership.

## Human Review

`dc-up` is a way to make routine repository maintenance visible and repeatable.

The tool should answer:

* what would change
* what was changed
* which template layer supplied each managed file
* which project-specific surfaces were preserved
* what still requires human review

This supports fast repository modernization without hiding authority,
overwriting local work, or scattering repeated instructions
across many repositories.

## Relationship to Accountability Surfaces

Accountability surface manifests describe
authority boundaries inside a repository.
They identify which files are managed infrastructure,
which files are generated, which files are public contracts,
and which files require human review.

`dc-up` can use these declarations to make safer decisions
about what to update, what to preserve, and what to report.

The template repository defines the canonical content.
The target repository defines its local work.
Accountability surfaces define the authority boundary between them.

## Long-Term Goal

The goal of `dc-up` is to make repository maintenance boring.

A maintainer should be able to open one repository,
bring the shared infrastructure up to the current baseline,
review the remaining project-specific work,
and continue working on the actual course, package, or software artifact.
