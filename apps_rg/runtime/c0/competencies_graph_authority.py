"""Deterministic competencies allocation-to-claim authority reconciliation."""
from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_IDENTITY_NOISE = frozenset(
    {
        "skill",
        "p2",
        "sr",
        "w12",
        "tech",
        "the",
        "and",
        "for",
        "from",
        "with",
        "across",
    }
)
_ROLE_AXIS_SIGNALS: Mapping[str, tuple[str, ...]] = {
    "partner_motions": ("partner", "partnership", "alliance"),
    "co_sell": ("co_sell", "cosell", "co-selling", "co_selling"),
    "hyperscaler_alliance": ("hyperscaler", "aws", "cloud_vendor", "cloud-vendor"),
    "joint_solution": ("joint_solution", "joint solution", "partner_led_ai_solutions"),
    "gtm_enablement": ("enablement", "gtm", "technical_close", "go-to-market"),
}


def _strings(values: Iterable[Any] | None) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values or ():
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _tokens(value: Any) -> set[str]:
    return {
        token
        for token in _TOKEN_RE.findall(str(value or "").casefold())
        if token not in _IDENTITY_NOISE and len(token) >= 3
    }


def _term_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return str(value.get("text") or value.get("term") or "").strip()
    return str(value or "").strip()


def _role_axes(*values: Any) -> list[str]:
    text = " ".join(str(value or "") for value in values).casefold()
    return sorted(
        axis
        for axis, signals in _ROLE_AXIS_SIGNALS.items()
        if any(signal.casefold() in text for signal in signals)
    )


def _authority_by_root(plan: Mapping[str, Any]) -> dict[str, dict[str, set[str]]]:
    authority: dict[str, dict[str, set[str]]] = {}
    for raw in plan.get("facts") or []:
        if not isinstance(raw, Mapping):
            continue
        root_id = str(raw.get("role_episode_bundle_id") or raw.get("fact_id") or "")
        if not root_id:
            continue
        authority[root_id] = {
            "skills": set(_strings(raw.get("graph_skill_node_ids"))),
            "facts": set(
                _strings(
                    [
                        root_id,
                        raw.get("fact_id"),
                        *list(raw.get("linked_identity_fact_ids") or []),
                        *list(raw.get("linked_source_fact_ids") or []),
                    ]
                )
            ),
            "metrics": set(_strings(raw.get("metric_outcome_ids"))),
        }
    return authority


def _match_score(
    assignment: Mapping[str, Any],
    *,
    category: Mapping[str, Any],
    term: Any,
    root_authority: Mapping[str, Mapping[str, set[str]]],
) -> tuple[int, list[str]]:
    root_id = str(assignment.get("root_id") or "")
    skill_id = str(assignment.get("skill_id") or "")
    fact_id = str(assignment.get("fact_id") or "")
    category_skills = set(_strings(category.get("graph_skill_node_ids")))
    category_facts = set(_strings(category.get("source_fact_ids")))
    term_sources = set(
        _strings(term.get("source_fact_ids")) if isinstance(term, Mapping) else []
    )
    if isinstance(term, Mapping) and term.get("source_fact_id"):
        term_sources.add(str(term.get("source_fact_id")))
    reasons: list[str] = []
    score = 0
    if skill_id and skill_id in category_skills:
        score += 1000
        reasons.append("EXACT_SKILL_ID")
    if root_id and root_id in category_facts | term_sources:
        score += 900
        reasons.append("EXACT_ROOT_ID")
    if fact_id and fact_id in category_facts | term_sources:
        score += 850
        reasons.append("EXACT_FACT_ID")
    sibling_skills = set((root_authority.get(root_id) or {}).get("skills") or set())
    sibling_overlap = sorted(sibling_skills & category_skills)
    if sibling_overlap:
        score += 700 + min(len(sibling_overlap), 9)
        reasons.append("EXACT_ROOT_SIBLING_SKILL_ID")
    lexical_overlap = sorted(_tokens(skill_id) & _tokens(_term_text(term)))
    if lexical_overlap:
        score += 100 * len(lexical_overlap)
        reasons.append("EXACT_SKILL_TERM_TOKEN:" + ",".join(lexical_overlap))
    return score, reasons


def reconcile_competencies_allocation_claim_units(
    parsed: dict[str, Any],
    *,
    selected_plan: Mapping[str, Any],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Bind each competencies allocation unit to one visible term without changing text."""

    assignments = sorted(
        (
            dict(row)
            for row in selected_plan.get("allocation_assignments") or []
            if isinstance(row, Mapping) and row.get("section_id") == "competencies"
        ),
        key=lambda row: str(row.get("claim_unit_id") or ""),
    )
    categories = [
        row
        for row in parsed.get("competencies") or []
        if isinstance(row, dict)
    ]
    claim_ledger = [
        dict(row)
        for row in parsed.get("claim_ledger") or []
        if isinstance(row, Mapping)
    ]
    root_authority = _authority_by_root(selected_plan)
    candidates: list[dict[str, Any]] = []
    for assignment in assignments:
        for category_index, category in enumerate(categories):
            for term_index, term in enumerate(category.get("terms") or []):
                text = _term_text(term)
                if not text:
                    continue
                score, reasons = _match_score(
                    assignment,
                    category=category,
                    term=term,
                    root_authority=root_authority,
                )
                if score <= 0:
                    continue
                candidates.append(
                    {
                        "claim_unit_id": str(assignment.get("claim_unit_id") or ""),
                        "category_index": category_index,
                        "term_index": term_index,
                        "score": score,
                        "reasons": reasons,
                        "assignment": assignment,
                    }
                )
    candidates.sort(
        key=lambda row: (
            -int(row["score"]),
            str(row["claim_unit_id"]),
            int(row["category_index"]),
            int(row["term_index"]),
        )
    )
    matched_units: set[str] = set()
    matched_terms: set[tuple[int, int]] = set()
    matches: list[dict[str, Any]] = []
    for candidate in candidates:
        unit_id = str(candidate["claim_unit_id"])
        term_key = (int(candidate["category_index"]), int(candidate["term_index"]))
        if unit_id in matched_units or term_key in matched_terms:
            continue
        assignment = candidate["assignment"]
        fact_id = str(assignment.get("fact_id") or "")
        if not fact_id or fact_id not in allowed_fact_ids:
            continue
        category = categories[term_key[0]]
        original = category.get("terms")[term_key[1]]
        term = dict(original) if isinstance(original, Mapping) else {"text": _term_text(original)}
        term["source_fact_id"] = fact_id
        term["source_fact_ids"] = [fact_id]
        term["source_skill_ids"] = _strings(
            [*list(term.get("source_skill_ids") or []), assignment.get("skill_id")]
        )
        term["allocation_claim_unit_id"] = unit_id
        category["terms"][term_key[1]] = term
        category["allocation_claim_unit_ids"] = _strings(
            [*list(category.get("allocation_claim_unit_ids") or []), unit_id]
        )
        matched_units.add(unit_id)
        matched_terms.add(term_key)
        claim_row = next(
            (
                row
                for row in claim_ledger
                if str(row.get("claim_text") or row.get("claim") or "").strip()
                == term["text"]
                and not str(row.get("claim_unit_id") or "").strip()
            ),
            None,
        )
        if claim_row is None:
            claim_row = {"claim_text": term["text"]}
            claim_ledger.append(claim_row)
        claim_row["source_fact_ids"] = [fact_id]
        claim_row["claim_unit_id"] = unit_id
        matches.append(
            {
                "claim_unit_id": unit_id,
                "visible_claim_text": term["text"],
                "category_id": str(
                    category.get("category_id") or category.get("category_label") or ""
                ),
                "skill_id": str(assignment.get("skill_id") or ""),
                "fact_id": fact_id,
                "root_id": str(assignment.get("root_id") or ""),
                "graph_path_ids": _strings(assignment.get("graph_path_ids")),
                "citation_refs": _strings(assignment.get("citation_refs")),
                "score": int(candidate["score"]),
                "match_reasons": list(candidate["reasons"]),
            }
        )
    expected_units = {
        str(row.get("claim_unit_id") or "") for row in assignments if row.get("claim_unit_id")
    }
    unmatched = sorted(expected_units - matched_units)
    receipt: dict[str, Any] = {
        "schema_version": "competencies_allocation_claim_reconciliation_v1",
        "section_id": "competencies",
        "allocation_plan_digest": str(selected_plan.get("allocation_plan_digest") or ""),
        "allocated_claim_unit_count": len(expected_units),
        "matched_claim_unit_count": len(matched_units),
        "matched_visible_term_count": len(matched_terms),
        "unmatched_claim_unit_ids": unmatched,
        "matches": sorted(matches, key=lambda row: row["claim_unit_id"]),
        "visible_wording_changed": False,
        "authority_source": "FROZEN_RESUME_GRAPH_ALLOCATION",
        "pass": bool(expected_units) and not unmatched and len(matches) == len(expected_units),
    }
    receipt["receipt_digest"] = stable_digest(receipt)
    parsed["claim_ledger"] = claim_ledger
    return receipt


def build_competencies_graph_authority_discrepancy_ledger(
    *,
    selected_plan: Mapping[str, Any],
    proof_pool_metadata: Mapping[str, Any],
    parsed: Mapping[str, Any],
    reconciliation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Record every authority-eligible graph candidate and its final disposition."""

    assignments = [
        dict(row)
        for row in selected_plan.get("allocation_assignments") or []
        if isinstance(row, Mapping) and row.get("section_id") == "competencies"
    ]
    assertion_by_skill: dict[str, dict[str, Any]] = {}
    for raw in proof_pool_metadata.get("graph_skill_embedding_assertion_bindings") or []:
        if not isinstance(raw, Mapping):
            continue
        skill_id = str(raw.get("skill_id") or "")
        if skill_id:
            assertion_by_skill[skill_id] = dict(raw)
    visible_by_unit = {
        str(row.get("claim_unit_id") or ""): str(row.get("visible_claim_text") or "")
        for row in reconciliation_receipt.get("matches") or []
        if isinstance(row, Mapping)
    }
    rows: list[dict[str, Any]] = []
    for raw in selected_plan.get("graph_candidate_decision_ledger") or []:
        if not isinstance(raw, Mapping) or raw.get("authority_pass") is not True:
            continue
        candidate_id = str(raw.get("candidate_id") or "")
        candidate_type = str(raw.get("candidate_type") or "")
        root_id = str(raw.get("root_id") or candidate_id)
        skill_ids = _strings(
            [candidate_id if candidate_type == "leaf_skill" else "", *list(raw.get("graph_skill_node_ids") or [])]
        )
        metric_ids = _strings(
            [candidate_id if candidate_type == "metric_outcome" else "", *list(raw.get("metric_outcome_ids") or [])]
        )
        fact_ids = _strings(
            [candidate_id if candidate_type == "source_fact" else "", *list(raw.get("linked_source_fact_ids") or [])]
        )
        related_assignments = [
            row
            for row in assignments
            if candidate_id
            in {
                str(row.get("root_id") or ""),
                str(row.get("skill_id") or ""),
                str(row.get("fact_id") or ""),
                str(row.get("metric_outcome_id") or ""),
            }
            or root_id == str(row.get("root_id") or "")
        ]
        assertion = next(
            (assertion_by_skill[skill_id] for skill_id in skill_ids if skill_id in assertion_by_skill),
            {},
        )
        claim_units = _strings(row.get("claim_unit_id") for row in related_assignments)
        authority = raw.get("authority") if isinstance(raw.get("authority"), Mapping) else {}
        rows.append(
            {
                "candidate_id": candidate_id,
                "candidate_type": candidate_type,
                "assertion_id": str(assertion.get("assertion_id") or ""),
                "skill_ids": skill_ids,
                "fact_ids": fact_ids,
                "source_references": _strings(
                    list(raw.get("source_refs") or []) + list(authority.get("source_refs") or [])
                ),
                "graph_paths": _strings(
                    [raw.get("candidate_path_id"), raw.get("path_signature")]
                ),
                "metric_outcome_ids": metric_ids,
                "role_axis_labels": _role_axes(candidate_id, root_id, raw.get("claim_text")),
                "embedding_rank": assertion.get("rank")
                or assertion.get("embedding_rank")
                or assertion.get("dense_rank"),
                "exact_eligibility_result": "ELIGIBLE",
                "allocation_decision": (
                    "ALLOCATED_PRIMARY"
                    if candidate_id
                    in {
                        str(row.get(field) or "")
                        for row in related_assignments
                        for field in ("skill_id", "fact_id", "metric_outcome_id")
                    }
                    else "ALLOCATED_ROOT_AUTHORITY"
                    if related_assignments
                    else "NOT_ALLOCATED"
                ),
                "selector_decision": str(raw.get("decision") or ""),
                "rejection_reason": _strings(raw.get("reason_codes")),
                "allocation_claim_unit_ids": claim_units,
                "visible_claim_unit_usage": [
                    {"claim_unit_id": unit_id, "visible_claim_text": visible_by_unit[unit_id]}
                    for unit_id in claim_units
                    if unit_id in visible_by_unit
                ],
            }
        )
    selected_skills = _strings(selected_plan.get("selected_skill_ids"))
    selected_metrics = _strings(selected_plan.get("selected_metrics"))
    ledger: dict[str, Any] = {
        "schema_version": "competencies_graph_authority_discrepancy_ledger_v1",
        "section_id": "competencies",
        "allocation_plan_digest": str(selected_plan.get("allocation_plan_digest") or ""),
        "eligible_candidate_count": len(rows),
        "selected_unique_leaf_skill_count": len(selected_skills),
        "selected_unique_metric_count": len(selected_metrics),
        "co_sell_authority_ids": sorted(
            candidate_id
            for candidate_id in selected_skills
            if "co_sell" in candidate_id.casefold() or "cosell" in candidate_id.casefold()
        ),
        "allocation_reconciliation_pass": reconciliation_receipt.get("pass") is True,
        "production_graph_mutated": False,
        "rows": rows,
    }
    ledger["ledger_digest"] = stable_digest(ledger)
    return ledger


__all__ = [
    "build_competencies_graph_authority_discrepancy_ledger",
    "reconcile_competencies_allocation_claim_units",
]
