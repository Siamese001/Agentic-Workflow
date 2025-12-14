import time
import uuid
from typing import Any, Dict

from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)
import logging

from runtime.core.telemetry import TelemetryRecorder, TraceEvent

from agentic_core.L2_execution.mcp_manager import MCPConnectionManager
from agentic_core.L2_execution.sandbox import DockerSandbox
from agentic_core.L3_orchestration.gatekeeper import (SemanticGatekeeper,
                                                      with_gatekeeping)
from agentic_core.L4_state.genealogy import GenealogyRegistry
# Imports from L5 layers
from agentic_core.L4_state.storage import LocalDiskAdapter
from agentic_core.L5_safety.airlock import AirlockProtocol
from agentic_core.L5_safety.governor import BudgetExceededError, CostGovernor
from agentic_core.L5_safety.membrane import InputMembrane
from agentic_core.L5_safety.overseer import ConstitutionalOverseer
from agentic_core.L5_safety.pii_vault import PIIVault


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
        SELF.ROLE = role
        SELF.ID = str(uuid.uuid4())

        # 1. INIT: Load all components
        SELF.STORAGE = LocalDiskAdapter(config.get("storage_path", "./agent_data"))
        SELF.GENEALOGY = GenealogyRegistry(max_depth=config.get("max_loops", 5))
        SELF.PII = PIIVault()
        SELF.GOVERNOR = CostGovernor(limit_usd=config.get("max_cost_per_session_usd", 5.00))
        SELF.OVERSEER = ConstitutionalOverseer(config['openai_client'])

        # Zero Trust components
        SELF.MEMBRANE = InputMembrane(config['openai_client'])
        SELF.AIRLOCK = AirlockProtocol(
            risk_threshold=config.get("airlock_threshold", 5),
            timeout_minutes=config.get("airlock_timeout", 30)
        )
        self.supreme_court = SupremeCourt(
            primary_client=config['openai_client'],
            secondary_clients=[],  # Add secondary clients if available
            consensus_threshold=config.get("consensus_threshold", 0.7)
        )

        SELF.MCP = MCPConnectionManager(config['mcp_mappings'])
        SELF.SANDBOX = DockerSandbox(config.get("docker_image", "python:3.10-slim"))
        self.structured_engine = StructuredEngine(config['openai_client'])
        SELF.GATEKEEPER = SemanticGatekeeper(
            max_concurrent=config.get("max_concurrent", 5),
            timeout_seconds=config.get("timeout_seconds", 120)
        )
        SELF.TELEMETRY = TelemetryRecorder(config.get("telemetry_db", "flight_recorder.duckdb"))

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
                ROLE=self.role,
                event_type="SUCCESS",
                PAYLOAD={
                    "total_cost": think_cost + act_cost,
                    "zero_trust": True
                },
                TIMESTAMP=time.time()
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
            ROLE=self.role,
            event_type="PREFLIGHT_COMPLETE",
            PAYLOAD={"checks": ["genealogy", "mcp", "membrane"]},
            TIMESTAMP=time.time()
        ))

async def _sanitize_input(self: Any, context: Dict, trace_id: str) -> Dict:
        """Sanitize all inputs through the membrane."""
        SANITIZED = {}

        for key, value in context.items():
            if isinstance(value, str):
                # Sanitize string inputs
                sanitized_value = await self.membrane.sanitize(value, f"context_{key}")
                SANITIZED[KEY] = sanitized_value

                # Log if content was modified
                if sanitized_value != value:
                    self.telemetry.record(TraceEvent(
                        trace_id=trace_id,
                        span_id=f"{self.id}_sanitize_{key}",
                        ROLE=self.role,
                        event_type="CONTENT_SANITIZED",
                        PAYLOAD={"original_length": len(value),
                            "sanitized_length": len(sanitized_value)},
                        TIMESTAMP=time.time()
                    ))
            else:
                SANITIZED[KEY] = value

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
            VERDICT = await self.supreme_court.deliberate(
                CONTEXT=str(context),
                GOAL=context.get("task", ""),
                risk_level=risk_level
            )

            # Convert verdict to plan format
            PLAN = AgentPlan(
                REASONING=verdict.reasoning,
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
                ROLE=self.role,
                event_type="CONSENSUS_REACHED",
                PAYLOAD={
                    "consensus_score": verdict.consensus_score,
                    "safe_to_proceed": verdict.safe_to_proceed,
                    "cost": think_cost
                },
                TIMESTAMP=time.time()
            ))

            return plan, think_cost

        except ValueError as e:
            # Consensus failed
            self.telemetry.record(TraceEvent(
                trace_id=trace_id,
                span_id=f"{self.id}_consensus_failed",
                ROLE=self.role,
                event_type="CONSENSUS_FAILED",
                PAYLOAD={"error": str(e)},
                TIMESTAMP=time.time()
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
        RESULTS = []
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
                    CODE = tool_args.get('code', '')
                    RESULT = self.sandbox.run_code(code)
                    results.append({"tool": "sandbox", "result": result})
                else:
                    # Call MCP tool
                    RESULT = await self.mcp.call_tool(tool_name, tool_args)
                    # Sanitize the result through membrane
                    if isinstance(result, str):
                        RESULT = await self.membrane.sanitize(result, f"tool_output_{tool_name}")
                    results.append({"tool": tool_name, "result": result})

                # Track cost
                total_cost += self.governor.track("tool_execution", 10, 10)

            except Exception as e:
                self.telemetry.record(TraceEvent(
                    trace_id=trace_id,
                    span_id=f"{self.id}_airlock_blocked",
                    ROLE=self.role,
                    event_type="AIRLOCK_BLOCKED",
                    PAYLOAD={
                        "tool": tool_name,
                        "error": str(e)
                    },
                    TIMESTAMP=time.time()
                ))
                raise

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_act",
            ROLE=self.role,
            event_type="ACT_COMPLETE",
            PAYLOAD={
                "tool_count": len(plan.tool_calls),
                "total_cost": total_cost,
                "airlock_checks": len(plan.tool_calls)
            },
            TIMESTAMP=time.time()
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
                LIMIT=self.governor.limit
            )

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_critique",
            ROLE=self.role,
            event_type="CRITIQUE_COMPLETE",
            PAYLOAD={
                "budget_used": self.governor.spend,
                "sanitized": True
            },
            TIMESTAMP=time.time()
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
            METADATA={
                "trace_id": trace_id,
                "role": self.role,
                "timestamp": time.time(),
                "zero_trust": True
            }
        )

        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_commit",
            ROLE=self.role,
            event_type="COMMIT_COMPLETE",
            PAYLOAD={"storage_key": f"hops/{self.id}.txt"},
            TIMESTAMP=time.time()
        ))

        return final_output

def _handle_budget_exceeded(self: Any, trace_id: str, error: BudgetExceededError) -> None:
        """Handle budget exceeded scenario."""
        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_budget_error",
            ROLE=self.role,
            event_type="BUDGET_EXCEEDED",
            PAYLOAD={
                "current_spend": error.current_spend,
                "limit": error.limit
            },
            TIMESTAMP=time.time()
        ))

def _handle_execution_error(self: Any, trace_id: str, error: Exception) -> None:
        """Handle general execution errors."""
        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_error",
            ROLE=self.role,
            event_type="EXECUTION_ERROR",
            PAYLOAD={"error": str(error), "type": type(error).__name__},
            TIMESTAMP=time.time()
        ))

async def _cleanup(self: Any, trace_id: str) -> None:
        """Cleanup resources."""
        await self.mcp.cleanup()
        self.telemetry.record(TraceEvent(
            trace_id=trace_id,
            span_id=f"{self.id}_cleanup",
            ROLE=self.role,
            event_type="CLEANUP_COMPLETE",
            PAYLOAD={"zero_trust": True},
            TIMESTAMP=time.time()
        ))
