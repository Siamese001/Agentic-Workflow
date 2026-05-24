"""Structured gate-closure map for executive-summary X1D reconcile (SSOT).

String fragments are compatibility shims; stable finding codes are authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RECONCILIATION_POLICY_VERSION = "executive_summary_gate_closure_v1"


@dataclass(frozen=True)
class GateClosureRecord:
    gate_id: str
    closed_axis: str
    forbidden_finding_codes: tuple[str, ...]
    allowed_residual_finding_codes: tuple[str, ...]
    fragment_shims: tuple[str, ...]
    required_gate_status: str = "pass"
    evidence_ref_required: bool = True


# Residual quality dimensions — never suppressed by gate-closure reconcile.
RESIDUAL_QUALITY_FINDING_CODES: frozenset[str] = frozenset(
    {
        "residual_executive_clarity",
        "residual_narrative_coherence",
        "residual_commercial_fit",
        "residual_unsupported_phrasing",
        "residual_weak_synthesis",
    }
)

RESIDUAL_QUALITY_FRAGMENT_SHIMS: tuple[tuple[str, str], ...] = (
    ("residual_executive_clarity", "unclear executive positioning"),
    ("residual_executive_clarity", "executive positioning is unclear"),
    ("residual_narrative_coherence", "weak narrative coherence"),
    ("residual_narrative_coherence", "narrative coherence is weak"),
    ("residual_commercial_fit", "poor commercial fit"),
    ("residual_commercial_fit", "weak commercial fit"),
    ("residual_unsupported_phrasing", "unsupported phrasing"),
    ("residual_weak_synthesis", "weak synthesis"),
)


EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP: tuple[GateClosureRecord, ...] = (
    GateClosureRecord(
        gate_id="x2_exec_summary_no_credential_dump",
        closed_axis="credential_metric_inventory",
        forbidden_finding_codes=(
            "credential_metric_stack_despite_gate_pass",
            "credential_inventory_despite_gate_pass",
        ),
        allowed_residual_finding_codes=("residual_executive_clarity", "residual_weak_synthesis"),
        fragment_shims=(
            "metric/credential stack",
            "credential inventory despite passing the deterministic gate",
            "credential inventory despite passing",
            "credential/certification inventory",
            "credential dump",
        ),
    ),
    GateClosureRecord(
        gate_id="x2_exec_summary_evidence_utilization",
        closed_axis="evidence_utilization",
        forbidden_finding_codes=(
            "unused_facts_penalty_despite_util_gate_pass",
            "penalize under-use when util gate passed",
        ),
        allowed_residual_finding_codes=("residual_weak_synthesis",),
        fragment_shims=(
            "penalize under-use",
            "unused_fact_ids",
            "under-use of allowed_fact_packet",
        ),
    ),
    GateClosureRecord(
        gate_id="x2_exec_summary_no_mechanism_inventory",
        closed_axis="mechanism_inventory",
        forbidden_finding_codes=("mechanism_inventory_despite_gate_pass",),
        allowed_residual_finding_codes=(),
        fragment_shims=(
            "mechanism inventory",
            "comma-chain architecture dump",
        ),
    ),
    GateClosureRecord(
        gate_id="x2_exec_summary_sentence_count_6",
        closed_axis="sentence_count",
        forbidden_finding_codes=("sentence_count_penalty_despite_gate_pass",),
        allowed_residual_finding_codes=(),
        fragment_shims=(
            "fewer than six sentences",
            "sentence count",
        ),
    ),
)


def _gate_pass_with_evidence(
    gate_id: str,
    deterministic_gate_summary: dict[str, Any],
) -> tuple[bool, str | None]:
    entry = deterministic_gate_summary.get(gate_id)
    if not isinstance(entry, dict):
        return False, None
    if not entry.get("pass"):
        return False, None
    detail = str(entry.get("detail") or "ok")
    return True, f"deterministic_gate_summary.{gate_id}.pass=true detail={detail!r}"


def classify_finding_code(finding_text: str) -> str | None:
    """Map finding prose to a stable code (forbidden or residual)."""
    blob = str(finding_text or "").strip().lower()
    if not blob:
        return None
    for code, fragment in RESIDUAL_QUALITY_FRAGMENT_SHIMS:
        if fragment in blob:
            return code
    for record in EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP:
        for fragment in record.fragment_shims:
            if fragment.lower() in blob:
                return record.forbidden_finding_codes[0]
    return None


def finding_is_contract_invalid_under_gate_closures(
    finding_text: str,
    deterministic_gate_summary: dict[str, Any],
) -> tuple[bool, str | None, str | None]:
    """Return (invalid, suppressing_gate_id, evidence_ref) when finding may be suppressed."""
    code = classify_finding_code(finding_text)
    if code is None:
        return False, None, None
    if code in RESIDUAL_QUALITY_FINDING_CODES:
        return False, None, None
    for record in EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP:
        if code not in record.forbidden_finding_codes:
            continue
        ok, evidence_ref = _gate_pass_with_evidence(record.gate_id, deterministic_gate_summary)
        if ok:
            return True, record.gate_id, evidence_ref
    return False, None, None


def core_gate_closure_map():
    """Export apps_rg closure map for agentic_core reconcile engine (W2)."""
    from agentic_core.runtime.judges.panel.gate_closure_reconcile import (
        GateClosureMap,
        GateClosureRule,
    )

    rules = tuple(
        GateClosureRule(
            gate_id=record.gate_id,
            forbidden_finding_codes=frozenset(record.forbidden_finding_codes),
        )
        for record in EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP
    )
    return GateClosureMap(rules=rules, version=RECONCILIATION_POLICY_VERSION)


__all__ = [
    "EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP",
    "GateClosureRecord",
    "RECONCILIATION_POLICY_VERSION",
    "RESIDUAL_QUALITY_FINDING_CODES",
    "classify_finding_code",
    "core_gate_closure_map",
    "finding_is_contract_invalid_under_gate_closures",
]
