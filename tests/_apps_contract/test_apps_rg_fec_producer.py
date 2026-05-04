"""Contract tests for apps_rg FEC producer.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W3.P1.
"""

from __future__ import annotations

import pytest


def test_import_registers_producer() -> None:
    from apps_shared.cert.fec_producer import clear_registry, get_producer, _noop_producer  # noqa: PLC2701

    clear_registry()
    assert get_producer("apps_rg") is _noop_producer

    import apps_rg.cert  # noqa: F401

    resolved = get_producer("apps_rg")
    assert resolved is not _noop_producer
    assert callable(resolved)


def test_grounded_path_jd_plus_role() -> None:
    from apps_rg.cert.fec_producer import produce_fec

    ctx = {
        "route_id": "apps_rg.generate_v1",
        "jd_evidence_sources": ["jd_001.pdf"],
        "role_evidence_sources": ["role_a.json", "role_b.json"],
        "repo_signal_sources": [],
    }
    fec = produce_fec(ctx)
    assert fec["schema_version"] == "1.1"
    assert fec["producer"] == "apps_rg.cert.fec_producer"
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"
    assert fec["retrieval_sources"] == ["jd_001.pdf", "role_a.json", "role_b.json"]
    assert fec["source_ladder"]["jd_evidence_sources"] == ["jd_001.pdf"]


def test_grounded_path_jd_plus_repo() -> None:
    from apps_rg.cert.fec_producer import produce_fec

    ctx = {
        "jd_evidence_sources": ["jd.pdf"],
        "repo_signal_sources": ["commit_abc", "commit_def"],
    }
    fec = produce_fec(ctx)
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"


def test_partial_jd_only() -> None:
    """JD-only without role or repo evidence is partial, not grounded."""
    from apps_rg.cert.fec_producer import produce_fec

    ctx = {"jd_evidence_sources": ["jd.pdf"]}
    fec = produce_fec(ctx)
    assert fec["grounded"] is False
    assert fec["evidence_sufficiency"] == "partial"


def test_empty_context_yields_shape_valid_empty() -> None:
    from apps_rg.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.1"
    assert fec["grounded"] is False
    assert fec["retrieval_sources"] == []
    assert fec["evidence_sufficiency"] == "empty"
    assert fec["source_ladder"]["jd_evidence_sources"] == []
    # v1.1 fields present even on empty context
    assert "jd_present" in fec
    assert "jd_ref" in fec
    assert "research_depth_profile" in fec
    assert "freshness_violations" in fec
    assert "citation_anchor_count" in fec
    assert "recruiter_outreach_overlay_present" in fec


def test_malformed_inputs_never_raise() -> None:
    from apps_rg.cert.fec_producer import produce_fec

    fec = produce_fec(None)  # type: ignore[arg-type]
    assert isinstance(fec, dict)
    fec = produce_fec({"jd_evidence_sources": 99, "role_evidence_sources": "nope"})
    assert fec["source_ladder"]["jd_evidence_sources"] == []
    assert fec["source_ladder"]["role_evidence_sources"] == []


def test_resolver_round_trip() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_rg.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_rg", produce_fec)

    fec = resolve_fec("apps_rg", {"jd_evidence_sources": ["a"], "role_evidence_sources": ["b"]})
    assert fec["producer"] == "apps_rg.cert.fec_producer"
    assert fec["evidence_sufficiency"] == "grounded"


def test_v11_jd_context_fields() -> None:
    """v1.1: jd_context dict populates jd_present, jd_ref, jd_content_hash."""
    from apps_rg.cert.fec_producer import produce_fec

    ctx = {
        "jd_evidence_sources": ["jd.pdf"],
        "role_evidence_sources": ["role.json"],
        "jd_context": {
            "jd_ref": "JD-2024-001",
            "jd_content_hash": "abc123",
        },
    }
    fec = produce_fec(ctx)
    assert fec["jd_present"] is True
    assert fec["jd_ref"] == "JD-2024-001"
    assert fec["jd_content_hash"] == "abc123"
    assert fec["recruiter_outreach_overlay_present"] is True


def test_v11_c0_bundle_fields() -> None:
    """v1.1: c0_bundle claim_evidence_map and freshness_report surfaced."""
    from apps_rg.cert.fec_producer import produce_fec

    ctx = {
        "jd_evidence_sources": ["jd.pdf"],
        "role_evidence_sources": ["role.json"],
        "jd_context": {"jd_ref": "JD-X"},
        "c0_bundle": {
            "claim_evidence_map": {
                "unsupported_claim_count": 2,
                "jd_unsupported_claim_count": 1,
                "jd_to_company_evidence_map_present": True,
            },
            "freshness_report": {"violation_count": 3},
        },
    }
    fec = produce_fec(ctx)
    assert fec["unsupported_claim_count"] == 2
    assert fec["jd_unsupported_claim_count"] == 1
    assert fec["jd_to_company_evidence_map_present"] is True
    assert fec["freshness_violations"] == 3


def test_v11_research_depth_profile() -> None:
    """v1.1: research_depth_profile forwarded from context."""
    from apps_rg.cert.fec_producer import produce_fec

    ctx = {"research_depth_profile": "DOSSIER"}
    fec = produce_fec(ctx)
    assert fec["research_depth_profile"] == "DOSSIER"


@pytest.fixture(autouse=True)
def _restore_registry():
    from apps_shared.cert.fec_producer import clear_registry
    yield
    clear_registry()
