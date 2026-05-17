"""Unit tests for tools.refactor_decisions.precedent_scope (W3)."""

from tools.refactor_decisions.precedent_scope import (
    layer_matches,
    normalize_repo_path,
    repo_areas_compatible_strong,
    repo_areas_compatible_suggestive,
)


def test_normalize_repo_path():
    assert normalize_repo_path("  a/b\\c  ") == "a/b/c"


def test_strong_requires_row_under_query_prefix():
    assert repo_areas_compatible_strong("agentic_core/L2", "agentic_core/L2/foo")
    assert repo_areas_compatible_strong("agentic_core/L2", "agentic_core/L2")
    assert not repo_areas_compatible_strong("agentic_core/L2", "apps_rg/foo")
    assert not repo_areas_compatible_strong("agentic_core/L2", "")
    assert repo_areas_compatible_strong("", "anything")


def test_suggestive_allows_same_top_level():
    assert repo_areas_compatible_suggestive("agentic_core/L2", "agentic_core/L3")
    assert not repo_areas_compatible_suggestive("apps_rg", "agentic_core/L2")
    assert not repo_areas_compatible_suggestive("scoped", "")
    assert repo_areas_compatible_suggestive("", "scoped")


def test_layer_matches():
    assert layer_matches("", "L2")
    assert layer_matches("L2", "L2")
    assert layer_matches("L2", "")
    assert not layer_matches("L2", "L3")
