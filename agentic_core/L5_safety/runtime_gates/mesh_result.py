"""Canonical 00C.7 ``GateMeshResult`` schema.

This sits alongside ``orchestrator.MeshResult`` (the lighter execution
record) and provides the doctrine-shaped aggregation handoff that Exit
consumes per 00C.7 *GATE MESH RESULT CONTRACT*.

``GateMeshResult`` is computed from a list of ``GateDecision`` instances
(usually ``MeshResult.decisions``) plus the set of required gate IDs for
the surface being evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.L5_safety.runtime_gates.digest import mesh_digest
from agentic_core.L5_safety.runtime_gates.contracts import (
    SCHEMA_VERSION,
    Disposition,
    GateDecision,
    Result,
    Severity,
)


_HARD_FAIL_DISPOSITIONS: frozenset[Disposition] = frozenset(
    {
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.QUARANTINE,
    }
)
_MATERIAL_SEVERITIES: frozenset[Severity] = frozenset(
    {Severity.HIGH, Severity.CRITICAL}
)


@dataclass
class GateMeshResult:
    """Doctrine 00C.7 GateMeshResult.

    All list fields are stable copies — callers must not mutate the
    embedded ``verdicts`` after construction (00C.7 immutability).
    """

    request_id: str
    run_id: str
    trace_root: str
    evaluated_surface: str
    evaluated_packet_ref: str
    required_gate_ids: list[str] = field(default_factory=list)
    completed_gate_ids: list[str] = field(default_factory=list)
    missing_gate_ids: list[str] = field(default_factory=list)
    verdicts: list[dict[str, Any]] = field(default_factory=list)
    hard_fail_present: bool = False
    unknown_material_present: bool = False
    warn_material_present: bool = False
    recommended_next_owner: str = "EXIT"
    recommended_disposition_summary: str = ""
    deterministic_digest: str = ""
    route_id: str = ""
    gate_mesh_schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "route_id": self.route_id,
            "evaluated_surface": self.evaluated_surface,
            "evaluated_packet_ref": self.evaluated_packet_ref,
            "required_gate_ids": list(self.required_gate_ids),
            "completed_gate_ids": list(self.completed_gate_ids),
            "missing_gate_ids": list(self.missing_gate_ids),
            "verdicts": list(self.verdicts),
            "hard_fail_present": self.hard_fail_present,
            "unknown_material_present": self.unknown_material_present,
            "warn_material_present": self.warn_material_present,
            "recommended_next_owner": self.recommended_next_owner,
            "recommended_disposition_summary": self.recommended_disposition_summary,
            "deterministic_digest": self.deterministic_digest,
            "gate_mesh_schema_version": self.gate_mesh_schema_version,
        }


def build_mesh_result(
    decisions: list[GateDecision],
    *,
    required_gate_ids: list[str],
    evaluated_surface: str,
    evaluated_packet_ref: str = "",
    request_id: str = "",
    run_id: str = "",
    trace_root: str = "",
    route_id: str = "",
    recommended_next_owner: str = "EXIT",
) -> GateMeshResult:
    """Aggregate a list of ``GateDecision`` into a 00C.7 ``GateMeshResult``.

    Aggregation rules from 00C.7:
    - Any CRITICAL FAIL keeps ``hard_fail_present=True``.
    - Material UNKNOWN flags ``unknown_material_present``.
    - WARN of material severity flags ``warn_material_present``.
    - Multiple PASS verdicts do not cancel a single hard FAIL.
    """
    verdicts: list[dict[str, Any]] = [d.to_verdict() for d in decisions]
    completed = [d.gate_id for d in decisions]
    missing = [gid for gid in required_gate_ids if gid not in completed]

    hard_fail = any(
        d.disposition in _HARD_FAIL_DISPOSITIONS
        or (d.result is Result.FAIL and d.severity in _MATERIAL_SEVERITIES)
        for d in decisions
    )
    unknown_material = any(
        d.result is Result.UNKNOWN and d.severity in _MATERIAL_SEVERITIES
        for d in decisions
    )
    warn_material = any(
        d.result is Result.WARN and d.severity in _MATERIAL_SEVERITIES
        for d in decisions
    )

    if hard_fail:
        summary = "DENY"
    elif unknown_material:
        summary = "ESCALATE_HITL"
    elif missing:
        summary = "BLOCK_EXIT"
    elif warn_material:
        summary = "MARK_DEGRADED"
    else:
        summary = "ALLOW"

    digest = mesh_digest(verdicts)
    # Ensure each verdict carries the digest (00C.7 deterministic_digest).
    for v, d in zip(verdicts, decisions, strict=False):
        if not v.get("deterministic_digest"):
            from agentic_core.L5_safety.runtime_gates.digest import verdict_digest

            v["deterministic_digest"] = verdict_digest(v)
            d.deterministic_digest = v["deterministic_digest"]

    return GateMeshResult(
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id=route_id,
        evaluated_surface=evaluated_surface,
        evaluated_packet_ref=evaluated_packet_ref,
        required_gate_ids=list(required_gate_ids),
        completed_gate_ids=completed,
        missing_gate_ids=missing,
        verdicts=verdicts,
        hard_fail_present=hard_fail,
        unknown_material_present=unknown_material,
        warn_material_present=warn_material,
        recommended_next_owner=recommended_next_owner,
        recommended_disposition_summary=summary,
        deterministic_digest=digest,
    )


__all__ = ["GateMeshResult", "build_mesh_result"]
