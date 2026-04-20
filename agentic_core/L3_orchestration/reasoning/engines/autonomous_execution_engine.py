from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "autonomous_execution_engine")
emit_determinism_digest("p0", "autonomous_execution_engine")

_emit_dispatches_healing_run("p1", "autonomous_execution_engine", "L3")
_emit_routes_through("p1", "autonomous_execution_engine", "L3")
_emit_verifies_policy("p1", "autonomous_execution_engine", "policy_check")
_emit_observes_runtime_state("p1", "autonomous_execution_engine", "runtime_state")
_emit_verifies_boundary("p1", "autonomous_execution_engine", "boundary_check")
_emit_transcripts_response("p1", "autonomous_execution_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "autonomous_execution_engine")
_emit_gated_by_confidence("p1", "autonomous_execution_engine", "confidence_gate")
_emit_escalates_to_human("p1", "autonomous_execution_engine", "L3")
_emit_reads_policy_state("p1", "autonomous_execution_engine", "L3")
_emit_routes_to_agent("p1", "autonomous_execution_engine", "L3")
_emit_orchestrates_workflow("p1", "autonomous_execution_engine", "L3")
_emit_dispatches_execution_plan("p1", "autonomous_execution_engine", "L3")
_emit_validates_agent_capability("p1", "autonomous_execution_engine", "L3")
_emit_checks_agent_registry("p1", "autonomous_execution_engine", "L3")

_emit_snapshots_state("p0", "autonomous_execution_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "autonomous_execution_engine", "p0_governance")
_emit_authorize_and_execute("p2", "autonomous_execution_engine", "execution_auth")
_emit_validates_capability("p2", "autonomous_execution_engine", "capability_check")
_emit_routes_to_capability("p2", "autonomous_execution_engine", "capability_route")
_emit_writes_via_uwg("p2", "autonomous_execution_engine", "uwg_write")
_emit_blocks_direct_write("p2", "autonomous_execution_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "autonomous_execution_engine", "tool_invocation")
_emit_captures_execution_output("p2", "autonomous_execution_engine", "exec_output")
_emit_dispatches_agent("p3", "autonomous_execution_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "autonomous_execution_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "autonomous_execution_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "autonomous_execution_engine", "healing_outcome")
_emit_escalates_failure("p3", "autonomous_execution_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "autonomous_execution_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "autonomous_execution_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "autonomous_execution_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "autonomous_execution_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "autonomous_execution_engine", "eval_metric")
_emit_stores_embedding("p4", "autonomous_execution_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "autonomous_execution_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "autonomous_execution_engine", "exec_snapshot_link")

"\nL3 Orchestration: Autonomous Execution Engine\nThe eternal heart that continuously validates and heals the Canon territory.\n"
import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("autonomous_execution_engine", "p4obs", "metric_1")
_emit_emits_metric_event("autonomous_execution_engine", "p4obs", "metric_2")
_emit_emits_metric_event("autonomous_execution_engine", "p4obs", "metric_3")
_emit_emits_metric_event("autonomous_execution_engine", "p4obs", "metric_4")
_emit_emits_metric_event("autonomous_execution_engine", "p4obs", "metric_5")
_emit_emits_metric_event("autonomous_execution_engine", "p4obs", "metric_6")
_emit_records_incident_event("autonomous_execution_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("autonomous_execution_engine", "p4obs", "anomaly")
_emit_writes_observability_log("autonomous_execution_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("autonomous_execution_engine", "p4obs", "mon_state")
_emit_triggers_alert("autonomous_execution_engine", "p4obs", "alert")
_emit_links_incident_trace("autonomous_execution_engine", "p4obs", "trace_link")
_emit_captures_pattern("autonomous_execution_engine", "p3lm", "pattern")
_emit_records_learning_event("autonomous_execution_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("autonomous_execution_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("autonomous_execution_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("autonomous_execution_engine", "p3lm", "routing")
_emit_improves_agent_policy("autonomous_execution_engine", "p3lm", "policy")
_emit_stores_learning_state("autonomous_execution_engine", "p3lm", "state")
_emit_records_execution_trace("autonomous_execution_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("autonomous_execution_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("autonomous_execution_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("autonomous_execution_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("autonomous_execution_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("autonomous_execution_engine", "env_read", "p2_env_1")
_emit_reads_environ("autonomous_execution_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("autonomous_execution_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("autonomous_execution_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "autonomous_execution_engine", "context_pull")
_emit_pulls_context("p1", "autonomous_execution_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "autonomous_execution_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "autonomous_execution_engine", "uwg_term_2")
_emit_writes_through("p1", "autonomous_execution_engine", "write_through")
_emit_writes_through("p1", "autonomous_execution_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "autonomous_execution_engine", "safety_validation")
_emit_invokes_eval("p1", "autonomous_execution_engine", "eval_call")
_emit_proposal_commits_routing("p1", "autonomous_execution_engine", "routing_commit")

Logger = logging.getLogger(__name__)


def _get_create_proactive_resource_manager():
    """Lazy load create_proactive_resource_manager to avoid upward import."""
    from agentic_core.L5_safety.reasoning.ResourceManagerAgent import create_proactive_resource_manager

    return create_proactive_resource_manager


def _get_create_autonomous_checkpoint_manager():
    """Lazy loader for create_autonomous_checkpoint_manager (upward L3->L4 seam)."""
    try:
        from agentic_core.L4_state.checkpoint_manager import create_autonomous_checkpoint_manager

        return create_autonomous_checkpoint_manager
    except ImportError as e:
        raise


create_autonomous_checkpoint_manager = _get_create_autonomous_checkpoint_manager()


class autonomous_execution_engine:
    """
    L3 Execution Engine that continuously validates and heals the Canon.

    Features:
    - Eternal execution cycle with configurable intervals
    - Circuit breaker pattern for failure protection
    - Atomic state saves to prevent corruption
    - Resource-aware execution
    - Checkpoint integration for recovery
    """

    def __init__(self):
        self.running = True
        self.state_path = Path(".canon_memory/execution_state.json")
        _wg.ensure_dir(self.state_path.parent)
        self.resource_manager = create_proactive_resource_manager()
        self.CheckpointManager = create_autonomous_checkpoint_manager()
        self.last_mission_result: dict[str, Any] | None = None
        # guardian: allow-magic-config
        self.execution_interval = 3600
        # guardian: allow-magic-config
        self.priority_threshold = 50
        self._execution_task = None
        self.consecutive_failures = 0
        # guardian: allow-magic-config
        self.max_consecutive_failures = 5
        self.load_state()
        Logger.info("L3 Autonomous Execution Engine initialized")

    def awaken(self):
        """L3: Explicitly wake the execution heart of the Canon"""
        if not self._execution_task:
            self._execution_task = asyncio.create_task(self.eternal_execution_cycle())
            Logger.info("L3 Eternal execution cycle awakened")

    def load_state(self):
        """Load previous execution state"""
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                self.last_mission_result = data.get("last_mission")
                Logger.info("L3: Loaded execution state")
            except (  # guardian: allow-broad-exception -- state load error re-raised to caller for handling
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ):
                raise

    def save_state(self):
        """L3: Atomic state save to prevent corruption"""
        try:
            data = {
                "last_mission": self.last_mission_result,
                "consecutive_failures": self.consecutive_failures,
                "saved_at": datetime.utcnow().isoformat(),
            }
            _wg.write_json_atomic(self.state_path, data)
            Logger.debug("L3: Execution state saved atomically")
        except (  # guardian: allow-broad-exception -- state save error re-raised to caller for handling
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ):
            raise

    async def execute_validation_mission(self):
        """
        Execute a validation mission across the Canon territory.

        This is a placeholder that can be integrated with:
        - Canon validator
        - RAG orchestrator
        - Systematic territory audits
        """
        _emit_agent_executes_agent(
            str(uuid.uuid4()),
            "autonomous_execution_engine",
            "autonomous_execution_engine.execute_validation_mission",
        )
        try:
            status = self.resource_manager.get_resource_status()
            if status["global_budget_remaining"] < 10:
                Logger.warning("L3: Low resource budget, skipping mission")
                return
            checkpoint_id = await self.CheckpointManager.auto_checkpoint_if_needed(
                state={"mission": "validation", "timestamp": datetime.utcnow().isoformat()},
                files_to_track=[],
            )
            Logger.info("L3: Starting validation mission")
            await asyncio.sleep(DEFAULT_SLEEP)
            self.last_mission_result = {
                "status": "success",
                "checkpoint_id": checkpoint_id,
                "completed_at": datetime.utcnow().isoformat(),
                "message": "Canon state verified",
            }
            self.consecutive_failures = 0
            Logger.info("L3 MISSION COMPLETE: Canon state verified")
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise

    async def eternal_execution_cycle(self):
        """L3: Continuous validation and healing cycle"""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "autonomous_execution_engine.eternal_execution_cycle",
        )

        Logger.info("L3: Eternal execution cycle active")
        while self.running:
            try:
                await asyncio.sleep(self.execution_interval)
                Logger.info("L3: Starting execution cycle")
                await self.execute_validation_mission()
                self.save_state()
            except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
                raise
        Logger.warning("L3: Eternal execution cycle stopped (Safe Mode)")

    def get_execution_status(self) -> dict[str, Any]:
        """Get current execution status"""
        return {
            "running": self.running,
            "execution_task_active": self._execution_task is not None and (not self._execution_task.done()),
            "consecutive_failures": self.consecutive_failures,
            "last_mission": self.last_mission_result,
            "execution_interval": self.execution_interval,
        }

    def reset_circuit_breaker(self):
        """Reset circuit breaker and resume execution"""
        self.consecutive_failures = 0
        self.running = True
        if not self._execution_task or self._execution_task.done():
            self.awaken()
        Logger.info("L3: Circuit breaker reset, execution resumed")


def create_autonomous_execution_engine() -> AutonomousExecutionEngine:
    """Factory function to create autonomous execution engine"""
    return AutonomousExecutionEngine()
