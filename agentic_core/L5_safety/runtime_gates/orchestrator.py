"""Gate-mesh orchestrator.

Dispatches the 29 runtime gates in the spec-defined order and short-circuits
when any gate emits a stop-condition violation or a hard deny disposition.

Spec dispatch order: U0 -> L1 -> L0 -> C0 -> PromptAssembly -> L2 -> L4 -> L3
-> Exit -> UWG -> L6.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.digest import verdict_digest
from agentic_core.L5_safety.runtime_gates.otel_spans import (
    SPAN_BYPASS_DETECTED,
    SPAN_GATE_EVALUATE,
    SPAN_GATE_VERDICT,
    SPAN_MESH_COMPLETE,
    SPAN_MESH_START,
    SPAN_UNKNOWN_MATERIAL,
    SPAN_WARN_MATERIAL,
    emit_event,
    emit_span,
)
from agentic_core.L5_safety.runtime_gates.types import (
    Disposition,
    GateContext,
    GateDecision,
    Result,
    Severity,
)

# Spec-aligned dispatch order (full mesh, all 29 gates).
DISPATCH_ORDER: tuple[str, ...] = (
    # U0 ingress
    "G01",
    "G02",
    # L1 cognition
    "G03",
    # L0 routing + safety
    "G04",
    "G05",
    "G06",
    "G07",
    # C0 retrieval / grounding
    "G08",
    "G09",
    # Prompt assembly
    "G10",
    # L2 execution
    "G11",
    "G12",
    "G13",
    "G14",
    "G15",
    # L4 state / memory
    "G16",
    "G17",
    # L3 orchestration
    "G18",
    "G19",
    "G20",
    # Exit evaluation
    "G21",
    "G22",
    "G23",
    "G24",
    "G26",
    # UWG
    "G27",
    # L6 observability / learning
    "G25",
    "G28",
    "G29",
)

# Dispositions that halt the mesh.
HALT_DISPOSITIONS: frozenset[Disposition] = frozenset(
    {
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.QUARANTINE,
        Disposition.REDACT,
        Disposition.ESCALATE_HITL,
    }
)


@dataclass(slots=True)
class MeshResult:
    """Outcome of a full mesh dispatch."""

    decisions: list[GateDecision] = field(default_factory=list)
    halted_at: str | None = None
    halt_reason: str | None = None

    @property
    def passed(self) -> bool:
        return self.halted_at is None

    @property
    def final_disposition(self) -> Disposition | None:
        return self.decisions[-1].disposition if self.decisions else None


def _enrich_decision(decision: GateDecision, ctx: GateContext) -> GateDecision:
    """Carry context envelope fields onto the verdict and infer ``result``.

    - Populates request_id/run_id/trace_root/tenant_id/policy_hash/etc.
    - Maps ``disposition`` → ``result`` when the gate did not set ``result``
      explicitly (existing gates only set ``disposition``):
        DENY/QUARANTINE/BLOCK_COMMIT  -> FAIL
        ABSTAIN/SAFE_FALLBACK         -> WARN
        ESCALATE_HITL                 -> UNKNOWN (material — never PASS)
        REDACT/SHRINK_SCOPE/MARK_DEGRADED/RETRY/HEAL/REROUTE -> WARN
        ALLOW/COMMIT_REQUEST/CLARIFY  -> PASS
    - Computes deterministic digest.
    """
    # Carry envelope fields if the gate didn't set them.
    if not decision.request_id:
        decision.request_id = ctx.request_id
    if not decision.run_id:
        decision.run_id = ctx.run_id
    if not decision.trace_root:
        decision.trace_root = ctx.trace_root
    if not decision.trace_id:
        decision.trace_id = ctx.trace_id
    if not decision.tenant_id:
        decision.tenant_id = ctx.tenant_id
    if not decision.policy_hash:
        decision.policy_hash = ctx.policy_hash
    if not decision.blueprint_hash:
        decision.blueprint_hash = ctx.blueprint_hash
    if not decision.replay_key:
        decision.replay_key = ctx.replay_key
    if not decision.evaluated_packet_ref:
        decision.evaluated_packet_ref = ctx.evaluated_packet_ref

    # Infer ``result`` when caller still has the default ``Result.PASS``.
    # We use a sentinel-style check: if the disposition is non-ALLOW but result
    # is still PASS, recompute. This keeps gates that explicitly set result
    # untouched.
    disp = decision.disposition
    if decision.result is Result.PASS:
        if disp in (Disposition.DENY, Disposition.QUARANTINE, Disposition.BLOCK_COMMIT):
            decision.result = Result.FAIL
            if decision.severity is Severity.INFO:
                decision.severity = Severity.HIGH
        elif disp is Disposition.ESCALATE_HITL:
            decision.result = Result.UNKNOWN
            if decision.severity is Severity.INFO:
                decision.severity = Severity.HIGH
        elif disp in (
            Disposition.ABSTAIN,
            Disposition.SAFE_FALLBACK,
            Disposition.REDACT,
            Disposition.SHRINK_SCOPE,
            Disposition.MARK_DEGRADED,
            Disposition.RETRY,
            Disposition.HEAL,
            Disposition.REROUTE,
        ):
            decision.result = Result.WARN
            if decision.severity is Severity.INFO:
                decision.severity = Severity.LOW
        # ALLOW / COMMIT_REQUEST / CLARIFY keep PASS.

    # Stamp deterministic digest so verdicts are replayable (00C.7).
    if not decision.deterministic_digest:
        decision.deterministic_digest = verdict_digest(decision.to_verdict())
    return decision


def run_mesh(
    ctx: GateContext,
    *,
    order: tuple[str, ...] = DISPATCH_ORDER,
    halt_on: frozenset[Disposition] = HALT_DISPOSITIONS,
    halt_on_stop_condition: bool = True,
) -> MeshResult:
    """Dispatch every gate in `order`, short-circuiting on halt conditions.

    Emits the doctrine 00C.8 OTEL spans:
    - ``runtime_gate.mesh.start``
    - ``runtime_gate.evaluate`` (per gate)
    - ``runtime_gate.verdict`` (per gate)
    - ``runtime_gate.unknown_material`` / ``runtime_gate.warn_material`` when applicable
    - ``runtime_gate.bypass_detected`` when a gate raises mid-evaluation
    - ``runtime_gate.mesh.complete``
    """
    mesh_attrs = {
        "request_id": ctx.request_id,
        "run_id": ctx.run_id,
        "trace_root": ctx.trace_root,
        "tenant_id": ctx.tenant_id,
        "gate_count": len(order),
    }
    emit_event(SPAN_MESH_START, mesh_attrs)

    result = MeshResult()
    for gate_id in order:
        eval_attrs = {
            "gate_id": gate_id,
            "request_id": ctx.request_id,
            "run_id": ctx.run_id,
            "trace_root": ctx.trace_root,
        }
        with emit_span(SPAN_GATE_EVALUATE, eval_attrs):
            try:
                decision = evaluate(gate_id, ctx)
            except (KeyError, ValueError, TypeError, AttributeError) as exc:
                # guardian: allow-broad-evaluator-failure -- a single broken
                # gate must not collapse the mesh; emit bypass span and
                # synthesize an UNKNOWN verdict so Exit sees the gap.
                emit_event(
                    SPAN_BYPASS_DETECTED,
                    {"gate_id": gate_id, "error": str(exc)},
                )
                decision = GateDecision(
                    gate_id=gate_id,
                    disposition=Disposition.ESCALATE_HITL,
                    reason_codes=["evaluator_exception"],
                    metadata={"error": str(exc)},
                )
                decision.result = Result.UNKNOWN
                decision.severity = Severity.HIGH
        decision = _enrich_decision(decision, ctx)
        emit_event(
            SPAN_GATE_VERDICT,
            {
                "gate_id": decision.gate_id,
                "result": decision.result.value,
                "disposition": decision.disposition.value,
                "severity": decision.severity.value,
                "reason_codes": list(decision.reason_codes),
                "deterministic_digest": decision.deterministic_digest,
                "request_id": decision.request_id,
                "run_id": decision.run_id,
            },
        )
        if (
            decision.result is Result.UNKNOWN
            and decision.severity in (Severity.HIGH, Severity.CRITICAL)
        ):
            emit_event(
                SPAN_UNKNOWN_MATERIAL,
                {"gate_id": decision.gate_id, "reason_codes": list(decision.reason_codes)},
            )
        elif (
            decision.result is Result.WARN
            and decision.severity in (Severity.HIGH, Severity.CRITICAL)
        ):
            emit_event(
                SPAN_WARN_MATERIAL,
                {"gate_id": decision.gate_id, "reason_codes": list(decision.reason_codes)},
            )
        result.decisions.append(decision)
        if halt_on_stop_condition and decision.stop_condition_violated:
            result.halted_at = gate_id
            result.halt_reason = "stop_condition_violated"
            emit_event(
                SPAN_MESH_COMPLETE,
                {**mesh_attrs, "halted_at": gate_id, "reason": result.halt_reason},
            )
            return result
        if decision.disposition in halt_on:
            result.halted_at = gate_id
            result.halt_reason = f"halt_disposition:{decision.disposition.value}"
            emit_event(
                SPAN_MESH_COMPLETE,
                {**mesh_attrs, "halted_at": gate_id, "reason": result.halt_reason},
            )
            return result
    emit_event(SPAN_MESH_COMPLETE, {**mesh_attrs, "halted_at": None, "reason": None})
    return result


__all__ = ["DISPATCH_ORDER", "HALT_DISPOSITIONS", "MeshResult", "run_mesh"]
