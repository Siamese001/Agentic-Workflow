import time
import uuid
from typing import Dict, Any
from pydantic import BaseModel


logger = logging.getLogger(__name__)
# Imports from L5 layers
from agentic_core.L4_state.storage import LocalDiskAdapter
from agentic_core.L4_state.genealogy import GenealogyRegistry
from agentic_core.L5_safety.pii_vault import PIIVault
from agentic_core.L5_safety.governor import CostGovernor, BudgetExceededError
from agentic_core.L5_safety.overseer import ConstitutionalOverseer
from agentic_core.L5_safety.membrane import InputMembrane
from agentic_core.L5_safety.airlock import AirlockProtocol
from agentic_core.L2_execution.mcp_manager import MCPConnectionManager
from agentic_core.L2_execution.sandbox import DockerSandbox
from agentic_core.L3_orchestration.gatekeeper import SemanticGatekeeper, with_gatekeeping
from runtime.core.telemetry import TelemetryRecorder, TraceEvent
import logging

class AgentPlan(BaseModel):
    reasoning: str
    tool_calls: list[dict]

class SubatomicHop:
    """
    The Unified L5.5 Zero Trust Hop - Mission-Critical Cognitive Engine.

    Integrates all 5 layers plus Zero Trust protections:
    - L1: Cognition (Multi-model consensus)
    - L2: Execution (MCP tools + Sandbox + Airlock)
    - L3: Orchestration (Gatekeeper)
    - L4: State (Atomic storage + Genealogy)
    - L5: Safety (PII + Cost + Constitution + Membrane)
    """

def __init__(self: Any, role: str, config: Dict) -> None:
        self.role = role
        self.id = str(uuid.uuid4())

        # 1. INIT: Load all components
        self.storage = LocalDiskAdapter(config.get("storage_path", "./agent_data"))
        self.genealogy = GenealogyRegistry(max_depth=config.get("max_loops", 5))
        self.pii = PIIVault()
        self.governor = CostGovernor(limit_usd=config.get("max_cost_per_session_usd", 5.00))
        self.overseer = ConstitutionalOverseer(config['openai_client'])

        # Zero Trust components
        self.membrane = InputMembrane(config['openai_client'])
        self.airlock = AirlockProtocol(
            risk_threshold=config.get("airlock_threshold", 5),
            timeout_minutes=config.get("airlock_timeout", 30)
        )
        self.supreme_court = SupremeCourt(
            primary_client=config['openai_client'],
            secondary_clients=[],  # Add secondary clients if available
            consensus_threshold=config.get("consensus_threshold", 0.7)
        )

        self.mcp = MCPConnectionManager(config['mcp_mappings'])
        self.sandbox = DockerSandbox(config.get("docker_image", "python:3.10-slim"))
        self.structured_engine = StructuredEngine(config['openai_client'])
        self.gatekeeper = SemanticGatekeeper(
            max_concurrent=config.get("max_concurrent", 5),
            timeout_seconds=config.get("timeout_seconds", 120)
        )
        self.telemetry = TelemetryRecorder(config.get("telemetry_db", "flight_recorder.duckdb"))

async def run(self: Any, context: Dict) -> Any:
        """
        Execute the hardened hop with full L5.5 Zero Trust protection.

        Args:
            context: Input context containing task and parameters

        Returns:
            Processed output with all safety checks applied
        """
        trace_id = context.get('trace_id', self.id)

        return await with_gatekeeping(
            trace_id,
            f"SubatomicHop.run({self.role})",
            self._run_with_zero_trust(context, trace_id)
        )

async def _run_with_zero_trust(self: Any, context: Dict, trace_id: str) -> Any:
        """Internal method with all L5.5 Zero Trust protections applied."""
        try:
            # 2. PRE-FLIGHT
            await self._preflight_checks(context, trace_id)

            # 3. THINK (L1) - with Supreme Court consensus
            plan, think_cost = await self._execute_think_stage_with_consensus(context, trace_id)

            # 4. ACT (L2) - with Airlock protection
            results, act_cost = await self._execute_act_stage_with_airlock(plan, trace_id)

            # 5. CRITIQUE (L5) - with Membrane sanitization
            validated_output = await self._execute_critique_stage_with_membrane(results, trace_id)

            # 6. COMMIT (L4)
            final_output = await self._execute_commit_stage(validated_output, trace_id)

            # Record success
            self.telemetry.record(TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_complete",
                role=self.role,
                event_type="SUCCESS",
                payload={
                    "total_cost": think_cost + act_cost,
                    "zero_trust": True
                },
                timestamp=time.time()
            ))

            return final_output

        except BudgetExceededError as e:
            self._handle_budget_exceeded(trace_id, e)
            raise
        except Exception as e:
            self._handle_execution_error(trace_id, e)
            raise
        finally:
            await self._cleanup(trace_id)

async def _preflight_checks(self: Any, context: Dict, trace_id: str) -> None:
        """Pre-flight validation and setup."""
        # Check genealogy (am I in a loop?)
        context_hash = str(hash(str(context)))
        self.genealogy.register_attempt(trace_id, str(context.get("task", "")), context_hash)

        # Connect MCP tools
        await self.mcp.connect(self.role)

        # Sanitize input through membrane
        sanitized_context = await self._sanitize_input(context, trace_id)
        context.update(sanitized_context)

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_preflight",
            role=self.role,
            event_type="PREFLIGHT_COMPLETE",
            payload={"checks": ["genealogy", "mcp", "membrane"]},
            timestamp=time.time()
        ))

async def _sanitize_input(self: Any, context: Dict, trace_id: str) -> Dict:
        """Sanitize all inputs through the membrane."""
        sanitized = {}

        for key, value in context.items():
            if isinstance(value, str):
                # Sanitize string inputs
                sanitized_value = await self.membrane.sanitize(value, f"context_{key}")
                sanitized[key] = sanitized_value

                # Log if content was modified
                if sanitized_value != value:
                    self.telemetry.record(TraceEvent(
                        trace_id=trace_id,
                        span_id=f"{self.id}_sanitize_{key}",
                        role=self.role,
                        event_type="CONTENT_SANITIZED",
                        payload={"original_length": len(value),
                            "sanitized_length": len(sanitized_value)},
                        timestamp=time.time()
                    ))
            else:
                sanitized[key] = value

        return sanitized

async def _execute_think_stage_with_consensus(self: Any,
     context: Dict,
     trace_id: str) -> tuple[AgentPlan,
     float]:
        float]:
        """Execute the thinking stage with multi-model consensus."""
        # Determine risk level for consensus
        risk_level = self._assess_task_risk(context.get("task", ""))

        # Query telemetry to see if we failed this before
        similar_failures = await self._check_past_failures(context.get("task", ""))

        # Generate consensus decision
        try:
            verdict = await self.supreme_court.deliberate(
                context=str(context),
                goal=context.get("task", ""),
                risk_level=risk_level
            )

            # Convert verdict to plan format
            plan = AgentPlan(
                reasoning=verdict.reasoning,
                tool_calls=[{
                    "name": "execute_plan",
                    "args": {"plan": verdict.chosen_plan}
                }]
            )

            # Track cost
            think_cost = self.governor.track("gpt-4", 300, 150)  # Higher cost for consensus

            self.telemetry.record(TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_consensus",
                role=self.role,
                event_type="CONSENSUS_REACHED",
                payload={
                    "consensus_score": verdict.consensus_score,
                    "safe_to_proceed": verdict.safe_to_proceed,
                    "cost": think_cost
                },
                timestamp=time.time()
            ))

            return plan, think_cost

        except ValueError as e:
            # Consensus failed
            self.telemetry.record(TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_consensus_failed",
                role=self.role,
                event_type="CONSENSUS_FAILED",
                payload={"error": str(e)},
                timestamp=time.time()
            ))
            raise

def _assess_task_risk(self: Any, task: str) -> str:
        """Assess the risk level of a task."""
        high_risk_keywords = [
            "delete", "remove", "destroy", "push", "deploy", "execute",
            "transfer", "send", "email", "payment", "purchase", "install"
        ]

        task_lower = task.lower()
        if any(keyword in task_lower for keyword in high_risk_keywords):
            return "high"
        elif any(keyword in task_lower for keyword in ["modify", "update", "change"]):
            return "medium"
        else:
            return "low"

async def _check_past_failures(self: Any, task: str) -> str:
        """Check telemetry for past failures on similar tasks."""
        try:
            # This would query telemetry via MCP
            # For now, return placeholder
            return "No similar failures found"
        except Exception:
            return "Unable to check past failures"

async def _execute_act_stage_with_airlock(self: Any,
     plan: AgentPlan,
     trace_id: str) -> tuple[list,
     float]:
        float]:
        """Execute the action stage with airlock protection."""
        results = []
        total_cost = 0.0

        for call in plan.tool_calls:
            tool_name = call.get('name', 'unknown')
            tool_args = call.get('args', {})

            # Check airlock for high-risk tools
            try:
                await self.airlock.acquire_permission(tool_name, tool_args)

                # Execute the tool
                if tool_name == 'run_python' or tool_args.get('code'):
                    # Run in sandbox
                    code = tool_args.get('code', '')
                    result = self.sandbox.run_code(code)
                    results.append({"tool": "sandbox", "result": result})
                else:
                    # Call MCP tool
                    result = await self.mcp.call_tool(tool_name, tool_args)
                    # Sanitize the result through membrane
                    if isinstance(result, str):
                        result = await self.membrane.sanitize(result, f"tool_output_{tool_name}")
                    results.append({"tool": tool_name, "result": result})

                # Track cost
                total_cost += self.governor.track("tool_execution", 10, 10)

            except Exception as e:
                self.telemetry.record(TraceEvent(
                    trace_id=trace_id,
                    span_id=f"{self.id}_airlock_blocked",
                    role=self.role,
                    event_type="AIRLOCK_BLOCKED",
                    payload={
                        "tool": tool_name,
                        "error": str(e)
                    },
                    timestamp=time.time()
                ))
                raise

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_act",
            role=self.role,
            event_type="ACT_COMPLETE",
            payload={
                "tool_count": len(plan.tool_calls),
                "total_cost": total_cost,
                "airlock_checks": len(plan.tool_calls)
            },
            timestamp=time.time()
        ))

        return results, total_cost

async def _execute_critique_stage_with_membrane(self: Any, results: list, trace_id: str) -> str:
        """Apply L5 safety checks with membrane sanitization."""
        output_text = f"Plan executed. Results: {results}"

        # Sanitize output through membrane
        sanitized_output = await self.membrane.sanitize(output_text, "agent_output")

        # Constitutional validation
        await self.overseer.verify(sanitized_output)

        # Budget check
        if self.governor.spend > self.governor.limit:
            raise BudgetExceededError(
                f"Budget exceeded: ${self.governor.spend:.2f} > ${self.governor.limit:.2f}",
                current_spend=self.governor.spend,
                limit=self.governor.limit
            )

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_critique",
            role=self.role,
            event_type="CRITIQUE_COMPLETE",
            payload={
                "budget_used": self.governor.spend,
                "sanitized": True
            },
            timestamp=time.time()
        ))

        return sanitized_output

async def _execute_commit_stage(self: Any, output_text: str, trace_id: str) -> str:
        """Commit results to storage."""
        # Restore PII if needed
        final_output = self.pii.restore(trace_id, output_text)

        # Atomic write to storage
        await self.storage.write_blob(
            f"hops/{self.id}.txt",
            final_output.encode(),
            metadata={
                "trace_id": trace_id,
                "role": self.role,
                "timestamp": time.time(),
                "zero_trust": True
            }
        )

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_commit",
            role=self.role,
            event_type="COMMIT_COMPLETE",
            payload={"storage_key": f"hops/{self.id}.txt"},
            timestamp=time.time()
        ))

        return final_output

def _handle_budget_exceeded(self: Any, trace_id: str, error: BudgetExceededError) -> None:
        """Handle budget exceeded scenario."""
        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_budget_error",
            role=self.role,
            event_type="BUDGET_EXCEEDED",
            payload={
                "current_spend": error.current_spend,
                "limit": error.limit
            },
            timestamp=time.time()
        ))

def _handle_execution_error(self: Any, trace_id: str, error: Exception) -> None:
        """Handle general execution errors."""
        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_error",
            role=self.role,
            event_type="EXECUTION_ERROR",
            payload={"error": str(error), "type": type(error).__name__},
            timestamp=time.time()
        ))

async def _cleanup(self: Any, trace_id: str) -> None:
        """Cleanup resources."""
        await self.mcp.cleanup()
        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_cleanup",
            role=self.role,
            event_type="CLEANUP_COMPLETE",
            payload={"zero_trust": True},
            timestamp=time.time()
        ))
