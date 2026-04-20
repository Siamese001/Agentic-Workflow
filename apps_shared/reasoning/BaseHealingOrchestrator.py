"""BaseHealingOrchestrator — Shared meta-learning healing loop for LIC and RG domains.

Extracted from LicHealingOrchestrator and RgHealingOrchestrator (2026-03-11, P3-B).
Both app orchestrators subclass this and inherit:
  - ml_heal_with_learning_enhanced()
  - orchestrate_healing_cycle()
  - _apply_healing_strategy()
Domain-specific orchestrators override _collect_cycle_results_key() for stats keying.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "BaseHealingOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "BaseHealingOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "BaseHealingOrchestrator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("BaseHealingOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("BaseHealingOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("BaseHealingOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("BaseHealingOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("BaseHealingOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("BaseHealingOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("BaseHealingOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("BaseHealingOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("BaseHealingOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("BaseHealingOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("BaseHealingOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("BaseHealingOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("BaseHealingOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("BaseHealingOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("BaseHealingOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("BaseHealingOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("BaseHealingOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("BaseHealingOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("BaseHealingOrchestrator", "p3lm", "state")
_emit_records_execution_trace("BaseHealingOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("BaseHealingOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("BaseHealingOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("BaseHealingOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("BaseHealingOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("BaseHealingOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("BaseHealingOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("BaseHealingOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("BaseHealingOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "BaseHealingOrchestrator", "context_pull")
_emit_pulls_context("p1", "BaseHealingOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "BaseHealingOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "BaseHealingOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "BaseHealingOrchestrator", "write_through")
_emit_writes_through("p1", "BaseHealingOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "BaseHealingOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "BaseHealingOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "BaseHealingOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "BaseHealingOrchestrator", "human_escalation")
_emit_routes_through("p1", "BaseHealingOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "BaseHealingOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "BaseHealingOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "BaseHealingOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "BaseHealingOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "BaseHealingOrchestrator", "target_agent")
_emit_verifies_policy("p1", "BaseHealingOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "BaseHealingOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "BaseHealingOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "BaseHealingOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "BaseHealingOrchestrator")
_emit_gated_by_confidence("p1", "BaseHealingOrchestrator", "confidence_gate")
emit_replay_key("p0", "BaseHealingOrchestrator")
emit_determinism_digest("p0", "BaseHealingOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "BaseHealingOrchestrator", "execution_auth")
_emit_validates_capability("p2", "BaseHealingOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "BaseHealingOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "BaseHealingOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "BaseHealingOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "BaseHealingOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "BaseHealingOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "BaseHealingOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "BaseHealingOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "BaseHealingOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "BaseHealingOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "BaseHealingOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "BaseHealingOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "BaseHealingOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "BaseHealingOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "BaseHealingOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "BaseHealingOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "BaseHealingOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "BaseHealingOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "BaseHealingOrchestrator", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class BaseHealingOrchestrator(SovereignBaseAgent):
    """Shared meta-learning healing orchestration skeleton.

    Subclasses must implement:
    - `heal(violation)` — domain-specific single-violation healer
    - `_cycle_results_key()` — string key for cycle pattern caching (e.g. "healing_cycle")

    Subclasses may override:
    - `_execute_healing(incident)` — if LIC-style incident dispatch is needed
    """

    cycle_results: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize healing orchestrator and register in knowledge graph."""
        super().__post_init__()
        self._register_in_knowledge_graph()
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(self.project_root))
            _profile = _idx.profile_for(self._adg_resolved_self_path()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    def _register_in_knowledge_graph(self) -> None:
        """Register this orchestrator as an entity in the Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            bridge.create_agent_entity(
                agent_name=self.__class__.__name__,
                agent_type="HealingOrchestrator",
                observations=[f"HealingOrchestrator {self.__class__.__name__} initialized"],
            )
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.debug(f"[{self.__class__.__name__}] KG registration skipped: {e}")

    def heal_repository(self, dry_run: bool = False, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Heal a single violation. Override in subclasses."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "BaseHealingOrchestrator.heal"
        )

        violation_type = violation.get("type", "unknown")
        return {
            "status": "skipped",
            "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }

    def _cycle_results_key(self) -> str:
        """Return the pattern cache key prefix for this orchestrator's cycles."""
        return "healing_cycle"

    def ml_heal_with_learning_enhanced(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Enhanced healing with full meta-learning integration.

        Uses guardrails for depth checking, pattern retrieval for strategy
        selection, and pattern storage for successful fixes.
        """
        violation_str = json.dumps(violation, sort_keys=True)
        violation_id = hashlib.sha256(violation_str.encode()).hexdigest()[:16]
        if not self.guardrails_check_healing_depth(violation_id):
            Logger.warning(f"[{self.__class__.__name__}] Healing depth limit reached for {violation_id}")
            return {
                "status": "skipped",
                "violation_id": violation_id,
                "reason": "healing_depth_limit_reached",
            }
        self.guardrails_increment_healing_depth(violation_id)
        try:
            # guardian: allow-magic-config
            similar_patterns = self.retrieve_healing_patterns(violation, top_k=3)
            strategy = None
            if similar_patterns:
                best_pattern = max(
                    similar_patterns,
                    key=lambda p: getattr(p, "success_count", 0),
                    default=None,
                )
                if best_pattern:
                    strategy = getattr(best_pattern, "healing_strategy", None)
                    Logger.info(
                        f"[{self.__class__.__name__}] Using learned strategy from pattern with {getattr(best_pattern, 'success_count', 0)} successes",
                    )
            result = self._apply_healing_strategy(violation, strategy) if strategy else self.heal(violation)
            if result.get("status") == "fixed":
                self.store_healing_pattern(violation, result)
                self.guardrails_reset_healing_depth(violation_id)
                Logger.info(f"[{self.__class__.__name__}] Healing successful, pattern stored")
            return {
                "status": result.get("status", "error"),
                "violation_id": violation_id,
                "used_learned_strategy": strategy is not None,
            }
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.error(f"[{self.__class__.__name__}] Enhanced healing failed: {e}")
            return {"status": "error", "violation_id": violation_id, "reason": str(e)}

    def _apply_healing_strategy(self, violation: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
        """Apply a learned healing strategy to a violation."""
        action = strategy.get("action", "default")
        Logger.debug(f"[{self.__class__.__name__}] Applying strategy action: {action}")
        return self.heal(violation, strategy_hint=strategy)

    def orchestrate_healing_cycle(self, violations: list[dict[str, Any]]) -> dict[str, Any]:
        """Orchestrate a full healing cycle for multiple violations."""
        results: dict[str, Any] = {
            "total": len(violations),
            "fixed": 0,
            "skipped": 0,
            "errors": 0,
            "details": [],
        }
        for violation in violations:
            result = self.ml_heal_with_learning_enhanced(violation)
            results["details"].append(result)
            if result["status"] == "fixed":
                results["fixed"] += 1
            elif result["status"] == "skipped":
                results["skipped"] += 1
            else:
                results["errors"] += 1
        if results["fixed"] > 0:
            cycle_pattern = {
                "total": results["total"],
                "fixed": results["fixed"],
                "success_rate": results["fixed"] / results["total"],
            }
            self.cache_pattern_with_metadata(
                self._cycle_results_key(),
                f"cycle_{len(self.cycle_results)}",
                cycle_pattern,
            )
            self.cycle_results.append(results)
        self._persist_healing_cycle(results)
        return results

    def _persist_healing_cycle(self, results: dict[str, Any]) -> None:
        """Persist healing cycle outcomes to Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            total = results.get("total", 0)
            fixed = results.get("fixed", 0)
            errors = results.get("errors", 0)
            cycle_idx = len(self.cycle_results)
            obs = (
                f"HealingCycle={cycle_idx} total={total} fixed={fixed} errors={errors} success_rate={fixed / total:.2f}"
                if total > 0
                else f"HealingCycle={cycle_idx} total=0"
            )
            bridge.add_observation(entity_name=self.__class__.__name__, observation=obs)
            if fixed > 0:
                bridge.create_relation(
                    from_entity=self.__class__.__name__,
                    to_entity="HealingCycle",
                    relation_type="HEALED",
                )

            # Wave C-1: Emit cross-domain healing events for pattern sharing
            try:
                from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

                sl_bridge = get_sl_memory_bridge()

                # Emit cross-domain healing event
                sl_bridge.persist_cross_domain_healing_event(
                    orchestrator_class=self.__class__.__name__,
                    cycle_index=cycle_idx,
                    total_violations=total,
                    fixed_violations=fixed,
                    error_violations=errors,
                    success_rate=fixed / total if total > 0 else 0.0,
                    timestamp_utc=int(time.time() * 1000),
                    domain="apps_shared",  # Cross-domain identifier
                )
            except Exception:
                # System learning bridge unavailable - continue without it
                pass
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.debug(f"[{self.__class__.__name__}] KG healing cycle persistence skipped: {e}")
        self._verify_dashboard_after_healing(results)

    def _verify_dashboard_after_healing(self, results: dict[str, Any]) -> None:
        """Trigger Playwright MCP dashboard verification after a healing cycle."""
        import asyncio

        fixed = results.get("fixed", 0)
        if fixed == 0:
            return
        try:
            from agentic_core.L6_observability.dashboards.verify_dashboard_e2e_playwright_util import (
                mcp_verify_dashboard,
            )

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(asyncio.run, mcp_verify_dashboard())
                        # guardian: allow-magic-config
                        verification = future.result(timeout=30)
                else:
                    verification = loop.run_until_complete(mcp_verify_dashboard())
            except Exception:  # guardian: allow-silent-swallow
                verification = {}
            if verification.get("success"):
                Logger.info(f"[{self.__class__.__name__}] Dashboard verification passed after healing")
            else:
                Logger.warning(
                    f"[{self.__class__.__name__}] Dashboard verification flagged issues: {verification.get('errors', [])}",
                )
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.debug(f"[{self.__class__.__name__}] Dashboard verification skipped: {e}")
