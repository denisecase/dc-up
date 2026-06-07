"""Template source access."""

from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from dc_up.errors import TemplateFetchError

__all__ = ["TemplateSource", "fetch_template_text"]


@dataclass(frozen=True)
class TemplateSource:
    """Canonical template source."""

    repository: str = "denisecase/templates"
    ref: str = "main"
    local_path: Path | None = None


def fetch_template_text(
    *,
    source: TemplateSource,
    layer: str,
    path: str,
) -> str | None:
    """Fetch one template file.

    Args:
        source: Template source.
        layer: Template layer, such as ALL-PY.
        path: Repository-relative managed file path.

    Returns:
        File text, or None if the template file does not exist.

    Raises:
        TemplateFetchError: If fetching fails for a reason other than not found.
    """
    if source.local_path is not None:
        return _fetch_local_template_text(
            local_path=source.local_path,
            layer=layer,
            path=path,
        )

    return _fetch_github_template_text(
        repository=source.repository,
        ref=source.ref,
        layer=layer,
        path=path,
    )


def _fetch_local_template_text(
    *,
    local_path: Path,
    layer: str,
    path: str,
) -> str | None:
    """Fetch template text from a local templates repository."""
    template_path = local_path.expanduser().resolve() / layer / path

    if not template_path.exists():
        template_path_with_suffix = Path(f"{template_path}.template")
        if not template_path_with_suffix.exists():
            return None
        template_path = template_path_with_suffix

    if template_path.is_dir():
        return None

    try:
        return template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TemplateFetchError(
            f"Could not read template file: {template_path}"
        ) from exc


def _fetch_github_template_text(
    *,
    repository: str,
    ref: str,
    layer: str,
    path: str,
) -> str | None:
    """Fetch template text from GitHub raw content."""
    raw_path = f"{layer}/{path}"
    url = f"https://raw.githubusercontent.com/{repository}/{ref}/{raw_path}"

    text = _fetch_url_text(url)
    if text is not None:
        return text

    template_url = f"{url}.template"
    return _fetch_url_text(template_url)


def _fetch_url_text(url: str) -> str | None:
    """Fetch text from a trusted HTTPS URL, returning None for HTTP 404."""
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise TemplateFetchError(f"Invalid URL scheme: {url}")

    if parsed.netloc != "raw.githubusercontent.com":
        raise TemplateFetchError(f"Invalid template host: {url}")

    request = Request(  # noqa: S310
        url,
        headers={
            "User-Agent": "dc-up",
        },
    )

    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310
            return response.read().decode("utf-8")
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise TemplateFetchError(f"Could not fetch template file: {url}") from exc
    except URLError as exc:
        raise TemplateFetchError(f"Could not fetch template file: {url}") from exc
