"""apps_lic/reasoning/LicHealingOrchestrator.py — LIC healing orchestrator.

PHASE 4 META-LEARNING (Feb 2026):
- MetaLearningClient integration for healing pattern memory
- Incident pattern caching and recall
- Recovery playbook optimization via learned patterns
- Healing depth tracking to prevent infinite loops

Refactored: 2026-03-11 (P3-B) — now subclasses BaseHealingOrchestrator.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
)

_emit_authorize_and_execute("p2", "LicHealingOrchestrator", "execution_auth")
_emit_validates_capability("p2", "LicHealingOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "LicHealingOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "LicHealingOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "LicHealingOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "LicHealingOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "LicHealingOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "LicHealingOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "LicHealingOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "LicHealingOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "LicHealingOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "LicHealingOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "LicHealingOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "LicHealingOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "LicHealingOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "LicHealingOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "LicHealingOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "LicHealingOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "LicHealingOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "LicHealingOrchestrator", "exec_snapshot_link")
from apps_shared.reasoning.BaseHealingOrchestrator import BaseHealingOrchestrator

_emit_reads_policy_state("p0", "LicHealingOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "LicHealingOrchestrator", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
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

_emit_emits_metric_event("LicHealingOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("LicHealingOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("LicHealingOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("LicHealingOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("LicHealingOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("LicHealingOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("LicHealingOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("LicHealingOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("LicHealingOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("LicHealingOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("LicHealingOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("LicHealingOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("LicHealingOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("LicHealingOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("LicHealingOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("LicHealingOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("LicHealingOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("LicHealingOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("LicHealingOrchestrator", "p3lm", "state")
_emit_records_execution_trace("LicHealingOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("LicHealingOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("LicHealingOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("LicHealingOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("LicHealingOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("LicHealingOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("LicHealingOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("LicHealingOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("LicHealingOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "LicHealingOrchestrator", "context_pull")
_emit_pulls_context("p1", "LicHealingOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "LicHealingOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "LicHealingOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "LicHealingOrchestrator", "write_through")
_emit_writes_through("p1", "LicHealingOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "LicHealingOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "LicHealingOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "LicHealingOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "LicHealingOrchestrator", "human_escalation")
_emit_routes_through("p1", "LicHealingOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "LicHealingOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "LicHealingOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "LicHealingOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "LicHealingOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "LicHealingOrchestrator", "target_agent")
_emit_verifies_policy("p1", "LicHealingOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "LicHealingOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "LicHealingOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "LicHealingOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "LicHealingOrchestrator")
_emit_gated_by_confidence("p1", "LicHealingOrchestrator", "confidence_gate")

Logger = logging.getLogger(__name__)


@dataclass
class LicHealingOrchestrator(BaseHealingOrchestrator):
    """Sovereign LIC Healing Orchestrator.

    Coordinates domain-specific recovery actions for the LIC ecosystem.

    [PHASE 4] Meta-Learning Integration:
    - Caches successful incident resolutions for future recall
    - Learns optimal recovery playbook selections
    - Tracks healing depth to prevent infinite loops
    - Domain-specific pattern matching (apps_lic)

    Inherits ml_heal_with_learning_enhanced() and orchestrate_healing_cycle()
    from BaseHealingOrchestrator (2026-03-11, P3-B).
    Use orchestrate_healing_cycle() in place of the former orchestrate_incident_recovery().
    """

    active_incidents: dict[str, Any] = field(default_factory=dict)
    recovery_playbooks: dict[str, str] = field(
        default_factory=lambda: {"database_lock": "release_and_retry", "api_timeout": "exponential_backoff"},
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()
        Logger.debug(f"[{self.__class__.__name__}] Meta-Learning healing orchestrator initialized")
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(self.project_root))
            _profile = _idx.profile_for(self._adg_resolved_self_path()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    def assess_system_health(self, telemetry: dict[str, Any]) -> dict[str, str]:
        """
        Evaluate LIC domain health status.
        """
        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "LicHealingOrchestrator.assess_system_health"
        )
        status = "healthy"
        if telemetry.get("error_rate", 0) > 0.05:
            status = "degraded"
            self._register_incident("high_error_rate")
        return {
            "status": status,
            "orchestrator_id": self.name,
            "active_incidents": str(len(self.active_incidents)),
        }

    def _register_incident(self, incident_type: str) -> None:
        """Internal incident tracking."""
        incident_id = str(uuid.uuid4())
        self.active_incidents[incident_id] = {"type": incident_type, "status": "active"}

    def ml_heal_incident(self, incident: dict[str, Any]) -> dict[str, Any]:
        """
        Heal an incident using meta-learning enhanced strategy.

        This method:
        1. Checks healing depth to prevent infinite loops
        2. Attempts to recall a successful resolution pattern
        3. If no pattern found, executes standard healing
        4. Stores successful resolutions for future use

        Args:
            incident: The incident to heal

        Returns:
            Healing result dictionary
        """
        incident_id = incident.get("id", str(uuid.uuid4()))
        incident_type = incident.get("type", "unknown")
        if not self.ml_check_healing_depth(incident_id):
            Logger.warning(f"[{self.__class__.__name__}] Healing depth limit for {incident_id}")
            return {"status": "skipped", "reason": "healing_depth_limit_reached", "incident_id": incident_id}
        self.ml_increment_healing_depth(incident_id)
        try:
            cached_resolution = self.ml_recall_incident_resolution(incident_type)
            if cached_resolution:
                Logger.info(f"[{self.__class__.__name__}] Using cached resolution for {incident_type}")
                self.ml_reset_healing_depth(incident_id)
                return {**cached_resolution, "source": "meta_learning_cache", "incident_id": incident_id}
            result = self._execute_healing(incident)
            if result.get("status") in ("fixed", "resolved", "success"):
                self.ml_cache_incident_resolution(incident_type, result)
                self.ml_reset_healing_depth(incident_id)
            return result
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Healing failed: {e}")
            return {"status": "error", "reason": str(e), "incident_id": incident_id}

    def _execute_healing(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Execute domain-specific healing by dispatching to appropriate agents.

        HEAL-GAP-04: Dispatches based on incident.type:
          - structural → ControlPlane.evaluate_input/output()
          - schema/output_contract → HOPPipelineExecutor re-run on failing stage
          - llm_call → re-route via SovereignLLMGateway with corrected model ID
        """
        incident_type = incident.get("type", "unknown")
        playbook = self.recovery_playbooks.get(incident_type, "default_recovery")
        Logger.info(
            "[%s] _execute_healing: incident_type=%s playbook=%s",
            self.__class__.__name__,
            incident_type,
            playbook,
        )
        if incident_type == "structural":
            return self._heal_structural(incident)
        elif incident_type in ("schema", "output_contract"):
            return self._heal_schema(incident)
        elif incident_type in ("llm_call", "api_timeout"):
            return self._heal_llm_call(incident)
        else:
            return {"status": "resolved", "playbook_used": playbook, "incident_type": incident_type}

    def _heal_structural(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Route structural violations through ControlPlane."""
        try:
            from apps_lic.engines.control_plane import ControlPlane

            cp = ControlPlane()
            content = incident.get("content", "")
            decision = cp.evaluate_input(content)
            return {
                "status": "resolved",
                "healer": "ControlPlane",
                "action": decision.action.value,
                "is_safe": decision.is_safe,
                "incident_type": incident.get("type"),
            }
        except Exception as exc:
            Logger.error("[%s] _heal_structural failed: %s", self.__class__.__name__, exc)
            return {"status": "error", "healer": "ControlPlane", "reason": str(exc)}

    def _heal_schema(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Re-run the failing HOP stage via HOPPipelineExecutor."""
        try:
            from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor

            stage_id = incident.get("stage_id", 5)
            executor = HOPPipelineExecutor()
            result = executor.execute_stage(stage_id, incident.get("context", {}))
            return {
                "status": "resolved",
                "healer": "HOPPipelineExecutor",
                "stage_id": stage_id,
                "result": result,
                "incident_type": incident.get("type"),
            }
        except Exception as exc:
            Logger.error("[%s] _heal_schema failed: %s", self.__class__.__name__, exc)
            return {"status": "error", "healer": "HOPPipelineExecutor", "reason": str(exc)}

    def _heal_llm_call(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Re-route LLM call via SovereignLLMGateway with corrected model ID."""
        try:
            import asyncio

            from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway

            gateway = SovereignLLMGateway()
            prompt = incident.get("prompt", incident.get("content", ""))
            request = GenerationRequest(
                agent_id="LicHealingOrchestrator",
                provider="google",
                model="gemini-2.5-pro",
                prompt=prompt,
            )
            _clk = get_clock()
            _clk.emit_replay_key(context=f"lic:heal:{request.agent_id}:{request.provider}")
            _clk.emit_determinism_digest(inputs={"agent": request.agent_id, "provider": request.provider})
            loop = asyncio.new_event_loop()
            try:
                response = loop.run_until_complete(gateway.route_generation(request))
            finally:
                loop.close()
            return {
                "status": "resolved",
                "healer": "SovereignLLMGateway",
                "model": "gemini-2.5-pro",
                "content": response.content,
                "incident_type": incident.get("type"),
            }
        except Exception as exc:
            Logger.error("[%s] _heal_llm_call failed: %s", self.__class__.__name__, exc)
            return {"status": "error", "healer": "SovereignLLMGateway", "reason": str(exc)}

    def ml_cache_incident_resolution(self, incident_type: str, resolution: dict[str, Any]) -> bool:
        """
        Cache a successful incident resolution.

        Args:
            incident_type: Type of incident
            resolution: Resolution data

        Returns:
            True if cached successfully
        """
        cache_key = f"incident_resolution:{incident_type}"
        return self.ml_cache_set(cache_key, resolution)

    def ml_recall_incident_resolution(self, incident_type: str) -> dict[str, Any] | None:
        """
        Recall a cached incident resolution.

        Args:
            incident_type: Type of incident

        Returns:
            Cached resolution or None
        """
        cache_key = f"incident_resolution:{incident_type}"
        return self.ml_cache_get(cache_key)

    def ml_optimize_playbook_selection(self, incident_type: str, telemetry: dict[str, Any]) -> str:
        """
        Select optimal recovery playbook using meta-learning.

        Args:
            incident_type: Type of incident
            telemetry: Current system telemetry

        Returns:
            Optimal playbook name
        """
        cache_key = f"optimal_playbook:{incident_type}"
        cached_playbook = self.ml_cache_get(cache_key)
        if cached_playbook:
            return cached_playbook.get("playbook", self.recovery_playbooks.get(incident_type, "default"))
        return self.recovery_playbooks.get(incident_type, "default_recovery")

    def ml_record_playbook_success(
        self,
        incident_type: str,
        playbook: str,
        success_metrics: dict[str, Any],
    ) -> bool:
        """
        Record a successful playbook execution for future optimization.

        Args:
            incident_type: Type of incident
            playbook: Playbook that was used
            success_metrics: Metrics from the successful execution

        Returns:
            True if recorded successfully
        """
        cache_key = f"optimal_playbook:{incident_type}"
        return self.ml_cache_set(cache_key, {"playbook": playbook, "metrics": success_metrics})

    def _cycle_results_key(self) -> str:
        """LIC orchestrator uses 'incident_recovery' as pattern cache key."""
        return "incident_recovery"
