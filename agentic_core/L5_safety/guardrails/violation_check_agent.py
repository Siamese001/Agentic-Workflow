from __future__ import annotations

"""Constitutional Overseer for validating ActionRequests.

This module provides safety validation for action requests, including:
- ConstitutionalOverseer: Validates actions against forbidden commands
- SafetyInspectorAgent: Scans files for security violations with Socratic Judge

Typical usage:
    overseer = create_overseer()
    result = await overseer.validate_action(request)

    inspector = create_safety_inspector()
    violations = await inspector.scan_file("path/to/file.py")
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail
# This boosts alignment detection — review and integrate appropriately


# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

import logging
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import subatomic_testing_mixin
from agentic_core.L1_cognition.P1_interfaces import ActionRequest

Logger: logging.Logger = logging.getLogger(__name__)


class ViolationCheck:
    """Result of a safety Violation check."""

    def __init__(self, is_violation: bool, reason: str = "") -> None:
        self.is_violation = is_violation
        self.reason = reason


class ConstitutionalOverseer:
    """Overseer that validates ActionRequests against safety rules."""

    def __init__(self) -> None:
        """Initialize the overseer with default safety rules."""
        self._forbidden_commands = [
            "rm\\s+-rf\\s+/",
            "rm\\s+-rf\\s+\\.",
            "dd\\s+if=/dev/zero",
            "mkfs\\.",
            "curl\\s+https?://(?!localhost|127\\.0\\.0\\.1)",
            "wget\\s+https?://(?!localhost|127\\.0\\.0\\.1)",
            "nc\\s+-l",
            "telnet\\s+\\d",
            "sudo\\s+su",
            "chmod\\s+777",
            "chown\\s+root",
            "apt-get\\s+install",
            "pip\\s+install\\s+--force",
            "yum\\s+install",
            "eval\\s+\\$",
            "exec\\s+\\$",
            "sh\\s+-c",
        ]
        self._compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self._forbidden_commands]
        LOGGER.info(
            f"Constitutional Overseer initialized with {len(self._forbidden_commands)} forbidden patterns"
        )

    async def validate_action(self, request: ActionRequest) -> ViolationCheck:
        """Validate an ActionRequest against safety rules.

        Args:
            request: The ActionRequest to validate

        Returns:
            ViolationCheck with validation result
        """
        if request.action_type == "tool_execution":
            return await self._validate_tool_execution(request)
        elif request.action_type == "file_operations":
            return await self._validate_file_operations(request)
        elif request.action_type == "diagnostic_tool_creation":
            return ViolationCheck(False, "Diagnostic tool creation is allowed")
        else:
            return ViolationCheck(True, f"Unknown action type: {request.action_type}")

    async def _validate_tool_execution(self, request: ActionRequest) -> ViolationCheck:
        """Validate tool execution requests."""
        tool_path = request.parameters.get("tool_path", "")
        args = request.parameters.get("args", [])
        if tool_path:
            Violation = self._check_forbidden_patterns(tool_path)
            if Violation:
                return Violation
        for arg in args:
            Violation = self._check_forbidden_patterns(str(arg))
            if Violation:
                return Violation
        if "shell" in request.parameters.get("execution_mode", ""):
            shell_cmd = request.parameters.get("shell_command", "")
            Violation = self._check_forbidden_patterns(shell_cmd)
            if Violation:
                return Violation
        return ViolationCheck(False, "Action validated - SAFE")

    async def _validate_file_operations(self, request: ActionRequest) -> ViolationCheck:
        """Validate file operation requests."""
        operation = request.parameters.get("operation", "")
        file_path = request.parameters.get("file_path", "")
        dangerous_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "/root/",
            "/sys/",
            "/proc/",
            "/dev/",
        ]
        for path in dangerous_paths:
            if path in file_path:
                return ViolationCheck(True, f"Access to sensitive path forbidden: {path}")
        if operation == "delete":
            critical_extensions = [".py", ".sh", ".bat", ".cmd", ".ps1"]
            if any(file_path.endswith(ext) for ext in critical_extensions):
                return ViolationCheck(True, "Deletion of executable files is forbidden")
        return ViolationCheck(False, "File operation validated - SAFE")

    def _check_forbidden_patterns(self, text: str) -> ViolationCheck:
        """Check text against forbidden command patterns.

        Args:
            text: Text to check

        Returns:
            ViolationCheck if Violation found, None if safe
        """
        for pattern in self._compiled_patterns:
            if pattern.search(text):
                return ViolationCheck(True, f"Forbidden command pattern detected: {pattern.pattern}")
        return None

    def add_forbidden_pattern(self, pattern: str) -> Any:
        """Add a new forbidden pattern.

        Args:
            pattern: Regex pattern to add
        """
        try:
            compiled: Any = re.compile(pattern, re.IGNORECASE)
            self._compiled_patterns.append(compiled)
            self._forbidden_commands.append(pattern)
            LOGGER.info(f"Added forbidden pattern: {pattern}")
        except re.error as e:
            LOGGER.error(f"Invalid regex pattern: {e}")

    def get_forbidden_patterns(self) -> list[str]:
        """Get list of forbidden patterns.

        Returns:
            List of forbidden command patterns
        """
        return self._forbidden_commands.copy()


@dataclass
class SafetyInspectorAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    L5 Safety Inspector with Socratic Judge for false positive mitigation.

    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Compliance with intelligent Violation verification.
    """

    def __init__(self, enable_socratic_judge: bool = True) -> None:
        """
        Initialize the SafetyInspectorAgent.

        Args:
            enable_socratic_judge: Whether to use LLM verification for false positives
        """
        self.enable_socratic_judge = enable_socratic_judge
        self._false_positive_cache = set()
        self.secret_patterns = [
            "api[_-]?key\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "secret[_-]?key\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "password\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "token\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "aws[_-]?access[_-]?key\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "aws[_-]?secret[_-]?key\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "private[_-]?key\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "auth[_-]?token\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "client[_-]?secret\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "database[_-]?url\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
        ]
        self.todo_patterns = ["#\\s*TODO", "#\\s*FIXME", "#\\s*HACK", "#\\s*XXX"]
        self.print_patterns = ["print\\s*\\(", "sys\\.stdout\\.write"]
        self.debugger_patterns = [
            "import pdb",
            "pdb\\.set_trace",
            "import ipdb",
            "ipdb\\.set_trace",
            "breakpoint\\(\\)",
        ]
        self.eval_patterns = ["eval\\s*\\(", "exec\\s*\\(", "__import__\\s*\\(", "compile\\s*\\("]
        LOGGER.info(f"SafetyInspectorAgent initialized (Socratic Judge: {enable_socratic_judge})")

    async def scan_file(self, file_path: str) -> dict[str, list[str]]:
        """
        Scan a file for security violations.

        Args:
            file_path: Path to the file to scan

        Returns:
            Dictionary mapping Violation types to list of violations
        """
        violations: Any = {
            "secrets": [],
            "todos": [],
            "prints": [],
            "debuggers": [],
            "empty_except": [],
            "bare_except": [],
            "evals": [],
        }
        try:
            with open(file_path, encoding="utf-8") as f:
                content: Any = f.read()
                lines: Any = content.split()
            for pattern in self.secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if self.enable_socratic_judge and file_path not in self._false_positive_cache:
                        verification: Any = await self._socratic_verify(
                            file_path,
                            f"Potential secret matching pattern: {pattern}",
                            "Is this actually a hardcoded secret or a false positive (test data, example, placeholder)?",
                        )
                        if verification == "YES":
                            violations["secrets"].append(f"Line with potential secret: {pattern}")
                        else:
                            self._false_positive_cache.add(file_path)
                            LOGGER.info(f"Socratic Judge marked as false positive: {file_path}")
                    else:
                        violations["secrets"].append(f"Line with potential secret: {pattern}")
                    break
            for i, line in enumerate(lines, 1):
                for pattern in self.todo_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations["todos"].append(f"Line {i}: {line.strip()}")
            for i, line in enumerate(lines, 1):
                for pattern in self.print_patterns:
                    if re.search(pattern, line):
                        violations["prints"].append(f"Line {i}: {line.strip()}")
            for i, line in enumerate(lines, 1):
                for pattern in self.debugger_patterns:
                    if re.search(pattern, line):
                        violations["debuggers"].append(f"Line {i}: {line.strip()}")
            for i, line in enumerate(lines, 1):
                if re.search("except\\s*:", line):
                    violations["bare_except"].append(f"Line {i}: {line.strip()}")
                elif re.search("except\\s+pass\\s*:", line) or re.search("except\\s*\\n\\s*pass", content):
                    violations["empty_except"].append(f"Line {i}: {line.strip()}")
            for i, line in enumerate(lines, 1):
                for pattern in self.eval_patterns:
                    if re.search(pattern, line):
                        if self.enable_socratic_judge and file_path not in self._false_positive_cache:
                            verification: Any = await self._socratic_verify(
                                file_path,
                                f"Dangerous eval/exec usage: {line.strip()}",
                                "Is this actually dangerous dynamic execution or a safe usage (e.g., JSON parsing, AST manipulation)?",
                            )
                            if verification == "YES":
                                violations["evals"].append(f"Line {i}: {line.strip()}")
                            else:
                                self._false_positive_cache.add(file_path)
                                LOGGER.info(f"Socratic Judge marked eval as false positive: {file_path}")
                        else:
                            violations["evals"].append(f"Line {i}: {line.strip()}")
        except Exception as e:
            LOGGER.error(f"Error scanning file {file_path}: {e}")
        return violations

    async def _socratic_verify(self, file_path: str, issue: str, question: str) -> str:
        """
        Ask LLM router MCP to verify if an issue is actually a Violation.
        Phase 16B: Replaced direct google.generativeai with sovereign LLM router.

        Args:
            file_path: Path to the file being checked
            issue: Description of the potential issue
            question: Specific question about the issue

        Returns:
            "YES" if it's a real Violation, "NO" if it's a false positive
        """
        try:
            from agentic_core.L2_execution.mcp.llm_router_mcp_client import get_llm_router_client

            llm_router = get_llm_router_client()
            with open(file_path, encoding="utf-8") as f:
                code_snippet = f.read()
            prompt = f"""\nRole: Socratic Judge - Expert Code Security Reviewer\n\nContext: Analyzing potential code Violation in {file_path}\nIssue: {issue}\nQuestion: {question}\n\nCode Snippet:\n{code_snippet[:2000]}  # Limit to first 2000 chars\n```\n\nInstructions:\n1. Analyze the code context carefully\n2. Determine if this is a REAL security Violation or just:\n   - Test data/example code\n   - Placeholder/mock value\n   - Documentation comment\n   - Safe usage of a potentially dangerous function\n\n3. Consider:\n   - Is the code in a test file?\n   - Is the value obviously fake (e.g., "xxx", "test", "example")?\n   - Is this a demonstration or documentation?\n   - Is the usage actually safe in this context?\n\nAnswer with ONLY "YES" if it's a real Violation or "NO" if it's a false positive.\n"""
            result_dict = await llm_router.validate_content(prompt, validation_type="socratic_judge")
            if isinstance(result_dict, dict):
                response_text = result_dict.get("response", result_dict.get("reason", ""))
            else:
                response_text = str(result_dict)
            result = response_text.strip().upper()
            if "YES" in result[:10]:
                LOGGER.info(f"Socratic Judge (MCP): REAL Violation in {file_path}")
                return "YES"
            elif "NO" in result[:10]:
                LOGGER.info(f"Socratic Judge (MCP): False positive in {file_path}")
                return "NO"
            else:
                LOGGER.warning(f"Socratic Judge ambiguous response: {result}")
                return "YES"
        except Exception as e:
            LOGGER.error(f"Socratic Judge (MCP) error: {e}")
            return "YES"

    def clear_false_positive_cache(self) -> Any:
        """Clear the false positive cache."""
        self._false_positive_cache.clear()
        LOGGER.info("False positive cache cleared")

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Scan repository for security violations and report findings.

        Scans Python files for hardcoded secrets, debug statements, eval/exec
        usage, and other security concerns. Safety violations require manual
        review and cannot be auto-fixed.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, generate detailed security report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        """
        super().heal_repository(dry_run=dry_run, **kwargs)

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "skipped": 0,
                "cycle_detected": True,
            }
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 0,
                "skipped": 1,
                "depth_limited": True,
            }
        _call_path.add(agent_name)

        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0

        try:
            LOGGER.info(f"[{agent_name}] Scanning repository for security violations...")

            # Scan source directories
            source_dirs = [
                Path(self.project_root) / "agentic_core",
                Path(self.project_root) / "apps_lic",
                Path(self.project_root) / "apps_rg",
                Path(self.project_root) / "apps_shared",
            ]

            all_violations = []

            for source_dir in source_dirs:
                if not source_dir.exists():
                    continue

                for py_file in source_dir.rglob("*.py"):
                    # Skip __pycache__ and test files
                    if "__pycache__" in str(py_file):
                        skipped += 1
                        continue

                    try:
                        file_violations = self.scan_file(py_file)
                        if file_violations:
                            violations_found += len(file_violations)
                            all_violations.extend(file_violations)
                    except Exception as e:
                        LOGGER.error(f"  Error scanning {py_file}: {e}")
                        errors += 1

            if violations_found > 0:
                LOGGER.warning(f"  Found {violations_found} security violations")

                if execute and not dry_run:
                    # Generate a security report (we don't auto-fix security issues)
                    import json

                    report_path = Path(self.project_root) / "logs" / "security_scan_report.json"
                    report_path.parent.mkdir(parents=True, exist_ok=True)

                    report = {
                        "scan_date": str(Path(__file__).stat().st_mtime),
                        "total_violations": violations_found,
                        "violations": [
                            {
                                "file": str(v.get("file", "")),
                                "type": v.get("type", ""),
                                "line": v.get("line", 0),
                            }
                            for v in all_violations[:100]  # Limit to 100 for report size
                        ],
                        "note": "Security violations require manual review",
                    }

                    with open(report_path, "w", encoding="utf-8") as f:
                        json.dump(report, f, indent=2)

                    LOGGER.info(f"  Generated security report: {report_path}")
                    # Note: violations_fixed stays 0 because security issues need manual review

            else:
                LOGGER.info("  No security violations found")

            LOGGER.info(f"[{agent_name}] Complete: {violations_found} violations (manual review required)")

            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": errors,
                "skipped": skipped,
                "agent": agent_name,
                "dry_run": dry_run,
                "note": "Security violations require manual review",
            }

        finally:
            _call_path.discard(agent_name)

    def heal(self, violation: dict) -> dict:
        """Heal safety inspection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (safety, constitutional, socratic)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        violation_type = violation.get("type", "")
        path = violation.get("path", "")

        Logger.info(f"[SAFETY_INSPECTOR] Inspecting {violation_type} at {path}")

        # Safety inspections require manual review
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Safety violations require manual review",
        }


def create_overseer() -> ConstitutionalOverseer:
    """Factory function to create overseer instance."""
    return ConstitutionalOverseer()


def create_safety_inspector(enable_socratic_judge: bool = True) -> SafetyInspectorAgent:
    """Factory function to create SafetyInspectorAgent instance."""
    return SafetyInspectorAgent(enable_socratic_judge)
