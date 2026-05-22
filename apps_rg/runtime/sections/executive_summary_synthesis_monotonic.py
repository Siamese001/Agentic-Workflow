"""Monotonic acceptance rules for executive_summary synthesis regen (apps_rg only)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_sentence_count_4_5,
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


def _prior_failed_sentence_count(prior_reject_reason: str) -> bool:
    blob = str(prior_reject_reason or "").lower()
    return (
        "4-5 sentences" in blob
        or "4 or 5" in blob
        or "found 3" in blob
        or "found 2" in blob
        or "found 1" in blob
        or "legacy 2-3" in blob
    )


def _prior_needs_evidence_weave(prior_reject_reason: str) -> bool:
    blob = str(prior_reject_reason or "").lower()
    return (
        "claim_ledger_rows" in blob
        or "evidence_utilization" in blob
        or "need_at_least" in blob
        or "sentence_" in blob and "below_" in blob
    )


def _prior_needs_prose_tighten(prior_reject_reason: str) -> bool:
    blob = str(prior_reject_reason or "").lower()
    return (
        "mechanism_inventory" in blob
        or "mechanism inventory" in blob
        or "meta or filler" in blob
        or "credential" in blob
        or "generic_exec_opener" in blob
    )


def evaluate_synthesis_regen_monotonicity(
    *,
    prior_parsed: dict[str, Any],
    prior_reject_reason: str,
    new_parsed: dict[str, Any],
    max_shrink_ratio: float = 0.10,
) -> tuple[bool, dict[str, Any]]:
    """Reject regen candidates that regress substance vs the prior attempt.

    Waives shrink/ledger regression when the prior failure was evidence weave or
    the candidate clearly improves ledger coverage (more rows or unique fact ids).
    """
    pre_text = str(prior_parsed.get("resume_display_text") or "")
    post_text = str(new_parsed.get("resume_display_text") or "")
    pre_wc = _resume_word_count(pre_text)
    post_wc = _resume_word_count(post_text)
    pre_ledger = list(prior_parsed.get("claim_ledger") or [])
    post_ledger = list(new_parsed.get("claim_ledger") or [])
    pre_facts = _unique_source_fact_ids(pre_ledger)
    post_facts = _unique_source_fact_ids(post_ledger)
    pre_sent_ok, _ = check_exec_summary_sentence_count_4_5(pre_text)
    post_sent_ok, _ = check_exec_summary_sentence_count_4_5(post_text)

    ledger_rows_gained = len(post_ledger) > len(pre_ledger)
    facts_gained = len(post_facts) > len(pre_facts)
    evidence_repair = _prior_needs_evidence_weave(prior_reject_reason)
    prose_repair = _prior_needs_prose_tighten(prior_reject_reason)

    detail: dict[str, Any] = {
        "pre_resume_word_count": pre_wc,
        "post_resume_word_count": post_wc,
        "pre_claim_ledger_rows": len(pre_ledger),
        "post_claim_ledger_rows": len(post_ledger),
        "pre_unique_source_fact_ids": len(pre_facts),
        "post_unique_source_fact_ids": len(post_facts),
        "prior_failed_sentence_count": _prior_failed_sentence_count(prior_reject_reason),
        "prior_needs_evidence_weave": evidence_repair,
        "ledger_rows_gained": ledger_rows_gained,
        "facts_gained": facts_gained,
    }
    reasons: list[str] = []

    waive_shrink = (
        _prior_failed_sentence_count(prior_reject_reason)
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
        reasons.append("claim_ledger_row_count_regressed")

    if post_facts and pre_facts and post_facts < pre_facts and not (evidence_repair and facts_gained):
        reasons.append("unique_source_fact_ids_regressed")

    if pre_sent_ok and not post_sent_ok:
        reasons.append("sentence_count_regressed")

    # Prose-tighten regen must not drop weave progress when prior also failed utilization.
    if prose_repair and evidence_repair and not ledger_rows_gained and len(post_ledger) < len(pre_ledger):
        reasons.append("prose_repair_dropped_ledger_rows")

    accepted = not reasons
    detail["accepted"] = accepted
    detail["rejection_reasons"] = reasons
    detail["shrink_waived"] = waive_shrink
    return accepted, detail
