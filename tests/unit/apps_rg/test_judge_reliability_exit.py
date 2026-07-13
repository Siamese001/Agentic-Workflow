from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from agentic_core.L4_state.contracts.app_domain import (
    AppDomainContractError,
    ApprovedJudgeCalibrationBaseline,
)
from agentic_core.L4_state.contracts.app_domain_lookup import AppDomainLookupError, InMemoryAppDomainStore
from agentic_core.L4_state.contracts.records import stamp_digest
from apps_rg.runtime.bindings.exit_binding import (
    ExitGateVerdict,
    _evaluate_judge_reliability_gate,
    _resolve_judge_reliability_gate,
)


def _baseline(**overrides) -> ApprovedJudgeCalibrationBaseline:
    values = {
        "baseline_id": "baseline::apps-rg::exec-positioning::v1",
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "status": "active",
        "judge_id": "rg::executive_positioning_judge::v1",
        "judge_version": "v1",
        "rubric_hash": "e3cec96dfac21b61056f4f5d1d150fa769e3242a5e4b93c4c907afe8b731fdb1",
        "rubric_version": "1.0.0",
        "provider_profile_ref": "local_qwen_generator",
        "dataset_id": "apps_rg_executive_positioning",
        "dataset_version": "v1",
        "n": 40,
        "spearman_rho": 0.9,
        "p_value": 0.001,
        "threshold": 0.8,
        "approved_use": "ALLOW_ADVISORY_ONLY",
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "promotion_receipt_ref": "promotion::receipt::1",
        "uwg_receipt_ref": "uwg::receipt::1",
    }
    values.update(overrides)
    return stamp_digest(ApprovedJudgeCalibrationBaseline(**values))


def test_missing_baseline_keeps_informational_judge_advisory():
    gate = _evaluate_judge_reliability_gate(None)
    assert gate.verdict == ExitGateVerdict.WARN


def test_valid_approved_baseline_is_bounded_and_readable():
    baseline = _baseline()
    store = InMemoryAppDomainStore()
    store.put_judge_calibration_baseline(baseline)
    assert store.get_judge_calibration_baseline(baseline.baseline_id) == baseline
    gate = _resolve_judge_reliability_gate(baseline.baseline_id, store=store)
    assert gate.verdict == ExitGateVerdict.WARN
    assert "ALLOW_ADVISORY_ONLY" in gate.reason


def test_unknown_baseline_reference_fails_closed():
    gate = _resolve_judge_reliability_gate(
        "baseline::missing",
        store=InMemoryAppDomainStore(),
    )
    assert gate.verdict == ExitGateVerdict.UNKNOWN


def test_expired_or_identity_mismatched_baseline_is_rejected():
    expired = _baseline(
        approved_at=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    )
    mismatched = _baseline(judge_version="v2")
    dataset_mismatched = _baseline(dataset_version="v2")
    assert _evaluate_judge_reliability_gate(expired).verdict == ExitGateVerdict.UNKNOWN
    assert _evaluate_judge_reliability_gate(mismatched).verdict == ExitGateVerdict.UNKNOWN
    assert _evaluate_judge_reliability_gate(dataset_mismatched).verdict == ExitGateVerdict.UNKNOWN


def test_approved_use_postures_remain_bounded():
    assert (
        _evaluate_judge_reliability_gate(_baseline(approved_use="ALLOW_FOR_EVAL")).verdict
        == ExitGateVerdict.PASS
    )
    assert (
        _evaluate_judge_reliability_gate(_baseline(approved_use="REQUIRE_HUMAN_REVIEW")).verdict
        == ExitGateVerdict.UNKNOWN
    )
    assert (
        _evaluate_judge_reliability_gate(_baseline(approved_use="DISABLE_FOR_SURFACE")).verdict
        == ExitGateVerdict.WARN
    )


def test_non_uwg_baseline_cannot_be_constructed():
    with pytest.raises(AppDomainContractError):
        _baseline(created_by_surface="L6")


def test_l4_lookup_rejects_digest_tampering():
    baseline = _baseline()
    tampered = dataclasses.replace(baseline, dataset_version="v2")
    store = InMemoryAppDomainStore()
    store.put_judge_calibration_baseline(tampered)
    with pytest.raises(AppDomainLookupError, match="digest invalid"):
        store.get_judge_calibration_baseline(tampered.baseline_id)
