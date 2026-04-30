"""Tests for formal-exception negative-control helpers (Phase B.5).

All tests operate on in-memory row iterables. No live runtime-ADG
database, no real OTel pipeline. Exercises each CC-*-0N control both
on the passing path and on the violation path.
"""

from __future__ import annotations

import json

import pytest

from tools.runtime_cert.negative_controls import (
    CC_EVAL_01,
    CC_EVAL_02,
    CC_SHARED_03,
    CC_UW_02,
    NegativeControlResult,
    R3_CONTRACT_SET,
    check_apps_eval_no_r3_contract_leak,
    check_apps_shared_sealed_artifact_proof_only,
    check_no_eval_of_evaluator_circularity,
    check_underwriting_no_r3_contract_leak,
)


# ---------------------------------------------------------------------------
# CC-EVAL-01 (eval-of-evaluator circularity)
# ---------------------------------------------------------------------------


def test_cc_eval_01_passes_with_no_apps_eval_traces() -> None:
    rows = [
        {"trace_id": "t1", "span_id": "s1", "parent_span_id": None,
         "app_name": "apps_rfp"},
        {"trace_id": "t1", "span_id": "s2", "parent_span_id": "s1",
         "app_name": "apps_rfp"},
    ]
    r = check_no_eval_of_evaluator_circularity(rows)
    assert r.passed is True
    assert r.violation_count == 0
    assert r.control_id == CC_EVAL_01


def test_cc_eval_01_passes_with_apps_eval_root_no_descendants() -> None:
    rows = [
        {"trace_id": "t1", "span_id": "s1", "parent_span_id": None,
         "app_name": "apps_eval"},
        {"trace_id": "t1", "span_id": "s2", "parent_span_id": "s1",
         "app_name": "apps_rfp"},
    ]
    r = check_no_eval_of_evaluator_circularity(rows)
    assert r.passed is True


def test_cc_eval_01_fails_when_apps_eval_descendant_exists() -> None:
    rows = [
        {"trace_id": "t1", "span_id": "s1", "parent_span_id": None,
         "app_name": "apps_eval"},
        {"trace_id": "t1", "span_id": "s2", "parent_span_id": "s1",
         "app_name": "apps_eval", "span_name": "evaluator.invoke_evaluator"},
    ]
    r = check_no_eval_of_evaluator_circularity(rows)
    assert r.passed is False
    assert r.violation_count == 1
    assert r.violations[0]["descendant_span_id"] == "s2"
    assert "circularity" in r.failure_reasons[0]


def test_cc_eval_01_multiple_traces_isolated() -> None:
    """A violation in trace t1 must not affect trace t2's pass status."""
    rows = [
        # t1: circular
        {"trace_id": "t1", "span_id": "s1", "parent_span_id": None,
         "app_name": "apps_eval"},
        {"trace_id": "t1", "span_id": "s2", "parent_span_id": "s1",
         "app_name": "apps_eval"},
        # t2: clean apps_eval run
        {"trace_id": "t2", "span_id": "s3", "parent_span_id": None,
         "app_name": "apps_eval"},
        {"trace_id": "t2", "span_id": "s4", "parent_span_id": "s3",
         "app_name": "apps_rfp"},
    ]
    r = check_no_eval_of_evaluator_circularity(rows)
    assert r.violation_count == 1
    assert r.violations[0]["trace_id"] == "t1"


def test_cc_eval_01_missing_trace_id_recorded_in_notes() -> None:
    rows = [
        {"span_id": "s1", "parent_span_id": None, "app_name": "apps_eval"},
        {"trace_id": "", "span_id": "s2", "parent_span_id": None,
         "app_name": "apps_eval"},
    ]
    r = check_no_eval_of_evaluator_circularity(rows)
    assert r.passed is True  # no resolvable trace -> no violation
    assert any("missing or empty trace_id" in n for n in r.notes)
    assert r.query_summary["rows_without_trace_id"] == 2


# ---------------------------------------------------------------------------
# CC-EVAL-02 (apps_eval R3 contract leak)
# ---------------------------------------------------------------------------


def test_cc_eval_02_fails_when_apps_eval_emits_R3_contract_outside_surface() -> None:
    rows = [
        {"app_name": "apps_eval", "contract_name": "SealedArtifact",
         "span_id": "s1", "route_shape": "R3_grounded_read"},
    ]
    r = check_apps_eval_no_r3_contract_leak(rows)
    assert r.passed is False
    assert r.violation_count == 1
    assert r.violations[0]["contract_name"] == "SealedArtifact"
    assert r.control_id == CC_EVAL_02


def test_cc_eval_02_passes_for_non_r3_contracts() -> None:
    rows = [
        {"app_name": "apps_eval", "contract_name": "EvaluationResult",
         "span_id": "s1"},
        {"app_name": "apps_eval", "contract_name": "SomeOtherContract",
         "span_id": "s2"},
    ]
    r = check_apps_eval_no_r3_contract_leak(rows)
    assert r.passed is True
    assert r.violation_count == 0


def test_cc_eval_02_passes_when_r3_contract_on_allowed_surface() -> None:
    rows = [
        {"app_name": "apps_eval", "contract_name": "SealedArtifact",
         "span_id": "s1", "route_shape": "evaluator_only"},
    ]
    r = check_apps_eval_no_r3_contract_leak(rows)
    assert r.passed is True


def test_cc_eval_02_passes_with_custom_allowed_surfaces() -> None:
    rows = [
        {"app_name": "apps_eval", "contract_name": "L1PlanContract",
         "span_id": "s1", "route_shape": "custom_eval_surface"},
    ]
    r = check_apps_eval_no_r3_contract_leak(
        rows, allowed_surfaces=frozenset({"custom_eval_surface"})
    )
    assert r.passed is True


def test_cc_eval_02_ignores_rows_for_other_apps() -> None:
    rows = [
        {"app_name": "apps_rfp", "contract_name": "SealedArtifact",
         "span_id": "s1", "route_shape": "R3_grounded_read"},
    ]
    r = check_apps_eval_no_r3_contract_leak(rows)
    assert r.passed is True
    assert r.query_summary["rows_for_app"] == 0


# ---------------------------------------------------------------------------
# CC-UW-02 (apps_underwriting_ai R3 contract leak)
# ---------------------------------------------------------------------------


def test_cc_uw_02_fails_when_underwriting_emits_R3_contract_outside_surface() -> None:
    rows = [
        {"app_name": "apps_underwriting_ai", "contract_name": "SealedArtifact",
         "span_id": "s1", "route_shape": "R3_grounded_read"},
    ]
    r = check_underwriting_no_r3_contract_leak(rows)
    assert r.passed is False
    assert r.violation_count == 1
    assert r.control_id == CC_UW_02


def test_cc_uw_02_passes_on_allowed_regulatory_surface() -> None:
    rows = [
        {"app_name": "apps_underwriting_ai", "contract_name": "L1PlanContract",
         "span_id": "s1", "route_shape": "regulated_decision"},
    ]
    r = check_underwriting_no_r3_contract_leak(rows)
    assert r.passed is True


def test_cc_uw_02_passes_for_non_r3_contracts() -> None:
    rows = [
        {"app_name": "apps_underwriting_ai",
         "contract_name": "UnderwritingDecision", "span_id": "s1"},
    ]
    r = check_underwriting_no_r3_contract_leak(rows)
    assert r.passed is True


# ---------------------------------------------------------------------------
# CC-SHARED-03 (SealedArtifact proof-only)
# ---------------------------------------------------------------------------


def test_cc_shared_03_fails_when_production_SealedArtifact_from_proof_path() -> None:
    rows = [
        {
            "contract_name": "SealedArtifact",
            "source_path": "apps_shared/proof/scenario_base.py",
            "span_id": "s1",
            "trace_id": "t1",
            "environment": "production",
        },
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is False
    assert r.violation_count == 1
    assert "apps_shared/proof/" in r.violations[0]["source_path"]
    assert r.control_id == CC_SHARED_03


def test_cc_shared_03_passes_when_proof_row_is_explicitly_test_environment() -> None:
    rows = [
        {
            "contract_name": "SealedArtifact",
            "source_path": "apps_shared/proof/scenario_base.py",
            "span_id": "s1",
            "environment": "test",
        },
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is True


def test_cc_shared_03_passes_when_span_kind_is_proof() -> None:
    rows = [
        {
            "contract_name": "SealedArtifact",
            "source_path": "apps_shared/proof/scenario_base.py",
            "span_id": "s1",
            "span_kind": "proof",
        },
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is True


def test_cc_shared_03_passes_when_source_outside_proof_path() -> None:
    rows = [
        {
            "contract_name": "SealedArtifact",
            "source_path": "agentic_core/L2_execution/observability/l2_otel_emitter.py",
            "span_id": "s1",
        },
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is True


def test_cc_shared_03_handles_windows_path_style() -> None:
    rows = [
        {
            "contract_name": "SealedArtifact",
            "source_path": "apps_shared\\proof\\scenario_base.py",
            "span_id": "s1",
            "environment": "production",
        },
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is False


def test_cc_shared_03_unknown_source_recorded_in_notes_not_violation() -> None:
    rows = [
        {"contract_name": "SealedArtifact", "span_id": "s1"},  # no source_path
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is True
    assert r.query_summary["rows_with_unknown_source"] == 1
    assert any("unknown" in n.lower() or "source_path" in n for n in r.notes)


def test_cc_shared_03_reads_from_attributes_dict() -> None:
    """source_path may live inside an attributes mapping."""
    rows = [
        {
            "contract_name": "SealedArtifact",
            "span_id": "s1",
            "environment": "production",
            "attributes": {"source_path": "apps_shared/proof/harness.py"},
        },
    ]
    r = check_apps_shared_sealed_artifact_proof_only(rows)
    assert r.passed is False


# ---------------------------------------------------------------------------
# NegativeControlResult schema invariants
# ---------------------------------------------------------------------------


def test_result_serializable_to_json_safe_dict() -> None:
    r = check_no_eval_of_evaluator_circularity(
        [
            {"trace_id": "t1", "span_id": "s1", "parent_span_id": None,
             "app_name": "apps_eval"},
            {"trace_id": "t1", "span_id": "s2", "parent_span_id": "s1",
             "app_name": "apps_eval"},
        ]
    )
    d = r.to_dict()
    assert d["control_id"] == CC_EVAL_01
    assert d["passed"] is False
    assert d["violation_count"] == 1
    # Must survive json.dumps (no frozen types leak through).
    json.dumps(d)


def test_result_rejects_passed_with_violations() -> None:
    with pytest.raises(ValueError, match="contradicts violation_count"):
        NegativeControlResult(
            control_id=CC_EVAL_01,
            passed=True,  # inconsistent with len(violations)=1
            violation_count=1,
            violations=({"x": 1},),
            query_summary={},
            failure_reasons=(),
            notes=(),
        )


def test_result_rejects_count_mismatch() -> None:
    with pytest.raises(ValueError, match="violation_count=2 does not match"):
        NegativeControlResult(
            control_id=CC_EVAL_01,
            passed=False,
            violation_count=2,  # but violations has 1
            violations=({"x": 1},),
            query_summary={},
            failure_reasons=(),
            notes=(),
        )


def test_result_rejects_empty_control_id() -> None:
    with pytest.raises(ValueError, match="control_id must be non-empty"):
        NegativeControlResult(
            control_id="",
            passed=True,
            violation_count=0,
            violations=(),
            query_summary={},
            failure_reasons=(),
            notes=(),
        )


# ---------------------------------------------------------------------------
# Defensive field handling
# ---------------------------------------------------------------------------


def test_helpers_tolerate_empty_row_iterable() -> None:
    assert check_no_eval_of_evaluator_circularity([]).passed is True
    assert check_apps_eval_no_r3_contract_leak([]).passed is True
    assert check_underwriting_no_r3_contract_leak([]).passed is True
    assert check_apps_shared_sealed_artifact_proof_only([]).passed is True


def test_helpers_tolerate_rows_missing_optional_fields() -> None:
    """Rows missing app_name, contract_name, etc. must not crash."""
    rows = [
        {},
        {"span_id": "s1"},
        {"trace_id": "t1"},
        {"app_name": None, "contract_name": None},
    ]
    # None of these may raise.
    assert check_no_eval_of_evaluator_circularity(rows).passed is True
    assert check_apps_eval_no_r3_contract_leak(rows).passed is True
    assert check_underwriting_no_r3_contract_leak(rows).passed is True
    assert check_apps_shared_sealed_artifact_proof_only(rows).passed is True


def test_helpers_read_app_name_from_attributes() -> None:
    """app_name may live under attributes rather than as a top-level field."""
    rows = [
        {
            "trace_id": "t1",
            "span_id": "s1",
            "parent_span_id": None,
            "attributes": {"app_name": "apps_eval"},
        },
        {
            "trace_id": "t1",
            "span_id": "s2",
            "parent_span_id": "s1",
            "attributes": {"app_name": "apps_eval"},
        },
    ]
    r = check_no_eval_of_evaluator_circularity(rows)
    assert r.passed is False
    assert r.violation_count == 1


# ---------------------------------------------------------------------------
# R3_CONTRACT_SET sanity
# ---------------------------------------------------------------------------


def test_R3_CONTRACT_SET_contains_canonical_8_plus_PromptEnvelope() -> None:
    """Mirrors R3_GROUNDED_READ_CONTRACTS + the PromptEnvelope
    equivalence-group member."""
    expected = {
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "PromptEnvelope",
        "SealedArtifact",
        "ExitReviewPacket",
    }
    assert R3_CONTRACT_SET == expected
