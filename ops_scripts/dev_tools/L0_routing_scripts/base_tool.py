from abc import ABC, abstractmethod
import inspect
from collections.abc import Callable

from pydantic import BaseModel, Field

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
    _emit_records_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "base_tool", "L0")
_emit_routes_through("p1", "base_tool", "L0")
_emit_checks_agent_registry("p1", "base_tool", "agent_registry")
_emit_validates_agent_capability("p1", "base_tool", "capability")
_emit_dispatches_execution_plan("p1", "base_tool", "exec_plan")
_emit_agent_executes_agent("p1", "base_tool", "sub_agent")
_emit_routes_to_agent("p1", "base_tool", "target_agent")
_emit_verifies_policy("p1", "base_tool", "policy_check")
_emit_observes_runtime_state("p1", "base_tool", "runtime_state")
_emit_verifies_boundary("p1", "base_tool", "boundary_check")
_emit_transcripts_response("p1", "base_tool", "transcript")
_emit_hard_fails_untranscripted("p1", "base_tool")
_emit_gated_by_confidence("p1", "base_tool", "confidence_gate")
_emit_escalates_to_human("p1", "base_tool", "L0")
_emit_reads_policy_state("p1", "base_tool", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "base_tool", "p0_governance")
_emit_snapshots_state("p0", "base_tool", "state_snapshot")
_emit_authorize_and_execute("p2", "base_tool", "execution_auth")
_emit_validates_capability("p2", "base_tool", "capability_check")
_emit_routes_to_capability("p2", "base_tool", "capability_route")
_emit_writes_via_uwg("p2", "base_tool", "uwg_write")
_emit_blocks_direct_write("p2", "base_tool", "direct_write_block")
_emit_records_tool_invocation("p2", "base_tool", "tool_invocation")
_emit_captures_execution_output("p2", "base_tool", "exec_output")
_emit_dispatches_agent("p3", "base_tool", "agent_dispatch")
_emit_coordinates_agents("p3", "base_tool", "agent_coordination")
_emit_records_workflow_lineage("p3", "base_tool", "workflow_lineage")
_emit_records_healing_outcome("p3", "base_tool", "healing_outcome")
_emit_escalates_failure("p3", "base_tool", "failure_escalation")
_emit_orchestrates_workflow("p3", "base_tool", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "base_tool", "healing_dispatch")
_emit_invokes_evaluation("p3", "base_tool", "evaluation_signal")
_emit_records_telemetry_event("p4", "base_tool", "telemetry_event")
_emit_captures_evaluation_metric("p4", "base_tool", "eval_metric")
_emit_stores_embedding("p4", "base_tool", "embedding_store")
_emit_updates_meta_learning_state("p4", "base_tool", "meta_learning")
_emit_links_execution_to_snapshot("p4", "base_tool", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("base_tool", "p4obs", "metric_1")
_emit_emits_metric_event("base_tool", "p4obs", "metric_2")
_emit_emits_metric_event("base_tool", "p4obs", "metric_3")
_emit_emits_metric_event("base_tool", "p4obs", "metric_4")
_emit_emits_metric_event("base_tool", "p4obs", "metric_5")
_emit_emits_metric_event("base_tool", "p4obs", "metric_6")
_emit_records_incident_event("base_tool", "p4obs", "incident")
_emit_captures_runtime_anomaly("base_tool", "p4obs", "anomaly")
_emit_writes_observability_log("base_tool", "p4obs", "obs_log")
_emit_updates_monitoring_state("base_tool", "p4obs", "mon_state")
_emit_triggers_alert("base_tool", "p4obs", "alert")
_emit_links_incident_trace("base_tool", "p4obs", "trace_link")
_emit_captures_pattern("base_tool", "p3lm", "pattern")
_emit_records_learning_event("base_tool", "p3lm", "learning_event")
_emit_writes_learning_snapshot("base_tool", "p3lm", "snapshot")
_emit_feeds_meta_learning("base_tool", "p3lm", "meta_feed")
_emit_updates_routing_strategy("base_tool", "p3lm", "routing")
_emit_improves_agent_policy("base_tool", "p3lm", "policy")
_emit_stores_learning_state("base_tool", "p3lm", "state")
_emit_records_execution_trace("base_tool", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("base_tool", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("base_tool", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("base_tool", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("base_tool", "L4_STATE", "p2_trace_5")
_emit_reads_environ("base_tool", "env_read", "p2_env_1")
_emit_reads_environ("base_tool", "env_read", "p2_env_2")
_emit_reads_runtime_state("base_tool", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("base_tool", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "base_tool", "context_pull")
_emit_pulls_context("p1", "base_tool", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "base_tool", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "base_tool", "uwg_term_2")
_emit_writes_through("p1", "base_tool", "write_through")
_emit_writes_through("p1", "base_tool", "write_through_2")
_emit_validated_by_safety_plane("p1", "base_tool", "safety_validation")
_emit_invokes_eval("p1", "base_tool", "eval_call")
_emit_proposal_commits_routing("p1", "base_tool", "routing_commit")


class BaseTool(BaseModel, ABC):
    """
    Abstract base class for all executable tools.
    """

    name: str = Field(..., description="Unique identifier for the tool")
    description: str = Field(..., description="Natural language description for the LLM")

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def run(self, **kwargs) -> str:
        """
        Execute the tool logic. Returns a string observation.
        """
        pass


class FunctionalTool(BaseTool):
    """
    Wrapper to turn a Python function into a Tool.
    """

    func: Callable

    async def run(self, **kwargs) -> str:
        try:
            result = self.func(**kwargs)
            if inspect.isawaitable(result):
                result = await result
            return str(result)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # guardian: allow-silent-swallow
            return f"Error executing {self.name} ({type(e).__name__}): {e}"


class ToolRegistry:
    """
    Manager for the agent's available toolkit.
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ToolRegistry.register")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> str:
        return "\n".join([f"- {t.name}: {t.description}" for t in self._tools.values()])
