# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

---

## [0.1.2] - 2026-06-10

### Changed

- Restored Lychee link-check workflow.
- Lychee behavior configured through `.github/lychee.toml`.
- Added/updated managed baseline files for `AGENTS.md` guidance.
- Clarified `ALL` versus `ALL-PY` agent instructions.
- Moved Python-specific agent guidance to the `ALL-PY` layer.

### Fixed

- Repo identity fields separated as `github_handle`, `repo_name`, `repo_url`, and `site_url`.
- Removed the combined `owner/repo` value from repository context.
- Moved review surfaces from hard-coded Python constants into packaged TOML data.
- Reduced report maintenance burden using detected buckets.
- Fixed strict typing issues in config loading and validation.

---

## [0.1.1] - 2026-06-06

### Changed

- Release and README.md

---

## [0.1.0] - 2026-06-06

### Added

- Initial `dc-up` command-line package.
- Added dry-run default command: `dc-up`.
- Added write mode: `dc-up --write`.
- Added human review TODO command: `dc-up todo`.
- Added repository detection from the current working directory.
- Added additive template layer inference.
- Added managed-file planning for canonical baseline files.
- Added GitHub raw template fetching from `denisecase/templates`.
- Added optional local template source support.
- Added minimal repository identity token rendering.
- Added conservative write behavior for managed baseline files only.

---

## Notes on Versioning and Releases

- We use **SemVer**:
  - **MAJOR** - breaking changes
  - **MINOR** - backward-compatible additions
  - **PATCH** - fixes, documentation, tooling
- Versions are driven by git tags.
- Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

## Release Procedure

Follow these steps when creating a new release.

### Task 1. Update release metadata

1. Update `CITATION.cff`: change `version` and `date-released`
2. Update `CHANGELOG.md`: move from unreleased, add entry, update links
3. Update `pyproject.toml`: update `[tool.hatch.version] fallback-version`

### Task 2. Validate

````shell
uv lock --upgrade
uv sync --extra dev --extra docs --upgrade
uvx pre-commit install

uv run dc-up
uv run dc-up todo

git add -A
uvx pre-commit run --all-files
# rerun if changes made
uvx pre-commit run --all-files

uv run python -m pytest
uv run python -m pyright
uv run python -m zensical build

uv run python -c "import shutil; from pathlib import Path; shutil.rmtree(Path('dist'), ignore_errors=True)"

uv build
uvx twine check dist/*
```

### Task 4. Commit, push, tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
````

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

## Only As Needed (delete a tag)

```shell
git tag -d vX.Z.Y
git push origin :refs/tags/vX.Z.Y
```

## Links

[Unreleased]: https://github.com/denisecase/dc-up/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/denisecase/dc-up/releases/tag/v0.1.2
[0.1.1]: https://github.com/denisecase/dc-up/releases/tag/v0.1.1
[0.1.0]: https://github.com/denisecase/dc-up/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
