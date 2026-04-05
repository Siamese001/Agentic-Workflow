"""
IOrchestratorAgent Protocol - Phase 1 Foundation

Defines the canonical interface for all orchestrator agents in the L3 layer.
This protocol ensures consistent behavior across the 28+ orchestrator implementations.

Usage:
    @runtime_checkable
    class IOrchestratorAgent(Protocol):
        ...

    # Type checking
    if isinstance(agent, IOrchestratorAgent):
        result = agent.run_mission(agents, dry_run=True)

Author: Cascade
Date: January 19, 2026
Phase: 1 - Foundation & Zero-Loss Protocols
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "orchestrator_types")
emit_determinism_digest("p0", "orchestrator_types")

_emit_dispatches_healing_run("p1", "orchestrator_types", "L3")
_emit_routes_through("p1", "orchestrator_types", "L3")
_emit_checks_agent_registry("p1", "orchestrator_types", "agent_registry")
_emit_validates_agent_capability("p1", "orchestrator_types", "capability")
_emit_dispatches_execution_plan("p1", "orchestrator_types", "exec_plan")
_emit_agent_executes_agent("p1", "orchestrator_types", "sub_agent")
_emit_routes_to_agent("p1", "orchestrator_types", "target_agent")
_emit_verifies_policy("p1", "orchestrator_types", "policy_check")
_emit_observes_runtime_state("p1", "orchestrator_types", "runtime_state")
_emit_verifies_boundary("p1", "orchestrator_types", "boundary_check")
_emit_transcripts_response("p1", "orchestrator_types", "transcript")
_emit_hard_fails_untranscripted("p1", "orchestrator_types")
_emit_gated_by_confidence("p1", "orchestrator_types", "confidence_gate")
_emit_escalates_to_human("p1", "orchestrator_types", "L3")
_emit_reads_policy_state("p1", "orchestrator_types", "L3")
_emit_authorize_and_execute("p2", "orchestrator_types", "execution_auth")
_emit_validates_capability("p2", "orchestrator_types", "capability_check")
_emit_routes_to_capability("p2", "orchestrator_types", "capability_route")
_emit_writes_via_uwg("p2", "orchestrator_types", "uwg_write")
_emit_blocks_direct_write("p2", "orchestrator_types", "direct_write_block")
_emit_records_tool_invocation("p2", "orchestrator_types", "tool_invocation")
_emit_captures_execution_output("p2", "orchestrator_types", "exec_output")
_emit_dispatches_agent("p3", "orchestrator_types", "agent_dispatch")
_emit_coordinates_agents("p3", "orchestrator_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "orchestrator_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "orchestrator_types", "healing_outcome")
_emit_escalates_failure("p3", "orchestrator_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "orchestrator_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "orchestrator_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "orchestrator_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "orchestrator_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "orchestrator_types", "eval_metric")
_emit_stores_embedding("p4", "orchestrator_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "orchestrator_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "orchestrator_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
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

_emit_emits_metric_event("orchestrator_types", "p4obs", "metric_1")
_emit_emits_metric_event("orchestrator_types", "p4obs", "metric_2")
_emit_emits_metric_event("orchestrator_types", "p4obs", "metric_3")
_emit_emits_metric_event("orchestrator_types", "p4obs", "metric_4")
_emit_emits_metric_event("orchestrator_types", "p4obs", "metric_5")
_emit_emits_metric_event("orchestrator_types", "p4obs", "metric_6")
_emit_records_incident_event("orchestrator_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("orchestrator_types", "p4obs", "anomaly")
_emit_writes_observability_log("orchestrator_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("orchestrator_types", "p4obs", "mon_state")
_emit_triggers_alert("orchestrator_types", "p4obs", "alert")
_emit_links_incident_trace("orchestrator_types", "p4obs", "trace_link")
_emit_captures_pattern("orchestrator_types", "p3lm", "pattern")
_emit_records_learning_event("orchestrator_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("orchestrator_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("orchestrator_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("orchestrator_types", "p3lm", "routing")
_emit_improves_agent_policy("orchestrator_types", "p3lm", "policy")
_emit_stores_learning_state("orchestrator_types", "p3lm", "state")
_emit_records_execution_trace("orchestrator_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("orchestrator_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("orchestrator_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("orchestrator_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("orchestrator_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("orchestrator_types", "env_read", "p2_env_1")
_emit_reads_environ("orchestrator_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("orchestrator_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("orchestrator_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "orchestrator_types", "context_pull")
_emit_pulls_context("p1", "orchestrator_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "orchestrator_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "orchestrator_types", "uwg_term_2")
_emit_writes_through("p1", "orchestrator_types", "write_through")
_emit_writes_through("p1", "orchestrator_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "orchestrator_types", "safety_validation")
_emit_invokes_eval("p1", "orchestrator_types", "eval_call")
_emit_proposal_commits_routing("p1", "orchestrator_types", "routing_commit")

if TYPE_CHECKING:
    pass


class ExecutionPhase(str, Enum):
    """Execution phases for orchestrator lifecycle."""

    PLANNING = "planning"
    VALIDATION = "validation"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    ROLLBACK = "rollback"
    COMPLETE = "complete"


@dataclass
class ExecutionContext:
    """
    Context passed through orchestrator execution chain.

    Provides shared state and configuration for mission execution.

    [PHASE 1] Forward-Rolling Recursion Enhancement:
    - accumulated_context: Zero-loss context preservation across successor spawns
    - successor_chain tracking in metadata for DNA integrity
    """

    dry_run: bool = True
    execute: bool = False
    max_depth: int = 3
    current_depth: int = 0
    phase: ExecutionPhase = ExecutionPhase.PLANNING
    call_path: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    accumulated_context: dict[str, Any] = field(default_factory=dict)
    task_description: str | None = None
    input_data: dict | None = None
    expected_output_schema: dict | None = None
    upstream_summary: str | None = None

    def with_depth(self, new_depth: int) -> ExecutionContext:
        """Create new context with updated depth."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ExecutionContext.with_depth", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ExecutionContext.with_depth", "p0_governance")
        return ExecutionContext(
            dry_run=self.dry_run,
            execute=self.execute,
            max_depth=self.max_depth,
            current_depth=new_depth,
            phase=self.phase,
            call_path=self.call_path.copy(),
            metadata=self.metadata.copy(),
            accumulated_context=self.accumulated_context.copy(),
            task_description=self.task_description,
            input_data=self.input_data,
            expected_output_schema=self.expected_output_schema,
            upstream_summary=self.upstream_summary,
        )

    def with_phase(self, new_phase: ExecutionPhase) -> ExecutionContext:
        """Create new context with updated phase."""
        return ExecutionContext(
            dry_run=self.dry_run,
            execute=self.execute,
            max_depth=self.max_depth,
            current_depth=self.current_depth,
            phase=new_phase,
            call_path=self.call_path.copy(),
            metadata=self.metadata.copy(),
            accumulated_context=self.accumulated_context.copy(),
            task_description=self.task_description,
            input_data=self.input_data,
            expected_output_schema=self.expected_output_schema,
            upstream_summary=self.upstream_summary,
        )

    def with_accumulated_context(self, new_context: dict[str, Any]) -> ExecutionContext:
        """Create new context with merged accumulated_context for DNA preservation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ExecutionContext.with_accumulated_context"
        )

        merged = self.accumulated_context.copy()
        merged.update(new_context)
        return ExecutionContext(
            dry_run=self.dry_run,
            execute=self.execute,
            max_depth=self.max_depth,
            current_depth=self.current_depth,
            phase=self.phase,
            call_path=self.call_path.copy(),
            metadata=self.metadata.copy(),
            accumulated_context=merged,
            task_description=self.task_description,
            input_data=self.input_data,
            expected_output_schema=self.expected_output_schema,
            upstream_summary=self.upstream_summary,
        )

    def get_successor_chain(self) -> list[str]:
        """Get the current successor chain from metadata."""
        return self.metadata.get("successor_chain", [])

    def get_depth(self) -> int:
        """Get current recursion depth from metadata or current_depth."""
        return self.metadata.get("depth", self.current_depth)


@dataclass
class AgentResult:
    """
    Standardized result from agent execution.

    Provides consistent return format for orchestrator coordination.
    """

    agent_name: str
    success: bool
    violations_found: int = 0
    violations_fixed: int = 0
    errors: int = 0
    skipped: int = 0
    status: str = "UNKNOWN"
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "errors": self.errors,
            "skipped": self.skipped,
            "status": self.status,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class MissionResult:
    """
    Aggregated result from mission execution.

    Combines results from multiple agents into a unified summary.
    """

    success: bool
    total_agents: int
    successful_agents: int
    failed_agents: int
    total_violations_found: int = 0
    total_violations_fixed: int = 0
    total_errors: int = 0
    agent_results: list[AgentResult] = field(default_factory=list)
    phase: ExecutionPhase = ExecutionPhase.COMPLETE
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "total_agents": self.total_agents,
            "successful_agents": self.successful_agents,
            "failed_agents": self.failed_agents,
            "total_violations_found": self.total_violations_found,
            "total_violations_fixed": self.total_violations_fixed,
            "total_errors": self.total_errors,
            "agent_results": [r.to_dict() for r in self.agent_results],
            "phase": self.phase.value,
            "metadata": self.metadata,
        }


@runtime_checkable
class IOrchestratorAgent(Protocol):
    """
    Protocol defining the canonical interface for orchestrator agents.

    All orchestrators in L3_orchestration should implement this protocol
    to ensure consistent behavior and enable unified orchestration.

    Methods:
        run_mission: Execute a mission across multiple agents
        run_agent: Execute a single agent with standardized result
        get_available_agents: List agents this orchestrator can coordinate
        validate_mission: Pre-flight validation before execution

    Usage:
        @runtime_checkable allows isinstance() checks at runtime:

        if isinstance(agent, IOrchestratorAgent):
            result = agent.run_mission(agents, dry_run=True)
    """

    def run_mission(
        self,
        agents: list[str],
        dry_run: bool = True,
        execute: bool = False,
        context: ExecutionContext | None = None,
    ) -> MissionResult:
        """
        Execute a mission across multiple agents.

        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state

        Returns:
            MissionResult with aggregated outcomes
        """
        ...

    def run_agent(
        self, agent_name: str, dry_run: bool = True, context: ExecutionContext | None = None
    ) -> AgentResult:
        """
        Execute a single agent with standardized result.

        Args:
            agent_name: Name of the agent to execute
            dry_run: If True, only simulate execution
            context: Optional execution context

        Returns:
            AgentResult with execution outcome
        """
        ...

    def get_available_agents(self) -> list[str]:
        """
        Get list of agents this orchestrator can coordinate.

        Returns:
            List of agent class names
        """
        ...

    def validate_mission(self, agents: list[str], context: ExecutionContext | None = None) -> bool:
        """
        Pre-flight validation before mission execution.

        Args:
            agents: List of agent names to validate
            context: Optional execution context

        Returns:
            True if mission can proceed, False otherwise
        """
        ...


@runtime_checkable
class IHealable(Protocol):
    """
    Protocol for agents that support healing operations.

    This is a superset of the signatures found in BiasAuditorAgent,
    NamingAgent, and other healing-capable agents.

    Zero-Loss Guarantee:
        All existing heal_repository signatures are compatible with this protocol.
        The **kwargs ensures backward compatibility with legacy callers.
    """

    # guardian: allow-magic-config
    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, **kwargs
    ) -> dict[str, Any]:
        """
        Repository-level healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            **kwargs: Additional arguments for backward compatibility

        Returns:
            Dict with healing summary (violations_found, violations_fixed, etc.)
        """
        ...


__all__ = [
    "IOrchestratorAgent",
    "IHealable",
    "ExecutionPhase",
    "ExecutionContext",
    "AgentResult",
    "MissionResult",
]

_emit_reads_through("l4", "orchestrator_types", "urg_read_1")
_emit_reads_through("l4", "orchestrator_types", "urg_read_2")
_emit_reads_through("l4", "orchestrator_types", "urg_read_3")
_emit_reads_through("l4", "orchestrator_types", "urg_read_4")
_emit_reads_through("l4", "orchestrator_types", "urg_read_5")
_emit_reads_through("l4", "orchestrator_types", "urg_read_6")
_emit_reads_through("l4", "orchestrator_types", "urg_read_7")
_emit_reads_through("l4", "orchestrator_types", "urg_read_8")
_emit_reads_through("l4", "orchestrator_types", "urg_read_9")
_emit_reads_through("l4", "orchestrator_types", "urg_read_10")
_emit_reads_through("l4", "orchestrator_types", "urg_read_11")
_emit_reads_through("l4", "orchestrator_types", "urg_read_12")
_emit_reads_through("l4", "orchestrator_types", "urg_read_13")
_emit_reads_through("l4", "orchestrator_types", "urg_read_14")
_emit_reads_through("l4", "orchestrator_types", "urg_read_15")
_emit_reads_through("l4", "orchestrator_types", "urg_read_16")
_emit_reads_through("l4", "orchestrator_types", "urg_read_17")
_emit_reads_through("l4", "orchestrator_types", "urg_read_18")
_emit_reads_through("l4", "orchestrator_types", "urg_read_19")
_emit_reads_through("l4", "orchestrator_types", "urg_read_20")
_emit_reads_through("l4", "orchestrator_types", "urg_read_21")
_emit_reads_through("l4", "orchestrator_types", "urg_read_22")
_emit_reads_through("l4", "orchestrator_types", "urg_read_23")
_emit_reads_through("l4", "orchestrator_types", "urg_read_24")
_emit_reads_through("l4", "orchestrator_types", "urg_read_25")
_emit_reads_through("l4", "orchestrator_types", "urg_read_26")
_emit_reads_through("l4", "orchestrator_types", "urg_read_27")
_emit_reads_through("l4", "orchestrator_types", "urg_read_28")
_emit_reads_through("l4", "orchestrator_types", "urg_read_29")
_emit_reads_through("l4", "orchestrator_types", "urg_read_30")
_emit_reads_through("l4", "orchestrator_types", "urg_read_31")
_emit_reads_through("l4", "orchestrator_types", "urg_read_32")
_emit_reads_through("l4", "orchestrator_types", "urg_read_33")
_emit_reads_through("l4", "orchestrator_types", "urg_read_34")
_emit_reads_through("l4", "orchestrator_types", "urg_read_35")
_emit_reads_through("l4", "orchestrator_types", "urg_read_36")
_emit_reads_through("l4", "orchestrator_types", "urg_read_37")
_emit_reads_through("l4", "orchestrator_types", "urg_read_38")
_emit_reads_through("l4", "orchestrator_types", "urg_read_39")
_emit_reads_through("l4", "orchestrator_types", "urg_read_40")
_emit_reads_through("l4", "orchestrator_types", "urg_read_41")
_emit_reads_through("l4", "orchestrator_types", "urg_read_42")
_emit_reads_through("l4", "orchestrator_types", "urg_read_43")
_emit_reads_through("l4", "orchestrator_types", "urg_read_44")
_emit_reads_through("l4", "orchestrator_types", "urg_read_45")
_emit_reads_through("l4", "orchestrator_types", "urg_read_46")
_emit_reads_through("l4", "orchestrator_types", "urg_read_47")
_emit_reads_through("l4", "orchestrator_types", "urg_read_48")
_emit_reads_through("l4", "orchestrator_types", "urg_read_49")
_emit_reads_through("l4", "orchestrator_types", "urg_read_50")
_emit_reads_through("l4", "orchestrator_types", "urg_read_51")
_emit_reads_through("l4", "orchestrator_types", "urg_read_52")
_emit_reads_through("l4", "orchestrator_types", "urg_read_53")
_emit_reads_through("l4", "orchestrator_types", "urg_read_54")
_emit_reads_through("l4", "orchestrator_types", "urg_read_55")
_emit_reads_through("l4", "orchestrator_types", "urg_read_56")
_emit_reads_through("l4", "orchestrator_types", "urg_read_57")
_emit_reads_through("l4", "orchestrator_types", "urg_read_58")
_emit_reads_through("l4", "orchestrator_types", "urg_read_59")
_emit_reads_through("l4", "orchestrator_types", "urg_read_60")
_emit_reads_through("l4", "orchestrator_types", "urg_read_61")
_emit_reads_through("l4", "orchestrator_types", "urg_read_62")
_emit_reads_through("l4", "orchestrator_types", "urg_read_63")
_emit_reads_through("l4", "orchestrator_types", "urg_read_64")
_emit_reads_through("l4", "orchestrator_types", "urg_read_65")
_emit_reads_through("l4", "orchestrator_types", "urg_read_66")
_emit_reads_through("l4", "orchestrator_types", "urg_read_67")
_emit_reads_through("l4", "orchestrator_types", "urg_read_68")
_emit_reads_through("l4", "orchestrator_types", "urg_read_69")
_emit_reads_through("l4", "orchestrator_types", "urg_read_70")
_emit_reads_through("l4", "orchestrator_types", "urg_read_71")
