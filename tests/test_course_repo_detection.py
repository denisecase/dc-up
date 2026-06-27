"""tests/test_course_repo_detection.py.

Tests for course repository detection logic.
"""

from dc_up.baseline_utils import looks_like_course_repo

# Mock rules for testing
MOCK_RULES: dict[str, object] = {
    "course_pattern": r"^[a-zA-Z]+-\d{2}-.+$",
    "course_prefixes": ["cintel-", "datafun-", "ml-"],
}


def test_course_detection_regex_dash_pattern():
    """Verify that pre-NN-post pattern with dashes is detected."""
    assert (
        looks_like_course_repo(
            repo_name_only="aml-02-something",
            files={"pyproject.toml"},
            rules=MOCK_RULES,
        )
        is True
    )


def test_course_detection_legacy_prefix():
    """Verify that legacy prefix matching still works."""
    assert (
        looks_like_course_repo(
            repo_name_only="cintel-01-intro", files={"pyproject.toml"}, rules=MOCK_RULES
        )
        is True
    )


def test_course_detection_non_course_repo():
    """Verify that standard repos are not flagged as course repos."""
    assert (
        looks_like_course_repo(
            repo_name_only="my-cool-project", files={"pyproject.toml"}, rules=MOCK_RULES
        )
        is False
    )


def test_course_detection_missing_pyproject():
    """Verify that a course-named repo is detected even without pyproject.toml."""
    assert (
        looks_like_course_repo(
            repo_name_only="aml-02-something", files={"README.md"}, rules=MOCK_RULES
        )
        is True
    )


def test_course_detection_admin_guard():
    """Verify that admin repositories are explicitly ignored."""
    assert (
        looks_like_course_repo(
            repo_name_only="ml-00-admin", files={"pyproject.toml"}, rules=MOCK_RULES
        )
        is False
    )
