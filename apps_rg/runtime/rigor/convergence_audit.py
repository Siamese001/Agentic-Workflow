"""Runtime guard: rigor-critical gates declared in lane_registry must appear in X2 bundles."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.rigor.lane_registry import C0_CRITICAL_GATES, spec_for_lane


def _gate_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(r.get("gate_id") or r.get("id") or "")
        for r in rows
        if r.get("gate_id") or r.get("id")
    }


def audit_missing_rigor_critical(
    *,
    lane: str,
    present: set[str],
    c0_sidecar: bool = False,
) -> dict[str, Any]:
    crit = set(spec_for_lane(lane).critical_gates)
    c0_skip = set(C0_CRITICAL_GATES) if not c0_sidecar else set()
    missing = sorted(g for g in crit if g not in present and g not in c0_skip)
    if missing:
        return {"status": "BLOCK", "missing_rigor_critical_gates": missing}
    return {"status": "PASS", "missing_rigor_critical_gates": []}


def apply_rigor_convergence_to_x2_payload(
    payload: dict[str, Any],
    *,
    lane: str,
    gates: list[dict[str, Any]],
    c0_sidecar: bool = False,
) -> dict[str, Any]:
    """Annotate x2_gate_outputs.json; inject BLOCK rows for missing rigor-critical gates."""
    audit = audit_missing_rigor_critical(
        lane=lane,
        present=_gate_ids(gates),
        c0_sidecar=c0_sidecar,
    )
    out = dict(payload)
    out["rigor_convergence_audit"] = audit
    if audit["status"] != "BLOCK":
        return out
    augmented = list(gates)
    for gate_id in audit["missing_rigor_critical_gates"]:
        augmented.append(
            {
                "gate_id": gate_id,
                "pass": False,
                "verdict": "BLOCK",
                "reason": "rigor_critical_gate_missing_from_runtime_bundle",
                "rigor_convergence": True,
            }
        )
    failed = [g["gate_id"] for g in augmented if not g.get("pass")]
    out["gates"] = augmented
    out["failed_gates"] = failed
    out["x2_failed"] = len(failed)
    out["x2_passed"] = sum(1 for g in augmented if g.get("pass"))
    out["total_x2_gates"] = len(augmented)
    out["rigor_convergence_status"] = "BLOCK"
    return out
