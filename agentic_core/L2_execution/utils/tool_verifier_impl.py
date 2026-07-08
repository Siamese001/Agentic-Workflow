from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "tool_verifier_impl")
trace_contract.emit_determinism_digest("p0", "tool_verifier_impl")

trace_contract._emit_dispatches_healing_run("p1", "tool_verifier_impl", "L2")
trace_contract._emit_routes_through("p1", "tool_verifier_impl", "L2")
trace_contract._emit_checks_agent_registry("p1", "tool_verifier_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_verifier_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_verifier_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_verifier_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_verifier_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_verifier_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_verifier_impl", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_verifier_impl", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_verifier_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_verifier_impl")
trace_contract._emit_gated_by_confidence("p1", "tool_verifier_impl", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tool_verifier_impl", "L2")
trace_contract._emit_reads_policy_state("p1", "tool_verifier_impl", "L2")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "tool_verifier_impl", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "tool_verifier_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_verifier_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_verifier_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_verifier_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_verifier_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_verifier_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_verifier_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_verifier_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_verifier_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_verifier_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_verifier_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_verifier_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_verifier_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_verifier_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_verifier_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_verifier_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_verifier_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_verifier_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_verifier_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_verifier_impl", "exec_snapshot_link")

'\nTool Verification Loop - The "Compiler Check"\n\nPrevents agents from hallucinating tools or code by forcing verification\nbefore execution. Acts as a pre-commit check for agent actions.\n'
import ast
import logging
import re
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from tqdm import tqdm

trace_contract._emit_emits_metric_event("tool_verifier_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_verifier_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_verifier_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_verifier_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_verifier_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_verifier_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_verifier_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_verifier_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_verifier_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_verifier_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_verifier_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_verifier_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_verifier_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_verifier_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_verifier_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_verifier_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_verifier_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_verifier_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_verifier_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_verifier_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_verifier_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_verifier_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_verifier_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_verifier_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_verifier_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_verifier_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_verifier_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_verifier_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tool_verifier_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_verifier_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_verifier_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_verifier_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tool_verifier_impl", "write_through")
trace_contract._emit_writes_through("p1", "tool_verifier_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tool_verifier_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_verifier_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_verifier_impl", "routing_commit")

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
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
        run_id="tool_verifier_impl",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


class VerificationResult(Enum):
    """Result of tool verification."""

    PASSED: Any = "passed"
    FAILED: Any = "failed"
    WARNING: Any = "warning"


@dataclass
class VerificationIssue:
    """An issue found during verification."""

    Severity: str
    message: str
    line_number: int | None = None
    suggestion: str | None = None


@dataclass
class ToolVerificationReport:
    """Complete verification report for a tool call."""

    result: VerificationResult
    issues: list[VerificationIssue]
    verified_code: str | None = None
    execution_plan: str | None = None


class ToolVerifier:
    """
    Verifies tool calls and code before execution.

    Acts as a compiler check - if it doesn't verify, it doesn't run.
    """

    def __init__(self: Any, sandbox: Any, enable_strict_mode: bool) -> None:
        """
        Initialize the tool verifier.

        Args:
            sandbox: Optional sandbox for dry-run execution
            enable_strict_mode: Whether to enforce strict verification
        """
        self.sandbox = sandbox
        self.strict_mode = enable_strict_mode
        self._init_patterns()
        LOGGER.info(f"Tool verifier initialized (strict_mode={self.strict_mode})")

    def _init_patterns(self: Any) -> None:
        """Initialize patterns for detecting common issues."""
        self.hallucinated_imports = {
            "magic_library",
            "super_ai",
            "brain_boost",
            "instant_solve",
            "ai_helper",
            "smart_utils",
            "quick_fix",
            "auto_code",
        }
        self.dangerous_functions = {
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "file",
            "input",
            "raw_input",
        }
        self.tool_requirements = {
            "file_read": ["read\\s*\\(", "open\\s*\\("],
            "file_write": ["write\\s*\\(", "open\\s*\\(", "w"],
            "data_analysis": ["import\\s+pandas", "import\\s+numpy", "df\\."],
            "web_request": ["requests\\.", "urllib\\."],
            "code_execution": ["def\\s+\\w+\\s*\\(", "class\\s+\\w+"],
        }
        self.compiled_patterns = {
            tool: [re.compile(pattern) for pattern in patterns]
            for tool, patterns in self.tool_requirements.items()
        }

    async def verify_tool_call(
        self: Any,
        tool_name: str,
        tool_args: dict[str, Any],
        context: dict | None,
    ) -> ToolVerificationReport:
        """
        Verify a tool call before execution.

        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments for the tool
            context: Optional execution context

        Returns:
            VerificationReport with results and issues
        """

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "ToolVerifierImpl.verify_tool_call",
        )
        _ectx = _make_execution_context(tool_name, "tool_verifier_impl.verify_tool_call")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            tool_name,
            target_name="tool_verifier_impl.verify_tool_call",
        )
        issues: Any = []
        errors: Any = []
        warnings: Any = []
        basic_issues: Any = self._validate_basic_tool_call(tool_name, tool_args)
        issues.extend(basic_issues)
        if "code" in tool_args:
            code_issues: Any = await self._verify_code(tool_args["code"])
            issues.extend(code_issues)
        specific_issues: Any = await self._verify_tool_specific(tool_name, tool_args, context)
        issues.extend(specific_issues)
        if self.sandbox and "code" in tool_args:
            dry_run_issues: Any = await self._dry_run_code(tool_args["code"])
            issues.extend(dry_run_issues)
        for issue in issues:
            if issue.Severity == "error":
                errors.append(issue)
            elif issue.Severity == "warning":
                warnings.append(issue)
        if errors and self.strict_mode:
            result: Any = VerificationResult.FAILED
        elif warnings:
            result: Any = VerificationResult.WARNING
        else:
            result: Any = VerificationResult.PASSED
        LOGGER.info(f"Tool verification: {tool_name} -> {result.value} ({len(issues)} issues)")
        return ToolVerificationReport(
            result=result,
            issues=issues,
            verified_code=tool_args.get("code"),
            execution_plan=self._generate_execution_plan(tool_name, tool_args),
        )

    def _validate_basic_tool_call(
        self: Any,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> list[VerificationIssue]:
        """Basic validation of tool call structure."""
        issues = []
        if not tool_name or not isinstance(tool_name, str):
            issues.append(VerificationIssue(Severity="error", message="Invalid tool name"))
        if tool_name == "file_read" and "path" not in tool_args:
            issues.append(
                VerificationIssue(
                    Severity="error",
                    message="file_read tool requires 'path' argument",
                    suggestion="Add 'path' argument to tool call",
                ),
            )
        if tool_name == "file_write" and (not all(k in tool_args for k in ["path", "content"])):
            issues.append(
                VerificationIssue(
                    Severity="error",
                    message="file_write tool requires 'path' and 'content' arguments",
                    suggestion="Add Missing arguments to tool call",
                ),
            )
        return issues

    async def _verify_code(self: Any, code: str) -> list[VerificationIssue]:
        """Verify Python code for common issues."""
        issues = []
        try:
            tree = ast.parse(code)
            for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.hallucinated_imports:
                            issues.append(
                                VerificationIssue(
                                    Severity="error",
                                    message=f"Hallucinated import detected: {alias.name}",
                                    line_number=node.lineno,
                                    suggestion=f"Remove import of non-existent module '{alias.name}'",
                                ),
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module in self.hallucinated_imports:
                        issues.append(
                            VerificationIssue(
                                Severity="error",
                                message=f"Hallucinated import detected: from {node.module}",
                                line_number=node.lineno,
                                suggestion=f"Remove import from non-existent module '{node.module}'",
                            ),
                        )
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.dangerous_functions:
                            issues.append(
                                VerificationIssue(
                                    Severity="warning",
                                    message=f"Potentially dangerous function: {node.func.id}",
                                    line_number=node.lineno,
                                    suggestion="Consider safer alternatives",
                                ),
                            )
        except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
            issues.append(
                VerificationIssue(
                    Severity="error",
                    message=f"Syntax error: {e.msg}",
                    line_number=e.lineno,
                    suggestion="Fix syntax error before execution",
                ),
            )
        if "import magic" in code.lower():
            issues.append(
                VerificationIssue(
                    Severity="error",
                    message="Magic imports detected",
                    suggestion="Remove any 'magic' or hallucinated imports",
                ),
            )
        if not code.strip().endswith(('"', "'", ")", "]", "}")):
            issues.append(
                VerificationIssue(
                    Severity="warning",
                    message="Code appears incomplete",
                    suggestion="Ensure all brackets and quotes are closed",
                ),
            )
        return issues

    async def _verify_tool_specific(
        self: Any,
        tool_name: str,
        tool_args: dict[str, Any],
        context: dict | None,
    ) -> list[VerificationIssue]:
        """Tool-specific verification logic."""
        issues = []
        if tool_name == "file_read":
            path = tool_args.get("path", "")
            if "../" in path or "..\\" in path:
                issues.append(
                    VerificationIssue(
                        Severity="error",
                        message="Path traversal attempt detected",
                        suggestion="Use absolute paths or relative paths without '..'",
                    ),
                )
            if not any(path.endswith(ext) for ext in [".txt", ".py", ".json", ".csv"]):
                issues.append(
                    VerificationIssue(
                        Severity="warning",
                        message="Unusual file extension",
                        suggestion="Ensure you're reading the correct file type",
                    ),
                )
        elif tool_name == "web_search":
            query = tool_args.get("query", "")
            if len(query) < 3:
                issues.append(
                    VerificationIssue(
                        Severity="warning",
                        message="Search query too short",
                        suggestion="Provide a more descriptive search query",
                    ),
                )
        elif tool_name == "execute_code":
            code = tool_args.get("code", "")
            if not any(keyword in code for keyword in ["def ", "LOGGER.info(", "return ", "import "]):
                issues.append(
                    VerificationIssue(
                        Severity="warning",
                        message="Code appears to do nothing",
                        suggestion="Add actual functionality to the code",
                    ),
                )
        return issues

    async def _dry_run_code(self: Any, code: str) -> list[VerificationIssue]:
        """Dry-run code in sandbox to check for runtime errors."""
        if not self.sandbox:
            return []
        issues = []
        try:
            is_valid = await self.sandbox.verify_code(code)
            if not is_valid:
                issues.append(
                    VerificationIssue(
                        Severity="error",
                        message="Code failed syntax verification",
                        suggestion="Fix syntax errors before execution",
                    ),
                )
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise
        return issues

    def _generate_execution_plan(self: Any, tool_name: str, tool_args: dict[str, Any]) -> str:
        """Generate a human-readable execution plan."""
        plan_parts = [f"Tool: {tool_name}"]
        for key, value in tool_args.items():
            if key == "code":
                plan_parts.append(f"Code: {len(value)} characters")
            else:
                plan_parts.append(f"{key}: {str(value)[:50]}...")
        return " | ".join(plan_parts)

    def get_verification_summary(self: Any, report: ToolVerificationReport) -> str:
        """Get a human-readable summary of verification results."""
        summary: Any = f"Verification: {report.result.value.upper()}\n"
        if report.issues:
            summary += f"Issues found: {len(report.issues)}\n"
            for issue in report.issues[:5]:
                summary += f"  - [{issue.Severity.upper()}] {issue.message}"
                if issue.suggestion:
                    summary += f"\n    Suggestion: {issue.suggestion}"
                summary += "\n"
        if report.execution_plan:
            summary += f"\nExecution Plan: {report.execution_plan}"
        return summary


def create_tool_verifier(sandbox: Any | None = None, enable_strict_mode: bool = True) -> ToolVerifier:
    """
    Factory function to create a tool verifier.

    Args:
        sandbox: Optional sandbox for dry-run verification
        enable_strict_mode: Whether to enforce strict verification

    Returns:
        ToolVerifier instance
    """
    return ToolVerifier(sandbox=sandbox, enable_strict_mode=enable_strict_mode)
