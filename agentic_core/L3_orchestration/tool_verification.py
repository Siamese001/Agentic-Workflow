import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class VerificationResult(Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


""" Tool Verification Loop - The "Compiler Check"

Prevents agents from hallucinating tools or code by forcing verification
before execution. Acts as a pre-commit check for agent actions.
"""
"""Result of tool verification."""


@dataclass
class VerificationIssue:
    """An issue found during verification."""
    _severity: str  # "error", "warning", "info"
    _message: str
    _line_number: Optional[int] = None
    _suggestion: Optional[str] = None


@dataclass
class ToolVerificationReport:
    """Complete verification report for a tool call."""
    result: VerificationResult
    issues: List[VerificationIssue]
    _verified_code: Optional[str] = None
    _execution_plan: Optional[str] = None


class ToolVerifier:
    """ Acts as a compiler check - if it doesn't verify, it doesn't run.
    """
    def __init__(self, sandbox: Any = None, enable_strict_mode: bool = False):
        """
        Initialize the tool verifier.

        Args:
            sandbox: Optional sandbox for dry-run execution
            enable_strict_mode: Whether to enforce strict verification
        """
        self.sandbox = sandbox
        self.strict_mode = enable_strict_mode
        logger.info(f"Tool verifier initialized (strict_mode={self.strict_mode})")
        self._init_patterns()


def _init_patterns(self: Any) -> None:
    """Initialize patterns for detecting common issues."""

    # Hallucinated imports
    self.hallucinated_imports = {
        'magic_library', 'super_ai', 'brain_boost', 'instant_solve',
        'ai_helper', 'smart_utils', 'quick_fix', 'auto_code'
    }

    # Dangerous functions
    self.dangerous_functions = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input'
    }

    # Required patterns for different tool types
    self.tool_requirements = {
        'file_read': [r'read\s*\(', r'open\s*\('],
        'file_write': [r'write\s*\(', r'open\s*\(', 'w'],
        'data_analysis': [r'import\s+pandas', r'import\s+numpy', r'df\.'],
        'web_request': [r'requests\.', r'urllib\.'],
        'code_execution': [r'def\s+\w+\s*\(', r'class\s+\w+']
    }

    # Compile regex patterns
    self.compiled_patterns = {
        tool: [re.compile(pattern) for pattern in patterns]
        for tool, patterns in self.tool_requirements.items()
    }


async def verify_tool_call(self: Any,
                           tool_name: str,
                           tool_args: Dict[str,
                                           Any],
                           context: Optional[Dict]) -> ToolVerificationReport:
    """ """
    issues = []

    # 1. Basic validation
    basic_issues = self._validate_basic_tool_call(tool_name, tool_args)
    issues.extend(basic_issues)

    # 2. Code-specific verification
    if 'code' in tool_args:
        code_issues = await self._verify_code(tool_args['code'])
        issues.extend(code_issues)

    # 3. Tool-specific verification
    specific_issues = await self._verify_tool_specific(
        tool_name, tool_args, context
    )
    issues.extend(specific_issues)

    # 4. Dry-run in sandbox if available
    if self.sandbox and 'code' in tool_args:
        dry_run_issues = await self._dry_run_code(tool_args['code'])
        issues.extend(dry_run_issues)

    # Determine overall result
    errors = [issue for issue in issues if issue._severity == "error"]
    warnings = [issue for issue in issues if issue._severity == "warning"]

    if errors and self.strict_mode:
        result = VerificationResult.FAILED
    elif warnings:
        result = VerificationResult.WARNING
    else:
        result = VerificationResult.PASSED

    logger.info(
        f"Tool verification: {tool_name} -> {result.value} ({len(issues)} issues)")

    return ToolVerificationReport(
        result=result,
        issues=issues,
        _verified_code=tool_args.get('code'),
        _execution_plan=self._generate_execution_plan(tool_name, tool_args)
    )


def _validate_basic_tool_call(self: Any,
                              tool_name: str,
                              tool_args: Dict[str,
                                              Any]) -> List[VerificationIssue]:
    """Basic validation of tool call structure."""
    issues = []

    # Check if tool name is valid
    if not tool_name or not isinstance(tool_name, str):
        issues.append(VerificationIssue(
            _severity="error",
            _message="Invalid tool name"
        ))

    # Check required arguments
    if tool_name == "file_read" and "path" not in tool_args:
        issues.append(VerificationIssue(
            _severity="error",
            _message="file_read tool requires 'path' argument",
            _suggestion="Add 'path' argument to tool call"
        ))

    if tool_name == "file_write" and not all(k in tool_args for k in ["path", "content"]):
        issues.append(VerificationIssue(
            _severity="error",
            _message="file_write tool requires 'path' and 'content' arguments",
            _suggestion="Add missing arguments to tool call"
        ))

    return issues


async def _verify_code(self: Any, code: str) -> List[VerificationIssue]:
    """Verify Python code for common issues."""
    issues = []

    try:
        # Parse AST to check syntax
        tree = ast.parse(code)

        # Check for dangerous imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.hallucinated_imports:
                        issues.append(VerificationIssue(
                            _severity="error",
                            _message=f"Hallucinated import detected: {alias.name}",
                            _line_number=node.lineno,
                            _suggestion=f"Remove import of non-existent module '{alias.name}'"
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in self.hallucinated_imports:
                    issues.append(VerificationIssue(
                        _severity="error",
                        _message=f"Hallucinated import detected: from {node.module}",
                        _line_number=node.lineno,
                        _suggestion=f"Remove import from non-existent module '{node.module}'"
                    ))

            # Check for dangerous function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.dangerous_functions:
                        issues.append(VerificationIssue(
                            _severity="warning",
                            _message=f"Potentially dangerous function: {node.func.id}",
                            _line_number=node.lineno,
                            _suggestion="Consider safer alternatives"
                        ))

    except SyntaxError as e:
        issues.append(VerificationIssue(
            _severity="error",
            _message=f"Syntax error: {e.msg}",
            _line_number=e.lineno,
            _suggestion="Fix syntax error before execution"
        ))

    # Additional pattern-based checks
    if 'import magic' in code.lower():
        issues.append(VerificationIssue(
            _severity="error",
            _message="Magic imports detected",
            _suggestion="Remove any 'magic' or hallucinated imports"
        ))

    # Check for incomplete code
    if not code.strip().endswith(('"', "'", ')', ']', '}')):
        issues.append(VerificationIssue(
            _severity="warning",
            _message="Code appears incomplete",
            _suggestion="Ensure all brackets and quotes are closed"
        ))

    return issues


async def _verify_tool_specific(self: Any,
                                tool_name: str,
                                tool_args: Dict[str,
                                                Any],
                                context: Optional[Dict]) -> List[VerificationIssue]:
    """Tool-specific verification logic."""
    issues = []

    if tool_name == "file_read":
        path = tool_args.get("path", "")

        # Check for path traversal
        if "../" in path or "..\\" in path:
            issues.append(VerificationIssue(
                _severity="error",
                _message="Path traversal attempt detected",
                _suggestion="Use absolute paths or relative paths without '..'"
            ))

        # Check file extension
        if not any(path.endswith(ext) for ext in ['.txt', '.py', '.json', '.csv']):
            issues.append(VerificationIssue(
                _severity="warning",
                _message="Unusual file extension",
                _suggestion="Ensure you're reading the correct file type"))
    elif tool_name == "web_search":
        query = tool_args.get("query", "")

        if len(query) < 3:
            issues.append(VerificationIssue(
                _severity="warning",
                _message="Search query too short",
                _suggestion="Provide a more descriptive search query"
            ))

    elif tool_name == "execute_code":
        code = tool_args.get("code", "")

        # Check if code actually does something
        if not any(keyword in code for keyword in ["def ",
                                                   "logger.info(",
                                                   "return ",
                                                   "import "]):
            issues.append(VerificationIssue(
                _severity="warning",
                _message="Code appears to do nothing",
                _suggestion="Add actual functionality to the code"
            ))

    return issues


async def _dry_run_code(self: Any, code: str) -> List[VerificationIssue]:
    """Dry-run code in sandbox to check for runtime errors."""
    if not self.sandbox:
        return []

    issues = []

    try:
        # Use sandbox to verify code syntax
        is_valid = await self.sandbox.verify_code(code)

        if not is_valid:
            issues.append(VerificationIssue(
                _severity="error",
                _message="Code failed syntax verification",
                _suggestion="Fix syntax errors before execution"
            ))

    except Exception as e:
        issues.append(VerificationIssue(
            _severity="error",
            _message=f"Verification error: {str(e)}",
            _suggestion="Check code for obvious errors"
        ))

    return issues


def _generate_execution_plan(self: Any, tool_name: str, tool_args: Dict[str, Any]) -> str:
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
    summary = f"Verification: {report.result.value.upper()}\n"

    if report.issues:
        summary += f"Issues found: {len(report.issues)}\n"

        for issue in report.issues[:5]:  # Show first 5 issues
            summary += f"  - [{issue._severity.upper()}] {issue._message}"
            if issue._suggestion:
                summary += f"\n    Suggestion: {issue._suggestion}"
            summary += "\n"

    if report._execution_plan:
        summary += f"\nExecution Plan: {report._execution_plan}"

    return summary


def create_tool_verifier(
    sandbox: Any = None,
    enable_strict_mode: bool = True
) -> ToolVerifier:
    """ Creates and initializes a ToolVerifier instance. """
    return ToolVerifier(
        sandbox=sandbox,
        enable_strict_mode=enable_strict_mode
    )