"""Deterministic whole-resume graph allocation with immutable current-run reservations.

The allocator is deliberately pure Python.  It consumes authority-filtered candidate
sets, applies hard resource constraints before generation, and emits one immutable
plan plus a current-run usage ledger.  It never writes SQLite or any other durable
graph state.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    ALLOCATION_PLAN_SCHEMA_VERSION,
    USAGE_LEDGER_SCHEMA_VERSION,
    stable_digest,
)

WHOLE_RESUME_SCOPE = "WHOLE_RESUME"
SECTION_ONLY_SCOPE = "SECTION_ONLY"
ALLOCATION_SCOPES = frozenset({WHOLE_RESUME_SCOPE, SECTION_ONLY_SCOPE})
ALLOCATION_PLAN_ENV = "APPS_RG_RESUME_GRAPH_ALLOCATION_PLAN"
ALLOCATION_USAGE_LEDGER_ENV = "APPS_RG_RESUME_GRAPH_USAGE_LEDGER"
SECTION_EVIDENCE_CONTRACTS_ENV = "APPS_RG_SECTION_FINAL_GRAPH_EVIDENCE_CONTRACTS"
DEFAULT_MAX_CANDIDATES_PER_SLOT = 64

_ALLOCATION_DIGEST_EXCLUDED_KEYS = frozenset(
    {
        "allocation_plan_id",
        "allocation_plan_digest",
        "prior_seal",
        "prior_seals",
        "downstream_receipt",
        "downstream_receipts",
    }
)

_WORD_RE = re.compile(r"[a-z0-9]+")
_DIGIT_LETTER_RE = re.compile(r"(?<=\d)(?=[a-z])|(?<=[a-z])(?=\d)")
_METRIC_EQUIVALENTS = {
    "percent": "pct",
    "percentage": "pct",
    "million": "m",
    "millions": "m",
    "billion": "b",
    "billions": "b",
    "dollars": "usd",
    "dollar": "usd",
}
_EXACT_METRIC_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?:\$|\busd\s*)(\d+(?:\.\d+)?)\s*(m|million|b|billion)?\b", re.I), "USD"),
    (
        re.compile(r"\b(\d+(?:\.\d+)?)\s*(%|percent\b|percentage\b)", re.I),
        "PERCENT",
    ),
    (re.compile(r"\b(\d+(?:\.\d+)?)\s*(x|times)\b", re.I), "MULTIPLIER"),
    (
        re.compile(
            r"\b(\d+(?:\.\d+)?)\+?\s*(countries|clients|customers|partners|teams|"
            r"workflows|platforms|products|programs|markets|regions|applications|systems)\b",
            re.I,
        ),
        "COUNT",
    ),
)

CANONICAL_BULLET_CLAIM_UNITS: Mapping[str, tuple[str, ...]] = {
    "unify_bullets": tuple(f"bul_unify_{index:03d}" for index in range(1, 7)),
    "ibm_bullets": tuple(f"bul_ibm_{index:03d}" for index in range(1, 6)),
    "insurtech_bullets": tuple(f"bul_insurtech_{index:03d}" for index in range(1, 4)),
    "ey_bullets": tuple(f"bul_ey_{index:03d}" for index in range(1, 4)),
}
EMPLOYER_LANE_BY_SECTION: Mapping[str, str] = {
    "unify_bullets": "unify",
    "ibm_bullets": "ibm",
    "insurtech_bullets": "insurtech",
    "ey_bullets": "ey",
}
NARRATIVE_DERIVATION_POLICY: Mapping[str, str] = {
    "unify_narrative": "unify_bullets",
    "ibm_narrative": "ibm_bullets",
    "insurtech_narrative": "insurtech_bullets",
    "ey_narrative": "ey_bullets",
}
CANONICAL_VISIBLE_SECTIONS: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "executive_summary",
    "headline",
)
ALL_CLAIM_BEARING_SECTIONS: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)


class ResumeGraphAllocationError(RuntimeError):
    """Fail-closed allocation error with a machine-readable constraint receipt."""

    def __init__(self, message: str, *, receipt: Mapping[str, Any]):
        super().__init__(message)
        self.receipt = dict(receipt)


@dataclass(frozen=True, slots=True)
class _Slot:
    slot_id: str
    section_id: str
    metric_required: bool
    employer_lane: str
    counts_toward_global_uniqueness: bool


def normalize_metric_signature(value: str) -> str:
    """Normalize semantically equivalent metric surfaces for zero-reuse checks."""
    text = str(value or "").casefold().strip()
    text = text.replace("$", " usd ").replace("%", " pct ")
    text = text.replace("×", " x ")
    text = _DIGIT_LETTER_RE.sub(" ", text)
    tokens = [_METRIC_EQUIVALENTS.get(token, token) for token in _WORD_RE.findall(text)]
    return " ".join(tokens)


def extract_exact_metric_value_unit(value: str) -> tuple[str, str]:
    """Extract an explicit outcome value/unit; standards such as SOC 2 are not metrics."""
    text = str(value or "").strip()
    for pattern, base_unit in _EXACT_METRIC_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        number = str(match.group(1))
        suffix = str(match.group(2) or "").casefold() if match.lastindex and match.lastindex >= 2 else ""
        if base_unit == "USD" and suffix:
            scale = "M" if suffix in {"m", "million"} else "B"
            return number, f"USD_{scale}"
        if base_unit == "COUNT" and suffix:
            return number, "COUNT_" + suffix.upper()
        return number, base_unit
    return "", ""


def stable_edge_id(source: str, edge_type: str, target: str) -> str:
    payload = {"source": str(source), "edge_type": str(edge_type), "target": str(target)}
    return f"edge:{stable_digest(payload)[:24]}"


def _strings(values: Iterable[Any] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values or ():
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _slot_from_row(row: Mapping[str, Any]) -> _Slot:
    slot_id = str(row.get("slot_id") or row.get("claim_unit_id") or "").strip()
    section_id = str(row.get("section_id") or "").strip()
    if not slot_id or not section_id:
        raise ValueError("every allocation slot requires slot_id and section_id")
    return _Slot(
        slot_id=slot_id,
        section_id=section_id,
        metric_required=bool(row.get("metric_required")),
        employer_lane=str(row.get("employer_lane") or "").strip(),
        counts_toward_global_uniqueness=bool(
            row.get("counts_toward_global_uniqueness", True)
        ),
    )


def _candidate_identity(row: Mapping[str, Any], *, slot: _Slot) -> str:
    explicit = str(row.get("candidate_id") or "").strip()
    if explicit:
        return explicit
    return "cand:" + stable_digest(
        {
            "slot_id": slot.slot_id,
            "skill_id": row.get("skill_id"),
            "fact_id": row.get("fact_id"),
            "metric_outcome_id": row.get("metric_outcome_id"),
            "graph_path_ids": row.get("graph_path_ids"),
        }
    )[:24]


def _candidate_score(
    row: Mapping[str, Any],
) -> tuple[float, float, float, float, float, str]:
    return (
        round(float(row.get("proof_strength_raw") or 0.0), 6),
        round(float(row.get("path_confidence_raw") or 0.0), 6),
        round(float(row.get("source_independence_score") or 0.0), 6),
        round(float(row.get("target_alignment_score") or 0.0), 6),
        round(float(row.get("embedding_similarity") or 0.0), 9),
        str(row.get("candidate_id") or ""),
    )


def _candidate_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    proof, path, independence, target, embedding, candidate_id = _candidate_score(row)
    return (-proof, -path, -independence, -target, -embedding, candidate_id)


def _selection_margin_receipt(
    selected: Mapping[str, Any],
    eligible_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compare a selected row with its best locally eligible rejected peer.

    The allocator's objective is lexicographic, not a probability or a blended
    score.  The margin is therefore the signed difference at the first
    objective component that distinguishes the selected row from the best
    per-slot alternative.  A negative margin is expected when a globally
    feasible assignment must yield local rank to uniqueness or concentration
    constraints.
    """
    selected_id = str(selected.get("candidate_id") or "")
    alternatives = sorted(
        (
            row
            for row in eligible_rows
            if str(row.get("candidate_id") or "") != selected_id
        ),
        key=_candidate_sort_key,
    )
    if not alternatives:
        return {
            "selection_margin": 0.0,
            "selection_margin_available": False,
            "selection_margin_basis": "no_eligible_rejected_alternative",
            "best_eligible_rejected_candidate_id": "",
        }
    alternative = alternatives[0]
    components = (
        "proof_strength_raw",
        "path_confidence_raw",
        "source_independence_score",
        "target_alignment_score",
        "embedding_similarity",
    )
    basis = "stable_candidate_id_tie"
    margin = 0.0
    for field in components:
        selected_value = round(float(selected.get(field) or 0.0), 6)
        alternative_value = round(float(alternative.get(field) or 0.0), 6)
        if selected_value != alternative_value:
            basis = field
            margin = round(selected_value - alternative_value, 6)
            break
    return {
        "selection_margin": margin,
        "selection_margin_available": True,
        "selection_margin_basis": basis,
        "best_eligible_rejected_candidate_id": str(
            alternative.get("candidate_id") or ""
        ),
    }


def _normalize_candidate(
    raw: Mapping[str, Any],
    *,
    slot: _Slot,
) -> tuple[dict[str, Any], list[str]]:
    row = dict(raw)
    row["candidate_id"] = _candidate_identity(row, slot=slot)
    row["section_id"] = str(row.get("section_id") or slot.section_id)
    row["claim_unit_id"] = str(row.get("claim_unit_id") or slot.slot_id)
    row["skill_id"] = str(row.get("skill_id") or "").strip()
    row["fact_id"] = str(row.get("fact_id") or "").strip()
    row["metric_outcome_id"] = str(row.get("metric_outcome_id") or "").strip()
    row["metric_text"] = str(row.get("metric_text") or "").strip()
    row["normalized_metric_signature"] = str(
        row.get("normalized_metric_signature")
        or normalize_metric_signature(row["metric_text"])
    )
    row["employer_lane"] = str(row.get("employer_lane") or "").strip()
    row["source_family"] = str(
        row.get("source_family") or row["employer_lane"] or row["fact_id"]
    ).strip()
    row["graph_path_ids"] = _strings(row.get("graph_path_ids"))
    row["edge_ids"] = _strings(row.get("edge_ids"))
    row["citation_refs"] = _strings(row.get("citation_refs"))
    row["authority_pass"] = row.get("authority_pass") is True
    for key in (
        "proof_strength_raw",
        "target_alignment_score",
        "path_confidence_raw",
        "source_independence_score",
        "selection_margin",
    ):
        row[key] = round(float(row.get(key) or 0.0), 6)

    reasons: list[str] = []
    if not row["authority_pass"]:
        reasons.append("authority_gate_failed")
    if row["section_id"] != slot.section_id or row["claim_unit_id"] != slot.slot_id:
        reasons.append("slot_identity_mismatch")
    if not row["skill_id"]:
        reasons.append("missing_skill_id")
    if not row["fact_id"]:
        reasons.append("missing_fact_id")
    if not row["graph_path_ids"]:
        reasons.append("missing_graph_path_ids")
    if not row["edge_ids"]:
        reasons.append("missing_edge_ids")
    if not row["citation_refs"]:
        reasons.append("missing_citation_refs")
    if slot.employer_lane and row["employer_lane"] != slot.employer_lane:
        reasons.append("employer_locality_mismatch")
    if slot.metric_required:
        if not row["metric_outcome_id"]:
            reasons.append("metric_required_missing_metric_outcome_id")
        if not row["normalized_metric_signature"]:
            reasons.append("metric_required_missing_normalized_metric_signature")
        if not str(row.get("metric_value") or "").strip():
            reasons.append("metric_required_missing_exact_value")
        if not str(row.get("metric_unit") or "").strip():
            reasons.append("metric_required_missing_exact_unit")
    return row, reasons


def _assignment_view(row: Mapping[str, Any], *, slot: _Slot) -> dict[str, Any]:
    fields = (
        "candidate_id",
        "section_id",
        "claim_unit_id",
        "skill_id",
        "skill_label",
        "fact_id",
        "metric_outcome_id",
        "metric_text",
        "metric_value",
        "metric_unit",
        "normalized_metric_signature",
        "root_id",
        "employer_lane",
        "source_family",
        "proof_strength_raw",
        "target_alignment_score",
        "claim_entailment_score",
        "metric_binding_score",
        "path_confidence_raw",
        "source_independence_score",
        "selection_margin",
        "selection_margin_available",
        "selection_margin_basis",
        "best_eligible_rejected_candidate_id",
        "graph_path_ids",
        "edge_ids",
        "citation_refs",
    )
    out = {key: row.get(key) for key in fields if key in row}
    out["section_id"] = slot.section_id
    out["claim_unit_id"] = slot.slot_id
    out["metric_required"] = slot.metric_required
    out["counts_toward_global_uniqueness"] = slot.counts_toward_global_uniqueness
    return out


def _constraint_receipt(
    *,
    slots: Sequence[_Slot],
    eligible_by_slot: Mapping[str, Sequence[Mapping[str, Any]]],
    reason: str,
) -> dict[str, Any]:
    empty = [slot.slot_id for slot in slots if not eligible_by_slot.get(slot.slot_id)]
    return {
        "schema_version": "resume_graph_allocation_failure_v1",
        "reason": reason,
        "unsatisfied_constraints": [
            "authority_and_complete_path_candidate_per_slot" if empty else "global_uniqueness",
            *(["empty_eligible_slots:" + ",".join(empty)] if empty else []),
        ],
        "slot_count": len(slots),
        "eligible_candidate_count_by_slot": {
            slot.slot_id: len(eligible_by_slot.get(slot.slot_id) or ()) for slot in slots
        },
    }


def _validate_assignment_uniqueness(assignments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    visible = [row for row in assignments if row.get("counts_toward_global_uniqueness") is True]
    skill_counts = Counter(str(row.get("skill_id") or "") for row in visible)
    metric_counts = Counter(
        str(row.get("metric_outcome_id") or "")
        for row in visible
        if str(row.get("metric_outcome_id") or "")
    )
    signature_counts = Counter(
        str(row.get("normalized_metric_signature") or "")
        for row in visible
        if str(row.get("normalized_metric_signature") or "")
    )
    repeated_skills = sorted(key for key, count in skill_counts.items() if key and count > 1)
    repeated_metrics = sorted(key for key, count in metric_counts.items() if count > 1)
    repeated_signatures = sorted(key for key, count in signature_counts.items() if count > 1)
    return {
        "schema_version": "resume_graph_uniqueness_receipt_v1",
        "visible_assignment_count": len(visible),
        "repeated_skill_ids": repeated_skills,
        "repeated_metric_outcome_ids": repeated_metrics,
        "repeated_normalized_metric_signatures": repeated_signatures,
        "pass": not repeated_skills and not repeated_metrics and not repeated_signatures,
    }


def _allocation_digest_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _allocation_digest_value(item)
            for key, item in value.items()
            if key not in _ALLOCATION_DIGEST_EXCLUDED_KEYS
            and not (
                key.startswith("prior_")
                and key.endswith(("_seal", "_digest", "_receipt"))
            )
            and not (
                key.startswith("downstream_")
                and key.endswith(("_seal", "_digest", "_receipt"))
            )
        }
    if isinstance(value, (list, tuple)):
        return [_allocation_digest_value(item) for item in value]
    return value


def _plan_digest_payload(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Return the one canonical allocation digest domain.

    Prior seals and downstream receipts may be nested by later consumers. They
    are evidence about the allocation, not allocation inputs, so they cannot
    change the immutable plan identity.
    """

    return _allocation_digest_value(plan)


def canonical_allocation_digest(plan: Mapping[str, Any]) -> str:
    return stable_digest(_plan_digest_payload(plan))


def validate_resume_graph_allocation_plan(plan: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if str(plan.get("schema_version") or "") != ALLOCATION_PLAN_SCHEMA_VERSION:
        failures.append("schema_version")
    if str(plan.get("allocation_scope") or "") not in ALLOCATION_SCOPES:
        failures.append("allocation_scope")
    assignments = plan.get("assignments")
    if not isinstance(assignments, list) or not assignments:
        failures.append("assignments")
        assignments = []
    if len({str(row.get("claim_unit_id") or "") for row in assignments if isinstance(row, Mapping)}) != len(assignments):
        failures.append("claim_unit_assignment_uniqueness")
    uniqueness = _validate_assignment_uniqueness(
        [row for row in assignments if isinstance(row, Mapping)]
    )
    if uniqueness["pass"] is not True:
        failures.append("resource_uniqueness")
    if plan.get("uniqueness_receipt") != uniqueness:
        failures.append("uniqueness_receipt")
    expected_digest = canonical_allocation_digest(plan)
    if str(plan.get("allocation_plan_digest") or "") != expected_digest:
        failures.append("allocation_plan_digest")
    if str(plan.get("allocation_scope")) == SECTION_ONLY_SCOPE and plan.get(
        "global_uniqueness_claimed"
    ) is not False:
        failures.append("section_only_global_uniqueness_claim")
    return failures


def finalize_resume_graph_allocation_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute derived receipts and seal one immutable allocation digest."""
    out = dict(plan)
    out.pop("allocation_plan_id", None)
    out.pop("allocation_plan_digest", None)
    assignments = [
        dict(row) for row in out.get("assignments") or [] if isinstance(row, Mapping)
    ]
    assignments.sort(
        key=lambda row: (
            str(row.get("section_id") or ""),
            str(row.get("claim_unit_id") or ""),
            str(row.get("candidate_id") or ""),
        )
    )
    out["assignments"] = assignments
    out["uniqueness_receipt"] = _validate_assignment_uniqueness(assignments)
    digest = canonical_allocation_digest(out)
    out["allocation_plan_digest"] = digest
    out["allocation_plan_id"] = f"resume_graph_allocation:{digest[:20]}"
    failures = validate_resume_graph_allocation_plan(out)
    if failures:
        raise ValueError("invalid allocation plan: " + ", ".join(failures))
    return out


def allocate_candidate_sets(
    *,
    candidate_sets: Mapping[str, Sequence[Mapping[str, Any]]],
    slot_specs: Sequence[Mapping[str, Any]],
    graph_digest: str,
    policy_digest: str,
    allocation_scope: str = WHOLE_RESUME_SCOPE,
    representation_policy: Mapping[str, Any] | None = None,
    section_plan_digests: Mapping[str, str] | None = None,
    max_fact_reuse: int = 2,
    max_source_family_share: float = 0.75,
    max_candidates_per_slot: int = DEFAULT_MAX_CANDIDATES_PER_SLOT,
    max_search_states: int = 250000,
) -> dict[str, Any]:
    """Allocate one candidate per slot under immutable hard constraints.

    Candidate input order and slot dispatch order are normalized before search.
    The solver uses deterministic minimum-remaining-values backtracking with the
    policy objective tuple as its candidate order.  It returns only a complete
    feasible assignment; search-budget exhaustion and impossibility are sealed
    failures, never partial plans.
    """
    scope = str(allocation_scope or "").strip().upper()
    if scope not in ALLOCATION_SCOPES:
        raise ValueError(f"invalid allocation_scope: {allocation_scope!r}")
    slots = sorted((_slot_from_row(row) for row in slot_specs), key=lambda slot: slot.slot_id)
    if not slots or len({slot.slot_id for slot in slots}) != len(slots):
        raise ValueError("allocation slots must be non-empty with unique slot_id values")
    if not str(graph_digest or "").strip() or not str(policy_digest or "").strip():
        raise ValueError("graph_digest and policy_digest are required")
    max_fact_reuse = max(1, int(max_fact_reuse))
    max_family_uses = max(1, int(math.ceil(len(slots) * float(max_source_family_share))))

    eligible_by_slot: dict[str, list[dict[str, Any]]] = {}
    predecisions: list[dict[str, Any]] = []
    for slot in slots:
        normalized: list[dict[str, Any]] = []
        seen_candidates: set[str] = set()
        for raw in candidate_sets.get(slot.slot_id) or ():
            row, reasons = _normalize_candidate(raw, slot=slot)
            candidate_id = str(row["candidate_id"])
            if candidate_id in seen_candidates:
                reasons.append("duplicate_candidate_id_in_slot")
            seen_candidates.add(candidate_id)
            if reasons:
                predecisions.append(
                    {
                        "candidate_id": candidate_id,
                        "section_id": slot.section_id,
                        "claim_unit_id": slot.slot_id,
                        "decision": "rejected",
                        "reason_codes": sorted(set(reasons)),
                    }
                )
                continue
            normalized.append(row)
        normalized.sort(key=_candidate_sort_key)
        if len(normalized) > max_candidates_per_slot:
            for row in normalized[max_candidates_per_slot:]:
                predecisions.append(
                    {
                        "candidate_id": row["candidate_id"],
                        "section_id": slot.section_id,
                        "claim_unit_id": slot.slot_id,
                        "decision": "rejected",
                        "reason_codes": ["allocation_candidate_budget"],
                    }
                )
            normalized = normalized[:max_candidates_per_slot]
        eligible_by_slot[slot.slot_id] = normalized

    if any(not eligible_by_slot[slot.slot_id] for slot in slots):
        receipt = _constraint_receipt(
            slots=slots,
            eligible_by_slot=eligible_by_slot,
            reason="empty_eligible_candidate_pool",
        )
        raise ResumeGraphAllocationError(
            "resume graph allocation unsatisfied: empty eligible candidate pool",
            receipt=receipt,
        )

    slot_by_id = {slot.slot_id: slot for slot in slots}
    chosen: dict[str, dict[str, Any]] = {}
    used_skills: set[str] = set()
    used_metrics: set[str] = set()
    used_signatures: set[str] = set()
    fact_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    search_states = 0
    budget_exhausted = False

    def feasible_rows(slot: _Slot) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in eligible_by_slot[slot.slot_id]:
            visible = slot.counts_toward_global_uniqueness
            skill_id = str(row["skill_id"])
            metric_id = str(row.get("metric_outcome_id") or "")
            signature = str(row.get("normalized_metric_signature") or "")
            fact_id = str(row["fact_id"])
            family = str(row["source_family"])
            if visible and skill_id in used_skills:
                continue
            if visible and metric_id and metric_id in used_metrics:
                continue
            if visible and signature and signature in used_signatures:
                continue
            if visible and fact_counts[fact_id] >= max_fact_reuse:
                continue
            if visible and family_counts[family] >= max_family_uses:
                continue
            rows.append(row)
        rows.sort(
            key=lambda row: (
                fact_counts[str(row["fact_id"])],
                family_counts[str(row["source_family"])],
                *_candidate_sort_key(row),
            )
        )
        return rows

    def search() -> bool:
        nonlocal search_states, budget_exhausted
        if len(chosen) == len(slots):
            return True
        search_states += 1
        if search_states > max_search_states:
            budget_exhausted = True
            return False
        unresolved = [slot for slot in slots if slot.slot_id not in chosen]
        ranked = [(feasible_rows(slot), slot) for slot in unresolved]
        ranked.sort(key=lambda pair: (len(pair[0]), pair[1].slot_id))
        rows, slot = ranked[0]
        if not rows:
            return False
        for row in rows:
            visible = slot.counts_toward_global_uniqueness
            skill_id = str(row["skill_id"])
            metric_id = str(row.get("metric_outcome_id") or "")
            signature = str(row.get("normalized_metric_signature") or "")
            fact_id = str(row["fact_id"])
            family = str(row["source_family"])
            chosen[slot.slot_id] = row
            if visible:
                used_skills.add(skill_id)
                if metric_id:
                    used_metrics.add(metric_id)
                if signature:
                    used_signatures.add(signature)
                fact_counts[fact_id] += 1
                family_counts[family] += 1
            if search():
                return True
            if visible:
                used_skills.remove(skill_id)
                if metric_id:
                    used_metrics.remove(metric_id)
                if signature:
                    used_signatures.remove(signature)
                fact_counts[fact_id] -= 1
                family_counts[family] -= 1
            del chosen[slot.slot_id]
        return False

    if not search():
        conflicting_resources = sorted(
            {
                "skill_id",
                *(
                    ["metric_outcome_id", "normalized_metric_signature"]
                    if any(slot.metric_required for slot in slots)
                    else []
                ),
                "fact_id_concentration",
                "source_family_concentration",
            }
        )
        receipt = _constraint_receipt(
            slots=slots,
            eligible_by_slot=eligible_by_slot,
            reason="search_budget_exhausted" if budget_exhausted else "hard_constraints_unsatisfied",
        )
        receipt["unsatisfied_constraints"] = conflicting_resources
        receipt["search_states"] = search_states
        receipt["max_search_states"] = max_search_states
        raise ResumeGraphAllocationError(
            "resume graph allocation unsatisfied: " + ", ".join(conflicting_resources),
            receipt=receipt,
        )

    assignments = []
    for slot in slots:
        selected = dict(chosen[slot.slot_id])
        selected.update(
            _selection_margin_receipt(selected, eligible_by_slot[slot.slot_id])
        )
        assignments.append(_assignment_view(selected, slot=slot))
    selected_candidate_ids = {str(row["candidate_id"]) for row in assignments}
    candidate_decisions = list(predecisions)
    for slot in slots:
        for row in eligible_by_slot[slot.slot_id]:
            selected = str(row["candidate_id"]) in selected_candidate_ids
            candidate_decisions.append(
                {
                    "candidate_id": str(row["candidate_id"]),
                    "section_id": slot.section_id,
                    "claim_unit_id": slot.slot_id,
                    "decision": "selected" if selected else "rejected",
                    "reason_codes": [
                        "selected_by_global_allocation"
                        if selected
                        else "global_constraint_or_objective_not_selected"
                    ],
                }
            )
    candidate_decisions.sort(
        key=lambda row: (
            str(row.get("section_id") or ""),
            str(row.get("claim_unit_id") or ""),
            str(row.get("candidate_id") or ""),
        )
    )
    uniqueness = _validate_assignment_uniqueness(assignments)
    if uniqueness["pass"] is not True:
        raise AssertionError("allocator emitted a resource-reuse violation")
    section_counts = Counter(str(row["section_id"]) for row in assignments)
    required_counts = Counter(slot.section_id for slot in slots)
    budget_receipt = {
        "schema_version": "resume_graph_allocation_budget_receipt_v1",
        "required_assignment_count_by_section": dict(sorted(required_counts.items())),
        "actual_assignment_count_by_section": dict(sorted(section_counts.items())),
        "pass": section_counts == required_counts,
    }
    plan: dict[str, Any] = {
        "schema_version": ALLOCATION_PLAN_SCHEMA_VERSION,
        "allocation_scope": scope,
        "global_uniqueness_claimed": scope == WHOLE_RESUME_SCOPE,
        "graph_digest": str(graph_digest),
        "policy_digest": str(policy_digest),
        "section_plan_digests": dict(sorted((section_plan_digests or {}).items())),
        "representation_policy": dict(
            representation_policy
            or {
                "canonical_role_representation": "bullets",
                "narratives_are_derived_alternatives": True,
                "alternative_assignments_count_toward_global_uniqueness": False,
            }
        ),
        "assignments": assignments,
        "candidate_decisions": candidate_decisions,
        "solver_metadata": {
            "solver": "deterministic_mrv_constraint_search_v1",
            "stable_tie_break": "candidate_id_ascending",
            "objective_order": [
                "proof_strength_raw",
                "path_confidence_raw",
                "source_independence_score",
                "target_alignment_score",
                "stable_candidate_id",
            ],
            "selection_margin_policy": (
                "signed_first_differing_lexicographic_component_vs_"
                "best_locally_eligible_rejected_v1"
            ),
            "search_states": search_states,
            "max_search_states": max_search_states,
            "max_candidates_per_slot": max_candidates_per_slot,
            "candidate_input_order_independent": True,
            "section_dispatch_order_independent": True,
        },
        "hard_constraints": {
            "skill_id_zero_reuse": True,
            "metric_outcome_id_zero_reuse": True,
            "normalized_metric_signature_zero_reuse": True,
            "max_fact_reuse": max_fact_reuse,
            "max_source_family_uses": max_family_uses,
            "employer_locality": True,
            "authority_pass_required": True,
            "complete_path_required": True,
        },
        "uniqueness_receipt": uniqueness,
        "budget_receipt": budget_receipt,
        "candidate_conservation_receipt": {
            "candidate_count": len(candidate_decisions),
            "terminal_decision_count": sum(
                1 for row in candidate_decisions if row.get("decision") in {"selected", "rejected"}
            ),
            "pass": all(
                row.get("decision") in {"selected", "rejected"} for row in candidate_decisions
            ),
        },
        "durable_graph_state_mutated": False,
    }
    return finalize_resume_graph_allocation_plan(plan)


def build_resume_graph_usage_ledger(plan: Mapping[str, Any]) -> dict[str, Any]:
    failures = validate_resume_graph_allocation_plan(plan)
    if failures:
        raise ValueError("cannot build usage ledger from invalid allocation plan: " + ", ".join(failures))
    reservations: list[dict[str, Any]] = []
    for assignment in plan.get("assignments") or []:
        if not isinstance(assignment, Mapping):
            continue
        base = {
            "section_id": str(assignment.get("section_id") or ""),
            "claim_unit_id": str(assignment.get("claim_unit_id") or ""),
            "counts_toward_global_uniqueness": bool(
                assignment.get("counts_toward_global_uniqueness")
            ),
        }
        for resource_type, key in (
            ("skill_id", "skill_id"),
            ("fact_id", "fact_id"),
            ("source_family", "source_family"),
            ("metric_outcome_id", "metric_outcome_id"),
            ("normalized_metric_signature", "normalized_metric_signature"),
        ):
            resource_id = str(assignment.get(key) or "").strip()
            if resource_id:
                reservations.append(
                    {**base, "resource_type": resource_type, "resource_id": resource_id}
                )
    reservations.sort(
        key=lambda row: (
            row["resource_type"],
            row["resource_id"],
            row["section_id"],
            row["claim_unit_id"],
        )
    )
    ledger: dict[str, Any] = {
        "schema_version": USAGE_LEDGER_SCHEMA_VERSION,
        "allocation_plan_digest": str(plan.get("allocation_plan_digest") or ""),
        "allocation_scope": str(plan.get("allocation_scope") or ""),
        "current_run_only": True,
        "durable_graph_state_mutated": False,
        "reservations": reservations,
        "reservation_count": len(reservations),
    }
    ledger["usage_ledger_digest"] = stable_digest(ledger)
    return ledger


def _authority_rows_by_root(
    section_plan: Mapping[str, Any],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for raw in section_plan.get("graph_candidate_decision_ledger") or []:
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        root_id = str(row.get("root_id") or row.get("candidate_id") or "").strip()
        if not root_id:
            continue
        candidate_type = str(row.get("candidate_type") or "")
        bucket = grouped.setdefault(
            root_id,
            {"root": [], "leaf_skill": [], "source_fact": [], "metric_outcome": []},
        )
        bucket_key = "root" if candidate_type == "role_episode_root" else candidate_type
        if bucket_key in bucket:
            bucket[bucket_key].append(row)
    for bucket in grouped.values():
        for rows in bucket.values():
            rows.sort(key=lambda row: str(row.get("candidate_path_id") or ""))
    return grouped


def _default_slot_specs(
    section_plans: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for index in range(1, 9):
        slots.append(
            {
                "slot_id": f"competencies:skill:{index:02d}",
                "section_id": "competencies",
                "metric_required": False,
            }
        )
    for section_id, claim_units in CANONICAL_BULLET_CLAIM_UNITS.items():
        metric_available = any(
            extract_exact_metric_value_unit(str(row.get("metric") or ""))[0]
            for bucket in _authority_rows_by_root(section_plans[section_id]).values()
            for row in bucket["metric_outcome"]
            if row.get("authority_pass") is True
        )
        for index, claim_unit in enumerate(claim_units):
            slots.append(
                {
                    "slot_id": f"{section_id}:{claim_unit}",
                    "section_id": section_id,
                    "metric_required": metric_available and index == 0,
                    "employer_lane": EMPLOYER_LANE_BY_SECTION[section_id],
                }
            )
    for index in range(1, 4):
        slots.append(
            {
                "slot_id": f"executive_summary:claim:{index:02d}",
                "section_id": "executive_summary",
                "metric_required": index == 1,
            }
        )
    for index in range(1, 3):
        slots.append(
            {
                "slot_id": f"headline:skill:{index:02d}",
                "section_id": "headline",
                "metric_required": False,
            }
        )
    return slots


def _candidate_sets_from_section_plans(
    section_plans: Mapping[str, Mapping[str, Any]],
    slot_specs: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    grouped_by_section = {
        section_id: _authority_rows_by_root(plan)
        for section_id, plan in section_plans.items()
        if section_id in CANONICAL_VISIBLE_SECTIONS
    }
    for raw_slot in slot_specs:
        slot = _slot_from_row(raw_slot)
        rows: list[dict[str, Any]] = []
        for root_id, bucket in grouped_by_section[slot.section_id].items():
            roots = [row for row in bucket["root"] if row.get("authority_pass") is True]
            skills = [row for row in bucket["leaf_skill"] if row.get("authority_pass") is True]
            facts = [row for row in bucket["source_fact"] if row.get("authority_pass") is True]
            metrics = [row for row in bucket["metric_outcome"] if row.get("authority_pass") is True]
            if not roots or not skills or not facts:
                continue
            root = roots[0]
            employer_lane = str(root.get("employer_lane") or "")
            if slot.employer_lane and employer_lane != slot.employer_lane:
                continue
            metric_options: list[dict[str, Any] | None] = [None]
            if slot.metric_required:
                metric_options = []
                for metric in metrics:
                    value, unit = extract_exact_metric_value_unit(str(metric.get("metric") or ""))
                    if value and unit:
                        metric_options.append({**metric, "metric_value": value, "metric_unit": unit})
                if not metric_options:
                    continue
            for skill in skills:
                for fact in facts:
                    for metric in metric_options:
                        skill_id = str(skill.get("candidate_id") or "")
                        fact_id = str(fact.get("candidate_id") or "")
                        metric_id = str((metric or {}).get("candidate_id") or "")
                        graph_path_ids = [
                            str(root.get("candidate_path_id") or f"root:{root_id}"),
                            str(skill.get("candidate_path_id") or ""),
                            str(fact.get("candidate_path_id") or ""),
                        ]
                        edge_ids = [
                            stable_edge_id(root_id, "role_episode_contains_skill", skill_id),
                            stable_edge_id(root_id, "role_episode_supported_by_fact", fact_id),
                        ]
                        if metric is not None:
                            graph_path_ids.append(str(metric.get("candidate_path_id") or ""))
                            edge_ids.append(
                                stable_edge_id(
                                    root_id,
                                    "role_episode_has_metric_outcome",
                                    metric_id,
                                )
                            )
                        citation_refs = _strings(
                            list(fact.get("source_refs") or [])
                            + list((fact.get("authority") or {}).get("source_refs") or [])
                            + [fact_id]
                        )
                        skill_sources = _strings(
                            list(skill.get("source_refs") or [])
                            + list((skill.get("authority") or {}).get("source_refs") or [])
                        )
                        metric_text = str((metric or {}).get("metric") or "")
                        candidate: dict[str, Any] = {
                            "section_id": slot.section_id,
                            "claim_unit_id": slot.slot_id,
                            "skill_id": skill_id,
                            "skill_label": str(skill.get("skill_label") or ""),
                            "fact_id": fact_id,
                            "metric_outcome_id": metric_id,
                            "metric_text": metric_text,
                            "metric_value": str((metric or {}).get("metric_value") or ""),
                            "metric_unit": str((metric or {}).get("metric_unit") or ""),
                            "normalized_metric_signature": normalize_metric_signature(metric_text),
                            "root_id": root_id,
                            "employer_lane": employer_lane,
                            "source_family": employer_lane,
                            "authority_pass": True,
                            "proof_strength_raw": float(skill.get("proof_strength_raw") or 0.0),
                            "target_alignment_score": round(
                                (
                                    float(root.get("target_alignment_score") or 0.0)
                                    + float(skill.get("target_alignment_score") or 0.0)
                                    + float((metric or {}).get("target_alignment_score") or 0.0)
                                )
                                / (3 if metric is not None else 2),
                                6,
                            ),
                            "claim_entailment_score": 1.0,
                            "metric_binding_score": 1.0 if metric is not None else 0.0,
                            "path_confidence_raw": 1.0,
                            "source_independence_score": round(
                                min(len(set(citation_refs + skill_sources)), 4) / 4,
                                6,
                            ),
                            "graph_path_ids": _strings(graph_path_ids),
                            "edge_ids": edge_ids,
                            "citation_refs": citation_refs,
                            "root_claim_text": str(root.get("claim_text") or ""),
                            "root_claim_action": str(root.get("claim_action") or ""),
                            "root_claim_scope": str(root.get("claim_scope") or ""),
                            "root_claim_outcome": str(root.get("claim_outcome") or ""),
                        }
                        candidate["candidate_id"] = "alloc-cand:" + stable_digest(candidate)[:24]
                        rows.append(candidate)
        rows.sort(key=_candidate_sort_key)
        out[slot.slot_id] = rows
    return out


def _bind_embedding_candidates(
    candidate_sets: Mapping[str, Sequence[Mapping[str, Any]]],
    slot_specs: Sequence[Mapping[str, Any]],
    skill_scores_by_section: Mapping[str, Mapping[str, float]],
) -> dict[str, list[dict[str, Any]]]:
    """Narrow graph candidates to exact assertion eligibility before allocation."""
    missing_sections = sorted(
        set(ALL_CLAIM_BEARING_SECTIONS) - set(skill_scores_by_section)
    )
    if missing_sections:
        raise ResumeGraphAllocationError(
            "embedding candidate authority is incomplete",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["embedding_section_candidate_coverage"],
                "missing_sections": missing_sections,
            },
        )
    slot_section = {
        str(row.get("slot_id") or ""): str(row.get("section_id") or "")
        for row in slot_specs
    }
    narrowed: dict[str, list[dict[str, Any]]] = {}
    for slot_id, raw_rows in candidate_sets.items():
        section_id = slot_section.get(slot_id, "")
        scores = skill_scores_by_section.get(section_id) or {}
        rows: list[dict[str, Any]] = []
        for raw in raw_rows:
            skill_id = str(raw.get("skill_id") or "")
            if skill_id not in scores:
                continue
            row = dict(raw)
            row["embedding_similarity"] = round(float(scores[skill_id]), 9)
            rows.append(row)
        rows.sort(key=_candidate_sort_key)
        if not rows:
            raise ResumeGraphAllocationError(
                f"{slot_id}: no graph candidates remain after assertion eligibility",
                receipt={
                    "schema_version": "resume_graph_allocation_failure_v1",
                    "unsatisfied_constraints": ["embedding_candidate_intersection"],
                    "slot_id": slot_id,
                    "section_id": section_id,
                },
            )
        narrowed[slot_id] = rows
    return narrowed


def _bind_assignment_embedding_scores(
    plan: Mapping[str, Any],
    skill_scores_by_section: Mapping[str, Mapping[str, float]],
) -> dict[str, Any]:
    out = dict(plan)
    assignments: list[dict[str, Any]] = []
    for raw in plan.get("assignments") or []:
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        section_id = str(row.get("section_id") or "")
        skill_id = str(row.get("skill_id") or "")
        scores = skill_scores_by_section.get(section_id) or {}
        if skill_id not in scores:
            raise ResumeGraphAllocationError(
                f"{section_id}: allocated skill lacks an exact embedding candidate",
                receipt={
                    "schema_version": "resume_graph_allocation_failure_v1",
                    "unsatisfied_constraints": ["embedding_assignment_coverage"],
                    "section_id": section_id,
                    "skill_id": skill_id,
                },
            )
        row["embedding_similarity"] = round(float(scores[skill_id]), 9)
        assignments.append(row)
    out["assignments"] = assignments
    out["embedding_candidate_authority"] = {
        "schema_version": "resume_graph_embedding_candidate_authority_v1",
        "section_candidate_counts": {
            section_id: len(scores)
            for section_id, scores in sorted(skill_scores_by_section.items())
        },
        "similarity_is_claim_authority": False,
        "allocation_narrowing_only": True,
        "pass": True,
    }
    return finalize_resume_graph_allocation_plan(out)


def _append_derived_narrative_assignments(plan: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(plan)
    assignments = [dict(row) for row in plan.get("assignments") or []]
    decisions = [dict(row) for row in plan.get("candidate_decisions") or []]
    for narrative_section, bullet_section in sorted(NARRATIVE_DERIVATION_POLICY.items()):
        upstream = [row for row in assignments if row.get("section_id") == bullet_section]
        for index, source in enumerate(upstream, start=1):
            derived = dict(source)
            derived["section_id"] = narrative_section
            derived["claim_unit_id"] = f"{narrative_section}:derived:{index:02d}"
            derived["candidate_id"] = f"derived:{narrative_section}:{source['candidate_id']}"
            derived["derived_from_section_id"] = bullet_section
            derived["derived_from_claim_unit_id"] = str(source.get("claim_unit_id") or "")
            derived["counts_toward_global_uniqueness"] = False
            derived["metric_required"] = False
            assignments.append(derived)
            decisions.append(
                {
                    "candidate_id": derived["candidate_id"],
                    "section_id": narrative_section,
                    "claim_unit_id": derived["claim_unit_id"],
                    "decision": "selected",
                    "reason_codes": ["derived_alternative_from_frozen_bullet_allocation"],
                }
            )
    out["assignments"] = assignments
    out["candidate_decisions"] = sorted(
        decisions,
        key=lambda row: (
            str(row.get("section_id") or ""),
            str(row.get("claim_unit_id") or ""),
            str(row.get("candidate_id") or ""),
        ),
    )
    required = Counter(str(row.get("section_id") or "") for row in assignments)
    out["budget_receipt"] = {
        "schema_version": "resume_graph_allocation_budget_receipt_v1",
        "required_assignment_count_by_section": dict(sorted(required.items())),
        "actual_assignment_count_by_section": dict(sorted(required.items())),
        "pass": True,
    }
    out["candidate_conservation_receipt"] = {
        "candidate_count": len(out["candidate_decisions"]),
        "terminal_decision_count": len(out["candidate_decisions"]),
        "pass": True,
    }
    return finalize_resume_graph_allocation_plan(out)


def build_section_final_evidence_contracts(
    *,
    allocation_plan: Mapping[str, Any],
    section_plans: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    failures = validate_resume_graph_allocation_plan(allocation_plan)
    if failures:
        raise ValueError("allocation plan invalid: " + ", ".join(failures))
    contracts: dict[str, dict[str, Any]] = {}
    for section_id in ALL_CLAIM_BEARING_SECTIONS:
        source_plan = section_plans.get(section_id) or {}
        traversal = (
            source_plan.get("graph_traversal_receipt")
            if isinstance(source_plan.get("graph_traversal_receipt"), Mapping)
            else {}
        )
        assignments = [
            dict(row)
            for row in allocation_plan.get("assignments") or []
            if isinstance(row, Mapping) and row.get("section_id") == section_id
        ]
        derived_from = NARRATIVE_DERIVATION_POLICY.get(section_id, "")
        contract: dict[str, Any] = {
            "schema_version": "section_final_graph_evidence_contract_v1",
            "section_id": section_id,
            "allocation_scope": str(allocation_plan.get("allocation_scope") or ""),
            "allocation_plan_digest": str(
                allocation_plan.get("allocation_plan_digest") or ""
            ),
            "source_section_plan_id": str(source_plan.get("plan_id") or ""),
            "source_section_plan_digest": str(source_plan.get("plan_digest") or ""),
            "graph_digest": str(allocation_plan.get("graph_digest") or ""),
            "assignments": assignments,
            "assignment_count": len(assignments),
            "representation_mode": "DERIVED_ALTERNATIVE" if derived_from else "CANONICAL_VISIBLE",
            "derived_from_section_id": derived_from,
            "counts_toward_global_uniqueness": not bool(derived_from),
            "traversal_receipt_digest": str(traversal.get("events_digest") or ""),
            "traversal_conservation_pass": traversal.get("pass") is True,
            "pass": bool(assignments)
            and bool(source_plan.get("plan_digest"))
            and traversal.get("pass") is True,
        }
        contract["contract_digest"] = stable_digest(contract)
        contracts[section_id] = contract
    return contracts


def slice_section_plan_for_allocation(
    *,
    section_plan: Mapping[str, Any],
    allocation_plan: Mapping[str, Any],
    final_evidence_contract: Mapping[str, Any],
    section_id: str,
) -> dict[str, Any]:
    """Project the frozen global assignment into one canonical section fact plan."""
    from apps_rg.runtime.c0.c03_resume_graph_contracts import (
        finalize_canonical_section_plan,
    )

    failures = validate_resume_graph_allocation_plan(allocation_plan)
    if failures:
        raise ResumeGraphAllocationError(
            "cannot slice invalid allocation plan",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["allocation_plan_validation"],
                "validation_failures": failures,
            },
        )
    if str(final_evidence_contract.get("section_id") or "") != section_id:
        raise ValueError(f"{section_id}: final evidence contract section mismatch")
    allocation_digest = str(allocation_plan.get("allocation_plan_digest") or "")
    if str(final_evidence_contract.get("allocation_plan_digest") or "") != allocation_digest:
        raise ValueError(f"{section_id}: final evidence contract allocation digest mismatch")
    assignments = [
        dict(row)
        for row in allocation_plan.get("assignments") or []
        if isinstance(row, Mapping) and row.get("section_id") == section_id
    ]
    if not assignments:
        raise ResumeGraphAllocationError(
            f"{section_id}: frozen allocation has no assignments",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["section_assignment_coverage"],
                "section_id": section_id,
            },
        )
    by_root: dict[str, list[dict[str, Any]]] = {}
    for assignment in assignments:
        root_id = str(assignment.get("root_id") or "").strip()
        if not root_id:
            raise ValueError(f"{section_id}: assignment missing root_id")
        by_root.setdefault(root_id, []).append(assignment)
    preserve_root_authority = section_id == "competencies"
    source_facts_by_root = {
        str(row.get("role_episode_bundle_id") or row.get("fact_id") or ""): dict(row)
        for row in section_plan.get("facts") or []
        if isinstance(row, Mapping)
        and preserve_root_authority
        and str(row.get("role_episode_bundle_id") or row.get("fact_id") or "")
    }
    source_skills_by_root: dict[str, list[dict[str, Any]]] = {}
    for raw in section_plan.get("selected_skills") or []:
        if not isinstance(raw, Mapping):
            continue
        root_id = str(raw.get("role_episode_bundle_id") or "").strip()
        if preserve_root_authority and root_id in by_root:
            source_skills_by_root.setdefault(root_id, []).append(dict(raw))
    source_metrics_by_root: dict[str, list[dict[str, Any]]] = {}
    for raw in section_plan.get("selected_metrics_detail") or []:
        if not isinstance(raw, Mapping):
            continue
        root_id = str(raw.get("role_episode_bundle_id") or "").strip()
        if preserve_root_authority and root_id in by_root:
            source_metrics_by_root.setdefault(root_id, []).append(dict(raw))

    facts: list[dict[str, Any]] = []
    selected_skills: list[dict[str, Any]] = []
    selected_metrics_detail: list[dict[str, Any]] = []
    selected_edges: list[dict[str, Any]] = []
    allowed_ids: list[str] = []
    for root_id, rows in sorted(by_root.items()):
        rows.sort(key=lambda row: str(row.get("claim_unit_id") or ""))
        root_skills = {
            str(row.get("skill_id") or ""): dict(row)
            for row in source_skills_by_root.get(root_id, [])
            if str(row.get("skill_id") or "")
        }
        root_metrics = {
            str(row.get("metric_outcome_id") or ""): dict(row)
            for row in source_metrics_by_root.get(root_id, [])
            if str(row.get("metric_outcome_id") or "")
        }
        for assignment in rows:
            skill_id = str(assignment.get("skill_id") or "")
            if skill_id:
                root_skills.setdefault(
                    skill_id,
                    {
                        "skill_id": skill_id,
                        "role_episode_bundle_id": root_id,
                        "employer_lane": str(assignment.get("employer_lane") or ""),
                        "proof_strength_raw": float(
                            assignment.get("proof_strength_raw") or 0.0
                        ),
                        "target_alignment_score": float(
                            assignment.get("target_alignment_score") or 0.0
                        ),
                    },
                )
                root_skills[skill_id]["claim_unit_id"] = str(
                    assignment.get("claim_unit_id") or ""
                )
            metric_id = str(assignment.get("metric_outcome_id") or "")
            if metric_id:
                root_metrics.setdefault(
                    metric_id,
                    {
                        "metric_outcome_id": metric_id,
                        "role_episode_bundle_id": root_id,
                        "employer_lane": str(assignment.get("employer_lane") or ""),
                        "metric": str(assignment.get("metric_text") or ""),
                        "metric_value": str(assignment.get("metric_value") or ""),
                        "metric_unit": str(assignment.get("metric_unit") or ""),
                        "normalized_metric_signature": str(
                            assignment.get("normalized_metric_signature") or ""
                        ),
                    },
                )
                root_metrics[metric_id]["claim_unit_id"] = str(
                    assignment.get("claim_unit_id") or ""
                )
        skill_ids = sorted(root_skills)
        metric_ids = sorted(root_metrics)
        source_fact_ids = _strings(row.get("fact_id") for row in rows)
        metric_values = _strings(
            row.get("metric") or row.get("metric_text")
            for row in root_metrics.values()
        )
        first = rows[0]
        fact = dict(source_facts_by_root.get(root_id) or {})
        linked_identity_ids = _strings(
            list(fact.get("linked_identity_fact_ids") or []) + source_fact_ids
        )
        linked_source_ids = _strings(
            list(fact.get("linked_source_fact_ids") or []) + source_fact_ids
        )
        fact.update(
            {
                "fact_id": root_id,
                "candidate_fact_id": root_id,
                "claim_text": str(
                    fact.get("claim_text") or first.get("root_claim_text") or root_id
                ),
                "role_episode_bundle_id": root_id,
                "graph_evidence_type": "role_episode_bundle",
                "employer_lane": str(
                    fact.get("employer_lane") or first.get("employer_lane") or ""
                ),
                "source_employment": str(
                    fact.get("source_employment")
                    or fact.get("employer_lane")
                    or first.get("employer_lane")
                    or ""
                ),
                "graph_skill_node_ids": skill_ids,
                "metric_outcome_ids": metric_ids,
                "selected_metric_ids": metric_ids,
                "allowed_graph_evidence_ids": _strings(
                    list(fact.get("allowed_graph_evidence_ids") or [])
                    + [root_id, *source_fact_ids, *skill_ids, *metric_ids]
                ),
                "linked_identity_fact_ids": linked_identity_ids,
                "linked_source_fact_ids": linked_source_ids,
                "source_fact_ids": [root_id],
                "confidence": str(fact.get("confidence") or "HIGH"),
                "support_level": "allocation_authority_pass",
                "verification_status": "allocation_authority_pass",
                "metric_values": metric_values,
                "technologies": skill_ids,
                "domain": str(fact.get("domain") or first.get("root_claim_scope") or ""),
                "allocation_claim_unit_ids": [
                    str(row.get("claim_unit_id") or "") for row in rows
                ],
                "allocation_plan_digest": allocation_digest,
            }
        )
        facts.append(fact)
        allowed_ids.extend(fact["allowed_graph_evidence_ids"])
        selected_skills.extend(root_skills[skill_id] for skill_id in skill_ids)
        selected_metrics_detail.extend(
            root_metrics[metric_id] for metric_id in metric_ids
        )
        for row in rows:
            selected_edges.extend(
                {
                    "edge_id": edge_id,
                    "source": root_id,
                    "target": "",
                    "edge_type": "allocation_bound_graph_edge",
                }
                for edge_id in row.get("edge_ids") or []
            )
        source_edge_keys = {
            (
                str(edge.get("source") or ""),
                str(edge.get("edge_type") or ""),
                str(edge.get("target") or ""),
            )
            for edge in section_plan.get("selected_edges") or []
            if isinstance(edge, Mapping)
            and preserve_root_authority
            and str(edge.get("source") or "") == root_id
            and str(edge.get("target") or "") in fact["allowed_graph_evidence_ids"]
        }
        selected_edges.extend(
            {
                "source": source,
                "edge_type": edge_type,
                "target": target,
            }
            for source, edge_type, target in sorted(source_edge_keys)
        )
    out = dict(section_plan)
    out.pop("plan_id", None)
    out.pop("plan_digest", None)
    out.update(
        {
            "facts": facts,
            "required_fact_ids": [str(row["fact_id"]) for row in facts],
            "allowed_graph_evidence_ids": _strings(allowed_ids),
            "selected_nodes": sorted(by_root),
            "selected_edges": selected_edges,
            "selected_skills": selected_skills,
            "selected_skill_ids": _strings(
                row.get("skill_id") for row in selected_skills
            ),
            "selected_metrics": _strings(
                row.get("metric_outcome_id") for row in selected_metrics_detail
            ),
            "selected_metrics_detail": selected_metrics_detail,
            "selected_employer_lane_ids": _strings(
                row.get("employer_lane") for row in assignments
            ),
            "allocation_scope": str(allocation_plan.get("allocation_scope") or ""),
            "allocation_plan_id": str(allocation_plan.get("allocation_plan_id") or ""),
            "allocation_plan_digest": allocation_digest,
            "allocation_assignments": assignments,
            "final_graph_evidence_contract": dict(final_evidence_contract),
            "global_uniqueness_claimed": bool(
                allocation_plan.get("global_uniqueness_claimed")
            ),
            "durable_graph_state_mutated": False,
        }
    )
    return finalize_canonical_section_plan(out)


def build_whole_resume_graph_allocation(
    *,
    repo_root: Path,
    target_role: str = "",
    jd_text: str = "",
    briefing_text: str = "",
    section_order: Sequence[str] | None = None,
    embedding_skill_scores_by_section: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, Any]:
    """Traverse all claim-bearing lanes, allocate once, and freeze section slices."""
    from apps_rg.runtime.c0.c03_resume_graph_contracts import ResumeGraphSelectionPolicyV2
    from apps_rg.runtime.sections.graph_role_episode_selector import (
        build_selected_graph_evidence_plan_for_section,
    )

    requested = list(section_order or ALL_CLAIM_BEARING_SECTIONS)
    if set(requested) != set(ALL_CLAIM_BEARING_SECTIONS):
        raise ValueError("whole-resume allocation requires all eleven claim-bearing sections")
    section_plans: dict[str, dict[str, Any]] = {}
    for section_id in requested:
        plan, _ordered, _allowed = build_selected_graph_evidence_plan_for_section(
            repo_root=repo_root,
            section_id=section_id,
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
        )
        section_plans[section_id] = plan
    graph_digests = {
        str((plan.get("source_authority_contract") or {}).get("graph_digest") or "")
        for plan in section_plans.values()
    }
    graph_versions = {
        str((plan.get("source_authority_contract") or {}).get("graph_version") or "")
        for plan in section_plans.values()
    }
    if len(graph_digests) != 1 or "" in graph_digests:
        raise ResumeGraphAllocationError(
            "section graph source digests disagree",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["graph_source_digest_parity"],
                "observed_graph_digests": sorted(graph_digests),
            },
        )
    if len(graph_versions) != 1:
        raise ResumeGraphAllocationError(
            "section graph versions disagree",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["graph_version_parity"],
                "observed_graph_versions": sorted(graph_versions),
            },
        )
    graph_digest = next(iter(graph_digests))
    graph_version = next(iter(graph_versions))
    slot_specs = _default_slot_specs(section_plans)
    section_budgets: dict[str, dict[str, int]] = {}
    for slot in slot_specs:
        section_id = str(slot["section_id"])
        section_budgets.setdefault(section_id, {"min_assignments": 0, "max_assignments": 0})
        section_budgets[section_id]["min_assignments"] += 1
        section_budgets[section_id]["max_assignments"] += 1
    policy = ResumeGraphSelectionPolicyV2(
        graph_snapshot_digest=graph_digest,
        graph_version=graph_version,
        section_budgets=section_budgets,
    )
    candidates = _candidate_sets_from_section_plans(section_plans, slot_specs)
    if embedding_skill_scores_by_section is not None:
        candidates = _bind_embedding_candidates(
            candidates,
            slot_specs,
            embedding_skill_scores_by_section,
        )
    plan = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slot_specs,
        graph_digest=graph_digest,
        policy_digest=policy.policy_digest,
        representation_policy={
            "canonical_role_representation": "bullets",
            "narratives_are_derived_alternatives": True,
            "narrative_derivation_map": dict(sorted(NARRATIVE_DERIVATION_POLICY.items())),
            "alternative_assignments_count_toward_global_uniqueness": False,
        },
        section_plan_digests={
            section_id: str(section_plan.get("plan_digest") or "")
            for section_id, section_plan in section_plans.items()
        },
        max_fact_reuse=policy.max_fact_reuse,
        max_source_family_share=policy.max_source_family_share,
    )
    plan["selection_policy"] = policy.to_dict()
    plan["section_traversal_receipts"] = {
        section_id: {
            "plan_digest": str(section_plan.get("plan_digest") or ""),
            "events_digest": str(
                (section_plan.get("graph_traversal_receipt") or {}).get("events_digest")
                or ""
            ),
            "candidate_conservation_pass": bool(
                (section_plan.get("graph_candidate_receipt") or {}).get(
                    "candidate_conservation_pass"
                )
            ),
            "traversal_pass": bool(
                (section_plan.get("graph_traversal_receipt") or {}).get("pass")
            ),
        }
        for section_id, section_plan in sorted(section_plans.items())
    }
    plan = _append_derived_narrative_assignments(plan)
    if embedding_skill_scores_by_section is not None:
        plan = _bind_assignment_embedding_scores(
            plan,
            embedding_skill_scores_by_section,
        )
    ledger = build_resume_graph_usage_ledger(plan)
    contracts = build_section_final_evidence_contracts(
        allocation_plan=plan,
        section_plans=section_plans,
    )
    return {
        "allocation_plan": plan,
        "usage_ledger": ledger,
        "section_final_evidence_contracts": contracts,
        "section_plans": section_plans,
    }


def build_section_only_graph_allocation(
    *,
    section_plan: Mapping[str, Any],
    section_id: str,
) -> dict[str, Any]:
    """Freeze a standalone section without asserting whole-resume uniqueness."""
    facts_by_root = {
        str(row.get("role_episode_bundle_id") or row.get("fact_id") or ""): dict(row)
        for row in section_plan.get("facts") or []
        if isinstance(row, Mapping)
    }
    selected_skills = [
        dict(row)
        for row in section_plan.get("selected_skills") or []
        if isinstance(row, Mapping) and row.get("skill_id")
    ]
    if not selected_skills:
        raise ResumeGraphAllocationError(
            f"{section_id}: standalone graph plan has no selected skills",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["section_only_selected_skill_coverage"],
                "section_id": section_id,
            },
        )
    slot_specs: list[dict[str, Any]] = []
    candidates: dict[str, list[dict[str, Any]]] = {}
    for index, skill in enumerate(selected_skills, start=1):
        slot_id = f"{section_id}:section_only:{index:02d}"
        root_id = str(skill.get("role_episode_bundle_id") or "")
        fact = facts_by_root.get(root_id) or {}
        source_fact_ids = _strings(
            fact.get("linked_source_fact_ids") or fact.get("source_fact_ids") or [root_id]
        )
        source_fact_id = source_fact_ids[0] if source_fact_ids else root_id
        employer_lane = str(skill.get("employer_lane") or fact.get("employer_lane") or "")
        slot_specs.append(
            {
                "slot_id": slot_id,
                "section_id": section_id,
                "metric_required": False,
                "employer_lane": employer_lane,
            }
        )
        candidate = {
            "section_id": section_id,
            "claim_unit_id": slot_id,
            "skill_id": str(skill.get("skill_id") or ""),
            "fact_id": source_fact_id,
            "root_id": root_id,
            "employer_lane": employer_lane,
            "source_family": employer_lane or source_fact_id,
            "authority_pass": True,
            "proof_strength_raw": float(skill.get("proof_strength_raw") or 0.0),
            "target_alignment_score": float(skill.get("target_alignment_score") or 0.0),
            "path_confidence_raw": 1.0,
            "source_independence_score": 0.5,
            "graph_path_ids": [
                f"root:{root_id}",
                f"root:{root_id}/skill:{skill.get('skill_id')}",
                f"root:{root_id}/fact:{source_fact_id}",
            ],
            "edge_ids": [
                stable_edge_id(root_id, "role_episode_contains_skill", str(skill.get("skill_id") or "")),
                stable_edge_id(root_id, "role_episode_supported_by_fact", source_fact_id),
            ],
            "citation_refs": source_fact_ids,
            "root_claim_text": str(fact.get("claim_text") or root_id),
        }
        candidate["candidate_id"] = "section-only:" + stable_digest(candidate)[:24]
        candidates[slot_id] = [candidate]
    authority = section_plan.get("source_authority_contract") or {}
    plan = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slot_specs,
        graph_digest=str(authority.get("graph_digest") or "unknown"),
        policy_digest=stable_digest(
            {
                "scope": SECTION_ONLY_SCOPE,
                "section_id": section_id,
                "source_plan_digest": section_plan.get("plan_digest"),
            }
        ),
        allocation_scope=SECTION_ONLY_SCOPE,
        section_plan_digests={section_id: str(section_plan.get("plan_digest") or "")},
        max_fact_reuse=max(len(slot_specs), 1),
        max_source_family_share=1.0,
    )
    traversal = section_plan.get("graph_traversal_receipt") or {}
    contract: dict[str, Any] = {
        "schema_version": "section_final_graph_evidence_contract_v1",
        "section_id": section_id,
        "allocation_scope": SECTION_ONLY_SCOPE,
        "allocation_plan_digest": plan["allocation_plan_digest"],
        "source_section_plan_id": str(section_plan.get("plan_id") or ""),
        "source_section_plan_digest": str(section_plan.get("plan_digest") or ""),
        "graph_digest": str(authority.get("graph_digest") or ""),
        "assignments": list(plan["assignments"]),
        "assignment_count": len(plan["assignments"]),
        "representation_mode": "SECTION_ONLY",
        "derived_from_section_id": "",
        "counts_toward_global_uniqueness": False,
        "traversal_receipt_digest": str(traversal.get("events_digest") or ""),
        "traversal_conservation_pass": traversal.get("pass") is True,
        "pass": traversal.get("pass") is True,
    }
    contract["contract_digest"] = stable_digest(contract)
    return {
        "allocation_plan": plan,
        "usage_ledger": build_resume_graph_usage_ledger(plan),
        "final_evidence_contract": contract,
    }


def write_whole_resume_graph_allocation_bundle(
    bundle: Mapping[str, Any],
    *,
    output_dir: Path,
) -> dict[str, str]:
    """Persist current-run artifacts only; no canonical graph or SQLite mutation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    refs: dict[str, str] = {}
    artifacts = {
        "allocation_plan": "resume_graph_allocation_plan.json",
        "usage_ledger": "resume_graph_usage_ledger.json",
        "section_final_evidence_contracts": "section_final_graph_evidence_contracts.json",
        "section_plans": "c03_section_graph_plans.json",
    }
    for key, filename in artifacts.items():
        path = output_dir / filename
        path.write_text(
            json.dumps(bundle.get(key), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        refs[key] = str(path)
    return refs


def load_resume_graph_allocation_plan(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResumeGraphAllocationError(
            "allocation plan is missing or invalid",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["allocation_plan_load"],
                "path": str(path),
            },
        ) from exc
    if not isinstance(raw, dict):
        raise ResumeGraphAllocationError(
            "allocation plan must be a JSON object",
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["allocation_plan_shape"],
                "path": str(path),
            },
        )
    failures = validate_resume_graph_allocation_plan(raw)
    if failures:
        raise ResumeGraphAllocationError(
            "allocation plan validation failed: " + ", ".join(failures),
            receipt={
                "schema_version": "resume_graph_allocation_failure_v1",
                "unsatisfied_constraints": ["allocation_plan_validation"],
                "validation_failures": failures,
                "path": str(path),
            },
        )
    return raw


__all__ = [
    "ALLOCATION_SCOPES",
    "ALLOCATION_PLAN_ENV",
    "ALLOCATION_USAGE_LEDGER_ENV",
    "ResumeGraphAllocationError",
    "SECTION_ONLY_SCOPE",
    "SECTION_EVIDENCE_CONTRACTS_ENV",
    "WHOLE_RESUME_SCOPE",
    "ALL_CLAIM_BEARING_SECTIONS",
    "CANONICAL_VISIBLE_SECTIONS",
    "DEFAULT_MAX_CANDIDATES_PER_SLOT",
    "allocate_candidate_sets",
    "build_section_final_evidence_contracts",
    "build_section_only_graph_allocation",
    "build_resume_graph_usage_ledger",
    "build_whole_resume_graph_allocation",
    "canonical_allocation_digest",
    "extract_exact_metric_value_unit",
    "finalize_resume_graph_allocation_plan",
    "load_resume_graph_allocation_plan",
    "normalize_metric_signature",
    "slice_section_plan_for_allocation",
    "stable_edge_id",
    "validate_resume_graph_allocation_plan",
    "write_whole_resume_graph_allocation_bundle",
]
