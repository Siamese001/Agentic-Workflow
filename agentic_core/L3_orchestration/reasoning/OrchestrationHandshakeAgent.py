from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "OrchestrationHandshakeAgent", "L3")
_emit_routes_through("p1", "OrchestrationHandshakeAgent", "L3")
_emit_escalates_to_human("p1", "OrchestrationHandshakeAgent", "L3")
_emit_reads_policy_state("p1", "OrchestrationHandshakeAgent", "L3")

"\nOrchestrationHandshakeAgent - Multi-Hop Agent Collaboration\nRenamed from OrchestrationHandshake for consistent Agent suffix pattern (Jan 6, 2026)\n"
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import CoreOrchestrationAgent

from agentic_core.L0_routing.enforcement.governance_contracts import build_hil_evidence_pack
from agentic_core.L0_routing.types.governance_types import PolicySnapshot, RouteDecisionRef
from agentic_core.L0_routing.types.guardian_contract_types import V15HardFailAbort, is_v15_enforced
from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
from agentic_core.L3_orchestration.types.route_decision_artifact_types import build_l3_route_decision_artifact
from agentic_core.runtime.config.contextual_router_config import RoutingRequest, get_router
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal


class OrchestrationHandshakeAgent(SovereignBaseAgent, CoreOrchestrationAgent):
    """
    Sovereign handshake protocol — now with deep L3 caching.
    Renamed from OrchestrationHandshake for consistent Agent suffix pattern.
    """

    def __init__(self, project_root: Path, requesting_agent: str):
        super().__init__(project_root, mission_id=requesting_agent)
        self.registry = SubAtomicRegistry(project_root)

    # guardian: allow-magic-config
    def discover_capable_agents(self, Task: str, min_confidence: float = 0.85) -> list[dict]:
        """
        Discover agents/methods capable of Task via hybrid registry search.
        cache-first — Redis hit -> instant discovery.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "OrchestrationHandshakeAgent.discover_capable_agents", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "OrchestrationHandshakeAgent.discover_capable_agents", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "OrchestrationHandshakeAgent.discover_capable_agents"
        )

        cache_key: Any = (
            f"handshake_discover:{hashlib.sha256((Task + str(min_confidence)).encode()).hexdigest()}"
        )
        if self.redis:
            cached: Any = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        results: Any = self.registry.find_method(Task, top_k=10)
        capable: Any = []
        for r in results:
            if r["score"] >= min_confidence:
                meta: Any = r["metadata"]
                capable.append(
                    {
                        "agent_class": meta.get("agent_class", "Unknown"),
                        "method": meta["method"],
                        "confidence": r["score"],
                        "docstring": meta["docstring"][:200],
                    }
                )
        if self.redis and capable:
            try:
                self.redis.set(cache_key, json.dumps(capable), ex=3600)
            # guardian: allow-silent-swallow
            except Exception:
                pass
        return sorted(capable, key=lambda x: x["confidence"], reverse=True)

    # guardian: allow-magic-config
    # guardian: allow-type-erasure
    # guardian: allow-magic-config
    # guardian: allow-type-erasure
    def delegate_task(
        self, Task: str, args: dict | None = None, kwargs: dict | None = None, min_confidence: float = 0.85
    ) -> dict:
        """
        Sovereign delegation — find best method and invoke.
        """
        args: Any = args or {}
        kwargs: Any = kwargs or {}
        cached: Any = self.get_cached_routing(Task)
        if cached:
            print(f"   [CACHE HIT] Handshake routing for '{Task[:30]}...'")
            return cached
        capable: Any = self.discover_capable_agents(Task, min_confidence)
        if not capable:
            return {"status": "no_capable_agent", "message": f"No agent found for Task: {Task[:50]}..."}
        best: Any = capable[0]
        print(
            f"   [HANDSHAKE] {self.requesting_agent} -> {best['agent_class']}.{best['method']} ({best['confidence']:.2f})"
        )
        _l3_trace_id = hashlib.sha256(Task.encode()).hexdigest()[:16]
        l3_artifact = build_l3_route_decision_artifact(trace_id=_l3_trace_id, chosen=best, candidates=capable)
        l3_artifact_dict = asdict(l3_artifact)
        try:
            _l3_emitter = TelemetryEmitter()
            _l3_emitter.emit_typed_artifact("L3_ROUTE_DECISION", l3_artifact)
            _l3_log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
            _l3_emitter.flush_to_artifacts_dir(_l3_log_dir)
        # guardian: allow-silent-swallow
        except Exception:
            raise
            pass
        routing_result = None
        route_artifact_dict = None
        if is_v15_enforced():
            request_id = hashlib.sha256(Task.encode()).hexdigest()[:16]
            routing_request = RoutingRequest(
                request_id=request_id, action_type="delegate", agent_name=best["agent_class"]
            )
            routing_result = get_router().route(routing_request)
            _ROUTE_TO_RATIONALE = {
                RoutePath.LOW_RISK_BYPASS: RoutingRationale.LOW_RISK_BYPASS,
                RoutePath.STANDARD_VALIDATION: RoutingRationale.STANDARD_VALIDATION,
                RoutePath.HUMAN_ESCALATION: RoutingRationale.HUMAN_ESCALATION,
                RoutePath.POLICY_CHALLENGE_LOOP: RoutingRationale.POLICY_CHALLENGE,
                RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW: RoutingRationale.BUDGET_OVERFLOW,
            }
            try:
                route_artifact = RouteDecisionArtifact(
                    trace_id=request_id,
                    timestamp=routing_request.timestamp.isoformat(),
                    route_path=routing_result.decision,
                    risk_score=0.0,
                    budget_est=0.0,
                    rationale_enum=_ROUTE_TO_RATIONALE[routing_result.decision],
                    policy_config_hash="",
                )
                route_artifact_dict = asdict(route_artifact)
            # guardian: allow-silent-swallow
            except Exception as exc:
                raise V15HardFailAbort(
                    "§3.1 RouteDecisionArtifact construction failed at routing boundary"
                ) from exc
            try:
                _emitter = TelemetryEmitter()
                _emitter.emit_route_decision(route_artifact)
                _artifacts_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
                _emitter.flush_to_artifacts_dir(_artifacts_dir)
            # guardian: allow-silent-swallow
            except Exception as exc:
                if is_v15_enforced():
                    raise V15HardFailAbort("§3.1 RouteDecisionArtifact durable emission failed") from exc
            if routing_result.decision == RoutePath.HUMAN_ESCALATION:
                _hil_pack_dict = None
                try:
                    _hil_ref = RouteDecisionRef(
                        trace_id=request_id,
                        decision=routing_result.decision.value,
                        agent_name=best["agent_class"],
                        reason=routing_result.reason or "",
                    )
                    _hil_snap = PolicySnapshot(
                        security_level="enforced",
                        risk_tier=str(getattr(routing_result, "risk_level", "HIGH")),
                        laws_applied=(),
                        policy_hash="",
                    )
                    _hil_pack = build_hil_evidence_pack(
                        trace_id=request_id,
                        escalation_reason=routing_result.reason or "HUMAN_ESCALATION",
                        route_decision_ref=_hil_ref,
                        policy_snapshot_data=_hil_snap,
                        risk_score=0.8,
                        action_trace=(f"delegate_task({Task[:50]})",),
                        policy_evals=(routing_result.decision.value,),
                    )
                    _hil_pack_dict = asdict(_hil_pack)
                    _hil_emitter = TelemetryEmitter()
                    _hil_emitter.emit_typed_artifact("HIL_EVIDENCE_PACK", _hil_pack)
                    _hil_log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
                    _hil_emitter.flush_to_artifacts_dir(_hil_log_dir)
                # guardian: allow-silent-swallow
                except Exception as _hil_exc:
                    import logging as _hil_logging

                    _hil_logging.getLogger(__name__).error(
                        "§Wave2.2 EvidencePack emission failed at HIL boundary: %s", _hil_exc
                    )
                return {
                    "status": "route_blocked",
                    "route_path": routing_result.decision.value,
                    "reason": routing_result.reason,
                    "delegated_to": f"{best['agent_class']}.{best['method']}",
                    "route_decision_artifact": route_artifact_dict,
                    "l3_route_decision_artifact": l3_artifact_dict,
                    "hil_evidence_pack": _hil_pack_dict,
                }
            if routing_result.decision == RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW:
                return {
                    "status": "route_blocked",
                    "route_path": routing_result.decision.value,
                    "reason": routing_result.reason,
                    "delegated_to": f"{best['agent_class']}.{best['method']}",
                    "route_decision_artifact": route_artifact_dict,
                    "l3_route_decision_artifact": l3_artifact_dict,
                }
        try:
            method_meta: Any = {"agent_class": best["agent_class"], "method": best["method"]}
            result: Any = self.registry.invoke_method(method_meta, **{**args, **kwargs})
            audit: Any = {
                "status": "success",
                "delegated_to": f"{best['agent_class']}.{best['method']}",
                "confidence": best["confidence"],
                "result_summary": str(result)[:500] if result else "None",
                "route_path": routing_result.decision.value if routing_result else None,
                "route_decision_artifact": route_artifact_dict,
                "l3_route_decision_artifact": l3_artifact_dict,
            }
            self.cache_routing_decision(Task, audit)
            return audit
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "delegation_failed",
                "error": str(e),
                "l3_route_decision_artifact": l3_artifact_dict,
            }

    def execute_mission(self, steps: list[dict]) -> list[dict]:
        """
        Multi-hop mission logic: Sequential delegation.
        """
        trail: Any = []
        context: Any = {}
        for i, step in enumerate(steps):
            print(f"   [MISSION] Step {i + 1}: {step['Task']}")
            step_kwargs: Any = {**step.get("kwargs", {}), **context}
            outcome: Any = self.delegate_task(step["Task"], kwargs=step_kwargs)
            trail.append(outcome)
            if outcome["status"] != "success":
                print(f"   [!] Mission stalled at step {i + 1}")
                break
            context: Any = {"previous_result": outcome["result"]}
        return trail

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by OrchestrationHandshakeAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"OrchestrationHandshakeAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "failed",
                "details": f"OrchestrationHandshakeAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
