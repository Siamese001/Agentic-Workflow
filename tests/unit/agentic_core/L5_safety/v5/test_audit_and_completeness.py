"""Tests for `AuditManifest` + completeness reports (G8 — 00A.6)."""

from __future__ import annotations

from agentic_core.L5_safety.v5 import (
    AuditManifest,
    HashBindingReport,
    ReceiptChainCompletenessReport,
    ReconstructionReadinessReport,
    TraceCompletenessReport,
)
from agentic_core.L5_safety.v5.types import (
    AuditDetailLevel,
    DecisionVerdict,
    ReasonCode,
    RetentionBand,
)


def test_audit_manifest_serializes_all_required_fields() -> None:
    m = AuditManifest(
        request_id="r",
        trace_id="t",
        run_id="run",
        tenant_id="ten",
        caller_id="c",
        decision_verdict=DecisionVerdict.CERTIFY,
        reason_codes=(),
        compliance_hash="h",
        policy_hash="P",
        blueprint_hash="B",
        registry_digest_set=("D",),
        retention_class=RetentionBand.STANDARD,
        access_class="internal",
        redaction_policy="none",
        detail_level=AuditDetailLevel.FULL,
        generated_at="2026-04-26T22:00:00Z",
    )
    d = m.to_dict()
    for k in (
        "decision_verdict",
        "policy_hash",
        "retention_class",
        "detail_level",
        "redaction_policy",
    ):
        assert k in d


def test_receipt_chain_completeness() -> None:
    complete = ReceiptChainCompletenessReport(
        expected_receipts=("a", "b"),
        present_receipts=("a", "b"),
        missing_receipts=(),
        orphan_receipts=(),
        stale_receipts=(),
        cross_principal_receipts=(),
    )
    assert complete.complete is True
    incomplete = ReceiptChainCompletenessReport(
        expected_receipts=("a", "b"),
        present_receipts=("a",),
        missing_receipts=("b",),
        orphan_receipts=(),
        stale_receipts=(),
        cross_principal_receipts=(),
    )
    assert incomplete.complete is False


def test_hash_binding_report_passes_when_clean() -> None:
    r = HashBindingReport(
        expected_hashes={"x": "h1"},
        actual_hashes={"x": "h1"},
    )
    assert r.passed is True


def test_hash_binding_report_fails_on_mismatch() -> None:
    r = HashBindingReport(
        expected_hashes={"x": "h1"},
        actual_hashes={"x": "h2"},
        mismatched=("x",),
    )
    assert r.passed is False


def test_trace_completeness_orphan_detection() -> None:
    r = TraceCompletenessReport(
        expected_spans=("a", "b"),
        present_spans=("a", "c"),
        missing_spans=("b",),
        orphan_spans=("c",),
        parent_gap=(),
    )
    assert r.complete is False


def test_reconstruction_readiness_aggregates_three_signals() -> None:
    receipt = ReceiptChainCompletenessReport(
        expected_receipts=(),
        present_receipts=(),
        missing_receipts=(),
        orphan_receipts=(),
        stale_receipts=(),
        cross_principal_receipts=(),
    )
    hash_b = HashBindingReport(expected_hashes={}, actual_hashes={})
    trace = TraceCompletenessReport(
        expected_spans=(),
        present_spans=(),
        missing_spans=(),
        orphan_spans=(),
        parent_gap=(),
    )
    r = ReconstructionReadinessReport(
        receipt_chain=receipt,
        hash_binding=hash_b,
        trace_completeness=trace,
    )
    assert r.readiness_score == 1.0
    assert r.reconstructable is True

    # Force one component to fail
    bad_trace = TraceCompletenessReport(
        expected_spans=("a",),
        present_spans=(),
        missing_spans=("a",),
        orphan_spans=(),
        parent_gap=(),
    )
    r2 = ReconstructionReadinessReport(
        receipt_chain=receipt,
        hash_binding=hash_b,
        trace_completeness=bad_trace,
    )
    assert r2.readiness_score < 1.0
    assert r2.reconstructable is False
