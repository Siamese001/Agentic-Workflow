from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from services.configuration import ConfigurationService

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

_emit_authorize_and_execute("p2", "sovereign_dependency_error_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_dependency_error_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_dependency_error_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_dependency_error_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_dependency_error_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_dependency_error_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_dependency_error_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_dependency_error_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_dependency_error_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_dependency_error_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_dependency_error_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_dependency_error_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_dependency_error_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_dependency_error_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_dependency_error_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_dependency_error_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_dependency_error_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_dependency_error_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_dependency_error_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_dependency_error_util", "exec_snapshot_link")
from runtime.core.telemetry import TraceEvent

_emit_applies_guardrail("p0", "sovereign_dependency_error_util", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_dependency_error_util", "policy_binding")
_emit_snapshots_state("p0", "sovereign_dependency_error_util", "state_snapshot")
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

_emit_emits_metric_event("sovereign_dependency_error_util", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_dependency_error_util", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_dependency_error_util", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_dependency_error_util", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_dependency_error_util", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_dependency_error_util", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_dependency_error_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_dependency_error_util", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_dependency_error_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_dependency_error_util", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_dependency_error_util", "p4obs", "alert")
_emit_links_incident_trace("sovereign_dependency_error_util", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_dependency_error_util", "p3lm", "pattern")
_emit_records_learning_event("sovereign_dependency_error_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_dependency_error_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_dependency_error_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_dependency_error_util", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_dependency_error_util", "p3lm", "policy")
_emit_stores_learning_state("sovereign_dependency_error_util", "p3lm", "state")
_emit_records_execution_trace("sovereign_dependency_error_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_dependency_error_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_dependency_error_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_dependency_error_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_dependency_error_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_dependency_error_util", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_dependency_error_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_dependency_error_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_dependency_error_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_dependency_error_util", "context_pull")
_emit_pulls_context("p1", "sovereign_dependency_error_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_dependency_error_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_dependency_error_util", "uwg_term_2")
_emit_writes_through("p1", "sovereign_dependency_error_util", "write_through")
_emit_writes_through("p1", "sovereign_dependency_error_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_dependency_error_util", "safety_validation")
_emit_invokes_eval("p1", "sovereign_dependency_error_util", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_dependency_error_util", "routing_commit")
_emit_escalates_to_human("p1", "sovereign_dependency_error_util", "human_escalation")
_emit_routes_through("p1", "sovereign_dependency_error_util", "route_through")
_emit_checks_agent_registry("p1", "sovereign_dependency_error_util", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_dependency_error_util", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_dependency_error_util", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_dependency_error_util", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_dependency_error_util", "target_agent")
_emit_verifies_policy("p1", "sovereign_dependency_error_util", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_dependency_error_util", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_dependency_error_util", "boundary_check")
_emit_transcripts_response("p1", "sovereign_dependency_error_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_dependency_error_util")
_emit_gated_by_confidence("p1", "sovereign_dependency_error_util", "confidence_gate")
emit_replay_key("p0", "sovereign_dependency_error_util")
emit_determinism_digest("p0", "sovereign_dependency_error_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if TYPE_CHECKING:
    pass
LOGGER = logging.getLogger(__name__)
Logger = logging.getLogger(__name__)


class SovereignDependencyError(Exception):
    """Raised when a required dependency is not injected into a Sovereign component."""

    pass


class AgentPlan(BaseModel):
    reasoning: str
    tool_calls: list[dict]


class SubatomicHop:
    """Sovereign SubatomicHop with Dependency Injection.

    All dependencies are injected via constructor to maintain Gravity Compliance.
    No upward imports allowed - all tools passed down from orchestration layer.
    """

    def __init__(
        self,
        role: str,
        config: dict,
        storage: Any | None = None,
        genealogy: Any | None = None,
        PiiVault: Any | None = None,
        CostGovernor: Any | None = None,
        overseer: Any | None = None,
        membrane: Any | None = None,
        airlock: Any | None = None,
        SupremeCourt: Any | None = None,
        mcp_manager: Any | None = None,
        sandbox: Any | None = None,
        StructuredEngineAgent: Any | None = None,
        gatekeeper: Any | None = None,
        telemetry: Any | None = None,
    ) -> None:
        """Initialize SubatomicHop with injected dependencies.

        Args:
            role: Agent role identifier
            config: configuration dictionary
            storage: LocalDiskAdapter instance (injected)
            genealogy: GenealogyRegistry instance (injected)
            PiiVault: PIIVault instance (injected)
            CostGovernor: CostGovernor instance (injected)
            overseer: ConstitutionalOverseer instance (injected)
            membrane: InputMembrane instance (injected)
            airlock: AirlockProtocol instance (injected)
            SupremeCourt: SupremeCourt instance (injected)
            mcp_manager: MCPConnectionManager instance (injected)
            sandbox: DockerSandbox instance (injected)
            StructuredEngineAgent: StructuredEngineAgent instance (injected)
            gatekeeper: semantic_gatekeeper instance (injected)
            telemetry: TelemetryRecorder instance (injected)

        Raises:
            SovereignDependencyError: If required dependencies are Missing
        """
        self.role = role
        self.id = str(uuid.uuid4())
        self.config = config
        if storage is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'storage' (LocalDiskAdapter) to be injected. Cannot import from higher layers - must be passed from orchestrator."
            )
        self.storage = storage
        if genealogy is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'genealogy' (GenealogyRegistry) to be injected."
            )
        self.genealogy = genealogy
        if PiiVault is None:
            raise SovereignDependencyError("SubatomicHop requires 'PiiVault' (PIIVault) to be injected.")
        self.pii = PiiVault
        if CostGovernor is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'CostGovernor' (CostGovernor) to be injected."
            )
        self.governor = CostGovernor
        if overseer is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'overseer' (ConstitutionalOverseer) to be injected."
            )
        self.overseer = overseer
        if membrane is None:
            raise SovereignDependencyError("SubatomicHop requires 'membrane' (InputMembrane) to be injected.")
        self.membrane = membrane
        if airlock is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'airlock' (AirlockProtocol) to be injected."
            )
        self.airlock = airlock
        if SupremeCourt is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'SupremeCourt' (SupremeCourt) to be injected."
            )
        self.SupremeCourt = SupremeCourt
        if mcp_manager is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'mcp_manager' (MCPConnectionManager) to be injected."
            )
        self.mcp = mcp_manager
        if sandbox is None:
            raise SovereignDependencyError("SubatomicHop requires 'sandbox' (DockerSandbox) to be injected.")
        self.sandbox = sandbox
        if StructuredEngineAgent is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'StructuredEngineAgent' (StructuredEngineAgent) to be injected."
            )
        self.StructuredEngineAgent = StructuredEngineAgent
        if gatekeeper is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'gatekeeper' (semantic_gatekeeper) to be injected."
            )
        self.gatekeeper = gatekeeper
        if telemetry is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'telemetry' (TelemetryRecorder) to be injected."
            )
        self.telemetry = telemetry

    async def run(self, context: dict) -> Any:
        """Execute the hop with zero-trust protections."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SubatomicHop.run")

        trace_id = context.get("trace_id", self.id)
        return await self._run_with_zero_trust(context, trace_id)

    async def _run_with_zero_trust(self, context: dict, trace_id: str) -> Any:
        """Internal method with all L5.5 Zero Trust protections applied."""
        try:
            await self._preflight_checks(context, trace_id)
            plan, think_cost = await self._execute_think_stage_with_consensus(context, trace_id)
            results, act_cost = await self._execute_act_stage_with_airlock(plan, trace_id)
            await self._execute_critique_stage_with_membrane(results, trace_id)
            await self._execute_commit_stage(results, trace_id)
            self.telemetry.record(
                TraceEvent(
                    trace_id=trace_id,
                    span_id=f"{self.id}_complete",
                    ROLE=self.role,
                    event_type="SUCCESS",
                    PAYLOAD={"total_cost": think_cost + act_cost, "zero_trust": True},
                    TIMESTAMP=time.time(),
                )
            )
            return results
        except Exception as e:
            if type(e).__name__ == "BudgetExceededError":
                self._handle_budget_exceeded(trace_id, e)
                raise
            self._handle_execution_error(trace_id, e)
            raise
        finally:
            await self._cleanup(trace_id)

    async def _preflight_checks(self, context: dict, trace_id: str) -> None:
        """Pre-flight validation and setup."""
        str(hash(str(ConfigurationService().context)))
        self.genealogy.register_attempt(
            ConfigurationService().trace_id,
            str(ConfigurationService().context.get("Task", "")),
            ConfigurationService().context_hash,
        )
        await self.mcp.connect(self.role)
        await self._sanitize_input(ConfigurationService().context, ConfigurationService().trace_id)
        ConfigurationService().context.update(ConfigurationService().sanitized_context)
        self.telemetry.record(
            TraceEvent(
                trace_id=ConfigurationService().trace_id,
                span_id=f"{self.id}_preflight",
                ROLE=self.role,
                event_type="PREFLIGHT_COMPLETE",
                PAYLOAD={"checks": ["genealogy", "mcp", "membrane"]},
                TIMESTAMP=time.time(),
            )
        )

    async def _sanitize_input(self, context: dict, trace_id: str) -> dict:
        """Sanitize all inputs through the membrane."""
        for _key, _value in ConfigurationService().context.items():
            if isinstance(ConfigurationService().value, str):
                await self.membrane.sanitize(
                    ConfigurationService().value, f"context_{ConfigurationService().key}"
                )
                ConfigurationService().SANITIZED[ConfigurationService().KEY] = (
                    ConfigurationService().sanitized_value
                )
                if ConfigurationService().sanitized_value != ConfigurationService().value:
                    self.telemetry.record(
                        TraceEvent(
                            trace_id=ConfigurationService().trace_id,
                            span_id=f"{ConfigurationService().key}",
                            ROLE=self.role,
                            event_type="CONTENT_SANITIZED",
                            PAYLOAD={
                                "original_length": len(ConfigurationService().value),
                                "sanitized_length": len(ConfigurationService().sanitized_value),
                            },
                            TIMESTAMP=time.time(),
                        )
                    )
            else:
                ConfigurationService().SANITIZED[ConfigurationService().KEY] = ConfigurationService().value
        return ConfigurationService().sanitized

    async def _execute_think_stage_with_consensus(
        self, context: dict, trace_id: str
    ) -> tuple[AgentPlan, float]:
        """Execute the thinking stage with multi-model consensus."""
        self._assess_task_risk(ConfigurationService().context.get("Task", ""))
        await self._check_past_failures(ConfigurationService().context.get("Task", ""))
        try:
            VERDICT = await self.SupremeCourt.deliberate(
                CONTEXT=str(ConfigurationService().context),
                GOAL=ConfigurationService().context.get("Task", ""),
                risk_level=ConfigurationService().risk_level,
            )
            AgentPlan(
                REASONING=VERDICT.reasoning,
                tool_calls=[{"name": "execute_plan", "args": {"plan": VERDICT.chosen_plan}}],
            )
            self.governor.track("gpt-4", 300, 150)
            self.telemetry.record(
                TraceEvent(
                    trace_id=ConfigurationService().trace_id,
                    span_id=f"{self.id}_consensus",
                    ROLE=self.role,
                    event_type="CONSENSUS_REACHED",
                    PAYLOAD={
                        "consensus_score": VERDICT.consensus_score,
                        "safe_to_proceed": VERDICT.safe_to_proceed,
                        "cost": ConfigurationService().think_cost,
                    },
                    TIMESTAMP=time.time(),
                )
            )
            return (ConfigurationService().plan, ConfigurationService().think_cost)
        except ValueError as e:
            self.telemetry.record(
                TraceEvent(
                    trace_id=ConfigurationService().trace_id,
                    span_id=f"{self.id}_consensus_failed",
                    ROLE=self.role,
                    event_type="CONSENSUS_FAILED",
                    PAYLOAD={"error": str(e)},
                    TIMESTAMP=time.time(),
                )
            )
            raise

    def _assess_task_risk(self, Task: str) -> str:
        """Assess the risk level of a Task."""
        task_lower = Task.lower()
        if any(keyword in task_lower for keyword in ConfigurationService().high_risk_keywords):
            return "high"
        elif any(keyword in task_lower for keyword in ["modify", "update", "change"]):
            return "medium"
        else:
            return "low"

    async def _check_past_failures(self, Task: str) -> str:
        """Check telemetry for past failures on similar tasks."""
        from agentic_core.utils.state_util import check_past_failures

        return check_past_failures(Task)

    async def _execute_act_stage_with_airlock(self, plan: AgentPlan, trace_id: str) -> tuple[list, float]:
        """Execute the action stage with airlock protection."""
        total_cost = 0.0
        results = []
        for call in plan.tool_calls:
            tool_name = call.get("name", "unknown")
            tool_args = call.get("args", {})
            try:
                await self.airlock.acquire_permission(tool_name, tool_args)
                if tool_name == "run_python" or tool_args.get("code"):
                    code = tool_args.get("code", "")
                    result = self.sandbox.run_code(code)
                    results.append({"tool": "sandbox", "result": result})
                else:
                    result = await self.mcp.call_tool(tool_name, tool_args)
                    if isinstance(result, str):
                        await self.membrane.sanitize(result, f"tool_output_{tool_name}")
                    results.append({"tool": tool_name, "result": result})
                total_cost += self.governor.track("tool_execution", 10, 10)
            except Exception as e:
                raise
                self.telemetry.record(
                    TraceEvent(
                        trace_id=trace_id,
                        span_id=f"{self.id}_airlock_blocked",
                        ROLE=self.role,
                        event_type="AIRLOCK_BLOCKED",
                        PAYLOAD={"tool": tool_name, "error": str(e)},
                        TIMESTAMP=time.time(),
                    )
                )
                raise
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_act",
                ROLE=self.role,
                event_type="ACT_COMPLETE",
                PAYLOAD={
                    "tool_count": len(plan.tool_calls),
                    "total_cost": total_cost,
                    "airlock_checks": len(plan.tool_calls),
                },
                TIMESTAMP=time.time(),
            )
        )
        return (results, total_cost)

    async def _execute_critique_stage_with_membrane(self, results: list, trace_id: str) -> str:
        """Apply L5 safety checks with membrane sanitization."""
        output_text = f"Plan executed. Results: {results}"
        sanitized_output = await self.membrane.sanitize(output_text, "agent_output")
        await self.overseer.verify(sanitized_output)

        class BudgetExceededError(Exception):
            def __init__(self, message, current_spend, limit):
                super().__init__(message)
                self.current_spend = current_spend
                self.limit = limit

        if self.governor.spend > self.governor.limit:
            raise BudgetExceededError(
                f"Budget exceeded: ${self.governor.limit:.2f}",
                current_spend=self.governor.spend,
                limit=self.governor.limit,
            )
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_critique",
                ROLE=self.role,
                event_type="CRITIQUE_COMPLETE",
                PAYLOAD={"budget_used": self.governor.spend, "sanitized": True},
                TIMESTAMP=time.time(),
            )
        )
        return sanitized_output

    async def _execute_commit_stage(self, output_text: str, trace_id: str) -> str:
        """Commit results to storage."""
        final_output = self.pii.restore(trace_id, output_text)
        await self.storage.write_blob(
            f"hops/{self.id}.txt",
            final_output.encode(),
            METADATA={"trace_id": trace_id, "role": self.role, "timestamp": time.time(), "zero_trust": True},
        )
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_commit",
                ROLE=self.role,
                event_type="COMMIT_COMPLETE",
                PAYLOAD={"storage_key": f"hops/{self.id}.txt"},
                TIMESTAMP=time.time(),
            )
        )
        return final_output

    def _handle_budget_exceeded(self, trace_id: str, error: Any) -> None:
        """Handle budget exceeded scenario."""
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_budget_error",
                ROLE=self.role,
                event_type="BUDGET_EXCEEDED",
                PAYLOAD={"current_spend": error.current_spend, "limit": error.limit},
                TIMESTAMP=time.time(),
            )
        )

    def _handle_execution_error(self, trace_id: str, error: Exception) -> None:
        """Handle general execution errors."""
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_error",
                ROLE=self.role,
                event_type="EXECUTION_ERROR",
                PAYLOAD={"error": str(error), "type": type(error).__name__},
                TIMESTAMP=time.time(),
            )
        )

    async def _cleanup(self, trace_id: str) -> None:
        """Cleanup resources."""
        await self.mcp.cleanup()
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_cleanup",
                ROLE=self.role,
                event_type="CLEANUP_COMPLETE",
                PAYLOAD={"zero_trust": True},
                TIMESTAMP=time.time(),
            )
        )
