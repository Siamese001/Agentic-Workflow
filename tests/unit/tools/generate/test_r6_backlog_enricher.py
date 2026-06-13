from __future__ import annotations

from tools.generate.r6_backlog_enricher import BOUNDARY_STRING_RE


def test_boundary_string_regex_matches_module_reference() -> None:
    assert BOUNDARY_STRING_RE.match("tools.generate.r6_backlog_enricher") is not None


def test_boundary_string_regex_rejects_path_reference() -> None:
    assert BOUNDARY_STRING_RE.match("tools/generate/r6_backlog_enricher.py") is None
