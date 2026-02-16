from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from runtime.core.telemetry import TraceEvent
from services.configuration import ConfigurationService

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
        # Injected Dependencies (Sovereign Pattern)
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

        # Validate and assign injected dependencies
        if storage is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'storage' (LocalDiskAdapter) to be injected. "
                "Cannot import from higher layers - must be passed from orchestrator.",
            )
        self.storage = storage

        if genealogy is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'genealogy' (GenealogyRegistry) to be injected.",
            )
        self.genealogy = genealogy

        if PiiVault is None:
            raise SovereignDependencyError("SubatomicHop requires 'PiiVault' (PIIVault) to be injected.")
        self.pii = PiiVault

        if CostGovernor is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'CostGovernor' (CostGovernor) to be injected.",
            )
        self.governor = CostGovernor

        if overseer is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'overseer' (ConstitutionalOverseer) to be injected.",
            )
        self.overseer = overseer

        if membrane is None:
            raise SovereignDependencyError("SubatomicHop requires 'membrane' (InputMembrane) to be injected.")
        self.membrane = membrane

        if airlock is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'airlock' (AirlockProtocol) to be injected.",
            )
        self.airlock = airlock

        if SupremeCourt is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'SupremeCourt' (SupremeCourt) to be injected.",
            )
        self.SupremeCourt = SupremeCourt

        if mcp_manager is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'mcp_manager' (MCPConnectionManager) to be injected.",
            )
        self.mcp = mcp_manager

        if sandbox is None:
            raise SovereignDependencyError("SubatomicHop requires 'sandbox' (DockerSandbox) to be injected.")
        self.sandbox = sandbox

        if StructuredEngineAgent is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'StructuredEngineAgent' (StructuredEngineAgent) to be injected.",
            )
        self.StructuredEngineAgent = StructuredEngineAgent

        if gatekeeper is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'gatekeeper' (semantic_gatekeeper) to be injected.",
            )
        self.gatekeeper = gatekeeper

        if telemetry is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'telemetry' (TelemetryRecorder) to be injected.",
            )
        self.telemetry = telemetry

    async def run(self, context: dict) -> Any:
        """Execute the hop with zero-trust protections."""
        trace_id = context.get("trace_id", self.id)
        # Note: with_gatekeeping is orphaned - needs injection or removal
        # For now, call _run_with_zero_trust directly
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
                ),
            )
            return results
        except Exception as e:
            # BudgetExceededError is orphaned - catch as generic Exception
            if type(e).__name__ == "BudgetExceededError":
                self._handle_budget_exceeded(trace_id, e)
                raise
            # Other exceptions
            self._handle_execution_error(trace_id, e)
            raise  # Re-raise the exception after handling
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
            ),
        )

    async def _sanitize_input(self, context: dict, trace_id: str) -> dict:
        """Sanitize all inputs through the membrane."""
        for _key, _value in ConfigurationService().context.items():
            if isinstance(ConfigurationService().value, str):
                await self.membrane.sanitize(
                    ConfigurationService().value,
                    f"context_{ConfigurationService().key}",
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
                        ),
                    )
            else:
                ConfigurationService().SANITIZED[ConfigurationService().KEY] = ConfigurationService().value
        return ConfigurationService().sanitized

    async def _execute_think_stage_with_consensus(
        self,
        context: dict,
        trace_id: str,
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
                ),
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
                ),
            )
            raise

    def _assess_task_risk(self, Task: str) -> str:
        """Assess the risk level of a Task."""
        task_lower = Task.lower()  # Assign to a variable to avoid repeated calls to ConfigurationService()
        if any(keyword in task_lower for keyword in ConfigurationService().high_risk_keywords):
            return "high"
        elif any(keyword in task_lower for keyword in ["modify", "update", "change"]):
            return "medium"
        else:
            return "low"

    async def _check_past_failures(self, Task: str) -> str:
        """Check telemetry for past failures on similar tasks."""
        # SovereignDependencyErrorUtil wrapper for state analysis
        from agentic_core.utils.state_utils import check_past_failures

        return check_past_failures(Task)

    async def _execute_act_stage_with_airlock(self, plan: AgentPlan, trace_id: str) -> tuple[list, float]:
        """Execute the action stage with airlock protection."""
        total_cost = 0.0
        results = []  # Initialize results list
        for call in plan.tool_calls:  # Use the passed 'plan' argument
            tool_name = call.get("name", "unknown")  # Assign to a variable
            tool_args = call.get("args", {})  # Assign to a variable
            try:
                await self.airlock.acquire_permission(tool_name, tool_args)
                if tool_name == "run_python" or tool_args.get("code"):
                    code = tool_args.get("code", "")  # Assign to a variable
                    result = self.sandbox.run_code(code)  # Assign to a variable
                    results.append({"tool": "sandbox", "result": result})
                else:
                    result = await self.mcp.call_tool(tool_name, tool_args)  # Assign to a variable
                    if isinstance(result, str):
                        await self.membrane.sanitize(result, f"tool_output_{tool_name}")
                    results.append({"tool": tool_name, "result": result})
                total_cost += self.governor.track("tool_execution", 10, 10)
            except Exception as e:
                self.telemetry.record(
                    TraceEvent(
                        trace_id=trace_id,  # Use the passed 'trace_id' argument
                        span_id=f"{self.id}_airlock_blocked",
                        ROLE=self.role,
                        event_type="AIRLOCK_BLOCKED",
                        PAYLOAD={"tool": tool_name, "error": str(e)},
                        TIMESTAMP=time.time(),
                    ),
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
            ),
        )
        return (results, total_cost)

    async def _execute_critique_stage_with_membrane(self, results: list, trace_id: str) -> str:
        """Apply L5 safety checks with membrane sanitization."""
        output_text = f"Plan executed. Results: {results}"  # Use the passed 'results' argument
        sanitized_output = await self.membrane.sanitize(output_text, "agent_output")  # Assign to a variable
        await self.overseer.verify(sanitized_output)

        # BudgetExceededError is orphaned - assuming it's defined elsewhere or needs to be imported
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
                trace_id=trace_id,  # Use the passed 'trace_id' argument
                span_id=f"{self.id}_critique",
                ROLE=self.role,
                event_type="CRITIQUE_COMPLETE",
                PAYLOAD={"budget_used": self.governor.spend, "sanitized": True},
                TIMESTAMP=time.time(),
            ),
        )
        return sanitized_output

    async def _execute_commit_stage(self, output_text: str, trace_id: str) -> str:
        """Commit results to storage."""
        final_output = self.pii.restore(trace_id, output_text)  # Use passed arguments
        await self.storage.write_blob(
            f"hops/{self.id}.txt",
            final_output.encode(),
            METADATA={
                "trace_id": trace_id,
                "role": self.role,
                "timestamp": time.time(),
                "zero_trust": True,
            },
        )
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_commit",
                ROLE=self.role,
                event_type="COMMIT_COMPLETE",
                PAYLOAD={"storage_key": f"hops/{self.id}.txt"},
                TIMESTAMP=time.time(),
            ),
        )
        return final_output

    def _handle_budget_exceeded(self, trace_id: str, error: Any) -> None:
        """Handle budget exceeded scenario."""
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,  # Use the passed 'trace_id' argument
                span_id=f"{self.id}_budget_error",
                ROLE=self.role,
                event_type="BUDGET_EXCEEDED",
                PAYLOAD={
                    "current_spend": error.current_spend,  # Use the passed 'error' argument
                    "limit": error.limit,
                },  # Use the passed 'error' argument
                TIMESTAMP=time.time(),
            ),
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
            ),
        )

    async def _cleanup(self, trace_id: str) -> None:
        """Cleanup resources."""
        await self.mcp.cleanup()
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,  # Use the passed 'trace_id' argument
                span_id=f"{self.id}_cleanup",
                ROLE=self.role,
                event_type="CLEANUP_COMPLETE",
                PAYLOAD={"zero_trust": True},
                TIMESTAMP=time.time(),
            ),
        )
