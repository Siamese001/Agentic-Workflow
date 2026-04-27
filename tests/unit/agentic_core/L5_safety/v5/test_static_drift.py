"""Tests for `static_drift.py` (G7 — 00A.7 Static Governance & Structure Drift)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    ArchitectureDriftReport,
    GoldenSnapshotComparisonReport,
    PolicyWeakeningReport,
    StaticDriftEvidencePacket,
    StaticGovernanceReviewPacket,
)
from agentic_core.L5_safety.v5.types import StaticDriftKind


def test_static_review_packet_governance_changed_detection() -> None:
    p_changed = StaticGovernanceReviewPacket(
        review_id="r",
        changed_files=("a.py",),
        changed_authority_surfaces=(),
        policy_hash_before="P0",
        policy_hash_after="P1",  # changed
        blueprint_hash_before="B0",
        blueprint_hash_after="B0",
        registry_digest_before=("D",),
        registry_digest_after=("D",),
        scan_refs=(),
        waiver_refs=(),
        adr_refs=(),
        audit_replay_refs=(),
    )
    assert p_changed.governance_changed is True

    p_same = StaticGovernanceReviewPacket(
        review_id="r",
        changed_files=("a.py",),
        changed_authority_surfaces=(),
        policy_hash_before="P0",
        policy_hash_after="P0",
        blueprint_hash_before="B0",
        blueprint_hash_after="B0",
        registry_digest_before=("D",),
        registry_digest_after=("D",),
        scan_refs=(),
        waiver_refs=(),
        adr_refs=(),
        audit_replay_refs=(),
    )
    assert p_same.governance_changed is False


def test_drift_evidence_severity_validation() -> None:
    with pytest.raises(ValueError, match="severity"):
        StaticDriftEvidencePacket(
            evidence_id="e",
            drift_kind=StaticDriftKind.ARCHITECTURE,
            findings=("foo",),
            severity="bogus",
            waiver_required=False,
            adr_required=False,
        )


def test_architecture_drift_report_passed_when_clean() -> None:
    r = ArchitectureDriftReport(
        report_id="r",
        layer_boundary_violations=(),
        dependency_inversions=(),
        route_topology_changes=(),
        write_path_changes=(),
        retrieval_boundary_changes=(),
        prompt_assembly_boundary_changes=(),
        learning_boundary_changes=(),
        uwg_boundary_changes=(),
    )
    assert r.passed is True

    r_bad = ArchitectureDriftReport(
        report_id="r",
        layer_boundary_violations=("X",),
        dependency_inversions=(),
        route_topology_changes=(),
        write_path_changes=(),
        retrieval_boundary_changes=(),
        prompt_assembly_boundary_changes=(),
        learning_boundary_changes=(),
        uwg_boundary_changes=(),
    )
    assert r_bad.passed is False


def test_policy_weakening_report_aggregates() -> None:
    r = PolicyWeakeningReport(
        report_id="r",
        hard_constraint_weakening=("F-01.threshold↓",),
        risk_tier_weakening=(),
        hitl_threshold_weakening=(),
        sector_overlay_weakening=(),
        standards_fingerprint_weakening=(),
        replay_audit_weakening=(),
        egress_weakening=(),
        sandbox_weakening=(),
        credential_weakening=(),
        data_sensitivity_weakening=(),
    )
    assert r.weakened is True


def test_golden_snapshot_comparison_passed_when_no_drift() -> None:
    r = GoldenSnapshotComparisonReport(
        report_id="r",
        new_bypasses=(),
        deleted_gates=(),
        weakened_defaults=(),
        relaxed_scopes=(),
        missing_replay_metadata=(),
        missing_audit_metadata=(),
    )
    assert r.passed is True
