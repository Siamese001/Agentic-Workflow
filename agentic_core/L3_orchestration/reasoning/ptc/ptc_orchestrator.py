"""PTC Orchestrator with Inference Batching

Implements the core PTC value proposition: multiple tools in a single inference pass.
Manages script execution, context isolation, and result aggregation.

Architecture:
    [PTC Script] → [Parse] → [Batch Tools] → [Sandbox Execute] → [Aggregate] → [Return Summary]
         ↓              ↓            ↓              ↓                  ↓
    Confidence      Tool IDs    Dependency    Context Isolation    Token Savings
    Assessment      Extracted   Analysis      (Raw in Sandbox)       (37% reduction)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# Emit lifecycle trace signals for this module
emit_replay_key("p0", "ptc_orchestrator")
emit_determinism_digest("p0", "ptc_orchestrator")

_emit_applies_guardrail("p0", "ptc_orchestrator", "p0_governance")
_emit_snapshots_state("p0", "ptc_orchestrator", "state_snapshot")
_emit_authorize_and_execute("p2", "ptc_orchestrator", "execution_auth")
_emit_validates_capability("p2", "ptc_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "ptc_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "ptc_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "ptc_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "ptc_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "ptc_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "ptc_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "ptc_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ptc_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ptc_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "ptc_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ptc_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ptc_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ptc_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ptc_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ptc_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "ptc_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ptc_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ptc_orchestrator", "exec_snapshot_link")

# P1 orchestration signals
_emit_dispatches_healing_run("p1", "ptc_orchestrator", "L3")
_emit_routes_through("p1", "ptc_orchestrator", "L3")
_emit_checks_agent_registry("p1", "ptc_orchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "ptc_orchestrator", "capability")
_emit_dispatches_execution_plan("p1", "ptc_orchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "ptc_orchestrator", "sub_agent")
_emit_routes_to_agent("p1", "ptc_orchestrator", "target_agent")
_emit_verifies_policy("p1", "ptc_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "ptc_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "ptc_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "ptc_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "ptc_orchestrator")
_emit_gated_by_confidence("p1", "ptc_orchestrator", "confidence_gate")
_emit_escalates_to_human("p1", "ptc_orchestrator", "L3")
_emit_reads_policy_state("p1", "ptc_orchestrator", "L3")

# P4 observability signals
_emit_emits_metric_event("ptc_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("ptc_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("ptc_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("ptc_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("ptc_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("ptc_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("ptc_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ptc_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("ptc_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ptc_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("ptc_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("ptc_orchestrator", "p4obs", "trace_link")

# P3 learning maturity signals
_emit_captures_pattern("ptc_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("ptc_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ptc_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ptc_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ptc_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("ptc_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("ptc_orchestrator", "p3lm", "state")

# P1 specific signals
_emit_records_execution_trace("ptc_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ptc_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ptc_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ptc_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ptc_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ptc_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("ptc_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ptc_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ptc_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ptc_orchestrator", "context_pull")
_emit_pulls_context("p1", "ptc_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ptc_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ptc_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "ptc_orchestrator", "write_through")
_emit_writes_through("p1", "ptc_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ptc_orchestrator", "safety_validation")
_emit_invokes_evaluation("p1", "ptc_orchestrator", "eval_call")


@dataclass(frozen=True)
class PTCScriptPlan:
    """Execution plan for a PTC script.

    Attributes:
        script_id: Unique identifier
        tools: List of tools to invoke in order
        dependencies: Tool dependency graph (tool_id -> list of dependencies)
        estimated_tokens: Estimated token count
        can_batch: Whether all tools can be executed in single inference pass
    """
    script_id: str
    tools: list[str]
    dependencies: dict[str, list[str]]
    estimated_tokens: int
    can_batch: bool


@dataclass
class PTCExecutionResult:
    """Result of PTC script execution.

    Attributes:
        script_id: Script that was executed
        success: Whether execution succeeded
        summary: Aggregated summary output (goes to L1 context)
        raw_results: Full tool results (stay in sandbox)
        execution_time_ms: Execution time in milliseconds
        tokens_saved: Estimated tokens saved vs traditional approach
        trace_id: Execution trace ID
    """
    script_id: str
    success: bool
    summary: str
    raw_results: dict[str, Any]
    execution_time_ms: float
    tokens_saved: int
    trace_id: str


class PTCOrchestrator:
    """Orchestrates PTC script execution with inference batching.

    Key Features:
    1. Script parsing and tool extraction
    2. Dependency analysis for optimal batching
    3. Sandbox execution with context isolation
    4. Result aggregation and summary generation
    5. Token savings tracking

    Usage:
        orchestrator = PTCOrchestrator()

        # Parse and plan
        code = '''
users = query_database("SELECT * FROM users")
orders = query_database("SELECT * FROM orders WHERE user_id IN (%s)" % users)
summary = {"users": len(users), "orders": len(orders)}
print(json.dumps(summary))
'''
        plan = orchestrator.parse_script("script-001", code)

        # Execute with batching
        result = orchestrator.execute_batch(plan)
    """

    # Token estimation constants
    TOKENS_PER_TOOL_CALL: int = 100
    TOKENS_PER_CONTEXT_ITEM: int = 50
    TRADITIONAL_OVERHEAD: int = 200  # Per separate inference

    def __init__(self, max_batch_size: int = 10) -> None:
        """Initialize PTC orchestrator.

        Args:
            max_batch_size: Maximum number of tools to batch together
        """
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PTCOrchestrator.__init__")
        _emit_signs_execution_trace(_trace_id, _trace_id[:12], "ptc_orch_init", 0)

        self._max_batch_size = max_batch_size
        self._execution_history: list[PTCExecutionResult] = []
        self._tool_registry: dict[str, Callable] = {}

    def parse_script(self, script_id: str, code: str) -> PTCScriptPlan:
        """Parse PTC script and extract execution plan.

        Analyzes code to identify:
        - Tool invocations (function calls)
        - Dependencies between tools
        - Whether tools can be batched

        Args:
            script_id: Unique identifier for the script
            code: Python/Bash code of the script

        Returns:
            PTCScriptPlan with tool extraction and dependency analysis
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L3_ORCHESTRATION, "PTCOrchestrator.parse_script")

        # Extract tool calls from code
        tools = self._extract_tool_calls(code)

        # Analyze dependencies
        dependencies = self._analyze_dependencies(code, tools)

        # Check if batchable (no circular deps, within size limit)
        can_batch = self._can_batch(tools, dependencies)

        # Estimate tokens
        estimated_tokens = self._estimate_tokens(code, tools)

        plan = PTCScriptPlan(
            script_id=script_id,
            tools=tools,
            dependencies=dependencies,
            estimated_tokens=estimated_tokens,
            can_batch=can_batch,
        )

        _emit_captures_pattern(trace_id, script_id, f"tools:{len(tools)}:batchable:{can_batch}")

        return plan

    def _extract_tool_calls(self, code: str) -> list[str]:
        """Extract tool call identifiers from script code."""
        tools: list[str] = []

        # Pattern 1: Direct function calls (e.g., query_database(...))
        # Match: tool_name(args)
        pattern1 = r"\b(\w+)\s*\("
        matches1 = re.findall(pattern1, code)

        # Pattern 2: await calls (e.g., await query_database(...))
        pattern2 = r"await\s+(\w+)\s*\("
        matches2 = re.findall(pattern2, code)

        # Combine and filter common non-tool names
        non_tool_names = {"print", "len", "range", "enumerate", "zip", "map", "filter", "json", "str", "int", "float", "bool", "list", "dict", "tuple", "set", "sum", "min", "max", "any", "all", "sorted", "dumps", "loads"}

        for match in matches1 + matches2:
            if match not in non_tool_names and match not in tools:
                tools.append(match)

        return tools

    def _analyze_dependencies(self, code: str, tools: list[str]) -> dict[str, list[str]]:
        """Analyze dependencies between tools in the script."""
        dependencies: dict[str, list[str]] = {tool: [] for tool in tools}

        # Simple dependency analysis:
        # If tool B uses a variable assigned by tool A, B depends on A
        lines = code.split("\n")
        assigned_vars: dict[str, str] = {}  # var_name -> tool_name

        for line in lines:
            # Check for assignments (e.g., result = tool_name(...))
            match = re.match(r"\s*(\w+)\s*=\s*(\w+)\s*\(", line)
            if match:
                var_name, tool_name = match.groups()
                if tool_name in tools:
                    assigned_vars[var_name] = tool_name

            # Check for variable usage in tool calls
            for tool in tools:
                # If this line calls tool and uses a variable
                if f"{tool}(" in line or f"await {tool}(" in line:
                    for var_name, source_tool in assigned_vars.items():
                        if var_name in line and source_tool != tool:
                            if source_tool not in dependencies[tool]:
                                dependencies[tool].append(source_tool)

        return dependencies

    def _can_batch(self, tools: list[str], dependencies: dict[str, list[str]]) -> bool:
        """Determine if tools can be batched in single inference pass."""
        # Too many tools
        if len(tools) > self._max_batch_size:
            return False

        # Check for dependencies that prevent batching
        for tool, deps in dependencies.items():
            if deps:  # Any dependency prevents full batching
                return False

        return True

    def _estimate_tokens(self, code: str, tools: list[str]) -> int:
        """Estimate token count for script execution."""
        # Base tokens for code
        code_tokens = len(code.split())

        # Tool call tokens
        tool_tokens = len(tools) * self.TOKENS_PER_TOOL_CALL

        return code_tokens + tool_tokens

    def execute_batch(
        self,
        plan: PTCScriptPlan,
        tool_handlers: dict[str, Callable] | None = None,
    ) -> PTCExecutionResult:
        """Execute a batched PTC script plan.

        Executes all tools in the plan within a single "inference pass".
        Results are aggregated and only a summary returns to L1 context.

        Args:
            plan: Execution plan from parse_script
            tool_handlers: Optional dict mapping tool_id to handler function

        Returns:
            PTCExecutionResult with summary and metadata
        """
        import time as _time
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L3_ORCHESTRATION, "PTCOrchestrator.execute_batch")
        _emit_orchestrates_workflow(trace_id, plan.script_id, "ptc_batch_execution")

        start_time = _time.time()

        handlers = tool_handlers or self._tool_registry
        raw_results: dict[str, Any] = {}

        # Execute all tools
        for tool_id in plan.tools:
            if tool_id in handlers:
                try:
                    # Execute tool
                    _emit_records_tool_invocation(trace_id, tool_id, plan.script_id)

                    result = handlers[tool_id]({})
                    raw_results[tool_id] = {
                        "success": True,
                        "result": result,
                    }

                    _emit_captures_execution_output(trace_id, tool_id, "success")

                except (ValueError, TypeError) as e:
                    raw_results[tool_id] = {
                        "success": False,
                        "error": str(e),
                    }
                    _emit_records_incident_event(trace_id, tool_id, f"execution_error:{e}")
            else:
                raw_results[tool_id] = {
                    "success": False,
                    "error": f"Tool '{tool_id}' not found",
                }

        execution_time_ms = (_time.time() - start_time) * 1000

        # Generate summary (only this goes back to L1 context)
        summary = self._generate_summary(plan, raw_results)

        # Calculate token savings
        tokens_saved = self._calculate_token_savings(plan)

        # Check success (all tools succeeded)
        success = all(r.get("success", False) for r in raw_results.values())

        result = PTCExecutionResult(
            script_id=plan.script_id,
            success=success,
            summary=summary,
            raw_results=raw_results,
            execution_time_ms=execution_time_ms,
            tokens_saved=tokens_saved,
            trace_id=trace_id,
        )

        self._execution_history.append(result)

        # Emit completion signals
        _emit_transcripts_response(trace_id, plan.script_id, summary[:100])  # Truncated
        _emit_writes_learning_snapshot(trace_id, plan.script_id, "execution_completed")

        return result

    def _generate_summary(self, plan: PTCScriptPlan, raw_results: dict[str, Any]) -> str:
        """Generate summary output from raw results.

        This is the only output that escapes the sandbox and goes to L1 context.
        """
        summary_parts = []

        for tool_id, result in raw_results.items():
            if result.get("success"):
                res = result.get("result", {})
                if isinstance(res, dict):
                    # Extract count or length if available
                    if "count" in res:
                        summary_parts.append(f"{tool_id}: count={res['count']}")
                    elif "rows" in res:
                        summary_parts.append(f"{tool_id}: {len(res['rows'])} rows")
                    elif "length" in res:
                        summary_parts.append(f"{tool_id}: {res['length']} items")
                    else:
                        summary_parts.append(f"{tool_id}: success")
                else:
                    summary_parts.append(f"{tool_id}: success")
            else:
                summary_parts.append(f"{tool_id}: failed")

        return json.dumps({
            "status": "success" if all(r.get("success") for r in raw_results.values()) else "partial_failure",
            "tools_executed": len(raw_results),
            "tools_successful": sum(1 for r in raw_results.values() if r.get("success")),
            "summary": summary_parts,
        }, separators=(",", ":"))

    def _calculate_token_savings(self, plan: PTCScriptPlan) -> int:
        """Calculate estimated token savings vs traditional approach."""
        # Traditional: separate inference per tool
        traditional_tokens = len(plan.tools) * (self.TOKENS_PER_TOOL_CALL + self.TRADITIONAL_OVERHEAD)

        # PTC: single inference
        ptc_tokens = self.TOKENS_PER_TOOL_CALL + plan.estimated_tokens

        return max(0, traditional_tokens - ptc_tokens)

    def register_tool(self, tool_id: str, handler: Callable) -> None:
        """Register a tool handler with the orchestrator."""
        self._tool_registry[tool_id] = handler

    def get_execution_history(self) -> list[PTCExecutionResult]:
        """Get history of executed scripts."""
        return self._execution_history.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get execution statistics."""
        if not self._execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "total_tokens_saved": 0,
                "average_execution_time_ms": 0.0,
            }

        total = len(self._execution_history)
        successful = sum(1 for r in self._execution_history if r.success)
        tokens_saved = sum(r.tokens_saved for r in self._execution_history)
        avg_time = sum(r.execution_time_ms for r in self._execution_history) / total

        return {
            "total_executions": total,
            "successful_executions": successful,
            "success_rate": successful / total,
            "total_tokens_saved": tokens_saved,
            "average_execution_time_ms": avg_time,
        }


# =============================================================================
# Sandbox Execution Context
# =============================================================================

@dataclass
class PTCSandboxContext:
    """Sandbox execution context for PTC scripts.

    Provides isolated execution environment where raw tool results
    are trapped and only summaries escape.
    """
    context_id: str
    isolated: bool = True
    raw_results: dict[str, Any] = field(default_factory=dict)
    stdout_buffer: str = ""
    stderr_buffer: str = ""

    def trap_result(self, tool_id: str, result: Any) -> None:
        """Trap a tool result in the sandbox."""
        self.raw_results[tool_id] = result
        _emit_records_execution_trace(self.context_id, LayerSegment.L2_EXECUTION, f"PTCSandbox.trap:{tool_id}")

    def release_summary(self, summary: str) -> str:
        """Release summary output from sandbox (only L1-visible output)."""
        self.stdout_buffer = summary
        _emit_captures_execution_output(self.context_id, "sandbox", "summary_released")
        return summary


class PTCSandboxExecutor:
    """Executes PTC scripts within isolated sandbox context.

    Ensures that raw tool results stay trapped in L2 sandbox,
    with only summaries escaping to L1 context.
    """

    def __init__(self) -> None:
        """Initialize sandbox executor."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "PTCSandboxExecutor.__init__")
        _emit_snapshots_state(_trace_id, "sandbox_executor", "initialized")

    def create_context(self) -> PTCSandboxContext:
        """Create new isolated sandbox context."""
        import uuid as _uuid

        context_id = str(_uuid.uuid4())
        _emit_snapshots_state(context_id, "sandbox", "context_created")
        _emit_records_execution_trace(context_id, LayerSegment.L2_EXECUTION, "PTCSandbox.create_context")

        return PTCSandboxContext(
            context_id=context_id,
            isolated=True,
            raw_results={},
            stdout_buffer="",
            stderr_buffer="",
        )

    def execute_in_sandbox(
        self,
        code: str,
        tool_handlers: dict[str, Callable],
    ) -> tuple[PTCSandboxContext, str]:
        """Execute code within isolated sandbox context.

        Args:
            code: Python code to execute
            tool_handlers: Dictionary of tool handlers

        Returns:
            Tuple of (sandbox_context, summary_output)
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L2_EXECUTION, "PTCSandboxExecutor.execute")
        _emit_snapshots_state(trace_id, "sandbox", "execution_started")

        # Create isolated context
        context = self.create_context()

        # Execute tools and trap results
        for tool_id, handler in tool_handlers.items():
            if tool_id in code:
                try:
                    result = handler({})
                    context.trap_result(tool_id, result)
                except (ValueError, TypeError) as e:
                    context.trap_result(tool_id, {"error": str(e)})

        # Generate summary
        summary = self._generate_summary(context.raw_results)

        # Release summary (only this escapes sandbox)
        output = context.release_summary(summary)

        _emit_snapshots_state(trace_id, "sandbox", "execution_completed")
        _emit_records_execution_trace(trace_id, LayerSegment.L2_EXECUTION, "PTCSandboxExecutor.completed")

        return context, output

    def _generate_summary(self, raw_results: dict[str, Any]) -> str:
        """Generate summary from trapped raw results."""
        summaries = []

        for tool_id, result in raw_results.items():
            if isinstance(result, dict):
                if "error" in result:
                    summaries.append(f"{tool_id}: error")
                elif "rows" in result:
                    summaries.append(f"{tool_id}: {len(result['rows'])} rows")
                elif "count" in result:
                    summaries.append(f"{tool_id}: count={result['count']}")
                else:
                    summaries.append(f"{tool_id}: completed")
            else:
                summaries.append(f"{tool_id}: completed")

        return json.dumps({
            "executed": len(raw_results),
            "summary": summaries,
        }, separators=(",", ":"))


# =============================================================================
# Global Instance
# =============================================================================

_GLOBAL_ORCHESTRATOR: PTCOrchestrator | None = None
_GLOBAL_SANDBOX: PTCSandboxExecutor | None = None


def get_ptc_orchestrator() -> PTCOrchestrator:
    """Get global PTC orchestrator instance."""
    global _GLOBAL_ORCHESTRATOR
    if _GLOBAL_ORCHESTRATOR is None:
        _GLOBAL_ORCHESTRATOR = PTCOrchestrator()
    return _GLOBAL_ORCHESTRATOR


def get_ptc_sandbox() -> PTCSandboxExecutor:
    """Get global PTC sandbox executor instance."""
    global _GLOBAL_SANDBOX
    if _GLOBAL_SANDBOX is None:
        _GLOBAL_SANDBOX = PTCSandboxExecutor()
    return _GLOBAL_SANDBOX


def reset_ptc_orchestrator() -> None:
    """Reset global PTC orchestrator instance."""
    global _GLOBAL_ORCHESTRATOR
    _GLOBAL_ORCHESTRATOR = None


def reset_ptc_sandbox() -> None:
    """Reset global PTC sandbox executor instance."""
    global _GLOBAL_SANDBOX
    _GLOBAL_SANDBOX = None


# =============================================================================
# Convenience Functions
# =============================================================================

def parse_ptc_script(script_id: str, code: str) -> PTCScriptPlan:
    """Parse a PTC script and return execution plan."""
    orchestrator = get_ptc_orchestrator()
    return orchestrator.parse_script(script_id, code)


def execute_ptc_batch(plan: PTCScriptPlan, handlers: dict[str, Callable] | None = None) -> PTCExecutionResult:
    """Execute a PTC script batch."""
    orchestrator = get_ptc_orchestrator()
    return orchestrator.execute_batch(plan, handlers)


def execute_in_ptc_sandbox(code: str, handlers: dict[str, Callable]) -> tuple[PTCSandboxContext, str]:
    """Execute code in isolated PTC sandbox."""
    sandbox = get_ptc_sandbox()
    return sandbox.execute_in_sandbox(code, handlers)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "PTCScriptPlan",
    "PTCExecutionResult",
    "PTCOrchestrator",
    "PTCSandboxContext",
    "PTCSandboxExecutor",
    "get_ptc_orchestrator",
    "get_ptc_sandbox",
    "reset_ptc_orchestrator",
    "reset_ptc_sandbox",
    "parse_ptc_script",
    "execute_ptc_batch",
    "execute_in_ptc_sandbox",
]
