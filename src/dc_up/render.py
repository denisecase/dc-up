"""Minimal template rendering."""

from dc_up.types import RepositoryContext

__all__ = ["render_template"]


def render_template(text: str, target: RepositoryContext) -> str:
    """Render simple repository identity tokens.

    This is deliberately not a full template engine in v0.1.0.

    Args:
        text: Template text.
        target: Target repository context.

    Returns:
        Rendered text.
    """
    replacements = {
        "{{ repo_slug }}": target.repo_slug,
        "{{repo_slug}}": target.repo_slug,
        "{{ repo_name }}": target.repo_name,
        "{{repo_name}}": target.repo_name,
        "{{ repo_url }}": target.repo_url,
        "{{repo_url}}": target.repo_url,
        "{{ site_url }}": target.site_url,
        "{{site_url}}": target.site_url,
    }

    rendered = text
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)

    return rendered
