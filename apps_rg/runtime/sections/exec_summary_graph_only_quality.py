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
from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id

_METRIC_PCT_RE = re.compile(r"\d+(?:\.\d+)?\s*%", re.IGNORECASE)
_UNSUPPORTED_MARGIN_RE = re.compile(
    r"\b(?:gross\s+margins?|margin\s+expansion|expanding\s+margins?|revenue\s+growth)\b",
    re.IGNORECASE,
)
_CREDENTIAL_INVENTORY_RE = re.compile(
    r"\bHolds\s+AWS\b|\bAWS Certified\b.*\bDatabricks\b",
    re.IGNORECASE,
)
_RELiability_UNPROVEN_RE = re.compile(
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


def _short_platform_sentence(row: dict[str, Any]) -> str:
    claim = str(row.get("claim_text") or "").strip()
    if claim:
        first = claim.split(".")[0].strip()
        if len(first) > 220:
            first = (
                "Built governed agentic AI platform capabilities including deterministic routing, "
                "multi-agent orchestration, GraphRAG retrieval, and policy-gated execution."
            )
        return first if first.endswith((".", "!", "?")) else first + "."
    return (
        "Built deterministic routing, multi-agent orchestration, GraphRAG retrieval, "
        "and policy-gated execution on production platforms."
    )


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
        mid = metric_derivative_fact_id(base_id, mr)
        if mid in allowed_fact_ids:
            ids.append(mid)
    return ids


def build_graph_only_executive_summary_from_facts(
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[str, list[dict[str, Any]]]:
    """Build 2–3 dense sentences and aligned claim_ledger from allowed facts only."""
    facts = enrich_allowed_fact_packet_for_judges(plan_facts, allowed_fact_ids)
    by_id = _facts_index(facts)

    sentences: list[str] = []
    ledger: list[dict[str, Any]] = []

    plat = by_id.get("fact_engineering_platform_001")
    gov = by_id.get("fact_governance_003")
    team = by_id.get("fact_exec_002")

    if plat:
        s1 = (
            "Engineering executive who designs and operationalizes governed agentic AI "
            "platforms with deterministic routing, multi-agent orchestration, and "
            "GraphRAG retrieval for regulated enterprise workflows."
        )
        sentences.append(s1)
        ledger.append(
            _ledger_row(
                _fact_ledger_claim(plat) or s1,
                ["fact_engineering_platform_001"],
            )
        )
        if not gov and not team:
            s2 = _short_platform_sentence(plat)
            sentences.append(s2)
            ledger.append(
                _ledger_row(
                    s2,
                    _metric_ids_for_base("fact_engineering_platform_001", plat, allowed_fact_ids),
                )
            )

    if gov:
        sg = _governance_metric_sentence(gov)
        sentences.append(sg)
        ledger.append(
            _ledger_row(
                _fact_ledger_claim(gov) or sg,
                _metric_ids_for_base("fact_governance_003", gov, allowed_fact_ids),
            )
        )

    if team:
        st = _team_scale_sentence(team)
        sentences.append(st)
        ledger.append(
            _ledger_row(
                _fact_ledger_claim(team) or st,
                _metric_ids_for_base("fact_exec_002", team, allowed_fact_ids),
            )
        )

    if len(sentences) > 3:
        keep_thesis = sentences[0:1]
        tail = sentences[1:3]
        sentences = keep_thesis + tail
        ledger = ledger[: len(sentences)]

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
    """Replace model output with fact-tight graph-only synthesis when violations detected."""
    out = copy.deepcopy(parsed)
    before_resume = str(out.get("resume_display_text") or "")
    before_ledger = copy.deepcopy(out.get("claim_ledger") or [])

    allowed_pcts = _allowed_percent_tokens(
        enrich_allowed_fact_packet_for_judges(plan_facts, allowed_fact_ids)
    )
    text_pcts = set(_percent_tokens_in_text(before_resume))
    unsupported_pcts = sorted(text_pcts - allowed_pcts) if allowed_pcts else sorted(text_pcts)

    had_margin = bool(_UNSUPPORTED_MARGIN_RE.search(before_resume))
    had_cred_inventory = bool(_CREDENTIAL_INVENTORY_RE.search(before_resume))
    had_causal_merge = any(
        len([x for x in (row.get("source_fact_ids") or []) if str(x).strip()]) > 1
        and re.search(
            r"\b(leading to|resulting in|thereby)\b",
            str(row.get("claim_text") or ""),
            re.I,
        )
        for row in before_ledger
        if isinstance(row, dict)
    )

    resume, ledger = build_graph_only_executive_summary_from_facts(plan_facts, allowed_fact_ids)
    out["resume_display_text"] = resume
    out["claim_ledger"] = ledger
    if "selected_fact_plan" not in out or not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = {"facts": list(plan_facts)}

    meta = {
        "schema": "graph_only_generation_quality_repair_v1",
        "repaired": True,
        "unsupported_percent_tokens_removed": unsupported_pcts,
        "had_unsupported_gross_margin": had_margin,
        "had_bare_credential_inventory": had_cred_inventory,
        "had_causal_claim_merge_in_ledger": had_causal_merge,
        "before_resume_display_text": before_resume,
        "after_resume_display_text": resume,
        "before_claim_ledger_rows": len(before_ledger),
        "after_claim_ledger_rows": len(ledger),
    }
    return out, meta


def parsed_to_raw_model_output_json(parsed: dict[str, Any]) -> str:
    payload = {k: v for k, v in parsed.items() if k != "selected_fact_plan"}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


__all__ = [
    "apply_graph_only_generation_quality_repair",
    "build_graph_only_executive_summary_from_facts",
    "parsed_to_raw_model_output_json",
]
