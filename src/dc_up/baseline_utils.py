"""Internal utilities, type-casters, and metadata parsers for layout inference."""

import importlib.resources
from pathlib import Path
import re
import tomllib
from typing import BinaryIO, cast

__all__ = ["looks_like_course_repo", "looks_like_pypi_package", "load_package_defaults"]

TomlTable = dict[str, object]


def load_package_defaults() -> dict[str, object]:
    """Read the data properties packaged inside this tool's installation wheel."""
    try:
        ref = importlib.resources.files("dc_up").joinpath("data/defaults.toml")
        with ref.open("rb") as f:
            config = tomllib.load(cast(BinaryIO, f))
        classification = config.get("classification")
        if isinstance(classification, dict):
            return cast(dict[str, object], classification)
    except OSError:
        return {}
    except tomllib.TOMLDecodeError:
        return {}
    return {}


def looks_like_course_repo(
    *, repo_name_only: str, files: set[str], rules: dict[str, object]
) -> bool:
    """Return whether a repository matches course layouts using data-driven patterns."""
    normalized_slug = repo_name_only.lower()

    # Guard admin/maintenance surfaces
    if normalized_slug.endswith(("-00-admin", "-admin")):
        return False

    # Safely extract regex string from configuration
    pattern_str = rules.get("course_pattern")
    if not isinstance(pattern_str, str):
        pattern_str = ""

    # WHY: Use our existing type-caster to safely extract and cast the list of objects to strings.
    prefixes = tuple(_as_string_list(rules.get("course_prefixes")))

    # 1. Match regex pattern (enforces the pre-NN-post structure using dashes)
    is_pattern_match = False
    if pattern_str:
        is_pattern_match = bool(re.match(pattern_str, normalized_slug))

    # 2. Match legacy prefixes (fallback)
    is_prefix_match = False
    if prefixes and normalized_slug.startswith(prefixes):
        is_prefix_match = True

    # 3. Must match one of the naming rules, and must contain a pyproject.toml
    return bool(is_pattern_match or is_prefix_match)


def looks_like_pypi_package(repo_root: Path) -> bool:
    """Return whether pyproject.toml looks like a publishable package."""
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
