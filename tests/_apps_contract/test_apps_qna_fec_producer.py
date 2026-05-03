"""Contract tests for apps_qna FEC producer.

Plan: .windsurf/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md W1.P2.

Verifies:
- Importing ``apps_qna.cert`` auto-registers the producer in the shared registry.
- ``produce_fec`` returns a well-shaped FEC dict for template-only and grounded paths.
- Malformed / empty run_context never raises; yields shape-valid empty packet.
- Producer is idempotent — distinct returns on each call (never shares mutable state).
"""

from __future__ import annotations

import pytest


def test_import_registers_producer() -> None:
    from apps_shared.cert.fec_producer import clear_registry, get_producer, _noop_producer  # noqa: PLC2701

    clear_registry()
    # Before import, no producer
    assert get_producer("apps_qna") is _noop_producer

    import apps_qna.cert  # noqa: F401 — side-effect import

    resolved = get_producer("apps_qna")
    assert resolved is not _noop_producer
    assert callable(resolved)


def test_template_only_path() -> None:
    from apps_qna.cert.fec_producer import produce_fec

    ctx = {
        "route_id": "apps_qna.pack_build_single_step_v1",
        "template_ids": ["intake", "seal"],
        "c0_retrieval_sources": [],
    }
    fec = produce_fec(ctx)
    assert fec["schema_version"] == "1.0"
    assert fec["producer"] == "apps_qna.cert.fec_producer"
    assert fec["grounded"] is False
    assert fec["template_ids"] == ["intake", "seal"]
    assert fec["retrieval_sources"] == []
    assert fec["route_id"] == "apps_qna.pack_build_single_step_v1"
    assert fec["evidence_sufficiency"] == "template_only"


def test_grounded_path() -> None:
    from apps_qna.cert.fec_producer import produce_fec

    ctx = {
        "route_id": "apps_qna.rag_route_v1",
        "template_ids": ["intake"],
        "c0_retrieval_sources": ["doc_a.pdf", "doc_b.pdf"],
    }
    fec = produce_fec(ctx)
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"
    assert fec["retrieval_sources"] == ["doc_a.pdf", "doc_b.pdf"]


def test_empty_context_yields_shape_valid_empty() -> None:
    from apps_qna.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.0"
    assert fec["grounded"] is False
    assert fec["template_ids"] == []
    assert fec["retrieval_sources"] == []
    assert fec["route_id"] == ""
    assert fec["evidence_sufficiency"] == "empty"


def test_malformed_inputs_never_raise() -> None:
    from apps_qna.cert.fec_producer import produce_fec

    # Non-Mapping run_context
    fec = produce_fec(None)  # type: ignore[arg-type]
    assert isinstance(fec, dict)
    # Non-list template_ids
    fec = produce_fec({"template_ids": "not-a-list", "c0_retrieval_sources": 42})
    assert fec["template_ids"] == []
    assert fec["retrieval_sources"] == []


def test_resolver_round_trip() -> None:
    """resolve_fec via shared registry returns the apps_qna producer's output."""
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_qna.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_qna", produce_fec)

    fec = resolve_fec("apps_qna", {"template_ids": ["intake"]})
    assert fec["producer"] == "apps_qna.cert.fec_producer"
    assert fec["evidence_sufficiency"] == "template_only"


def test_distinct_return_per_call() -> None:
    """Producer must return a fresh dict each call — no shared mutable state."""
    from apps_qna.cert.fec_producer import produce_fec

    a = produce_fec({"template_ids": ["t1"]})
    b = produce_fec({"template_ids": ["t1"]})
    assert a == b
    assert a is not b
    a["template_ids"].append("mutated")
    assert "mutated" not in b["template_ids"]


@pytest.fixture(autouse=True)
def _restore_registry():
    """Ensure tests don't leak registry state across runs."""
    from apps_shared.cert.fec_producer import clear_registry
    yield
    clear_registry()
