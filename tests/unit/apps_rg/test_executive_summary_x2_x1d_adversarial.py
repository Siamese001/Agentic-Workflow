"""Adversarial / break attempts for X2/X1D contract, monotonicity, and judge X2 repair.

These tests encode failure modes we do not want regressions on (Brown & Brown cycle-2 class).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    repair_judge_regen_after_x2_fail,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    failed_x2_gate_ids,
    format_x2_gate_failures_reject_reason,
    gate_ids_from_x2_reject_reason,
)
from apps_rg.runtime.sections.executive_summary_synthesis_monotonic import (
    JUDGE_X2_REPAIR_ALLOW_SUBSTANCE_REGRESSION_GATE_IDS,
    JUDGE_X2_REPAIR_WAIVE_SHRINK_GATE_IDS,
    evaluate_synthesis_regen_monotonicity,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
    section_product_shape,
)
from apps_rg.runtime.sections.section_x2_x1d_contract import (
    audit_lane_x2_x1d_drift,
    extract_runtime_x2_gate_ids,
    lane_x2_x1d_spec,
)
from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_sentence_count_6

_REPO = Path(__file__).resolve().parents[3]
_MATRIX = _REPO / "artifacts" / "apps_rg" / "prompt_authority" / "x2_x1d_alignment_matrix.json"

_SIX_SENT = (
    "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu. "
    "Beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu. "
    "Gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi. "
    "Delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron. "
    "Epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi. "
    "Zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma."
)


def _ledger(n: int, *, extra_on_first: bool = False) -> list[dict]:
    rows = []
    for i in range(n):
        fids = [f"fact_{i:03d}"]
        if i == 0 and extra_on_first:
            fids.append("fact_extra")
        rows.append({"claim_text": f"claim {i}", "source_fact_ids": fids})
    return rows


def _brown_brown_failed_gates() -> list[dict]:
    return [
        {"gate_id": "x2_exec_summary_sentence_count_6", "pass": False, "reason": "fail"},
        {"gate_id": "x2_executive_summary_synthesis_quality", "pass": False, "reason": "fail"},
        {"gate_id": "x2_no_inferred_bridge_claims", "pass": False, "reason": "fail"},
    ]


# --- Monotonicity: must reject bad repairs -----------------------------------


def test_adversarial_wrong_context_rejects_brown_brown_fact_merge() -> None:
    """Same 7→6 fact merge must FAIL under synthesis_regen (the cycle-2 bug)."""
    prior = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(6, extra_on_first=True)}
    post = {"resume_display_text": _SIX_SENT[:200], "claim_ledger": _ledger(6)}
    reject = format_x2_gate_failures_reject_reason(_brown_brown_failed_gates())
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason=reject,
        new_parsed=post,
        failed_gate_ids=failed_x2_gate_ids(_brown_brown_failed_gates()),
        repair_context="synthesis_regen",
    )
    assert ok is False
    assert detail["rejection_reasons"]


def test_adversarial_judge_x2_repair_rejects_sentence_regression_from_good_baseline() -> None:
    prior = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(6, extra_on_first=True)}
    post = {"resume_display_text": "Only one short sentence.", "claim_ledger": _ledger(1)}
    gates = failed_x2_gate_ids(_brown_brown_failed_gates())
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason=format_x2_gate_failures_reject_reason(_brown_brown_failed_gates()),
        new_parsed=post,
        failed_gate_ids=gates,
        repair_context="judge_x2_repair",
    )
    assert ok is False
    assert "sentence_count_regressed" in detail["rejection_reasons"]


def test_adversarial_meta_filler_only_does_not_allow_fact_regression() -> None:
    """Waive shrink gate set includes meta_filler; substance regression set must not."""
    assert "x2_exec_summary_meta_filler_zero" in JUDGE_X2_REPAIR_WAIVE_SHRINK_GATE_IDS
    assert "x2_exec_summary_meta_filler_zero" not in JUDGE_X2_REPAIR_ALLOW_SUBSTANCE_REGRESSION_GATE_IDS
    prior = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(6, extra_on_first=True)}
    post = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(4)}
    gates = frozenset({"x2_exec_summary_meta_filler_zero"})
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason="x2_exec_summary_meta_filler_zero: fail",
        new_parsed=post,
        failed_gate_ids=gates,
        repair_context="judge_x2_repair",
    )
    assert ok is False
    assert any("claim_ledger" in r or "unique_source" in r for r in detail["rejection_reasons"])


def test_adversarial_empty_failed_gate_ids_no_judge_waivers() -> None:
    prior = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(6, extra_on_first=True)}
    short = "One two three four five six seven eight. " * 4
    post = {"resume_display_text": short, "claim_ledger": _ledger(3)}
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason="unrelated prose issue",
        new_parsed=post,
        failed_gate_ids=frozenset(),
        repair_context="judge_x2_repair",
    )
    assert ok is False
    assert detail.get("judge_x2_shape_repair") is False


def test_adversarial_gate_id_parsing_ignores_non_x2_tokens() -> None:
    reason = "not_a_gate: fail; x2_exec_summary_sentence_count_6: found 4"
    ids = gate_ids_from_x2_reject_reason(reason)
    assert ids == frozenset({"x2_exec_summary_sentence_count_6"})


# --- Per-lane drift contract: structural integrity ---------------------------


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_adversarial_lane_runtime_superset_of_ssot(lane: str) -> None:
    spec = lane_x2_x1d_spec(lane)
    runtime = extract_runtime_x2_gate_ids(
        x2_module_ref=spec.x2_module_ref,
        x2_run_function=spec.x2_run_function,
    )
    shape = section_product_shape(lane)
    missing = [g for g in shape.required_gate_ids if g not in runtime]
    assert not missing, f"{lane}: SSOT gates missing from runtime: {missing}"


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_adversarial_lane_audit_clean(lane: str) -> None:
    violations = audit_lane_x2_x1d_drift(lane)
    assert violations == [], "\n".join(f"{v.kind}: {v.detail}" for v in violations)


def test_adversarial_exec_retired_gates_not_in_runtime() -> None:
    runtime = extract_runtime_x2_gate_ids(
        x2_module_ref="apps_rg/runtime/validators/executive_summary_x2.py",
        x2_run_function="run_x2_gates",
    )
    overlap = RETIRED_EXEC_SUMMARY_X2_GATE_IDS & runtime
    assert not overlap, f"retired gates still emitted: {sorted(overlap)}"


def test_adversarial_matrix_samples_exist_in_runtime_per_lane() -> None:
    matrix = json.loads(_MATRIX.read_text(encoding="utf-8"))
    rows = {r["section_id"]: r for r in matrix["sections"]}
    for lane in GENERATED_LANES:
        spec = lane_x2_x1d_spec(lane)
        runtime = extract_runtime_x2_gate_ids(
            x2_module_ref=spec.x2_module_ref,
            x2_run_function=spec.x2_run_function,
        )
        for sample in rows[lane].get("x2_gates_sample") or []:
            assert sample in runtime, f"{lane}: matrix sample {sample!r} not in runtime"


def test_adversarial_simulated_missing_ssot_gate_would_fail_audit() -> None:
    """If SSOT listed a gate runtime does not emit, audit must catch it."""
    shape = section_product_shape("headline")
    runtime = extract_runtime_x2_gate_ids(
        x2_module_ref=shape.x2_module_ref,
        x2_run_function="run_headline_x2_gates",
    )
    fake_ssot = frozenset((*shape.required_gate_ids, "x2___synthetic_missing_gate___"))
    missing = sorted(fake_ssot - runtime)
    assert "x2___synthetic_missing_gate___" in missing


# --- repair_judge_regen_after_x2_fail integration (mocked LLM) -------------


def test_adversarial_x2_repair_accepts_when_monotonicity_passes_mock_llm() -> None:
    baseline = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(6, extra_on_first=True)}
    failed = _brown_brown_failed_gates()
    repaired = {
        "resume_display_text": _SIX_SENT,
        "claim_ledger": _ledger(6),
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
    }
    mock_result = MagicMock()
    mock_result.runtime_generation_status = "REAL_LLM"
    mock_result.raw_model_output = json.dumps(repaired)
    mock_result.to_dict.return_value = {"runtime_generation_status": "REAL_LLM"}

    with patch(
        "apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch.generate_section",
        return_value=mock_result,
    ):
        _raw, parsed, receipt = repair_judge_regen_after_x2_fail(
            [{"role": "user", "content": "x"}],
            {},
            baseline_parsed=baseline,
            regen_raw="{}",
            regen_parsed={"resume_display_text": "bad", "claim_ledger": []},
            failed_x2_gates=failed,
            selected_fact_plan={"facts": []},
            allowed_fact_ids={f"fact_{i:03d}" for i in range(6)},
            strategy_executive=True,
        )
    assert receipt.get("accepted") is True
    assert receipt.get("repair_context") is None  # schema field optional
    assert receipt.get("failed_gate_ids")
    assert "monotonicity" in receipt
    assert receipt["monotonicity"]["accepted"] is True
    assert parsed.get("resume_display_text")


def test_adversarial_x2_repair_rejects_when_repair_would_drop_sentences_mock_llm() -> None:
    baseline = {"resume_display_text": _SIX_SENT, "claim_ledger": _ledger(6)}
    failed = _brown_brown_failed_gates()
    bad_repair = {"resume_display_text": "One sentence only.", "claim_ledger": _ledger(1)}
    mock_result = MagicMock()
    mock_result.runtime_generation_status = "REAL_LLM"
    mock_result.raw_model_output = json.dumps(bad_repair)
    mock_result.to_dict.return_value = {}

    with patch(
        "apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch.generate_section",
        return_value=mock_result,
    ):
        _raw, _parsed, receipt = repair_judge_regen_after_x2_fail(
            [],
            {},
            baseline_parsed=baseline,
            regen_raw="{}",
            regen_parsed=bad_repair,
            failed_x2_gates=failed,
            selected_fact_plan={"facts": []},
            allowed_fact_ids=set(),
            strategy_executive=True,
        )
    assert receipt.get("accepted") is False
    assert receipt.get("rejected") == "monotonicity"


def test_six_sent_fixture_is_six_sentences() -> None:
    ok, _ = check_exec_summary_sentence_count_6(_SIX_SENT)
    assert ok is True
