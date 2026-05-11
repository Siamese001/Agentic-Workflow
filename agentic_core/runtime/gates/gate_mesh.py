"""Gate mesh evaluator — drives G21-G28 evaluators from a profile.

W8 plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

This module is generic (no apps_rg hardcoding).  App-specific gate
rules are injected via a GateProfile loaded by gate_profile_resolver.py.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Callable, Protocol

from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage
from agentic_core.runtime.gates.gate_types import (
    GATE_MESH_SCHEMA_VERSION,
    VERDICT_FAIL,
    VERDICT_NOT_APPLICABLE,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    GateMeshResult,
    GateVerdict,
    build_gate_mesh_result,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()


def _verdict_digest(gate_id: str, result: str, run_id: str) -> str:
    return _sha(f"{gate_id}|{result}|{run_id}")


# ── GateEvaluator protocol ────────────────────────────────────────────────────

class GateEvaluator(Protocol):
    """Protocol for a single gate evaluation callable."""

    def __call__(
        self,
        gate_id: str,
        gate_def: dict[str, Any],
        pkg: SealedWorkflowPackage,
        evidence: dict[str, Any],
        request_id: str,
        run_id: str,
        trace_root: str,
    ) -> GateVerdict: ...


# ── Evaluator registry ────────────────────────────────────────────────────────

# Maps gate_id prefix/family → evaluator function.
# Populated by register_evaluator().
_EVALUATOR_REGISTRY: dict[str, GateEvaluator] = {}


def register_evaluator(gate_id: str, fn: GateEvaluator) -> None:
    """Register a gate evaluator function for a given gate_id."""
    _EVALUATOR_REGISTRY[gate_id] = fn


def _fallback_unknown(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """Default evaluator: UNKNOWN — no evaluator registered for this gate."""
    return GateVerdict(
        gate_id=gate_id,
        gate_family=gate_def.get("gate_family", ""),
        evaluated_stage="exit",
        evaluated_surface="managed_workflow",
        evaluated_packet_ref=pkg.package_id,
        result=VERDICT_UNKNOWN,
        severity=gate_def.get("severity", "hard_fail"),
        unknown_reason=f"No evaluator registered for gate_id={gate_id!r}",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        deterministic_digest=_verdict_digest(gate_id, VERDICT_UNKNOWN, run_id),
        created_at=_now(),
    )


# ── Main mesh driver ──────────────────────────────────────────────────────────

def evaluate_gate_mesh(
    *,
    pkg: SealedWorkflowPackage,
    required_gate_ids: tuple[str, ...],
    gate_definitions: dict[str, dict[str, Any]],
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
    route_id: str = "",
    evaluator_registry: dict[str, GateEvaluator] | None = None,
) -> GateMeshResult:
    """Evaluate all required gates and return a GateMeshResult.

    Missing applicable gates become UNKNOWN (never PASS).
    Conditional gates that are NOT triggered become NOT_APPLICABLE (with reason).
    """
    registry = evaluator_registry if evaluator_registry is not None else _EVALUATOR_REGISTRY
    verdicts: list[GateVerdict] = []

    for gate_id in required_gate_ids:
        gate_def = gate_definitions.get(gate_id, {})
        evaluator = registry.get(gate_id, _fallback_unknown)
        verdict = evaluator(
            gate_id, gate_def, pkg, evidence, request_id, run_id, trace_root
        )
        verdicts.append(verdict)

    # Conditional gates: evaluate if triggered, else NOT_APPLICABLE with reason
    conditional_ids = [
        gid for gid, gdef in gate_definitions.items()
        if gdef.get("conditional", False) and gid not in required_gate_ids
    ]
    for gate_id in conditional_ids:
        gate_def = gate_definitions[gate_id]
        trigger_key = f"trigger_{gate_id.lower()}"
        is_triggered = bool(evidence.get(trigger_key, False))

        if is_triggered:
            evaluator = registry.get(gate_id, _fallback_unknown)
            verdict = evaluator(
                gate_id, gate_def, pkg, evidence, request_id, run_id, trace_root
            )
        else:
            default_reason = gate_def.get(
                "default_reason",
                f"Conditional gate {gate_id} not triggered for this execution form",
            )
            verdict = GateVerdict(
                gate_id=gate_id,
                gate_family=gate_def.get("gate_family", ""),
                evaluated_stage="exit",
                evaluated_surface="managed_workflow",
                evaluated_packet_ref=pkg.package_id,
                result=VERDICT_NOT_APPLICABLE,
                severity=gate_def.get("severity", "hard_fail"),
                not_applicable_reason=default_reason,
                request_id=request_id,
                run_id=run_id,
                trace_root=trace_root,
                deterministic_digest=_verdict_digest(gate_id, VERDICT_NOT_APPLICABLE, run_id),
                created_at=_now(),
            )
        verdicts.append(verdict)

    return build_gate_mesh_result(
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id=route_id,
        evaluated_surface="managed_workflow",
        evaluated_packet_ref=pkg.package_id,
        required_gate_ids=required_gate_ids,
        verdicts=tuple(verdicts),
    )
