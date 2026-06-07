# dc-up

[![PyPI](https://img.shields.io/pypi/v/dc-up?logo=pypi&label=pypi)](https://pypi.org/project/dc-up/)
[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://denisecase.github.io/dc-up/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/denisecase/dc-up)
[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![Python 3.14 Ready](https://github.com/denisecase/dc-up/actions/workflows/python-315-ready.yml/badge.svg?branch=main)](https://github.com/denisecase/dc-up/actions/workflows/python-315-ready.yml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI](https://github.com/denisecase/dc-up/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/denisecase/dc-up/actions/workflows/ci-python-zensical.yml)
[![Docs-Deploy](https://github.com/denisecase/dc-up/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/denisecase/dc-up/actions/workflows/deploy-zensical.yml)
[![Pre-Release](https://github.com/denisecase/dc-up/actions/workflows/pre-release.yml/badge.svg?branch=main)](https://github.com/denisecase/dc-up/actions/workflows/pre-release.yml)
[![Release](https://github.com/denisecase/dc-up/actions/workflows/release-pypi.yml/badge.svg)](https://github.com/denisecase/dc-up/actions/workflows/release-pypi.yml)
[![Links](https://github.com/denisecase/dc-up/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/denisecase/dc-up/actions/workflows/links.yml)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-brightgreen.svg)](https://github.com/denisecase/dc-up/security)

> Structural Explainability (SE) Manifest Schema

This repository defines the canonical `SE_MANIFEST.toml` schema
for the Structural Explainability ecosystem.

## Update a Repo based on Templates

```shell
uvx dc-up
uvx dc-up --write
```

## Developer Command Reference

<details>
<summary>Show command reference</summary>

### In a machine terminal

Open a machine terminal where you want the project:

```shell
git clone https://github.com/denisecase/dc-up

cd dc-up
code .
```

### In a VS Code terminal

```shell
uv self update
uv python pin 3.14
uv lock --upgrade
uv sync --extra dev --extra docs --upgrade

uvx pre-commit install

git add -A
uvx pre-commit run --all-files
# repeat if changes were made
uvx pre-commit run --all-files

# repo-specific
uv run dc-up
uv run dc-up --write

# types, tests, docs
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

</details>

## Annotations

[.annotations/annotations.md](./.annotations/annotations.md)

## Authority Manifest

[.accountability/surfaces.toml](./.accountability/surfaces.toml)

## Citation

[CITATION.cff](./CITATION.cff)

## License

[MIT](./LICENSE)
