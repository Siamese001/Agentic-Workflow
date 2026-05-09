"""W3 tests — l5_certification_ref on UWG/L4/L6 contracts.

Covers:
- CommitRequest: singular alias field alongside existing plural tuple
- UWGCommitReceipt: new l5_certification_ref field
- RuntimeExhaustBundle (runtime_trace variant): new field
- RuntimeExhaustBundle (shadow_eval variant): new field
"""
from __future__ import annotations

import dataclasses

import pytest


# ---------------------------------------------------------------------------
# CommitRequest — plural + singular both present
# ---------------------------------------------------------------------------

def test_commit_request_has_singular_l5_cert_ref_field():
    from agentic_core.L4_state.contracts.records import CommitRequest
    names = {f.name for f in dataclasses.fields(CommitRequest)}
    assert "l5_certification_ref" in names
    assert "l5_certification_refs" in names  # existing plural must be preserved


def test_commit_request_l5_cert_ref_empty_raises():
    from agentic_core.L4_state.contracts.records import CommitRequest
    with pytest.raises(ValueError, match="l5_certification_ref"):
        CommitRequest(
            commit_request_id="cr1",
            cleared_exit_review_packet_ref="ep1",
            request_id="r1",
            run_id="u1",
            trace_root="tr1",
            tenant_id="t1",
            policy_hash="ph1",
            blueprint_hash="bh1",
            route_contract_ref="rc1",
            replay_key="rk1",
            rollback_plan_ref="rp1",
            blast_radius="br1",
            l5_certification_ref="",
        )


def test_commit_request_l5_cert_ref_roundtrip():
    from agentic_core.L4_state.contracts.records import CommitRequest
    cr = CommitRequest(
        commit_request_id="cr2",
        cleared_exit_review_packet_ref="ep2",
        request_id="r2",
        run_id="u2",
        trace_root="tr2",
        tenant_id="t2",
        policy_hash="ph2",
        blueprint_hash="bh2",
        route_contract_ref="rc2",
        replay_key="rk2",
        rollback_plan_ref="rp2",
        blast_radius="br2",
        l5_certification_ref="cert-uwg-001",
    )
    assert cr.l5_certification_ref == "cert-uwg-001"


def test_commit_request_plural_still_defaults_empty_tuple():
    from agentic_core.L4_state.contracts.records import CommitRequest
    cr = CommitRequest(
        commit_request_id="cr3",
        cleared_exit_review_packet_ref="ep3",
        request_id="r3",
        run_id="u3",
        trace_root="tr3",
        tenant_id="t3",
        policy_hash="ph3",
        blueprint_hash="bh3",
        route_contract_ref="rc3",
        replay_key="rk3",
        rollback_plan_ref="rp3",
        blast_radius="br3",
        l5_certification_ref="cert-plural-test",  # singular required; plural is backward-compat
    )
    assert cr.l5_certification_refs == ()


# ---------------------------------------------------------------------------
# UWGCommitReceipt
# ---------------------------------------------------------------------------

def test_uwg_commit_receipt_has_l5_cert_ref_field():
    from agentic_core.L4_state.contracts.records import UWGCommitReceipt
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(UWGCommitReceipt)}


def test_uwg_commit_receipt_l5_cert_ref_empty_raises():
    from agentic_core.L4_state.contracts.records import UWGCommitReceipt
    with pytest.raises(ValueError, match="l5_certification_ref"):
        UWGCommitReceipt(
            commit_receipt_id="rcpt1",
            commit_request_ref="cr1",
            write_lock_receipt_ref="wl1",
            uwg_validation_receipt_ref="vr1",
            snapshot_before="sb1",
            snapshot_after="sa1",
            read_surface_refresh_plan_ref="rsr1",
            audit_append_receipt_ref="aar1",
            committed_at="2026-01-01T00:00:00",
            l5_certification_ref="",
        )


def test_uwg_commit_receipt_l5_cert_ref_roundtrip():
    from agentic_core.L4_state.contracts.records import UWGCommitReceipt
    r = UWGCommitReceipt(
        commit_receipt_id="rcpt2",
        commit_request_ref="cr2",
        write_lock_receipt_ref="wl2",
        uwg_validation_receipt_ref="vr2",
        snapshot_before="sb2",
        snapshot_after="sa2",
        read_surface_refresh_plan_ref="rsr2",
        audit_append_receipt_ref="aar2",
        committed_at="2026-01-01T00:00:00",
        l5_certification_ref="cert-uwg-rcpt-001",
    )
    assert r.l5_certification_ref == "cert-uwg-rcpt-001"


# ---------------------------------------------------------------------------
# RuntimeExhaustBundle — runtime_trace variant
# ---------------------------------------------------------------------------

def test_runtime_trace_exhaust_bundle_has_l5_cert_ref_field():
    from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import RuntimeExhaustBundle
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(RuntimeExhaustBundle)}


def test_runtime_trace_exhaust_bundle_l5_cert_ref_empty_raises():
    from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import RuntimeExhaustBundle
    with pytest.raises(ValueError, match="l5_certification_ref"):
        RuntimeExhaustBundle(
            raw_evidence_refs=(),
            lineage_manifest={},
            stage_map={},
            artifact_inventory=(),
            gap_report=(),
            ingest_quality_score=1.0,
            newest_span_age_seconds=0.0,
            bundle_id="b1",
            l5_certification_ref="",
        )


def test_runtime_trace_exhaust_bundle_l5_cert_ref_roundtrip():
    from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import RuntimeExhaustBundle
    b = RuntimeExhaustBundle(
        raw_evidence_refs=(),
        lineage_manifest={},
        stage_map={},
        artifact_inventory=(),
        gap_report=(),
        ingest_quality_score=1.0,
        newest_span_age_seconds=0.0,
        bundle_id="b2",
        l5_certification_ref="cert-exhaust-001",
    )
    assert b.l5_certification_ref == "cert-exhaust-001"


# ---------------------------------------------------------------------------
# RuntimeExhaustBundle — shadow_eval variant
# ---------------------------------------------------------------------------

def test_shadow_eval_exhaust_bundle_has_l5_cert_ref_field():
    from agentic_core.L6_observability.shadow_eval.contracts import RuntimeExhaustBundle
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(RuntimeExhaustBundle)}


def test_shadow_eval_exhaust_bundle_l5_cert_ref_empty_raises():
    from agentic_core.L6_observability.shadow_eval.contracts import RuntimeExhaustBundle
    with pytest.raises(ValueError, match="l5_certification_ref"):
        RuntimeExhaustBundle(
            runtime_exhaust_bundle_id="sb1",
            request_id="r1",
            run_id="u1",
            session_id="s1",
            tenant_id="t1",
            trace_root="tr1",
            completed_at="2026-01-01T00:00:00",
            runtime_boundary_crossed=False,
            l5_certification_ref="",
        )


def test_shadow_eval_exhaust_bundle_l5_cert_ref_roundtrip():
    from agentic_core.L6_observability.shadow_eval.contracts import RuntimeExhaustBundle
    b = RuntimeExhaustBundle(
        runtime_exhaust_bundle_id="sb2",
        request_id="r2",
        run_id="u2",
        session_id="s2",
        tenant_id="t2",
        trace_root="tr2",
        completed_at="2026-01-01T00:00:00",
        runtime_boundary_crossed=True,
        l5_certification_ref="cert-shadow-001",
    )
    assert b.l5_certification_ref == "cert-shadow-001"
