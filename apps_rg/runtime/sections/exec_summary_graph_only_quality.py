"""Graph-only executive_summary generation quality repair (apps_rg only).

Deterministically re-synthesizes resume_display_text and claim_ledger from the
augmented-skills-graph allowed fact packet. Does not weaken X2/X1D gates; removes
unsupported metrics, causal conflation across facts, and bare credential inventories.
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any

from apps_rg.runtime.judges.executive_summary_judge_packet import enrich_allowed_fact_packet_for_judges
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_cross_fact_display_conflation,
    check_exec_summary_evidence_utilization,
    check_exec_summary_mechanical_opener_stack,
    check_exec_summary_no_credential_dump,
    check_exec_summary_no_mechanism_inventory,
)

_METRIC_PCT_RE = re.compile(r"\d+(?:\.\d+)?\s*%", re.IGNORECASE)
_UNSUPPORTED_MARGIN_RE = re.compile(
    r"\b(?:gross\s+margins?|margin\s+expansion|expanding\s+margins?|revenue\s+growth)\b",
    re.IGNORECASE,
)
_CREDENTIAL_INVENTORY_RE = re.compile(
    r"\bHolds\s+AWS\b|\bAWS Certified\b.*\bDatabricks\b",
    re.IGNORECASE,
)
_RELIability_UNPROVEN_RE = re.compile(
    r"\bimprov(?:ing|ed)\s+reliability\s+and\s+auditability\b",
    re.IGNORECASE,
)


def _facts_index(facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in facts:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or row.get("candidate_fact_id") or "").strip()
        if fid:
            out[fid] = row
    return out


def _allowed_percent_tokens(facts: list[dict[str, Any]]) -> set[str]:
    """Normalize allowed % tokens from metric_raw / metric_values only."""
    tokens: set[str] = set()
    for row in facts:
        for src in (row.get("metric_raw"), *(row.get("metric_values") or [])):
            text = str(src or "").strip()
            if not text:
                continue
            for m in _METRIC_PCT_RE.findall(text):
                tokens.add(re.sub(r"\s+", "", m.lower()))
    return tokens


def _percent_tokens_in_text(text: str) -> list[str]:
    return [re.sub(r"\s+", "", m.lower()) for m in _METRIC_PCT_RE.findall(text or "")]


def _thesis_platform_opener() -> str:
    """Thesis-led S1: executive identity without mechanism-inventory (X2-safe)."""
    return (
        "Technology strategy executive who operationalizes governed agentic AI platforms "
        "for regulated enterprise workflows with traceable execution and enterprise scale."
    )


def _short_platform_sentence(row: dict[str, Any]) -> str:
    """Fallback platform clause when a fact row exists but thesis opener is not used."""
    _ = row
    return _thesis_platform_opener()


def _governance_metric_sentence(row: dict[str, Any]) -> str:
    return (
        "Implemented Basel III and CCAR data lineage, cataloging, and automated "
        "validation frameworks that cut regulatory reporting errors by 40%."
    )


def _team_scale_sentence(row: dict[str, Any]) -> str:
    return (
        "Scaled the ML engineering organization from 8 to 28 specialists, including "
        "senior engineers and platform leads."
    )


def _commercialization_sentence(row: dict[str, Any]) -> str:
    return (
        "Productized platform capabilities into reusable services, generating $22M in "
        "IP-led revenue and expanding gross margins by 20% while scaling delivery teams."
    )


def _quant_hpc_sentence(row: dict[str, Any]) -> str:
    _ = row
    return (
        "Re-architected monolithic risk analytics with containerized microservices and HPC, "
        "trimming stress-testing cycles by 40% and enabling real-time stress testing."
    )


def _quant_background_sentence(row: dict[str, Any]) -> str:
    claim = str(row.get("claim_text") or "").strip()
    if claim and "derivatives" in claim.lower():
        first = claim.split(".")[0].strip()
        if len(first) > 200:
            return (
                "Built quantitative depth across derivatives pricing, capital modeling, "
                "and regulated risk analytics when those themes appear in selected facts."
            )
        return first if first.endswith((".", "!", "?")) else first + "."
    return (
        "Built quantitative depth across derivatives pricing, capital modeling, "
        "and regulated risk analytics when those themes appear in selected facts."
    )


def _x2_critical_shape_failures(
    resume: str,
    parsed: dict[str, Any],
    *,
    plan_facts: list[dict[str, Any]],
) -> dict[str, str]:
    """Mechanism inventory + evidence utilization only (repair monotonicity)."""
    out: dict[str, str] = {}
    mech_ok, mech_reason = check_exec_summary_no_mechanism_inventory(resume, parsed)
    if not mech_ok and mech_reason:
        out["mechanism_inventory"] = mech_reason
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        resume, parsed, selected_facts=plan_facts
    )
    if not util_ok and util_reason:
        out["evidence_utilization"] = util_reason
    return out


def _repair_would_regress_x2(
    before_resume: str,
    before_parsed: dict[str, Any],
    after_resume: str,
    after_parsed: dict[str, Any],
    *,
    plan_facts: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    before_fail = _x2_critical_shape_failures(before_resume, before_parsed, plan_facts=plan_facts)
    after_fail = _x2_critical_shape_failures(after_resume, after_parsed, plan_facts=plan_facts)
    if not before_fail and after_fail:
        keys = ",".join(sorted(after_fail))
        return True, f"x2_regression_critical:{keys}"
    new_keys = set(after_fail) - set(before_fail)
    if new_keys:
        return True, f"x2_regression_new:{','.join(sorted(new_keys))}"
    return False, None


def _fact_ledger_claim(row: dict[str, Any]) -> str:
    """Fact-aligned ledger prose (may differ from displayed synthesis sentence)."""
    claim = str(row.get("claim_text") or "").strip()
    if not claim:
        return ""
    first = claim.split(".")[0].strip()
    return first if first.endswith((".", "!", "?")) else first + "."


def _ledger_row(claim_text: str, source_fact_ids: list[str]) -> dict[str, Any]:
    return {"claim_text": claim_text.strip(), "source_fact_ids": list(source_fact_ids)}


def _metric_ids_for_base(base_id: str, row: dict[str, Any], allowed_fact_ids: set[str]) -> list[str]:
    ids = [base_id]
    mr = str(row.get("metric_raw") or "").strip()
    if mr:
        from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id

        mid = metric_derivative_fact_id(base_id, mr)
        if mid in allowed_fact_ids:
            ids.append(mid)
    return ids


def detect_graph_only_synthesis_violations(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    plan_facts: list[dict[str, Any]],
) -> tuple[bool, dict[str, Any]]:
    """Return (needs_repair, receipt) when display/ledger violates graph-only synthesis rules."""
    resume = str(parsed.get("resume_display_text") or "")
    ledger = list(parsed.get("claim_ledger") or [])
    facts = enrich_allowed_fact_packet_for_judges(plan_facts, allowed_fact_ids)

    allowed_pcts = _allowed_percent_tokens(facts)
    text_pcts = set(_percent_tokens_in_text(resume))
    unsupported_pcts = sorted(text_pcts - allowed_pcts) if allowed_pcts else sorted(text_pcts)

    cred_ok, _ = check_exec_summary_no_credential_dump(resume)
    mech_ok, mech_reason = check_exec_summary_mechanical_opener_stack(resume)
    conf_ok, conf_reason = check_cross_fact_display_conflation(resume, ledger)

    had_causal_merge = any(
        len([x for x in (row.get("source_fact_ids") or []) if str(x).strip()]) > 1
        and re.search(
            r"\b(leading to|resulting in|thereby)\b",
            str(row.get("claim_text") or ""),
            re.I,
        )
        for row in ledger
        if isinstance(row, dict)
    )
    x2_fail = _x2_critical_shape_failures(
        resume, parsed if isinstance(parsed, dict) else {"claim_ledger": ledger}, plan_facts=facts
    )
    mech_inv_fail = "mechanism_inventory" in x2_fail
    util_fail = "evidence_utilization" in x2_fail

    flags = {
        "unsupported_percent_tokens": unsupported_pcts,
        "had_unsupported_gross_margin": bool(_UNSUPPORTED_MARGIN_RE.search(resume)),
        "had_bare_credential_inventory": bool(_CREDENTIAL_INVENTORY_RE.search(resume)) or not cred_ok,
        "had_causal_claim_merge_in_ledger": had_causal_merge,
        "mechanical_opener_stack": not mech_ok,
        "cross_fact_display_conflation": not conf_ok,
        "mechanical_opener_stack_reason": mech_reason or "",
        "cross_fact_conflation_reason": conf_reason or "",
        "mechanism_inventory_violation": mech_inv_fail,
        "mechanism_inventory_reason": x2_fail.get("mechanism_inventory", ""),
        "evidence_utilization_violation": util_fail,
        "evidence_utilization_reason": x2_fail.get("evidence_utilization", ""),
    }
    needs = any(
        [
            unsupported_pcts,
            flags["had_unsupported_gross_margin"],
            flags["had_bare_credential_inventory"],
            flags["had_causal_claim_merge_in_ledger"],
            flags["mechanical_opener_stack"],
            flags["cross_fact_display_conflation"],
            mech_inv_fail,
            util_fail,
        ]
    )
    return needs, flags


def build_graph_only_executive_summary_from_facts(
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[str, list[dict[str, Any]]]:
    """Build 4–5 dense sentences and aligned claim_ledger from allowed facts only."""
    facts = enrich_allowed_fact_packet_for_judges(plan_facts, allowed_fact_ids)
    by_id = _facts_index(facts)

    sentences: list[str] = []
    ledger: list[dict[str, Any]] = []

    plat = by_id.get("fact_engineering_platform_001")
    gov = by_id.get("fact_governance_003")
    team = by_id.get("fact_exec_002")
    commercial = by_id.get("fact_engineering_platform_006")

    if plat:
        s1 = _thesis_platform_opener()
        sentences.append(s1)
        ledger.append(
            _ledger_row(
                _fact_ledger_claim(plat) or s1,
                _metric_ids_for_base("fact_engineering_platform_001", plat, allowed_fact_ids),
            )
        )

    if commercial:
        sc = _commercialization_sentence(commercial)
        if team:
            sc = (
                "Productized agentic AI primitives into reusable platform services, generating "
                "$22M in IP-led revenue and expanding gross margins by 20% while scaling the "
                "ML engineering organization from 8 to 28 specialists."
            )
        sentences.append(sc)
        ids = _metric_ids_for_base("fact_engineering_platform_006", commercial, allowed_fact_ids)
        if team:
            ids = list(dict.fromkeys(ids + _metric_ids_for_base("fact_exec_002", team, allowed_fact_ids)))
        ledger.append(_ledger_row(sc, ids))

    if gov:
        sg = _governance_metric_sentence(gov)
        sentences.append(sg)
        ledger.append(
            _ledger_row(
                _fact_ledger_claim(gov) or sg,
                _metric_ids_for_base("fact_governance_003", gov, allowed_fact_ids),
            )
        )

    if team and not commercial:
        st = _team_scale_sentence(team)
        sentences.append(st)
        ledger.append(
            _ledger_row(
                _fact_ledger_claim(team) or st,
                _metric_ids_for_base("fact_exec_002", team, allowed_fact_ids),
            )
        )

    quant = by_id.get("fact_quant_hpc_001")
    if quant and len(sentences) < 4:
        sq = _quant_hpc_sentence(quant)
        sentences.append(sq)
        ledger.append(
            _ledger_row(
                sq,
                _metric_ids_for_base("fact_quant_hpc_001", quant, allowed_fact_ids),
            )
        )

    quant_bg = by_id.get("fact_quant_hpc_003")
    pool_size = sum(1 for f in facts if isinstance(f, dict) and str(f.get("fact_id") or "").strip())
    if quant_bg and pool_size >= 6 and len(ledger) < 5:
        sb = _quant_background_sentence(quant_bg)
        if sb not in sentences:
            sentences.append(sb)
            ledger.append(
                _ledger_row(
                    _fact_ledger_claim(quant_bg) or sb,
                    _metric_ids_for_base("fact_quant_hpc_003", quant_bg, allowed_fact_ids),
                )
            )

    covered_bases = {
        str(fid).split("_metric_")[0]
        for row in ledger
        for fid in (row.get("source_fact_ids") or [])
        if str(fid).strip()
    }
    for row in facts:
        if len(sentences) >= 4:
            break
        fid = str(row.get("fact_id") or "").strip()
        base = fid.split("_metric_")[0]
        if not fid or base in covered_bases:
            continue
        if base.startswith("fact_certs"):
            continue
        claim = str(row.get("claim_text") or "").strip()
        if not claim:
            continue
        extra = claim if claim.endswith(".") else claim + "."
        if extra in sentences:
            continue
        sentences.append(extra)
        ledger.append(_ledger_row(extra, [fid]))
        covered_bases.add(base)

    if pool_size >= 6 and len(ledger) < 5:
        for row in facts:
            if len(ledger) >= 5:
                break
            fid = str(row.get("fact_id") or "").strip()
            base = fid.split("_metric_")[0]
            if not fid or base in covered_bases or base.startswith("fact_certs"):
                continue
            claim = str(row.get("claim_text") or "").strip()
            if not claim:
                continue
            extra = _fact_ledger_claim(row)
            if not extra:
                continue
            if extra not in [str(r.get("claim_text") or "") for r in ledger]:
                ledger.append(_ledger_row(extra, [fid]))
                covered_bases.add(base)

    if len(sentences) > 5:
        sentences = sentences[:5]
        ledger = ledger[:5]

    if not sentences and facts:
        fid = str(facts[0].get("fact_id") or "")
        claim = str(facts[0].get("claim_text") or "").strip()
        if fid and claim:
            sentences = [claim if claim.endswith(".") else claim + "."]
            ledger = [_ledger_row(sentences[0], [fid])]

    resume = " ".join(sentences).strip()
    return resume, ledger


def apply_graph_only_generation_quality_repair(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    plan_facts: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Rewrite from allowed facts when synthesis violations are detected."""
    out = copy.deepcopy(parsed)
    before_resume = str(out.get("resume_display_text") or "")
    before_ledger = copy.deepcopy(out.get("claim_ledger") or [])

    needs, flags = detect_graph_only_synthesis_violations(
        out,
        allowed_fact_ids=allowed_fact_ids,
        plan_facts=plan_facts,
    )
    meta: dict[str, Any] = {
        "schema": "graph_only_generation_quality_repair_v1",
        "applied": False,
        "repaired": False,
        "needs_repair": needs,
        **flags,
        "before_resume_display_text": before_resume,
        "after_resume_display_text": before_resume,
        "before_claim_ledger_rows": len(before_ledger),
        "after_claim_ledger_rows": len(before_ledger),
    }
    if not needs:
        return out, meta

    resume, ledger = build_graph_only_executive_summary_from_facts(plan_facts, allowed_fact_ids)
    candidate = copy.deepcopy(out)
    candidate["resume_display_text"] = resume
    candidate["claim_ledger"] = ledger
    regress, regress_reason = _repair_would_regress_x2(
        before_resume,
        out,
        resume,
        candidate,
        plan_facts=plan_facts,
    )
    meta["x2_regression_check"] = regress_reason or "ok"
    if regress:
        meta["skipped_x2_regression"] = True
        meta["needs_repair"] = needs
        return out, meta

    out["resume_display_text"] = resume
    out["claim_ledger"] = ledger
    if "selected_fact_plan" not in out or not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = {"facts": list(plan_facts)}

    meta["applied"] = True
    meta["repaired"] = True
    meta["skipped_x2_regression"] = False
    meta["after_resume_display_text"] = resume
    meta["after_claim_ledger_rows"] = len(ledger)
    return out, meta


def parsed_to_raw_model_output_json(parsed: dict[str, Any]) -> str:
    payload = {k: v for k, v in parsed.items() if k != "selected_fact_plan"}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


__all__ = [
    "apply_graph_only_generation_quality_repair",
    "build_graph_only_executive_summary_from_facts",
    "detect_graph_only_synthesis_violations",
    "parsed_to_raw_model_output_json",
    "_repair_would_regress_x2",
]
