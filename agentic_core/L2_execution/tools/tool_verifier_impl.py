from __future__ import annotations

"""
Tool Verification Loop - The "Compiler Check"

Prevents agents from hallucinating tools or code by forcing verification
before execution. Acts as a pre-commit check for agent actions.
"""
import ast
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

LOGGER = logging.getLogger(__name__)

Logger: Any = logging.getLogger(__name__)


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
            for node in ast.walk(tree):
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
        except SyntaxError as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
            issues.append(
                VerificationIssue(
                    Severity="error",
                    message=f"Verification error: {str(e)}",
                    suggestion="Check code for obvious errors",
                ),
            )
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
