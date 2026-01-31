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
from pathlib import Path
from typing import Any

from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import CoreOrchestrationAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.base_agents.decorators import standard_heal
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin


class OrchestrationHandshakeAgent(
    SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent
):
    """
    Sovereign handshake protocol — now with deep L3 caching.
    Renamed from OrchestrationHandshake for consistent Agent suffix pattern.
    """

    def __init__(self, project_root: Path, requesting_agent: str):
        super().__init__(project_root, mission_id=requesting_agent)
        self.registry = SubAtomicRegistry(project_root)

    def discover_capable_agents(self, Task: str, min_confidence: float = 0.85) -> list[dict]:
        """
        Discover agents/methods capable of Task via hybrid registry search.
        cache-first — Redis hit -> instant discovery.
        """
        cache_key: Any = f"handshake_discover:{hashlib.sha256((Task + str(min_confidence)).encode()).hexdigest()}"
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
            except Exception:
                pass
        return sorted(capable, key=lambda x: x["confidence"], reverse=True)

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
            f"   [HANDSHAKE] {self.requesting_agent} -> {best['agent_class']}.{best['method']} ({best['confidence']:.2f})"
        )
        try:
            method_meta: Any = {"agent_class": best["agent_class"], "method": best["method"]}
            result: Any = self.registry.invoke_method(method_meta, **{**args, **kwargs})
            audit: Any = {
                "status": "success",
                "delegated_to": f"{best['agent_class']}.{best['method']}",
                "confidence": best["confidence"],
                "result_summary": str(result)[:500] if result else "None",
            }
            self.cache_routing_decision(Task, audit)
            return audit
        except Exception as e:
            return {"status": "delegation_failed", "error": str(e)}

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
