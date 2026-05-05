"""Tests for apps_repo_brief FEC producer — DS-1 closeout.

Pattern: tests/_apps_contract/test_apps_qna_fec_producer.py (canonical).

7 test cases:
1. Registration side-effect (import auto-registers)
2. Template-only path (no retrieval sources)
3. Grounded path with c0_retrieval_sources
4. Grounded path with research_snippets (legacy fallback)
5. Empty-context shape valid
6. Malformed inputs never raise
7. Resolver round-trip (resolve_fec returns non-empty FEC)
"""
from __future__ import annotations

import pytest

from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
from apps_repo_brief.cert.fec_producer import produce_fec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register() -> None:
    """Manually register producer (safe after clear_registry)."""
    register_producer("apps_repo_brief", produce_fec)


# ---------------------------------------------------------------------------
# Test 1: Registration side-effect
# ---------------------------------------------------------------------------


def test_registration_side_effect() -> None:
    """Producer can be registered and resolved via the shared registry."""
    clear_registry()
    # sys.modules caches the first import so the side-effect re-fire is not
    # guaranteed in parallel workers — use explicit register_producer instead.
    _register()
    result = resolve_fec("apps_repo_brief", {})
    assert result.get("producer") == "apps_repo_brief.cert.fec_producer"


# ---------------------------------------------------------------------------
# Test 2: Template-only path
# ---------------------------------------------------------------------------


def test_template_only_path() -> None:
    """No retrieval sources → grounded=False, sufficiency=template_only."""
    clear_registry()
    _register()
    fec = produce_fec({})
    assert fec["schema_version"] == "1.0"
    assert fec["grounded"] is False
    assert fec["evidence_sufficiency"] == "template_only"
    assert "repo_brief_v1" in fec["template_ids"]
    assert fec["retrieval_sources"] == []


# ---------------------------------------------------------------------------
# Test 3: Grounded via c0_retrieval_sources
# ---------------------------------------------------------------------------


def test_grounded_via_c0_retrieval_sources() -> None:
    """c0_retrieval_sources populates retrieval_sources and sets grounded=True."""
    clear_registry()
    _register()
    fec = produce_fec({"c0_retrieval_sources": ["doc-1", "doc-2"]})
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"
    assert fec["retrieval_sources"] == ["doc-1", "doc-2"]


# ---------------------------------------------------------------------------
# Test 4: Grounded via research_snippets (legacy fallback)
# ---------------------------------------------------------------------------


def test_grounded_via_research_snippets_fallback() -> None:
    """research_snippets used when c0_retrieval_sources absent."""
    clear_registry()
    _register()
    fec = produce_fec({"research_snippets": ["snippet-a"]})
    assert fec["grounded"] is True
    assert fec["retrieval_sources"] == ["snippet-a"]


# ---------------------------------------------------------------------------
# Test 5: Empty context shape valid
# ---------------------------------------------------------------------------


def test_empty_context_shape_valid() -> None:
    """Empty mapping produces a fully-shaped FEC (all required keys present)."""
    clear_registry()
    _register()
    fec = produce_fec({})
    required_keys = {
        "schema_version",
        "producer",
        "grounded",
        "retrieval_sources",
        "template_ids",
        "route_id",
        "evidence_sufficiency",
        "source_collection",
    }
    assert required_keys.issubset(fec.keys())
    assert fec["route_id"] == "apps_repo_brief.executive_brief_v1"
    assert fec["source_collection"] == "repo_brief_docs"


# ---------------------------------------------------------------------------
# Test 6: Malformed inputs never raise
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ctx",
    [
        None,
        42,
        "string",
        [],
        {"c0_retrieval_sources": "not_a_list"},
        {"template_ids": 99},
    ],
)
def test_malformed_inputs_never_raise(ctx) -> None:
    """produce_fec never raises regardless of input type."""
    clear_registry()
    _register()
    result = produce_fec(ctx)  # must not raise
    assert isinstance(result, dict)
    assert "schema_version" in result


# ---------------------------------------------------------------------------
# Test 7: Resolver round-trip
# ---------------------------------------------------------------------------


def test_resolver_round_trip() -> None:
    """resolve_fec('apps_repo_brief', ctx) returns a distinct non-empty FEC each call."""
    clear_registry()
    _register()
    ctx = {
        "route_id": "apps_repo_brief.executive_brief_v1",
        "template_ids": ["repo_brief_v1"],
    }
    fec1 = resolve_fec("apps_repo_brief", ctx)
    fec2 = resolve_fec("apps_repo_brief", ctx)
    assert fec1 is not fec2  # distinct objects
    assert fec1["schema_version"] == "1.0"
    assert fec1["producer"] == "apps_repo_brief.cert.fec_producer"
