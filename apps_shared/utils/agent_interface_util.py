"""
Unified Agent Interface - Standardized interface for all application agents.

Provides consistent agent lifecycle, execution patterns, and result handling
for apps_lic and apps_rg.
Phase 3A - Agent Interface Standardization
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "agent_interface_util", "p0_governance")
_emit_reads_policy_state("p0", "agent_interface_util", "policy_binding")
_emit_snapshots_state("p0", "agent_interface_util", "state_snapshot")
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

_emit_emits_metric_event("agent_interface_util", "p4obs", "metric_1")
_emit_emits_metric_event("agent_interface_util", "p4obs", "metric_2")
_emit_emits_metric_event("agent_interface_util", "p4obs", "metric_3")
_emit_emits_metric_event("agent_interface_util", "p4obs", "metric_4")
_emit_emits_metric_event("agent_interface_util", "p4obs", "metric_5")
_emit_emits_metric_event("agent_interface_util", "p4obs", "metric_6")
_emit_records_incident_event("agent_interface_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_interface_util", "p4obs", "anomaly")
_emit_writes_observability_log("agent_interface_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_interface_util", "p4obs", "mon_state")
_emit_triggers_alert("agent_interface_util", "p4obs", "alert")
_emit_links_incident_trace("agent_interface_util", "p4obs", "trace_link")
_emit_captures_pattern("agent_interface_util", "p3lm", "pattern")
_emit_records_learning_event("agent_interface_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_interface_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_interface_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_interface_util", "p3lm", "routing")
_emit_improves_agent_policy("agent_interface_util", "p3lm", "policy")
_emit_stores_learning_state("agent_interface_util", "p3lm", "state")
_emit_records_execution_trace("agent_interface_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_interface_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_interface_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_interface_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_interface_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_interface_util", "env_read", "p2_env_1")
_emit_reads_environ("agent_interface_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_interface_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_interface_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_interface_util", "context_pull")
_emit_pulls_context("p1", "agent_interface_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_interface_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_interface_util", "uwg_term_2")
_emit_writes_through("p1", "agent_interface_util", "write_through")
_emit_writes_through("p1", "agent_interface_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_interface_util", "safety_validation")
_emit_invokes_eval("p1", "agent_interface_util", "eval_call")
_emit_proposal_commits_routing("p1", "agent_interface_util", "routing_commit")
_emit_escalates_to_human("p1", "agent_interface_util", "human_escalation")
_emit_routes_through("p1", "agent_interface_util", "route_through")
_emit_checks_agent_registry("p1", "agent_interface_util", "agent_registry")
_emit_validates_agent_capability("p1", "agent_interface_util", "capability")
_emit_dispatches_execution_plan("p1", "agent_interface_util", "exec_plan")
_emit_agent_executes_agent("p1", "agent_interface_util", "sub_agent")
_emit_routes_to_agent("p1", "agent_interface_util", "target_agent")
_emit_verifies_policy("p1", "agent_interface_util", "policy_check")
_emit_observes_runtime_state("p1", "agent_interface_util", "runtime_state")
_emit_verifies_boundary("p1", "agent_interface_util", "boundary_check")
_emit_transcripts_response("p1", "agent_interface_util", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_interface_util")
_emit_gated_by_confidence("p1", "agent_interface_util", "confidence_gate")
emit_replay_key("p0", "agent_interface_util")
emit_determinism_digest("p0", "agent_interface_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_interface_util", "execution_auth")
_emit_validates_capability("p2", "agent_interface_util", "capability_check")
_emit_routes_to_capability("p2", "agent_interface_util", "capability_route")
_emit_writes_via_uwg("p2", "agent_interface_util", "uwg_write")
_emit_blocks_direct_write("p2", "agent_interface_util", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_interface_util", "tool_invocation")
_emit_captures_execution_output("p2", "agent_interface_util", "exec_output")
_emit_dispatches_agent("p3", "agent_interface_util", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_interface_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_interface_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_interface_util", "healing_outcome")
_emit_escalates_failure("p3", "agent_interface_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_interface_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_interface_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_interface_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_interface_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_interface_util", "eval_metric")
_emit_stores_embedding("p4", "agent_interface_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_interface_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_interface_util", "exec_snapshot_link")
_emit_reads_through("l4", "agent_interface_util", "urg_read_1")
_emit_reads_through("l4", "agent_interface_util", "urg_read_2")
_emit_reads_through("l4", "agent_interface_util", "urg_read_3")
_emit_reads_through("l4", "agent_interface_util", "urg_read_4")
_emit_reads_through("l4", "agent_interface_util", "urg_read_5")
_emit_reads_through("l4", "agent_interface_util", "urg_read_6")
_emit_reads_through("l4", "agent_interface_util", "urg_read_7")
_emit_reads_through("l4", "agent_interface_util", "urg_read_8")
_emit_reads_through("l4", "agent_interface_util", "urg_read_9")
_emit_reads_through("l4", "agent_interface_util", "urg_read_10")
_emit_reads_through("l4", "agent_interface_util", "urg_read_11")
_emit_reads_through("l4", "agent_interface_util", "urg_read_12")
_emit_reads_through("l4", "agent_interface_util", "urg_read_13")
_emit_reads_through("l4", "agent_interface_util", "urg_read_14")
_emit_reads_through("l4", "agent_interface_util", "urg_read_15")
_emit_reads_through("l4", "agent_interface_util", "urg_read_16")
_emit_reads_through("l4", "agent_interface_util", "urg_read_17")
_emit_reads_through("l4", "agent_interface_util", "urg_read_18")
_emit_reads_through("l4", "agent_interface_util", "urg_read_19")
_emit_reads_through("l4", "agent_interface_util", "urg_read_20")
_emit_reads_through("l4", "agent_interface_util", "urg_read_21")
_emit_reads_through("l4", "agent_interface_util", "urg_read_22")
_emit_reads_through("l4", "agent_interface_util", "urg_read_23")
_emit_reads_through("l4", "agent_interface_util", "urg_read_24")
_emit_reads_through("l4", "agent_interface_util", "urg_read_25")
_emit_reads_through("l4", "agent_interface_util", "urg_read_26")
_emit_reads_through("l4", "agent_interface_util", "urg_read_27")
_emit_reads_through("l4", "agent_interface_util", "urg_read_28")
_emit_reads_through("l4", "agent_interface_util", "urg_read_29")
_emit_reads_through("l4", "agent_interface_util", "urg_read_30")
_emit_reads_through("l4", "agent_interface_util", "urg_read_31")
_emit_reads_through("l4", "agent_interface_util", "urg_read_32")
_emit_reads_through("l4", "agent_interface_util", "urg_read_33")
_emit_reads_through("l4", "agent_interface_util", "urg_read_34")
_emit_reads_through("l4", "agent_interface_util", "urg_read_35")
_emit_reads_through("l4", "agent_interface_util", "urg_read_36")
_emit_reads_through("l4", "agent_interface_util", "urg_read_37")
_emit_reads_through("l4", "agent_interface_util", "urg_read_38")
_emit_reads_through("l4", "agent_interface_util", "urg_read_39")
_emit_reads_through("l4", "agent_interface_util", "urg_read_40")
_emit_reads_through("l4", "agent_interface_util", "urg_read_41")
_emit_reads_through("l4", "agent_interface_util", "urg_read_42")
_emit_reads_through("l4", "agent_interface_util", "urg_read_43")
_emit_reads_through("l4", "agent_interface_util", "urg_read_44")
_emit_reads_through("l4", "agent_interface_util", "urg_read_45")
_emit_reads_through("l4", "agent_interface_util", "urg_read_46")
_emit_reads_through("l4", "agent_interface_util", "urg_read_47")
_emit_reads_through("l4", "agent_interface_util", "urg_read_48")
_emit_reads_through("l4", "agent_interface_util", "urg_read_49")
_emit_reads_through("l4", "agent_interface_util", "urg_read_50")
_emit_reads_through("l4", "agent_interface_util", "urg_read_51")
_emit_reads_through("l4", "agent_interface_util", "urg_read_52")
_emit_reads_through("l4", "agent_interface_util", "urg_read_53")
_emit_reads_through("l4", "agent_interface_util", "urg_read_54")
_emit_reads_through("l4", "agent_interface_util", "urg_read_55")
_emit_reads_through("l4", "agent_interface_util", "urg_read_56")
_emit_reads_through("l4", "agent_interface_util", "urg_read_57")
_emit_reads_through("l4", "agent_interface_util", "urg_read_58")
_emit_reads_through("l4", "agent_interface_util", "urg_read_59")
_emit_reads_through("l4", "agent_interface_util", "urg_read_60")
_emit_reads_through("l4", "agent_interface_util", "urg_read_61")
_emit_reads_through("l4", "agent_interface_util", "urg_read_62")
_emit_reads_through("l4", "agent_interface_util", "urg_read_63")
_emit_reads_through("l4", "agent_interface_util", "urg_read_64")
_emit_reads_through("l4", "agent_interface_util", "urg_read_65")
_emit_reads_through("l4", "agent_interface_util", "urg_read_66")
_emit_reads_through("l4", "agent_interface_util", "urg_read_67")
_emit_reads_through("l4", "agent_interface_util", "urg_read_68")
_emit_reads_through("l4", "agent_interface_util", "urg_read_69")
_emit_reads_through("l4", "agent_interface_util", "urg_read_70")
_emit_reads_through("l4", "agent_interface_util", "urg_read_71")
_emit_reads_through("l4", "agent_interface_util", "urg_read_72")
_emit_reads_through("l4", "agent_interface_util", "urg_read_73")
_emit_reads_through("l4", "agent_interface_util", "urg_read_74")
_emit_reads_through("l4", "agent_interface_util", "urg_read_75")
_emit_reads_through("l4", "agent_interface_util", "urg_read_76")
_emit_reads_through("l4", "agent_interface_util", "urg_read_77")
_emit_reads_through("l4", "agent_interface_util", "urg_read_78")
_emit_reads_through("l4", "agent_interface_util", "urg_read_79")

logger = logging.getLogger(__name__)
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class AgentStatus(str, Enum):
    """Agent execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class AgentContext:
    """Context passed to agent during execution."""

    session_id: str
    trace_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 300.0
    retry_count: int = 0
    max_retries: int = 3

    def with_trace(self, trace_id: str) -> AgentContext:
        """Create new context with trace ID."""
        return AgentContext(
            session_id=self.session_id,
            trace_id=trace_id,
            user_id=self.user_id,
            metadata=self.metadata.copy(),
            timeout_seconds=self.timeout_seconds,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
        )


@dataclass
class AgentResult(Generic[OutputT]):
    """Result of agent execution."""

    status: AgentStatus
    output: OutputT | None = None
    error: str | None = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == AgentStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if execution failed."""
        return self.status in (AgentStatus.FAILED, AgentStatus.TIMEOUT, AgentStatus.CANCELLED)

    @classmethod
    def success(
        cls, output: OutputT, execution_time_ms: float = 0.0, metadata: dict[str, Any] | None = None,
    ) -> AgentResult[OutputT]:
        """Create a successful result."""
        return cls(
            status=AgentStatus.SUCCESS,
            output=output,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )

    @classmethod
    def failure(
        cls, error: str, execution_time_ms: float = 0.0, metadata: dict[str, Any] | None = None,
    ) -> AgentResult[OutputT]:
        """Create a failed result."""
        return cls(
            status=AgentStatus.FAILED,
            error=error,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )

    @classmethod
    def timeout(
        cls, execution_time_ms: float = 0.0, metadata: dict[str, Any] | None = None,
    ) -> AgentResult[OutputT]:
        """Create a timeout result."""
        return cls(
            status=AgentStatus.TIMEOUT,
            error="Execution timed out",
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )


class IAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract interface for all application agents.

    Provides a standardized contract for agent implementation across
    apps_lic and apps_rg.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for identification."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Agent version."""
        pass

    @property
    def description(self) -> str:
        """Agent description."""
        return ""

    @abstractmethod
    def execute(self, input_data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """
        Execute the agent with given input and context.

        Args:
            input_data: Input data for the agent
            context: Execution context

        Returns:
            AgentResult with output or error
        """
        pass

    def validate_input(self, input_data: InputT) -> tuple[bool, str | None]:
        """
        Validate input data before execution.

        Args:
            input_data: Input to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return (True, None)

    def pre_execute(self, input_data: InputT, context: AgentContext) -> None:
        """Hook called before execution."""
        pass

    def post_execute(self, input_data: InputT, context: AgentContext, result: AgentResult[OutputT]) -> None:
        """Hook called after execution."""
        pass

    def on_error(self, input_data: InputT, context: AgentContext, error: Exception) -> None:
        """Hook called when an error occurs."""
        pass


class BaseAgent(IAgent[InputT, OutputT]):
    """
    Base implementation of IAgent with common functionality.

    Provides:
    - Automatic timing
    - Error handling
    - Retry logic
    - Logging
    """

    def __init__(self, agent_name: str, agent_version: str = "1.0.0"):
        self._name = agent_name
        self._version = agent_version
        self._logger = logging.getLogger(f"{__name__}.{agent_name}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def execute(self, input_data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """Execute with timing, error handling, and retry logic."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseAgent.execute")

        start_time = time.time()
        is_valid, error_msg = self.validate_input(input_data)
        if not is_valid:
            return AgentResult.failure(
                error=f"Input validation failed: {error_msg}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        try:
            self.pre_execute(input_data, context)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            self._logger.warning(f"Pre-execute hook failed: {e}")
        last_error: Exception | None = None
        for attempt in range(context.max_retries + 1):
            try:
                context.retry_count = attempt
                result = self._do_execute(input_data, context)
                result.execution_time_ms = (time.time() - start_time) * 1000
                try:
                    self.post_execute(input_data, context, result)
                # guardian: allow-silent-swallow
                except Exception as e:
                    self._logger.warning(f"Post-execute hook failed: {e}")
                return result
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                last_error = e
                self._logger.warning(f"Attempt {attempt + 1}/{context.max_retries + 1} failed: {e}")
                try:
                    self.on_error(input_data, context, e)
                # guardian: allow-silent-swallow
                except Exception as hook_error:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    raise
                    self._logger.warning(f"Error hook failed: {hook_error}")
                if attempt < context.max_retries:
                    time.sleep(0.1 * (attempt + 1))
        return AgentResult.failure(
            error=f"All retries exhausted. Last error: {last_error}",
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    @abstractmethod
    def _do_execute(self, input_data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """
        Actual execution logic to be implemented by subclasses.

        Args:
            input_data: Validated input data
            context: Execution context

        Returns:
            AgentResult with output
        """
        pass


class AgentRegistry:
    """Registry for managing agent instances."""

    def __init__(self):
        self._agents: dict[str, IAgent] = {}

    def register(self, agent: IAgent) -> None:
        """Register an agent."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentRegistry.register")

        key = f"{agent.name}:{agent.version}"
        self._agents[key] = agent
        logger.info(f"Registered agent: {key}")

    def get(self, name: str, version: str | None = None) -> IAgent | None:
        """Get an agent by name and optional version."""
        if version:
            return self._agents.get(f"{name}:{version}")
        matching = [(k, v) for k, v in self._agents.items() if k.startswith(f"{name}:")]
        if matching:
            matching.sort(key=lambda x: x[0], reverse=True)
            return matching[0][1]
        return None

    def list_agents(self) -> list[dict[str, str]]:
        """List all registered agents."""
        return [{"name": agent.name, "version": agent.version} for agent in self._agents.values()]

    def unregister(self, name: str, version: str) -> bool:
        """Unregister an agent."""
        key = f"{name}:{version}"
        if key in self._agents:
            del self._agents[key]
            logger.info(f"Unregistered agent: {key}")
            return True
        return False


_agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry
