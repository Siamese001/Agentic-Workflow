"""Runtime gate contracts — GateVerdict and GateMeshResult.

W8 plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Invariants:
- UNKNOWN is NEVER PASS.
- NOT_APPLICABLE requires not_applicable_reason.
- Missing applicable gate becomes UNKNOWN.
- Multiple PASS verdicts do not cancel one hard FAIL.
- GateVerdict is evidence only; Exit owns X3.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ── Verdict result constants ──────────────────────────────────────────────────

VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"
VERDICT_WARN = "WARN"
VERDICT_UNKNOWN = "UNKNOWN"
VERDICT_NOT_APPLICABLE = "NOT_APPLICABLE"

_VALID_RESULTS = frozenset({
    VERDICT_PASS, VERDICT_FAIL, VERDICT_WARN,
    VERDICT_UNKNOWN, VERDICT_NOT_APPLICABLE,
})

# UNKNOWN is never PASS — enforced structurally
_PASSING_RESULTS = frozenset({VERDICT_PASS})
_BLOCKING_HARD_FAIL = frozenset({VERDICT_FAIL})
_MATERIAL_UNKNOWN = frozenset({VERDICT_UNKNOWN})

GATE_MESH_SCHEMA_VERSION = "W8.a3f7e2"


@dataclass(frozen=True, slots=True)
class GateVerdict:
    """Evaluation result for a single gate.

    MUST NOT be confused with X3 — this is evidence only.
    Exit owns the X3 decision.
    """

    gate_id: str = ""
    gate_family: str = ""
    evaluated_stage: str = ""
    evaluated_surface: str = ""
    evaluated_packet_ref: str = ""

    # The result field is the gated value.
    # UNKNOWN is NEVER PASS — enforced in is_pass property.
    result: str = VERDICT_UNKNOWN

    disposition: str = ""
    severity: str = ""          # "hard_fail" | "warn" | "advisory"
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    score: float = 0.0
    threshold: float = 0.0
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    replay_refs: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0
    remediation_hint: str = ""

    # Provenance
    deterministic_digest: str = ""
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    tenant_id: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""

    # NOT_APPLICABLE and UNKNOWN require explicit reason
    not_applicable_reason: str = ""
    unknown_reason: str = ""

    created_at: str = ""

    schema_version: str = GATE_MESH_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.result not in _VALID_RESULTS:
            raise ValueError(
                f"GateVerdict: invalid result={self.result!r}. "
                f"Must be one of {sorted(_VALID_RESULTS)}"
            )
        if self.result == VERDICT_NOT_APPLICABLE and not self.not_applicable_reason:
            raise ValueError(
                f"GateVerdict gate_id={self.gate_id!r}: "
                "NOT_APPLICABLE requires not_applicable_reason to be non-empty"
            )

    @property
    def is_pass(self) -> bool:
        """UNKNOWN is NEVER PASS. Only PASS is a pass."""
        return self.result == VERDICT_PASS

    @property
    def is_hard_fail(self) -> bool:
        return self.result == VERDICT_FAIL and self.severity == "hard_fail"

    @property
    def is_material_unknown(self) -> bool:
        return self.result == VERDICT_UNKNOWN

    @property
    def is_not_applicable(self) -> bool:
        return self.result == VERDICT_NOT_APPLICABLE

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "gate_family": self.gate_family,
            "evaluated_stage": self.evaluated_stage,
            "evaluated_surface": self.evaluated_surface,
            "evaluated_packet_ref": self.evaluated_packet_ref,
            "result": self.result,
            "disposition": self.disposition,
            "severity": self.severity,
            "reason_codes": list(self.reason_codes),
            "score": self.score,
            "threshold": self.threshold,
            "evidence_refs": list(self.evidence_refs),
            "replay_refs": list(self.replay_refs),
            "confidence": self.confidence,
            "remediation_hint": self.remediation_hint,
            "deterministic_digest": self.deterministic_digest,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "tenant_id": self.tenant_id,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "replay_key": self.replay_key,
            "not_applicable_reason": self.not_applicable_reason,
            "unknown_reason": self.unknown_reason,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


def _compute_mesh_digest(
    request_id: str,
    run_id: str,
    required_gate_ids: tuple[str, ...],
    verdicts: tuple[GateVerdict, ...],
) -> str:
    payload = json.dumps({
        "request_id": request_id,
        "run_id": run_id,
        "required_gate_ids": sorted(required_gate_ids),
        "verdict_digests": sorted(v.deterministic_digest for v in verdicts),
    }, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class GateMeshResult:
    """Aggregate result of all gate evaluations for one request.

    Exit MUST inspect this before emitting any X3.
    """

    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    route_id: str = ""
    evaluated_surface: str = ""
    evaluated_packet_ref: str = ""

    required_gate_ids: tuple[str, ...] = field(default_factory=tuple)
    completed_gate_ids: tuple[str, ...] = field(default_factory=tuple)
    missing_gate_ids: tuple[str, ...] = field(default_factory=tuple)

    verdicts: tuple[GateVerdict, ...] = field(default_factory=tuple)

    # Aggregate signals — computed by build()
    hard_fail_present: bool = False
    unknown_material_present: bool = False
    warn_material_present: bool = False

    recommended_next_owner: str = ""
    recommended_disposition_summary: str = ""

    deterministic_digest: str = ""
    gate_mesh_schema_version: str = GATE_MESH_SCHEMA_VERSION

    @property
    def all_required_passed(self) -> bool:
        """True only when every required gate has a PASS verdict."""
        passed_ids = {v.gate_id for v in self.verdicts if v.is_pass}
        return all(gid in passed_ids for gid in self.required_gate_ids)

    @property
    def blocks_allow_finish(self) -> bool:
        """True when Exit must NOT emit X3D_ALLOW_FINISH."""
        return self.hard_fail_present or self.unknown_material_present or bool(self.missing_gate_ids)

    def get_verdict(self, gate_id: str) -> GateVerdict | None:
        for v in self.verdicts:
            if v.gate_id == gate_id:
                return v
        return None

    def as_dict(self) -> dict[str, Any]:
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
            "verdicts": [v.as_dict() for v in self.verdicts],
            "hard_fail_present": self.hard_fail_present,
            "unknown_material_present": self.unknown_material_present,
            "warn_material_present": self.warn_material_present,
            "recommended_next_owner": self.recommended_next_owner,
            "recommended_disposition_summary": self.recommended_disposition_summary,
            "deterministic_digest": self.deterministic_digest,
            "gate_mesh_schema_version": self.gate_mesh_schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


def build_gate_mesh_result(
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
    route_id: str,
    evaluated_surface: str,
    evaluated_packet_ref: str,
    required_gate_ids: tuple[str, ...],
    verdicts: tuple[GateVerdict, ...],
) -> GateMeshResult:
    """Construct a GateMeshResult from raw verdicts.

    Computes aggregate signals, missing gates (→ UNKNOWN), and digest.
    Missing required gates are treated as UNKNOWN — never as PASS.
    """
    completed = tuple(v.gate_id for v in verdicts)
    missing = tuple(gid for gid in required_gate_ids if gid not in completed)

    hard_fail = any(v.is_hard_fail for v in verdicts)
    mat_unknown = any(v.is_material_unknown for v in verdicts) or bool(missing)
    warn = any(v.result == VERDICT_WARN for v in verdicts)

    if hard_fail:
        next_owner = "exit::deny"
        summary = "Hard gate failure present — X3A_DENY_REROUTE or X3B_ESCALATE_HITL"
    elif mat_unknown or missing:
        next_owner = "exit::block_pending_evaluation"
        summary = "Material UNKNOWN or missing gates — ALLOW_FINISH blocked"
    elif warn:
        next_owner = "exit::conditional_allow"
        summary = "Warnings present — proceed if policy permits"
    else:
        next_owner = "exit::allow_finish"
        summary = "All required gates passed — X3D_ALLOW_FINISH eligible"

    digest = _compute_mesh_digest(request_id, run_id, required_gate_ids, verdicts)

    return GateMeshResult(
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id=route_id,
        evaluated_surface=evaluated_surface,
        evaluated_packet_ref=evaluated_packet_ref,
        required_gate_ids=required_gate_ids,
        completed_gate_ids=completed,
        missing_gate_ids=missing,
        verdicts=verdicts,
        hard_fail_present=hard_fail,
        unknown_material_present=mat_unknown,
        warn_material_present=warn,
        recommended_next_owner=next_owner,
        recommended_disposition_summary=summary,
        deterministic_digest=digest,
    )
