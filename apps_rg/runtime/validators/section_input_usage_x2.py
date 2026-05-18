"""Shared deterministic X2 gates for ``section_input_usage_ledger`` input-authority contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.section_proof.section_input_usage_ledger import (
    classify_source_fact_ids,
    summarize_claim_ledger_proof_axes,
)
from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult


def _load_json(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def append_section_input_usage_x2_gates(
    gates: list[X2GateResult],
    *,
    artifacts_dir: Path,
    allowed_fact_ids: set[str],
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any] | None,
) -> None:
    """Append standard input-authority gates (mutates ``gates``)."""

    def add(gate_id: str, passed: bool, observed: Any, threshold: Any, reason: str | None = None) -> None:
        gates.append(
            X2GateResult(
                gate_id=gate_id,
                gate_type="deterministic",
                pass_=passed,
                observed_value=observed,
                threshold=threshold,
                failure_reason=None if passed else reason,
                evidence_ref=gate_id,
            )
        )

    led_path = artifacts_dir / "section_input_usage_ledger.json"
    led_raw = _load_json(led_path)
    schema_ok = isinstance(led_raw, dict) and led_raw.get("schema") == "section_input_usage_ledger_v1"
    add(
        "x2_section_input_usage_ledger_present",
        schema_ok,
        led_raw.get("schema") if isinstance(led_raw, dict) else None,
        "section_input_usage_ledger_v1",
        None if schema_ok else "section_input_usage_ledger.json missing or schema mismatch",
    )

    riu = led_raw.get("required_input_usage") if isinstance(led_raw, dict) else None
    riu_ok = isinstance(riu, dict)

    jd_block = (riu or {}).get("jd_text") if riu_ok else None
    jd_req_ok = (
        isinstance(jd_block, dict)
        and jd_block.get("required") is True
        and jd_block.get("used") is True
        and jd_block.get("authority") == "TARGETING_INPUT"
    )
    add(
        "x2_jd_used_as_required_targeting_input",
        jd_req_ok,
        jd_block,
        "required_used_TARGETING_INPUT",
        None
        if jd_req_ok
        else "JD must be present in runtime payload and marked required TARGETING_INPUT with used=true",
    )

    br_block = (riu or {}).get("briefing_research") if riu_ok else None
    br_req_ok = (
        isinstance(br_block, dict)
        and br_block.get("required") is True
        and br_block.get("used") is True
        and br_block.get("authority") == "CONTEXT_INPUT"
    )
    add(
        "x2_briefing_used_as_required_context_input",
        br_req_ok,
        br_block,
        "required_used_CONTEXT_INPUT",
        None
        if br_req_ok
        else "Briefing/research must be present and marked required CONTEXT_INPUT with used=true",
    )

    tt_block = (riu or {}).get("target_title") if riu_ok else None
    tc_block = (riu or {}).get("target_company") if riu_ok else None
    title_co_ok = (
        isinstance(tt_block, dict)
        and isinstance(tc_block, dict)
        and tt_block.get("required") is True
        and tt_block.get("used") is True
        and tt_block.get("authority") == "POSITIONING_INPUT"
        and tc_block.get("required") is True
        and tc_block.get("used") is True
        and tc_block.get("authority") == "POSITIONING_INPUT"
    )
    add(
        "x2_title_company_used_as_required_positioning_input",
        title_co_ok,
        {"target_title": tt_block, "target_company": tc_block},
        "required_used_POSITIONING_INPUT_both",
        None
        if title_co_ok
        else "Target title and company must be present as required POSITIONING_INPUT with used=true",
    )

    eb = led_raw.get("evidence_boundary") if isinstance(led_raw, dict) else None
    eb_ok = isinstance(eb, dict)
    conv_ok = eb_ok and eb.get("non_evidence_inputs_used_as_claim_evidence") is not True
    add(
        "x2_no_non_evidence_inputs_as_claim_evidence",
        conv_ok,
        eb.get("non_evidence_inputs_used_as_claim_evidence") if eb_ok else None,
        False,
        None
        if conv_ok
        else "Non-evidence inputs must not be converted into claim evidence (model flags or claim rows)",
    )

    ids_in_rows_bad = False
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if not s:
                continue
            clf = classify_source_fact_ids([s], allowed_fact_ids=set(allowed_fact_ids))
            if clf["forbidden_hits"] or clf["briefing_like"] or clf["jd_like"]:
                ids_in_rows_bad = True
                break
        if ids_in_rows_bad:
            break

    ledger_says_bad = eb_ok and eb.get("non_evidence_inputs_in_source_fact_ids") is True
    no_reserved_ids_ok = not ids_in_rows_bad and not ledger_says_bad
    add(
        "x2_no_non_evidence_inputs_in_source_fact_ids",
        no_reserved_ids_ok,
        {
            "row_scan_found_reserved_non_resume_ids": ids_in_rows_bad,
            "ledger_non_evidence_inputs_in_source_fact_ids": eb.get(
                "non_evidence_inputs_in_source_fact_ids"
            )
            if eb_ok
            else None,
        },
        "reserved_non_resume_ids_absent_in_source_fact_ids",
        None
        if no_reserved_ids_ok
        else "source_fact_ids must not contain targeting/context/positioning-shaped reserved tokens",
    )

    selected_only_ok = True
    bad_ids: list[str] = []
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if not s:
                continue
            clf = classify_source_fact_ids([s], allowed_fact_ids=set(allowed_fact_ids))
            if clf["forbidden_hits"] or clf["unknown"]:
                selected_only_ok = False
                bad_ids.append(s)
    add(
        "x2_selected_fact_ids_only",
        selected_only_ok,
        sorted(set(bad_ids))[:32],
        "subset_of_ALLOWED_SOURCE_FACT_IDS",
        None if selected_only_ok else "source_fact_ids include non-allowed / forbidden tokens",
    )

    summary = summarize_claim_ledger_proof_axes(list(claim_ledger), allowed_fact_ids=set(allowed_fact_ids))
    claims_ok = int(summary.get("unsupported_claim_count") or 0) == 0 and int(
        summary.get("claims_with_targeting_input_in_source_fact_ids") or 0
    ) == 0 and int(summary.get("claims_with_context_input_in_source_fact_ids") or 0) == 0
    add(
        "x2_section_claims_supported_by_base_resume",
        claims_ok,
        summary,
        "no_unsupported_and_no_non_evidence_source_fact_id_claim_rows",
        None
        if claims_ok
        else "Material claims lack selected base-resume support or attribute non-evidence inputs as fact IDs",
    )

    cov_pass = True if text_claim_coverage is None else bool(text_claim_coverage.get("overall_pass"))
    led_summary = (led_raw or {}).get("claim_support_summary") if isinstance(led_raw, dict) else None
    acct_ok = isinstance(led_summary, dict)
    if acct_ok and isinstance(summary, dict):
        for k in (
            "displayed_claim_count",
            "unsupported_claim_count",
            "orphan_source_fact_id_count",
            "claims_with_targeting_input_in_source_fact_ids",
            "claims_with_context_input_in_source_fact_ids",
        ):
            if int(led_summary.get(k) or 0) != int(summary.get(k) or 0):
                acct_ok = False
                break
    acct_ok = acct_ok and cov_pass
    add(
        "x2_input_usage_accounting_consistent",
        acct_ok,
        {"ledger_summary": led_summary, "runtime_summary": summary, "coverage_overall_pass": cov_pass},
        "ledger_matches_claim_scan_and_coverage_pass",
        None if acct_ok else "section_input_usage_ledger counts mismatch or text_claim_coverage failed",
    )


__all__ = ["append_section_input_usage_x2_gates"]
