"""Gate-closure reconcile — suppress only contract-invalid findings on passed gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from agentic_core.runtime.judges.panel.score_law import normalize_panel_score

RECONCILE_POLICY_VERSION = "gate_closure_v1"


@dataclass(frozen=True)
class GateClosureRule:
    gate_id: str
    forbidden_finding_codes: frozenset[str]
    required_gate_status: str = "pass"


@dataclass(frozen=True)
class GateClosureMap:
    rules: tuple[GateClosureRule, ...]
    version: str = RECONCILE_POLICY_VERSION


def reconcile_against_gate_closures(
    body: Mapping[str, Any],
    gate_summary: Mapping[str, Any],
    closure_map: GateClosureMap,
) -> dict[str, Any]:
    """Return updated judge body + metadata; never FAIL→PASS unless all failures suppressed."""
    result = dict(body)
    findings = [str(x) for x in (result.get("findings") or [])]
    if not findings:
        return result

    norm = normalize_panel_score(result)
    if norm.pass_:
        return result

    suppressed: list[str] = []
    preserved: list[str] = []
    codes_by_gate = {r.gate_id: r for r in closure_map.rules}

    for finding in findings:
        code = _finding_code(finding)
        suppressed_this = False
        for gate_id, rule in codes_by_gate.items():
            gate = gate_summary.get(gate_id)
            if not isinstance(gate, Mapping) or gate.get("pass") is not True:
                continue
            if code in rule.forbidden_finding_codes:
                suppressed.append(finding)
                suppressed_this = True
                break
        if not suppressed_this:
            preserved.append(finding)

    if preserved:
        result["findings"] = preserved
        return result

    result["findings"] = []
    result["decisive_failure"] = False
    result["pass"] = float(result.get("score", 0)) >= float(result.get("threshold", norm.threshold))
    return result


def _finding_code(finding: str) -> str:
    text = finding.strip()
    if ":" in text:
        return text.split(":", 1)[0].strip().lower()
    return text.lower().replace(" ", "_")[:64]


__all__ = [
    "GateClosureMap",
    "GateClosureRule",
    "RECONCILE_POLICY_VERSION",
    "reconcile_against_gate_closures",
]
