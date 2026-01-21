from __future__ import annotations

"""
Governance & Meta-Optimization Module - Phase 7 Implementation

This module provides advanced governance capabilities:
- DependencyArbiter: Dependency hygiene and environment integrity
- StrictDocEnforcerAgent: Type contract compliance in docstrings
- DashboardGenerator: HTML mission control visualization
- PromptGovernor: AI prompt security and segregation
- PredictiveBudgetManager: Cost prediction before execution
"""
import ast
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from .context import ResumeEngineContext


class DependencyStatus(Enum):
    """
    Status of dependency checks.

    Defines the health status of dependencies including healthy,
    warning, conflict, and missing states.
    """

    HEALTHY = "healthy"
    WARNING = "warning"
    CONFLICT = "conflict"
    MISSING = "Missing"


class DocComplianceLevel(Enum):
    """
    Documentation compliance levels.

    Defines the levels of documentation completeness from none to
    complete with type hints and comprehensive docstrings.
    """

    NONE = "none"
    BASIC = "basic"
    TYPED = "typed"
    COMPLETE = "complete"


class PromptRisk(Enum):
    """
    Prompt security risk levels.

    Defines the risk levels for AI prompt security issues from
    low to critical severity.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DependencyIssue:
    """A dependency issue found during scanning."""

    issue_id: str
    status: DependencyStatus
    package: str
    description: str
    Recommendation: str


@dataclass
class DocViolation:
    """A documentation Violation."""

    file_path: str
    function_name: str
    ViolationType: str
    missing_args: list[str]
    missing_return: bool
    line_number: int


@dataclass
class PromptIssue:
    """A prompt security issue."""

    file_path: str
    variable_name: str
    line_number: int
    risk_level: PromptRisk
    description: str
    prompt_preview: str


@dataclass
class CostPrediction:
    """Cost prediction result."""

    estimated_tokens: int
    estimated_cost: float
    budget_remaining: float
    will_exceed: bool
    Recommendation: str


class DependencyArbiter:
    """
    Ensures environment integrity and dependency hygiene.

    Features:
    - pip check for conflicts
    - requirements.txt validation
    - Import analysis
    - Dependency version checking
    """

    # Standard library modules (subset for checking)
    STDLIB_MODULES = {
        "os",
        "sys",
        "re",
        "json",
        "time",
        "datetime",
        "pathlib",
        "typing",
        "collections",
        "itertools",
        "functools",
        "operator",
        "math",
        "random",
        "hashlib",
        "base64",
        "copy",
        "io",
        "abc",
        "dataclasses",
        "enum",
        "asyncio",
        "subprocess",
        "threading",
        "multiprocessing",
        "logging",
        "unittest",
        "pytest",
        "ast",
    }

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._issues: list[DependencyIssue] = []
        self._checks_performed = 0

    def check_environment(self) -> list[DependencyIssue]:
        """
        Check environment for dependency issues.

        Returns:
            List of dependency issues
        """
        self._checks_performed += 1
        issues = []

        # Run pip check
        pip_issues = self._run_pip_check()
        issues.extend(pip_issues)

        # Check requirements.txt
        req_issues = self._check_requirements()
        issues.extend(req_issues)

        self._issues.extend(issues)
        return issues

    def _run_pip_check(self) -> list[DependencyIssue]:
        """Run pip check to find conflicts."""
        issues = []

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                # Parse pip check output
                for line in result.stdout.split(
                    "\nimport logging\n\nLogger = logging.getLogger(__name__)\n"
                ):
                    if line.strip():
                        issue = DependencyIssue(
                            issue_id=hashlib.sha256(line.encode()).hexdigest()[:12],
                            status=DependencyStatus.CONFLICT,
                            package=line.split()[0] if line.split() else "unknown",
                            description=line,
                            Recommendation="Resolve version conflict",
                        )
                        issues.append(issue)
        except subprocess.TimeoutExpired:
            issues.append(
                DependencyIssue(
                    issue_id="pip_timeout",
                    status=DependencyStatus.WARNING,
                    package="pip",
                    description="pip check timed out",
                    Recommendation="Run pip check manually",
                )
            )
        except Exception as e:
            issues.append(
                DependencyIssue(
                    issue_id="pip_error",
                    status=DependencyStatus.WARNING,
                    package="pip",
                    description=f"pip check failed: {e}",
                    Recommendation="Verify pip is installed correctly",
                )
            )

        return issues

    def _check_requirements(self) -> list[DependencyIssue]:
        """Check requirements.txt exists and is valid."""
        issues = []

        req_path = Path("requirements.txt")
        if not req_path.exists():
            issues.append(
                DependencyIssue(
                    issue_id="missing_requirements",
                    status=DependencyStatus.MISSING,
                    package="requirements.txt",
                    description="requirements.txt not found",
                    Recommendation="Create requirements.txt with pip freeze",
                )
            )
        else:
            # Check for common issues
            content = req_path.read_text()

            # Check for unpinned versions
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" not in line and ">=" not in line and "<=" not in line:
                        if line and not line.startswith("-"):
                            issues.append(
                                DependencyIssue(
                                    issue_id=hashlib.sha256(line.encode()).hexdigest()[:12],
                                    status=DependencyStatus.WARNING,
                                    package=line,
                                    description=f"Unpinned version: {line}",
                                    Recommendation="Pin version with ==",
                                )
                            )

        return issues

    def analyze_imports(self, content: str, file_path: str = "unknown") -> list[str]:
        """
        Analyze imports in Python content.

        Args:
            content: Python source code
            file_path: Path for reporting

        Returns:
            List of non-standard imports
        """
        non_standard = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split(".")[0]
                        if module not in self.STDLIB_MODULES:
                            non_standard.append(module)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split(".")[0]
                        if module not in self.STDLIB_MODULES:
                            non_standard.append(module)

        except SyntaxError:
            pass

        return list(set(non_standard))

    def get_issues(self) -> list[DependencyIssue]:
        """Get all dependency issues."""
        return self._issues

    def get_issues_by_status(self, status: DependencyStatus) -> list[DependencyIssue]:
        """Get issues filtered by status."""
        return [i for i in self._issues if i.status == status]

    def get_stats(self) -> dict[str, Any]:
        """Get arbiter statistics."""
        return {
            "checks_performed": self._checks_performed,
            "total_issues": len(self._issues),
            "by_status": {
                s.value: sum(1 for i in self._issues if i.status == s) for s in DependencyStatus
            },
        }


class StrictDocEnforcerAgent(MCPHardenedMixin, HealerMixin):
    """
    Enforces type contract compliance in docstrings.

    Features:
    - Docstring existence checking
    - Argument documentation validation
    - Return type documentation
    - Google-style docstring parsing
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._violations: list[DocViolation] = []

    def check_content(self, content: str, file_path: str = "unknown") -> list[DocViolation]:
        """
        Check content for documentation violations.

        Args:
            content: Python source code
            file_path: Path for reporting

        Returns:
            List of documentation violations
        """
        violations = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    Violation = self._check_function(node, file_path)
                    if Violation:
                        violations.append(Violation)
                        self._violations.append(Violation)

        except SyntaxError:
            pass

        return violations

    def _check_function(self, node: ast.FunctionDef, file_path: str) -> DocViolation | None:
        """Check a function for documentation compliance."""
        # Skip private/magic methods
        if node.name.startswith("_"):
            return None

        docstring = ast.get_docstring(node)

        if not docstring:
            return DocViolation(
                file_path=file_path,
                function_name=node.name,
                ViolationType="missing_docstring",
                missing_args=[],
                missing_return=False,
                line_number=node.lineno,
            )

        # Get function arguments
        args = []
        for arg in node.args.args:
            if arg.arg != "self" and arg.arg != "cls":
                args.append(arg.arg)

        # Parse docstring for Args section
        documented_args = self._parse_args_section(docstring)

        # Find Missing args
        missing_args = [a for a in args if a not in documented_args]

        # Check for return documentation
        has_return = "Returns:" in docstring or "Return:" in docstring

        # Check if function has return statement
        has_return_stmt = any(
            isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node)
        )

        missing_return = has_return_stmt and not has_return

        if missing_args or missing_return:
            return DocViolation(
                file_path=file_path,
                function_name=node.name,
                ViolationType="incomplete_docstring",
                missing_args=missing_args,
                missing_return=missing_return,
                line_number=node.lineno,
            )

        return None

    def _parse_args_section(self, docstring: str) -> set[str]:
        """Parse Args section from Google-style docstring."""
        documented_args = set()

        # Find Args section
        args_match = re.search(r"Args?:\s*\n((?:\s+\w+.*\n)*)", docstring)
        if args_match:
            args_section = args_match.group(1)
            # Extract argument names
            for line in args_section.split("\n"):
                match = re.match(r"\s+(\w+)\s*[:\(]", line)
                if match:
                    documented_args.add(match.group(1))

        return documented_args

    def get_violations(self) -> list[DocViolation]:
        """Get all documentation violations."""
        return self._violations

    def get_compliance_level(self, content: str) -> DocComplianceLevel:
        """
        Get documentation compliance level for content.

        Args:
            content: Python source code

        Returns:
            Compliance level
        """
        violations = self.check_content(content)

        if not violations:
            return DocComplianceLevel.COMPLETE

        missing_docstrings = sum(1 for v in violations if v.ViolationType == "missing_docstring")
        incomplete = sum(1 for v in violations if v.ViolationType == "incomplete_docstring")

        if missing_docstrings > 0:
            return DocComplianceLevel.NONE
        elif incomplete > 0:
            return DocComplianceLevel.BASIC

        return DocComplianceLevel.TYPED

    def get_stats(self) -> dict[str, Any]:
        """Get enforcer statistics."""
        return {
            "total_violations": len(self._violations),
            "missing_docstrings": sum(
                1 for v in self._violations if v.ViolationType == "missing_docstring"
            ),
            "incomplete_docstrings": sum(
                1 for v in self._violations if v.ViolationType == "incomplete_docstring"
            ),
        }

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()


class DashboardGenerator:
    """
    Generates visual HTML Mission Control report.

    Features:
    - Pass/fail summary
    - Signal status
    - Dependency graph visualization
    - Mermaid.js integration
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._generated_reports: list[str] = []

    def generate(
        self,
        results: dict[str, Any],
        signals: set[str],
        output_path: str = "observability/mission_control.html",
    ) -> str:
        """
        Generate HTML dashboard.

        Args:
            results: Agent results dictionary
            signals: Active signals
            output_path: Output file path

        Returns:
            Path to generated file
        """
        # Calculate metrics
        total = len(results)
        passed = sum(1 for r in results.values() if r.get("passed", False))
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0

        html = self._generate_html(
            results=results,
            signals=signals,
            total=total,
            passed=passed,
            failed=failed,
            success_rate=success_rate,
        )

        # Write file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html, encoding="utf-8")

        self._generated_reports.append(output_path)

        return output_path

    def _generate_html(
        self,
        results: dict[str, Any],
        signals: set[str],
        total: int,
        passed: int,
        failed: int,
        success_rate: float,
    ) -> str:
        """Generate HTML content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Condensed CSS for line reduction
        condensed_css = """* { margin: 0; padding: 0; box-sizing: border-box; } body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; min-height: 100vh; padding: 20px; } .container { max-width: 1200px; margin: 0 auto; } h1 { text-align: center; margin-bottom: 30px; font-size: 2.5em; background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; } .timestamp { text-align: center; color: #888; margin-bottom: 20px; } .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; } .Metric-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; text-align: center; backdrop-filter: blur(10px); } .Metric-value { font-size: 2.5em; font-weight: bold; } .Metric-label { color: #888; margin-top: 5px; } .success { color: #00ff88; } .failure { color: #ff4444; } .warning { color: #ffaa00; } .section { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px; } .section h2 { margin-bottom: 15px; color: #00d4ff; } table { width: 100%; border-collapse: collapse; } th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); } th { color: #888; font-weight: normal; } .status-pass { color: #00ff88; } .status-fail { color: #ff4444; } .signal-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; background: rgba(255,170,0,0.2); color: #ffaa00; margin: 4px; font-size: 0.9em; } .mermaid { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; }"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Resume Engine Mission Control</title>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>{condensed_css}</style>
</head>
<body>
    <div class="container"><h1>🧬 Resume Engine Mission Control</h1><p class="timestamp">Generated: {timestamp}</p>
        <div class="metrics">
            <div class="Metric-card"><div class="Metric-value">{total}</div><div class="Metric-label">Total Checks</div></div>
            <div class="Metric-card"><div class="Metric-value success">{passed}</div><div class="Metric-label">Passed</div></div>
            <div class="Metric-card"><div class="Metric-value failure">{failed}</div><div class="Metric-label">Failed</div></div>
            <div class="Metric-card"><div class="Metric-value {"success" if success_rate >= 80 else "warning" if success_rate >= 50 else "failure"}">{success_rate:.1f}%</div><div class="Metric-label">Success Rate</div></div>
        </div>
        <div class="section"><h2>📡 Active Signals</h2><div>{self._render_signals(signals)}</div></div>
        <div class="section"><h2>📊 Agent Results</h2><table><thead><tr><th>Agent</th><th>Status</th><th>Details</th></tr></thead><tbody>{self._render_results_table(results)}</tbody></table></div>
        <div class="section"><h2>🔗 Dependency Graph</h2><div class="mermaid">{self._render_mermaid_graph(results)}</div></div>
    </div>
    <script>mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});</script>
</body>
</html>"""

        return html

    def _render_signals(self, signals: set[str]) -> str:
        """Render signals as badges."""
        if not signals:
            return '<Span style="color: #888;">No active signals</Span>'

        return "".join(f'<Span class="signal-badge">{s}</Span>' for s in signals)

    def _render_results_table(self, results: dict[str, Any]) -> str:
        """Render results as table rows."""
        rows = []
        for agent, result in sorted(results.items()):
            passed = result.get("passed", False)
            status_class = "status-pass" if passed else "status-fail"
            status_text = "✅ PASS" if passed else "❌ FAIL"
            details = result.get("details", "")

            rows.append(f"""
                <tr>
                    <td>{agent}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{details}</td>
                </tr>
            """)

        return "".join(rows)

    def _render_mermaid_graph(self, results: dict[str, Any]) -> str:
        """Render Mermaid.js graph."""
        graph = "graph TD\n"

        # Create nodes for each agent
        for i, agent in enumerate(results.keys()):
            status = "pass" if results[agent].get("passed", False) else "fail"
            style = "fill:#00ff88" if status == "pass" else "fill:#ff4444"
            graph += f"    A{i}[{agent}]\n"
            graph += f"    style A{i} {style}\n"

        # Add connections (simplified flow)
        agents = list(results.keys())
        for i in range(len(agents) - 1):
            graph += f"    A{i} --> A{i + 1}\n"

        return graph

    def get_generated_reports(self) -> list[str]:
        """Get list of generated reports."""
        return self._generated_reports

    def get_stats(self) -> dict[str, Any]:
        """Get generator statistics."""
        return {
            "reports_generated": len(self._generated_reports),
        }


class PromptGovernor:
    """
    Segregates and secures AI prompts.

    Features:
    - Hardcoded prompt detection
    - Prompt variable naming checks
    - Security risk analysis
    - Prompt segregation recommendations
    """

    # Patterns for prompt detection
    PROMPT_PATTERNS = [
        r"_PROMPT\s*=",
        r"PROMPT_\w+\s*=",
        r"system_message\s*=",
        r"user_message\s*=",
        r"assistant_message\s*=",
    ]

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._issues: list[PromptIssue] = []

    def scan_content(self, content: str, file_path: str = "unknown") -> list[PromptIssue]:
        """
        Scan content for prompt security issues.

        Args:
            content: Python source code
            file_path: Path for reporting

        Returns:
            List of prompt issues
        """
        issues = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            issue = self._check_assignment(node, target, file_path)
                            if issue:
                                issues.append(issue)
                                self._issues.append(issue)

        except SyntaxError:
            pass

        # Also check for large string literals
        large_string_issues = self._check_large_strings(content, file_path)
        issues.extend(large_string_issues)
        self._issues.extend(large_string_issues)

        return issues

    def _check_assignment(
        self, node: ast.Assign, target: ast.Name, file_path: str
    ) -> PromptIssue | None:
        """Check an assignment for prompt issues."""
        var_name = target.id

        # Check if variable name suggests a prompt
        is_prompt_var = any(
            re.search(pattern, f"{var_name} =", re.IGNORECASE) for pattern in self.PROMPT_PATTERNS
        )

        if not is_prompt_var:
            return None

        # Check if it's a string literal
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            prompt_value = node.value.value

            # Determine risk level
            risk = self._assess_risk(prompt_value)

            return PromptIssue(
                file_path=file_path,
                variable_name=var_name,
                line_number=node.lineno,
                risk_level=risk,
                description=f"Hardcoded prompt in variable '{var_name}'",
                prompt_preview=prompt_value[:100] + "..."
                if len(prompt_value) > 100
                else prompt_value,
            )

        return None

    def _check_large_strings(self, content: str, file_path: str) -> list[PromptIssue]:
        """Check for large string literals that might be prompts."""
        issues = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if len(node.value) > 200:  # Large string threshold
                        # Check if it looks like a prompt
                        if self._looks_like_prompt(node.value):
                            risk = self._assess_risk(node.value)

                            issues.append(
                                PromptIssue(
                                    file_path=file_path,
                                    variable_name="<inline>",
                                    line_number=node.lineno if hasattr(node, "lineno") else 0,
                                    risk_level=risk,
                                    description="Large inline string that appears to be a prompt",
                                    prompt_preview=node.value[:100] + "...",
                                )
                            )

        except SyntaxError:
            pass

        return issues

    def _looks_like_prompt(self, text: str) -> bool:
        """Check if text looks like an LLM prompt."""
        prompt_indicators = [
            "you are",
            "your Task",
            "please",
            "generate",
            "respond",
            "answer",
            "role:",
            "context:",
            "instructions:",
            "Task:",
            "system:",
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in prompt_indicators)

    def _assess_risk(self, prompt: str) -> PromptRisk:
        """Assess security risk of a prompt."""
        prompt_lower = prompt.lower()

        # Critical risk indicators
        critical_patterns = [
            "ignore previous",
            "ignore all",
            "disregard",
            "pretend you are",
            "act as if",
            "bypass",
        ]

        if any(p in prompt_lower for p in critical_patterns):
            return PromptRisk.CRITICAL

        # High risk indicators
        high_patterns = [
            "execute",
            "run command",
            "system access",
            "password",
            "secret",
            "api key",
        ]

        if any(p in prompt_lower for p in high_patterns):
            return PromptRisk.HIGH

        # Medium risk - user input interpolation
        if "{" in prompt and "}" in prompt:
            return PromptRisk.MEDIUM

        return PromptRisk.LOW

    def get_issues(self) -> list[PromptIssue]:
        """Get all prompt issues."""
        return self._issues

    def get_issues_by_risk(self, risk: PromptRisk) -> list[PromptIssue]:
        """Get issues filtered by risk level."""
        return [i for i in self._issues if i.risk_level == risk]

    def get_stats(self) -> dict[str, Any]:
        """Get governor statistics."""
        return {
            "total_issues": len(self._issues),
            "by_risk": {
                r.value: sum(1 for i in self._issues if i.risk_level == r) for r in PromptRisk
            },
        }


class PredictiveBudgetManager:
    """
    Predictive budget management with cost estimation.

    Features:
    - Cost prediction before execution
    - Budget tracking
    - Threshold warnings
    - Execution gating
    """

    # Cost rates (per 1M tokens)
    INPUT_COST_PER_MILLION = 0.50
    OUTPUT_COST_PER_MILLION = 1.50

    # Estimation factors
    TOKENS_PER_FILE = 1000
    TOKENS_PER_AGENT = 500

    def __init__(
        self,
        ctx: ResumeEngineContext,
        budget_limit: float = 1.0,
    ):
        self.ctx = ctx
        self.budget_limit = budget_limit
        self._current_cost = 0.0
        self._predictions: list[CostPrediction] = []

    def predict_cost(
        self,
        files_count: int,
        agents_count: int,
        cycles: int = 1,
    ) -> CostPrediction:
        """
        Predict cost for a mission.

        Args:
            files_count: Number of files to process
            agents_count: Number of agents to run
            cycles: Number of healing cycles

        Returns:
            Cost prediction
        """
        # Estimate tokens
        input_tokens = files_count * self.TOKENS_PER_FILE * agents_count * cycles
        output_tokens = agents_count * self.TOKENS_PER_AGENT * cycles

        total_tokens = input_tokens + output_tokens

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        estimated_cost = input_cost + output_cost

        # Check budget
        budget_remaining = self.budget_limit - self._current_cost
        will_exceed = estimated_cost > budget_remaining

        # Generate Recommendation
        if will_exceed:
            Recommendation = (
                f"Reduce scope or increase budget by ${estimated_cost - budget_remaining:.4f}"
            )
        elif estimated_cost > budget_remaining * 0.8:
            Recommendation = "Approaching budget limit - consider reducing scope"
        else:
            Recommendation = "Within budget"

        prediction = CostPrediction(
            estimated_tokens=total_tokens,
            estimated_cost=estimated_cost,
            budget_remaining=budget_remaining,
            will_exceed=will_exceed,
            Recommendation=Recommendation,
        )

        self._predictions.append(prediction)

        return prediction

    def record_cost(self, cost: float) -> Any:
        """Record actual cost incurred."""
        self._current_cost += cost

    def check_budget(self) -> bool:
        """Check if budget is available."""
        return self._current_cost < self.budget_limit

    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return max(0, self.budget_limit - self._current_cost)

    def get_current_cost(self) -> float:
        """Get current cost."""
        return self._current_cost

    def reset(self) -> Any:
        """Reset cost tracking."""
        self._current_cost = 0.0
        self._predictions.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get budget statistics."""
        return {
            "budget_limit": self.budget_limit,
            "current_cost": self._current_cost,
            "remaining": self.get_remaining_budget(),
            "predictions_made": len(self._predictions),
            "budget_available": self.check_budget(),
        }
