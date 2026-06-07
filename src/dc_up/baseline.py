"""Baseline layer inference and managed file declarations."""

from pathlib import Path
import tomllib
from typing import cast

__all__ = [
    "MANAGED_FILES",
    "PRESERVE_PATTERNS",
    "infer_layers",
]

TomlTable = dict[str, object]

COURSE_PREFIXES: tuple[str, ...] = (
    "datafun-",
    "streaming-",
    "cintel-",
    "nlp-",
)

MANAGED_FILES: tuple[str, ...] = (
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".markdownlint-cli2.yaml",
    ".pre-commit-config.yaml",
    "LICENSE",
    "shape.ps1",
    "zensical.toml",
    ".github/.yamllint.yml",
    ".github/dependabot.yml",
    ".github/lychee.toml",
    ".github/workflows/links.yml",
    ".vscode/extensions.json",
    "docs/index.md",
    "docs/project-instructions.md",
    "docs/your-files.md",
    "docs/api.md",
)


PRESERVE_PATTERNS: tuple[str, ...] = (
    "README.md",
    "docs/**",
    "src/**",
    "tests/**",
    "notebooks/**",
    "data/**",
    "sql/**",
    "artifacts/**",
)


def infer_layers(
    *,
    repo_root: Path,
    repo_slug: str,
    files: set[str],
) -> list[str]:
    """Infer additive template layers for a repository."""
    normalized_slug = repo_slug.lower()

    if "package.json" in files and "pyproject.toml" not in files:
        layers = ["ALL", "ALL-TS"]
    elif "notebook" in normalized_slug or normalized_slug.endswith("-notebooks"):
        layers = ["ALL", "ALL-PY", "ALL-PY-NB"]
    elif "kafka" in normalized_slug:
        layers = ["ALL", "ALL-PY", "ALL-PY-KAFKA"]
    elif normalized_slug == "dc-up" or _looks_like_pypi_package(repo_root):
        layers = ["ALL", "ALL-PY", "ALL-PY-SRC", "ALL-PY-PYPI"]
    else:
        layers = ["ALL", "ALL-PY", "ALL-PY-SRC"]

    if _looks_like_course_repo(repo_slug=repo_slug, files=files):
        layers.append("ALL-COURSE")

    return layers


def _has_console_scripts(project: TomlTable) -> bool:
    """Return whether project metadata declares console scripts."""
    scripts = _as_string_dict(project.get("scripts"))
    if scripts:
        return True

    entry_points = _as_table(project.get("entry-points"))
    console_scripts = _as_string_dict(entry_points.get("console_scripts"))

    return bool(console_scripts)


def _read_toml(path: Path) -> TomlTable:
    """Read a TOML file as typed object data."""
    with path.open("rb") as file:
        return cast(TomlTable, tomllib.load(file))


def _as_table(value: object) -> TomlTable:
    """Return value as a TOML table or an empty table."""
    if isinstance(value, dict):
        return cast(TomlTable, value)
    return {}


def _as_string_list(value: object) -> list[str]:
    """Return value as a list of strings."""
    if not isinstance(value, list):
        return []

    return [str(item) for item in cast(list[object], value)]


def _as_string_dict(value: object) -> dict[str, str]:
    """Return value as a string-to-string dictionary."""
    if not isinstance(value, dict):
        return {}

    table = cast(dict[object, object], value)
    return {str(key): str(item) for key, item in table.items()}


def _as_bool(value: object) -> bool:
    """Return value as a boolean."""
    if isinstance(value, bool):
        return value
    return False


def _looks_like_course_repo(*, repo_slug: str, files: set[str]) -> bool:
    """Return whether a repository looks like a course project repo."""
    normalized_slug = repo_slug.lower()

    if not normalized_slug.startswith(COURSE_PREFIXES):
        return False

    # Avoid admin/maintenance repos unless you decide they should get course docs.
    if normalized_slug.endswith("-00-admin") or normalized_slug.endswith("-admin"):
        return False

    # Require project repo shape, not just matching name.
    return "pyproject.toml" in files


def _looks_like_pypi_package(repo_root: Path) -> bool:
    """Return whether pyproject.toml looks like a publishable package.

    This is intentionally stricter than "has pyproject + src" so ordinary
    course repos do not accidentally receive PyPI release surfaces.
    """
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return False

    try:
        data = _read_toml(pyproject_path)
    except OSError:
        return False
    except tomllib.TOMLDecodeError:
        return False

    project = _as_table(data.get("project"))
    if not project:
        return False

    if _has_console_scripts(project):
        return True

    classifiers = _as_string_list(project.get("classifiers"))
    if any("PyPI" in item for item in classifiers):
        return True

    tool = _as_table(data.get("tool"))
    uv = _as_table(tool.get("uv"))

    return _as_bool(uv.get("package"))
