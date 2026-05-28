"""Monotonic acceptance rules for executive_summary synthesis regen (apps_rg only)."""

from __future__ import annotations

import re
from typing import Any, Literal

from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    gate_ids_from_x2_reject_reason,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_sentence_count_6,
)

RepairContext = Literal["synthesis_regen", "judge_x2_repair"]

# Post-judge X2 repair may tighten prose / merge claims while fixing shape gates.
JUDGE_X2_REPAIR_WAIVE_SHRINK_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_exec_summary_sentence_count_6",
        "x2_executive_summary_synthesis_quality",
        "x2_no_inferred_bridge_claims",
        "x2_exec_summary_evidence_utilization",
        "x2_exec_summary_mechanical_opener_stack_zero",
        "x2_exec_summary_stock_bridge_max_two",
        "x2_exec_summary_s5_no_derivatives_inventory",
        "x2_exec_summary_meta_filler_zero",
        "x2_exec_summary_cross_fact_conflation_zero",
        "x2_exec_summary_no_sentence_fragment",
        "x2_exec_summary_display_override_compliance",
    }
)

JUDGE_REGEN_COVERAGE_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_sentence_coverage_pass",
        "x2_unsupported_claim_zero",
        "x2_claim_coverage_accounting_consistent",
        "x2_material_clause_coverage_100",
        "x2_input_usage_accounting_consistent",
        "x2_claim_ledger_row_count_matches_sentence_count",
        "x2_self_check_claim_ledger_consistent",
    }
)

JUDGE_X2_REPAIR_ALLOW_SUBSTANCE_REGRESSION_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_executive_summary_synthesis_quality",
        "x2_no_inferred_bridge_claims",
        "x2_exec_summary_sentence_count_6",
        "x2_exec_summary_evidence_utilization",
    }
)


def _resume_word_count(text: str) -> int:
    return len(re.findall(r"\S+", str(text or "").strip()))


def _unique_source_fact_ids(claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if s:
                ids.add(s)
    return ids


def _prior_failed_sentence_count(prior_reject_reason: str, gate_ids: frozenset[str]) -> bool:
    if "x2_exec_summary_sentence_count_6" in gate_ids:
        return True
    blob = str(prior_reject_reason or "").lower()
    return (
        "exactly 6" in blob
        or "6 sentences" in blob
        or "sentence_count_6" in blob
        or "found 3" in blob
        or "found 2" in blob
        or "found 1" in blob
        or "legacy 2-3" in blob
    )


def _prior_needs_evidence_weave(prior_reject_reason: str, gate_ids: frozenset[str]) -> bool:
    if gate_ids & JUDGE_REGEN_COVERAGE_GATE_IDS:
        return True
    if gate_ids & {
        "x2_exec_summary_evidence_utilization",
        "x2_claim_ledger_materialized_or_gap_excused",
    }:
        return True
    blob = str(prior_reject_reason or "").lower()
    return (
        "claim_ledger_rows" in blob
        or "evidence_utilization" in blob
        or "need_at_least" in blob
        or "sentence_" in blob
        and "below_" in blob
    )


def _prior_needs_prose_tighten(prior_reject_reason: str, gate_ids: frozenset[str]) -> bool:
    if gate_ids & {
        "x2_executive_summary_synthesis_quality",
        "x2_no_inferred_bridge_claims",
        "x2_exec_summary_no_mechanism_inventory",
        "x2_exec_summary_meta_filler_zero",
    }:
        return True
    blob = str(prior_reject_reason or "").lower()
    return (
        "mechanism_inventory" in blob
        or "mechanism inventory" in blob
        or "meta or filler" in blob
        or "credential" in blob
        or "generic_exec_opener" in blob
        or "synthesis_quality" in blob
        or "inferred_bridge" in blob
    )


def evaluate_synthesis_regen_monotonicity(
    *,
    prior_parsed: dict[str, Any],
    prior_reject_reason: str,
    new_parsed: dict[str, Any],
    max_shrink_ratio: float = 0.10,
    failed_gate_ids: frozenset[str] | None = None,
    repair_context: RepairContext = "synthesis_regen",
) -> tuple[bool, dict[str, Any]]:
    """Reject regen candidates that regress substance vs the prior attempt.

    Waives shrink/ledger regression when the prior failure was evidence weave or
    the candidate clearly improves ledger coverage (more rows or unique fact ids).

    ``repair_context='judge_x2_repair'``: compare against the last X2-green baseline while
    fixing post-judge regen X2 failures — allow controlled fact/ledger shrink when gate IDs
    indicate synthesis/bridge/sentence-shape repair (RCA: gate-id reject_reason did not
    trigger legacy prose waivers).
    """
    gate_ids = failed_gate_ids or gate_ids_from_x2_reject_reason(prior_reject_reason)
    pre_text = str(prior_parsed.get("resume_display_text") or "")
    post_text = str(new_parsed.get("resume_display_text") or "")
    pre_wc = _resume_word_count(pre_text)
    post_wc = _resume_word_count(post_text)
    pre_ledger = list(prior_parsed.get("claim_ledger") or [])
    post_ledger = list(new_parsed.get("claim_ledger") or [])
    pre_facts = _unique_source_fact_ids(pre_ledger)
    post_facts = _unique_source_fact_ids(post_ledger)
    pre_sent_ok, _ = check_exec_summary_sentence_count_6(pre_text)
    post_sent_ok, _ = check_exec_summary_sentence_count_6(post_text)

    ledger_rows_gained = len(post_ledger) > len(pre_ledger)
    facts_gained = len(post_facts) > len(pre_facts)
    sentence_repair = _prior_failed_sentence_count(prior_reject_reason, gate_ids)
    evidence_repair = _prior_needs_evidence_weave(prior_reject_reason, gate_ids)
    prose_repair = _prior_needs_prose_tighten(prior_reject_reason, gate_ids)
    judge_x2_shape_repair = repair_context == "judge_x2_repair" and bool(
        gate_ids & JUDGE_X2_REPAIR_WAIVE_SHRINK_GATE_IDS
    )
    allow_substance_regression = judge_x2_shape_repair and bool(
        gate_ids & JUDGE_X2_REPAIR_ALLOW_SUBSTANCE_REGRESSION_GATE_IDS
    )

    detail: dict[str, Any] = {
        "repair_context": repair_context,
        "failed_gate_ids": sorted(gate_ids),
        "pre_resume_word_count": pre_wc,
        "post_resume_word_count": post_wc,
        "pre_claim_ledger_rows": len(pre_ledger),
        "post_claim_ledger_rows": len(post_ledger),
        "pre_unique_source_fact_ids": len(pre_facts),
        "post_unique_source_fact_ids": len(post_facts),
        "prior_failed_sentence_count": sentence_repair,
        "prior_needs_evidence_weave": evidence_repair,
        "prior_needs_prose_tighten": prose_repair,
        "judge_x2_shape_repair": judge_x2_shape_repair,
        "allow_substance_regression": allow_substance_regression,
        "ledger_rows_gained": ledger_rows_gained,
        "facts_gained": facts_gained,
    }
    reasons: list[str] = []

    waive_shrink = (
        sentence_repair
        or judge_x2_shape_repair
        or (evidence_repair and (ledger_rows_gained or facts_gained))
        or (evidence_repair and post_wc >= pre_wc)
    )
    if post_wc < pre_wc and pre_wc > 0 and not waive_shrink:
        shrink = (pre_wc - post_wc) / pre_wc
        detail["shrink_ratio"] = round(shrink, 4)
        if shrink > max_shrink_ratio:
            reasons.append(
                f"word_count_shrink_{shrink:.0%}_exceeds_{max_shrink_ratio:.0%}_without_sentence_count_repair"
            )

    if len(post_ledger) < len(pre_ledger) and not (evidence_repair and ledger_rows_gained):
        if not allow_substance_regression:
            reasons.append("claim_ledger_row_count_regressed")

    if post_facts and pre_facts and post_facts < pre_facts and not (evidence_repair and facts_gained):
        if not allow_substance_regression:
            reasons.append("unique_source_fact_ids_regressed")

    if pre_sent_ok and not post_sent_ok:
        reasons.append("sentence_count_regressed")

    # Prose-tighten regen must not drop weave progress when prior also failed utilization.
    if (
        prose_repair
        and evidence_repair
        and not ledger_rows_gained
        and len(post_ledger) < len(pre_ledger)
        and not allow_substance_regression
    ):
        reasons.append("prose_repair_dropped_ledger_rows")

    accepted = not reasons
    detail["accepted"] = accepted
    detail["rejection_reasons"] = reasons
    detail["shrink_waived"] = waive_shrink
    return accepted, detail
