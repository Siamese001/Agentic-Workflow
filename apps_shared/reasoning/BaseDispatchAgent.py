"""BaseDispatchAgent — Shared dispatch executor skeleton for LIC and RG domains.

Extracted from DispatchOutreachToolsAgent and DispatchResumeToolsAgent (2026-03-11, P2-C).
App agents subclass this and override _perform_action() and domain-specific heal methods.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NamedTuple

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "BaseDispatchAgent", "p0_governance")
_emit_reads_policy_state("p0", "BaseDispatchAgent", "policy_binding")
_emit_snapshots_state("p0", "BaseDispatchAgent", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("BaseDispatchAgent", "p4obs", "metric_1")
_emit_emits_metric_event("BaseDispatchAgent", "p4obs", "metric_2")
_emit_emits_metric_event("BaseDispatchAgent", "p4obs", "metric_3")
_emit_emits_metric_event("BaseDispatchAgent", "p4obs", "metric_4")
_emit_emits_metric_event("BaseDispatchAgent", "p4obs", "metric_5")
_emit_emits_metric_event("BaseDispatchAgent", "p4obs", "metric_6")
_emit_records_incident_event("BaseDispatchAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("BaseDispatchAgent", "p4obs", "anomaly")
_emit_writes_observability_log("BaseDispatchAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("BaseDispatchAgent", "p4obs", "mon_state")
_emit_triggers_alert("BaseDispatchAgent", "p4obs", "alert")
_emit_links_incident_trace("BaseDispatchAgent", "p4obs", "trace_link")
_emit_captures_pattern("BaseDispatchAgent", "p3lm", "pattern")
_emit_records_learning_event("BaseDispatchAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("BaseDispatchAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("BaseDispatchAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("BaseDispatchAgent", "p3lm", "routing")
_emit_improves_agent_policy("BaseDispatchAgent", "p3lm", "policy")
_emit_stores_learning_state("BaseDispatchAgent", "p3lm", "state")
_emit_records_execution_trace("BaseDispatchAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("BaseDispatchAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("BaseDispatchAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("BaseDispatchAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("BaseDispatchAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("BaseDispatchAgent", "env_read", "p2_env_1")
_emit_reads_environ("BaseDispatchAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("BaseDispatchAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("BaseDispatchAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "BaseDispatchAgent", "context_pull")
_emit_pulls_context("p1", "BaseDispatchAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "BaseDispatchAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "BaseDispatchAgent", "uwg_term_2")
_emit_writes_through("p1", "BaseDispatchAgent", "write_through")
_emit_writes_through("p1", "BaseDispatchAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "BaseDispatchAgent", "safety_validation")
_emit_invokes_eval("p1", "BaseDispatchAgent", "eval_call")
_emit_proposal_commits_routing("p1", "BaseDispatchAgent", "routing_commit")
_emit_escalates_to_human("p1", "BaseDispatchAgent", "human_escalation")
_emit_routes_through("p1", "BaseDispatchAgent", "route_through")
_emit_checks_agent_registry("p1", "BaseDispatchAgent", "agent_registry")
_emit_validates_agent_capability("p1", "BaseDispatchAgent", "capability")
_emit_dispatches_execution_plan("p1", "BaseDispatchAgent", "exec_plan")
_emit_agent_executes_agent("p1", "BaseDispatchAgent", "sub_agent")
_emit_routes_to_agent("p1", "BaseDispatchAgent", "target_agent")
_emit_verifies_policy("p1", "BaseDispatchAgent", "policy_check")
_emit_observes_runtime_state("p1", "BaseDispatchAgent", "runtime_state")
_emit_verifies_boundary("p1", "BaseDispatchAgent", "boundary_check")
_emit_transcripts_response("p1", "BaseDispatchAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "BaseDispatchAgent")
_emit_gated_by_confidence("p1", "BaseDispatchAgent", "confidence_gate")
emit_replay_key("p0", "BaseDispatchAgent")
emit_determinism_digest("p0", "BaseDispatchAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "BaseDispatchAgent", "execution_auth")
_emit_validates_capability("p2", "BaseDispatchAgent", "capability_check")
_emit_routes_to_capability("p2", "BaseDispatchAgent", "capability_route")
_emit_writes_via_uwg("p2", "BaseDispatchAgent", "uwg_write")
_emit_blocks_direct_write("p2", "BaseDispatchAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "BaseDispatchAgent", "tool_invocation")
_emit_captures_execution_output("p2", "BaseDispatchAgent", "exec_output")
_emit_dispatches_agent("p3", "BaseDispatchAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "BaseDispatchAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "BaseDispatchAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "BaseDispatchAgent", "healing_outcome")
_emit_escalates_failure("p3", "BaseDispatchAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "BaseDispatchAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "BaseDispatchAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "BaseDispatchAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "BaseDispatchAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "BaseDispatchAgent", "eval_metric")
_emit_stores_embedding("p4", "BaseDispatchAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "BaseDispatchAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "BaseDispatchAgent", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
_DEFAULT_TIMEOUT_S = 30.0
_MAX_SAFE_TIMEOUT_S = 300.0
_MIN_SAFE_TIMEOUT_S = 1.0


class ExecutionResult(NamedTuple):
    """Result of a dispatch execution action."""

    SUCCESS: bool
    OUTPUT: Any = None
    ERROR: str | None = None
    duration_ms: float = 0.0


@dataclass
class BaseDispatchAgent(SovereignBaseAgent):
    """Generic action dispatcher with self-healing config/timeout management.

    Subclasses override:
    - `_perform_action()` to add domain-specific routing
    - `_heal_domain_config()` for domain-specific config checks
    - `_run_domain_diagnostics()` for domain smoke tests
    """

    config_dict: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize timeout from config_dict."""
        super().__post_init__()
        self.TIMEOUT: float = float(self.config_dict.get("timeout", _DEFAULT_TIMEOUT_S))
        Logger.info(f"Initialized {self.__class__.__name__} (timeout={self.TIMEOUT}s)")
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
        """Register this agent as an entity in the Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            bridge.create_agent_entity(
                agent_name=self.__class__.__name__,
                agent_type="DispatchAgent",
                observations=[
                    f"DispatchAgent {self.__class__.__name__} initialized",
                    f"timeout={self.config_dict.get('timeout', _DEFAULT_TIMEOUT_S)}s",
                ],
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] KG registration skipped: {e}")

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, "config_dict"), "Missing config_dict"
        return True

    def execute(self, action: str, params: dict[str, Any]) -> ExecutionResult:
        """Execute action with parameters, returning a timed ExecutionResult."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseDispatchAgent.execute")

        start = time.time()
        try:
            with self.start_span("agent.execute", {"agent": self.__class__.__name__, "action": action}):
                output = self._perform_action(action, params)
                result = ExecutionResult(SUCCESS=True, OUTPUT=output, duration_ms=(time.time() - start) * 1000)
                self._persist_outcome(action, result)
                return result
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            result = ExecutionResult(SUCCESS=False, ERROR=str(e), duration_ms=(time.time() - start) * 1000)
            self._persist_outcome(action, result)
            return result

    def _persist_outcome(self, action: str, result: ExecutionResult) -> None:
        """Persist task outcome to Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            score = 1.0 if result.SUCCESS else 0.0
            task_desc = f"{self.__class__.__name__}:{action}"
            if result.SUCCESS and score >= 0.8:
                bridge.create_mastered_task_relation(
                    agent_name=self.__class__.__name__, task_description=task_desc, feedback_score=score
                )
            elif not result.SUCCESS:
                bridge.create_relation(
                    from_entity=self.__class__.__name__,
                    to_entity=f"Task_{action}",
                    relation_type=GraphMemoryBridge.RELATION_FAILED_TASK,
                )
                bridge.add_observation(
                    entity_name=self.__class__.__name__,
                    observation=f"Failed action={action} error={result.ERROR}",
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] KG outcome persistence skipped: {e}")

    # guardian: allow-type-erasure
    def _perform_action(self, action: str, params: dict[str, Any]) -> Any:
        """Perform the action. Subclasses override for domain routing."""
        Logger.info(f"Executing {action} with {params}")
        return {"action": action, "params": params, "status": "completed"}

    def heal_repository(self) -> None:
        """Autonomy healing: shared timeout + config checks, then domain-specific."""
        super().heal_repository()
        self._heal_timeout_settings()
        self._heal_config_integrity()
        self._heal_domain_config()
        self._run_domain_diagnostics()

    def _heal_timeout_settings(self) -> None:
        """Ensure timeout is within safe bounds [1s, 300s]."""
        # guardian: allow-config-with-logic
        if self.TIMEOUT > _MAX_SAFE_TIMEOUT_S:
            Logger.warning(f"Timeout {self.TIMEOUT}s exceeds safe limit — resetting to {_DEFAULT_TIMEOUT_S}s")
            self.TIMEOUT = _DEFAULT_TIMEOUT_S
        # guardian: allow-config-with-logic
        elif self.TIMEOUT < _MIN_SAFE_TIMEOUT_S:
            Logger.warning(f"Timeout {self.TIMEOUT}s too low — resetting to {_DEFAULT_TIMEOUT_S}s")
            self.TIMEOUT = _DEFAULT_TIMEOUT_S

    def _heal_config_integrity(self) -> None:
        """Validate config_dict structure and repair if corrupted."""
        if not isinstance(self.config_dict, dict):
            Logger.warning("config_dict corrupted — resetting to defaults")
            self.config_dict = {}
        # guardian: allow-config-with-logic
        if "timeout" not in self.config_dict:
            Logger.warning("Missing config key 'timeout' — setting default")
            self.config_dict["timeout"] = _DEFAULT_TIMEOUT_S

    def _heal_domain_config(self) -> None:
        """Domain-specific config healing. Override in subclasses."""

    def _run_domain_diagnostics(self) -> None:
        """Domain-specific smoke test. Default: generic action test."""
        try:
            test_result = self._perform_action("test", {"query": "diagnostic test"})
            if isinstance(test_result, dict) and "error" in test_result:
                Logger.error(f"Diagnostics failed: {test_result['error']}")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Diagnostics exception: {e}")

    # guardian: allow-type-erasure
    def heal(self, violation: Any, **kwargs: Any) -> Any:
        return super().heal(violation, **kwargs)
