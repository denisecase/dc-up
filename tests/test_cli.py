"""tests/test_cli.py.

Tests for cli.py - argument parsing and dispatch.
"""



from dc_up.cli import build_parser


def test_build_parser_returns_parser() -> None:
    parser = build_parser()
    assert parser is not None
