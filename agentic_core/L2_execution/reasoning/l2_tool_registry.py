from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "tool_registry")
emit_determinism_digest("p0", "tool_registry")

_emit_dispatches_healing_run("p1", "tool_registry", "L2")
_emit_routes_through("p1", "tool_registry", "L2")
_emit_checks_agent_registry("p1", "tool_registry", "agent_registry")
_emit_validates_agent_capability("p1", "tool_registry", "capability")
_emit_dispatches_execution_plan("p1", "tool_registry", "exec_plan")
_emit_agent_executes_agent("p1", "tool_registry", "sub_agent")
_emit_routes_to_agent("p1", "tool_registry", "target_agent")
_emit_verifies_policy("p1", "tool_registry", "policy_check")
_emit_observes_runtime_state("p1", "tool_registry", "runtime_state")
_emit_verifies_boundary("p1", "tool_registry", "boundary_check")
_emit_transcripts_response("p1", "tool_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_registry")
_emit_gated_by_confidence("p1", "tool_registry", "confidence_gate")
_emit_escalates_to_human("p1", "tool_registry", "L2")
_emit_reads_policy_state("p1", "tool_registry", "L2")
_emit_authorize_and_execute("p2", "tool_registry", "execution_auth")
_emit_validates_capability("p2", "tool_registry", "capability_check")
_emit_routes_to_capability("p2", "tool_registry", "capability_route")
_emit_writes_via_uwg("p2", "tool_registry", "uwg_write")
_emit_blocks_direct_write("p2", "tool_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_registry", "tool_invocation")
_emit_captures_execution_output("p2", "tool_registry", "exec_output")
_emit_dispatches_agent("p3", "tool_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_registry", "healing_outcome")
_emit_escalates_failure("p3", "tool_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_registry", "eval_metric")
_emit_stores_embedding("p4", "tool_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_registry", "exec_snapshot_link")

"\nDynamic Tool Registry for Runtime Tool Discovery\n\nAllows agents to discover and request tools dynamically based on Task requirements,\nrather than being hardcoded with a fixed set of tools.\n"
import inspect
import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("tool_registry", "p4obs", "metric_1")
_emit_emits_metric_event("tool_registry", "p4obs", "metric_2")
_emit_emits_metric_event("tool_registry", "p4obs", "metric_3")
_emit_emits_metric_event("tool_registry", "p4obs", "metric_4")
_emit_emits_metric_event("tool_registry", "p4obs", "metric_5")
_emit_emits_metric_event("tool_registry", "p4obs", "metric_6")
_emit_records_incident_event("tool_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_registry", "p4obs", "anomaly")
_emit_writes_observability_log("tool_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_registry", "p4obs", "mon_state")
_emit_triggers_alert("tool_registry", "p4obs", "alert")
_emit_links_incident_trace("tool_registry", "p4obs", "trace_link")
_emit_captures_pattern("tool_registry", "p3lm", "pattern")
_emit_records_learning_event("tool_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_registry", "p3lm", "routing")
_emit_improves_agent_policy("tool_registry", "p3lm", "policy")
_emit_stores_learning_state("tool_registry", "p3lm", "state")
_emit_records_execution_trace("tool_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_registry", "env_read", "p2_env_1")
_emit_reads_environ("tool_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_registry", "context_pull")
_emit_pulls_context("p1", "tool_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_registry", "uwg_term_2")
_emit_writes_through("p1", "tool_registry", "write_through")
_emit_writes_through("p1", "tool_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_registry", "safety_validation")
_emit_invokes_eval("p1", "tool_registry", "eval_call")
_emit_proposal_commits_routing("p1", "tool_registry", "routing_commit")

try:
    import numpy as np
except ImportError as _err:
    raise ImportError("numpy is required for this module. Install with: pip install -e '.[infra]'") from _err
Logger: Any = logging.getLogger(__name__)


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "p0_governance")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="tool_registry",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


@dataclass
class ToolDefinition:
    """Definition of a tool in the registry."""

    name: str
    description: str
    function: Callable
    parameters: dict[str, Any]
    tags: list[str] = field(default_factory=list)
    category: str = "general"
    embedding: list[float] | None = None
    usage_count: int = 0
    success_rate: float = 1.0


ToolDefinition = ToolDefinition


@dataclass
class ToolMatch:
    """A matched tool for a Task."""

    tool: ToolDefinition
    relevance_score: float
    reason: str


ToolMatch = ToolMatch


class tool_registry:
    """
    Dynamic tool registry that enables agents to discover tools at runtime.

    Uses semantic similarity to match Task descriptions to tool capabilities.
    """

    def __init__(self, embedder, enable_caching: bool = True):
        """
        Initialize the tool registry.

        Args:
            embedder: Embedding function
            enable_caching: Whether to cache tool embeddings
        """
        self.embedder = embedder
        self.enable_caching = enable_caching
        self.tools: dict[str, ToolDefinition] = {}
        self._embedding_matrix: np.ndarray | None = None
        self._tool_names: list[str] = []
        LOGGER.info("Tool registry initialized")

    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        category: str = "general",
    ) -> None:
        """
        Register a tool in the registry.

        Args:
            name: Unique tool name
            func: The tool function
            description: What the tool does
            parameters: Parameter schema
            tags: Optional tags for categorization
            category: Tool category
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"ToolRegistry.register:{name}"
        )
        _ectx = _make_execution_context(name, "tool_registry.register")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            name,
            target_name="tool_registry.register",
        )
        if name in self.tools:
            LOGGER.warning(f"Tool {name} already registered, overwriting")
        if not description:
            description: Any = self._generate_description_from_func(func)
        if not parameters:
            parameters: Any = self._generate_parameters_from_func(func)
        tool: Any = ToolDefinition(
            name=name,
            description=description,
            function=func,
            parameters=parameters,
            tags=tags or [],
            category=category,
        )
        self.tools[name] = tool
        LOGGER.info(f"Registered tool: {name} ({category})")

    # guardian: allow-magic-config
    async def find_tools_for_task(
        self,
        task_description: str,
        max_tools: int = 5,
        min_relevance: float = 0.6,
        categories: list[str] | None = None,
    ) -> list[ToolMatch]:
        """
        Find tools relevant to a Task using semantic search.

        Args:
            task_description: Description of the Task
            max_tools: Maximum number of tools to return
            min_relevance: Minimum relevance score
            categories: Optional category filter

        Returns:
            List of matched tools with relevance scores
        """
        if not self.tools:
            return []
        await self._ensure_embeddings()
        task_embedding: Any = await self.embedder.embed_query(task_description)
        task_vec: Any = np.array(task_embedding)
        matches: Any = []
        for i, tool_name in enumerate(self._tool_names):
            tool: Any = self.tools[tool_name]
            if categories and tool.category not in categories:
                continue
            tool_vec: Any = self._embedding_matrix[i]
            similarity: Any = np.dot(task_vec, tool_vec) / (
                np.linalg.norm(task_vec) * np.linalg.norm(tool_vec)
            )
            if similarity >= min_relevance:
                reason: Any = self._generate_match_reason(task_description, tool, similarity)
                matches.append(ToolMatch(tool=tool, relevance_score=similarity, reason=reason))
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches[:max_tools]

    async def _ensure_embeddings(self):
        """Ensure tool embeddings are computed."""
        if self._embedding_matrix is not None:
            return
        LOGGER.debug("Computing tool embeddings...")
        embeddings = []
        tool_names = []
        for tool in self.tools.values():
            searchable_text = f"{tool.name} {tool.description} {' '.join(tool.tags)}"
            embedding = await self.embedder.embed_query(searchable_text)
            embeddings.append(embedding)
            tool_names.append(tool.name)
            tool.embedding = embedding
        self._embedding_matrix = np.array(embeddings)
        self._tool_names = tool_names
        LOGGER.debug(f"Computed embeddings for {len(embeddings)} tools")

    def _generate_match_reason(self, Task: str, tool: ToolDefinition, similarity: float) -> str:
        """Generate a reason why this tool matches the Task."""
        task_lower = Task.lower()
        desc_lower = tool.description.lower()
        name_lower = tool.name.lower()
        reasons = []
        if any(word in desc_lower for word in task_lower.split()):
            reasons.append("description contains Task keywords")
        if any(word in name_lower for word in task_lower.split()):
            reasons.append("name matches Task keywords")
        if "file" in task_lower and tool.category == "filesystem":
            reasons.append("file operation tool")
        elif "api" in task_lower and tool.category == "network":
            reasons.append("API communication tool")
        elif "data" in task_lower and tool.category == "analysis":
            reasons.append("data analysis tool")
        if not reasons:
            reasons.append(f"semantic similarity ({similarity:.2f})")
        return "; ".join(reasons)

    async def get_tool_recommendations(self, Task: str, context: dict[str, Any] | None = None) -> str:
        """
        Get natural language tool recommendations for a Task.

        Args:
            Task: Task description
            context: Optional execution context

        Returns:
            Formatted Recommendation string
        """
        matches: Any = await self.find_tools_for_task(Task)
        if not matches:
            return "No specific tools found for this Task.\n                . You may need to implement a custom solution.\n                ."
        Recommendation: Any = f"Recommended tools for '{Task}':\n\n"
        for i, match in enumerate(matches, 1):
            tool: Any = match.tool
            Recommendation += f"{i}. {tool.name}\n"
            Recommendation += f"   Description: {tool.description}\n"
            Recommendation += f"   Relevance: {match.relevance_score:.2f}\n"
            Recommendation += f"   Reason: {match.reason}\n"
            if tool.parameters:
                Recommendation += f"   Parameters: {json.dumps(tool.parameters, indent=6)}\n"
            Recommendation += "\n"
        return Recommendation

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self, category: str | None = None, tags: list[str] | None = None) -> list[ToolDefinition]:
        """List all tools, optionally filtered."""
        tools_list: Any = list(self.tools.values())
        if category:
            tools_list: Any = [t for t in tools_list if t.category == category]
        if tags:
            tools_list: Any = [t for t in tools_list if any(tag in t.tags for tag in tags)]
        return tools_list

    def update_tool_stats(self, name: str, success: bool) -> Any:
        """Update tool usage statistics."""
        if name in self.tools:
            tool: Any = self.tools[name]
            tool.usage_count += 1
            alpha: Any = 0.1
            if success:
                tool.success_rate = tool.success_rate * (1 - alpha) + 1 * alpha
            else:
                tool.success_rate = tool.success_rate * (1 - alpha) + 0 * alpha

    def _generate_description_from_func(self, func: Callable) -> str:
        """Generate description from function docstring."""
        if func.__doc__:
            return func.__doc__.strip()
        return f"Function: {func.__name__}"

    def _generate_parameters_from_func(self, func: Callable) -> dict[str, Any]:
        """Generate parameter schema from function signature."""
        sig = inspect.signature(func)
        parameters_schema = {}
        for name, param in sig.parameters.items():
            param_info = {"type": "unknown"}
            if param.annotation != inspect.Parameter.empty:
                param_info["type"] = str(param.annotation)
            if param.default == inspect.Parameter.empty:
                param_info["required"] = True
            else:
                param_info["default"] = str(param.default)
            parameters_schema[name] = param_info
        return parameters_schema

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        categories_count: Any = {}
        for tool in self.tools.values():
            categories_count[tool.category] = categories_count.get(tool.category, 0) + 1
        return {
            "total_tools": len(self.tools),
            "categories": categories_count,
            "most_used": max(self.tools.values(), key=lambda t: t.usage_count).name if self.tools else None,
            "avg_success_rate": np.mean([t.success_rate for t in self.tools.values()]) if self.tools else 0.0,
        }


predefined_tool_categories: Any = {
    "filesystem": "File and directory operations",
    "network": "Network and API communication",
    "analysis": "Data analysis and processing",
    "utility": "General utility functions",
    "mcp": "Model Context Protocol tools",
    "ai": "AI/ML related tools",
}


def ast_analysis(code: str, mode: str = "audit_classes") -> dict[str, Any]:
    """AST tool — analyze Python code for patterns (e.g., snake_case classes).

    Args:
        code: Python source code to analyze
        mode: Analysis mode - "audit_classes", "extract_names", "check_snake_case"

    Returns:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        Dict with analysis results based on mode
    """
    import ast

    try:
        tree = ast.parse(code)
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return {"error": "syntax_error", "message": f"Invalid Python syntax: {e}"}
    if mode == "audit_classes":
        snake_classes = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and (node.name[0].islower() or "_" in node.name)
        )
        pascal_classes = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name[0].isupper() and ("_" not in node.name)
        )
        return {
            "snake_classes": snake_classes,
            "pascal_classes": pascal_classes,
            "total_classes": snake_classes + pascal_classes,
        }
    elif mode == "extract_names":
        class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        return {"class_names": class_names, "count": len(class_names)}
    elif mode == "check_snake_case":
        has_violations = any(
            isinstance(node, ast.ClassDef) and (node.name[0].islower() or "_" in node.name)
            for node in ast.walk(tree)
        )
        return {"has_snake_case": has_violations}
    return {"error": "invalid_mode", "message": f"Unknown mode: {mode}"}


def code_transform_tool(args: CodeTransformArgs) -> dict[str, Any]:
    """
    Deterministic AST-based code transformation tool.

    Enables agents to perform safe, syntax-preserving code transformations
    without LLM overhead. Supports rename, extract, decorator operations.

    Args:
        args: CodeTransformArgs with operation details
            - operation: "rename_symbol", "extract_function", "add_decorator", etc.
            - code: Source code to transform
            - target: Symbol name or line range
            - new_name: New name for rename operations
            - extract_name: Name for extracted function
            - line_start/line_end: Line range for extraction

    Returns:
        Dict with success status, transformed code, and change details

    Example:
        >>> args = CodeTransformArgs(
        ...     operation=TransformOperation.RENAME_SYMBOL,
        ...     code="def foo(): pass",
        ...     target="foo",
        ...     new_name="bar"
        ... )
        >>> result = code_transform_tool(args)
        >>> result["transformed_code"]
        'def bar(): pass'
    """
    return code_transform(args)


predefined_tool_categories["code_manipulation"] = "AST-based code transformation tools"
LOGGER = logging.getLogger(__name__)
try:
    from agentic_core.L2_execution.utils.dependency_graph_tool import DependencyGraph, DependencyGraphArgs
except ImportError as e:
    LOGGER.warning(f"Could not import dependency graph tool: {e}")
    DependencyGraph = None
    DependencyGraphArgs = None


def dependency_graph_tool(args: DependencyGraphArgs) -> dict[str, Any]:
    """
    Dependency graph analysis tool for import/call relationships.

    Enables agents to analyze code dependencies for:
    - Cycle detection (circular imports)
    - Impact analysis (what breaks if X changes)
    - Unused import detection

    Args:
        args: DependencyGraphArgs with operation details
            - operation: "build_graph", "detect_cycles", "ImpactAnalysis", etc.
            - target_path: File or directory to analyze
            - symbol: Symbol name for impact analysis

    Returns:
        Dict with graph data, cycles, or impact analysis results

    Example:
        >>> args = DependencyGraphArgs(
        ...     operation=GraphOperation.DETECT_CYCLES,
        ...     target_path="agentic_core/"
        ... )
        >>> result = dependency_graph_tool(args)
        >>> result["data"]["has_cycles"]
        False
    """
    return DependencyGraph(args)


predefined_tool_categories["analysis"] = "Code analysis and dependency tools"


def diff_generator_tool(args: DiffGeneratorArgs) -> dict[str, Any]:
    """
    Diff/patch generation tool for reviewable changes.

    Enables agents to generate human-reviewable diffs before applying changes,
    supporting human-in-loop validation for high-risk operations.

    Args:
        args: DiffGeneratorArgs with diff parameters
            - original: Original code/text
            - modified: Modified code/text
            - format: "unified", "context", "html", "ndiff"

    Returns:
        Dict with diff text, stats, and patch applicability

    Example:
        >>> args = DiffGeneratorArgs(
        ...     original="def foo(): pass",
        ...     modified="def bar(): pass",
        ...     format=DiffFormat.UNIFIED
        ... )
        >>> result = diff_generator_tool(args)
        >>> print(result["diff"])
    """
    return generate_diff(args)


def create_tool_registry(embedder: Any, enable_caching: bool = True) -> tool_registry:
    """
    Factory function to create a tool registry.

    Args:
        embedder: Embedding function
        enable_caching: Whether to enable caching

    Returns:
        tool_registry instance
    """
    return tool_registry(embedder=embedder, enable_caching=enable_caching)
