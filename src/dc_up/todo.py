"""Human action reporting for."""

from dc_up.types import RepositoryContext, TodoReport

__all__ = ["build_todo_report", "print_todo_report"]


DEFAULT_REVIEW_PATHS: tuple[str, ...] = (
    ".accountability/surfaces.toml",
    "README.md",
    "docs/project-instructions.md",
    "docs/working-files.md",
    "docs/success.md",
    "docs/example-output.md",
    "docs/index.md",
    "src/**",
    "tests/**",
    "notebooks/**",
    "sql/**",
    "data/raw/**",
)


DEFAULT_CONFIRMATIONS: tuple[str, ...] = (
    "repo-specific project description is accurate",
    "dataset paths and expected outputs are correct",
    "module-specific instructions still match the assignment",
    "tests still match intended student or package behavior",
    "notebook outputs are intentional, if notebooks are present",
    "protected surfaces still reflect human review boundaries",
)


def build_todo_report(target: RepositoryContext) -> TodoReport:
    """Build a repo-specific human review TODO report."""
    review_paths = list(DEFAULT_REVIEW_PATHS)
    confirmations = list(DEFAULT_CONFIRMATIONS)

    if "pyproject.toml" in target.files:
        review_paths.extend(
            [
                "pyproject.toml",
                "uv.lock",
            ]
        )
        confirmations.extend(
            [
                "package metadata is correct",
                "dependency groups match current tooling expectations",
            ]
        )

    if "package.json" in target.files:
        review_paths.append("package.json")
        confirmations.append("npm scripts and TypeScript tooling are current")

    if any(path.startswith("notebooks/") for path in target.files):
        confirmations.append("notebook execution state is intentional")

    if any(path.startswith("sql/") for path in target.files):
        confirmations.append("SQL examples and database paths are current")

    return TodoReport(
        target=target,
        review_paths=tuple(_dedupe(review_paths)),
        confirmations=tuple(_dedupe(confirmations)),
    )


def print_todo_report(report: TodoReport) -> None:
    """Print a human review TODO report."""
    print(f"PROJECT TODO: {report.target.repo_slug}")  # noqa: T201
    print("")  # noqa: T201

    print("Review repo-specific surfaces:")  # noqa: T201
    for path in report.review_paths:
        print(f"  {path}")  # noqa: T201

    print("")  # noqa: T201
    print("Confirm:")  # noqa: T201
    for item in report.confirmations:
        print(f"  {item}")  # noqa: T201


def _dedupe(items: list[str]) -> list[str]:
    """Deduplicate while preserving order."""
    seen: set[str] = set()
    result: list[str] = []

    for item in items:
        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result
