# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, workflow
from __future__ import annotations

# This boosts alignment detection — review and integrate appropriately
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: healer, memory, prompt, state
# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
OrchestrationHandshakeAgent - Multi-Hop Agent Collaboration
Renamed from OrchestrationHandshake for consistent Agent suffix pattern (Jan 6, 2026)
"""
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import CoreOrchestrationAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.utils.decorators import standard_heal
from agentic_core.L0_routing.enforcement.v15_p3_contracts import (
    build_hil_evidence_pack,
)
from agentic_core.L0_routing.types.guardian_contract import (
    V15HardFailAbort,
    is_v15_enforced,
)
from agentic_core.L0_routing.types.v15_contracts import TelemetryEmitter
from agentic_core.L0_routing.types.v15_p3_types import (
    PolicySnapshot,
    RouteDecisionRef,
)
from agentic_core.L0_routing.types.v15_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.L3_orchestration.types.route_decision_artifact_types import (
    build_l3_route_decision_artifact,
)
from agentic_core.runtime.config.contextual_router_config import (
    RoutingRequest,
    get_router,
)


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
                    },
                )
        if self.redis and capable:
            try:
                self.redis.set(cache_key, json.dumps(capable), ex=3600)
            # guardian: allow-silent-swallow
            except Exception:
                pass
        return sorted(capable, key=lambda x: x["confidence"], reverse=True)

    # guardian: allow-magic-config  # guardian: allow-type-erasure
    def delegate_task(
        self,
        Task: str,
        args: dict | None = None,
        kwargs: dict | None = None,
        min_confidence: float = 0.85,
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
            return {
                "status": "no_capable_agent",
                "message": f"No agent found for Task: {Task[:50]}...",
            }
        best: Any = capable[0]
        print(
            f"   [HANDSHAKE] {self.requesting_agent} -> {best['agent_class']}.{best['method']} ({best['confidence']:.2f})",
        )

        # §Wave2.1 — L3 Route Decision Artifact emission at routing boundary
        _l3_trace_id = hashlib.sha256(Task.encode()).hexdigest()[:16]
        l3_artifact = build_l3_route_decision_artifact(
            trace_id=_l3_trace_id,
            chosen=best,
            candidates=capable,
        )
        l3_artifact_dict = asdict(l3_artifact)
        try:
            _l3_emitter = TelemetryEmitter()
            _l3_emitter.emit_typed_artifact("L3_ROUTE_DECISION", l3_artifact)
            _l3_log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
            _l3_emitter.flush_to_artifacts_dir(_l3_log_dir)
        # guardian: allow-silent-swallow
        except Exception:
            pass  # §Wave2.1: emission failure must not block routing

        # §3.1 — V15 routing enforcement at orchestration boundary
        routing_result = None
        route_artifact_dict = None
        if is_v15_enforced():
            request_id = hashlib.sha256(Task.encode()).hexdigest()[:16]
            routing_request = RoutingRequest(
                request_id=request_id,
                action_type="delegate",
                agent_name=best["agent_class"],
            )
            routing_result = get_router().route(routing_request)

            # §3.1 — Attach RouteDecisionArtifact to audit return (fail-closed under V15)
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
                    risk_score=0.0,  # sentinel: RiskLevel is non-numeric str; type change proposed next wave
                    budget_est=0.0,  # not available at L3 seam
                    rationale_enum=_ROUTE_TO_RATIONALE[routing_result.decision],
                    policy_config_hash="",  # not available at L3 seam
                )
                route_artifact_dict = asdict(route_artifact)
            except Exception as exc:
                raise V15HardFailAbort(
                    "§3.1 RouteDecisionArtifact construction failed at routing boundary",
                ) from exc

            # §3.1 — Durable emission to TelemetryEmitter sink + flush to artifacts
            try:
                _emitter = TelemetryEmitter()
                _emitter.emit_route_decision(route_artifact)
                _artifacts_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
                _emitter.flush_to_artifacts_dir(_artifacts_dir)
            except Exception as exc:
                if is_v15_enforced():
                    raise V15HardFailAbort(
                        "§3.1 RouteDecisionArtifact durable emission failed",
                    ) from exc

            if routing_result.decision == RoutePath.HUMAN_ESCALATION:
                # §Wave2.2 — Emit EvidencePack at HIL escalation boundary
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
                        "§Wave2.2 EvidencePack emission failed at HIL boundary: %s",
                        _hil_exc,
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

        # Default implementation - OrchestrationHandshakeAgent manages orchestration handshakes
        try:
            return {
                "status": "skipped",
                "details": f"OrchestrationHandshakeAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"OrchestrationHandshakeAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
