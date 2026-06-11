"""Baseline layer inference and managed file declarations."""

from pathlib import Path
import tomllib
from typing import Literal, cast

__all__ = [
    "PRESERVE_PATTERNS",
    "infer_layers",
]

TomlTable = dict[str, object]

# Single base stack classification per repo (first match wins, see _classify_stack).
StackKind = Literal["ts", "notebook", "kafka", "pypi", "src"]

COURSE_PREFIXES: tuple[str, ...] = (
    "cintel-",
    "datafun-",
    "insights-",
    "ml-",
    "nlp-",
    "streaming-",
)


PRESERVE_PATTERNS: tuple[str, ...] = (
    "README.md",
    "artifacts/**",
    "data/**",
    "docs/**",
    "notebooks/**",
    "sql/**",
    "src/**",
    "tests/**",
)


# WHY: Base layers describe the repo's stack. Indexed by StackKind so the
# classification and the layer list can't drift apart, and so the prefix
# duplication (ALL, ALL-PY, ...) is declared once per kind, not per branch.
BASE_LAYERS: dict[StackKind, tuple[str, ...]] = {
    "kafka": ("ALL", "ALL-PY", "ALL-PY-KAFKA"),
    "notebook": ("ALL", "ALL-PY", "ALL-PY-NB"),
    "pypi": ("ALL", "ALL-PY", "ALL-PY-SRC", "ALL-PY-SRC-PYPI"),
    "src": ("ALL", "ALL-PY", "ALL-PY-SRC"),
    "ts": ("ALL", "ALL-TS"),
}

# WHY: Educational ("ALL-COURSE*") overrides, appended AFTER the base so the
# ed versions win (last layer wins). ALL-COURSE is always first because it
# overrides ALL; deeper course layers follow parent-first.
# OBS: "ts" is unreachable for courses (course repos require pyproject.toml,
#   which the "ts" classification excludes) - it's defensive.
# OBS: "notebook" gets ALL-COURSE only; there is no ALL-COURSE-PY-NB defined.
COURSE_OVERLAYS: dict[StackKind, tuple[str, ...]] = {
    "kafka": ("ALL-COURSE", "ALL-COURSE-PY-SRC", "ALL-COURSE-PY-SRC-KAFKA"),
    "notebook": ("ALL-COURSE",),
    "pypi": ("ALL-COURSE", "ALL-COURSE-PY-SRC"),
    "src": ("ALL-COURSE", "ALL-COURSE-PY-SRC"),
    "ts": ("ALL-COURSE",),
}


def infer_layers(
    *,
    repo_root: Path,
    repo_name: str,
    files: set[str],
) -> list[str]:
    """Infer additive template layers for a repository.

    The base layers describe the repo's stack. If the repo is a course repo,
    the matching course overlay is appended AFTER the base so the educational
    files override their ALL / ALL-PY counterparts (last layer wins).
    """
    slug = repo_name.lower()
    kind = _classify_stack(repo_root=repo_root, slug=slug, files=files)

    layers: list[str] = list(BASE_LAYERS[kind])

    if _looks_like_course_repo(repo_name_only=repo_name, files=files):
        layers.extend(COURSE_OVERLAYS[kind])

    return layers


def _classify_stack(
    *,
    repo_root: Path,
    slug: str,
    files: set[str],
) -> StackKind:
    """Classify a repository into one base stack kind (first match wins).

    Precedence is preserved from the original if/elif chain. This is the one
    place to special-case 'insights-' or 'ml-' later if they need it.
    """
    if "package.json" in files and "pyproject.toml" not in files:
        return "ts"
    if "notebook" in slug or slug.endswith("-notebooks"):
        return "notebook"
    if "kafka" in slug:
        return "kafka"
    if slug == "dc-up" or _looks_like_pypi_package(repo_root):
        return "pypi"
    return "src"


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


def _looks_like_course_repo(*, repo_name_only: str, files: set[str]) -> bool:
    """Return whether a repository looks like a course project repo."""
    normalized_slug = repo_name_only.lower()

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
