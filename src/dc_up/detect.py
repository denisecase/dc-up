"""Repository detection."""

import configparser
from pathlib import Path
import re

from dc_up.baseline import infer_layers
from dc_up.errors import RepositoryDetectionError
from dc_up.types import RepositoryContext

__all__ = ["detect_repository"]


GITHUB_REMOTE_RE = re.compile(
    r"(?:git@github\.com:|https://github\.com/)(?P<repo>[^/\s]+/[^/\s]+?)(?:\.git)?/?$"
)


def detect_repository(root: Path | None = None) -> RepositoryContext:
    """Detect the repository context.

    Args:
        root: Optional repository root. If None, detect from current directory.

    Returns:
        Repository context used by planning and TODO generation.

    Raises:
        RepositoryDetectionError: If the target directory cannot be resolved.
    """
    repo_root = _resolve_repo_root(root)
    files = _snapshot_files(repo_root)

    repo_slug = repo_root.name
    repo_name = _detect_repo_name(repo_root) or f"denisecase/{repo_slug}"

    repo_url = f"https://github.com/{repo_name}"
    site_url = f"https://denisecase.github.io/{repo_slug}/"

    layers = tuple(infer_layers(repo_root=repo_root, repo_slug=repo_slug, files=files))

    return RepositoryContext(
        root=repo_root,
        repo_slug=repo_slug,
        repo_name=repo_name,
        repo_url=repo_url,
        site_url=site_url,
        files=frozenset(files),
        layers=layers,
    )


def _resolve_repo_root(root: Path | None) -> Path:
    """Resolve the target repository root."""
    start = Path.cwd() if root is None else root
    start = start.expanduser().resolve()

    if not start.exists():
        raise RepositoryDetectionError(f"Repository path does not exist: {start}")

    if start.is_file():
        start = start.parent

    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate

    return start


def _snapshot_files(root: Path) -> set[str]:
    """Return repository-relative file and directory markers."""
    result: set[str] = set()

    ignored_dirs = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        "htmlcov",
        "node_modules",
    }

    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()

        if any(part in ignored_dirs for part in path.parts):
            continue

        if path.is_dir():
            result.add(rel)
            result.add(f"{rel}/")
        else:
            result.add(rel)

    return result


def _detect_repo_name(root: Path) -> str | None:
    """Infer owner/repo from .git/config if possible."""
    git_config = root / ".git" / "config"
    if not git_config.exists():
        return None

    parser = configparser.ConfigParser()
    try:
        parser.read(git_config, encoding="utf-8")
    except configparser.Error:
        return None

    section = 'remote "origin"'
    if not parser.has_section(section):
        return None

    url = parser.get(section, "url", fallback="")
    match = GITHUB_REMOTE_RE.search(url.strip())
    if match is None:
        return None

    return match.group("repo")
