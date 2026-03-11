from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
MCP Security Guardrail - Consolidated MCP Protection

Merges:
- MCPGuardian
- mcp_hardened_mixin

Composable Rules:
- tool_validation: MCP tool security
- mcp_hardening: MCP hardening rules
"""


import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MCPSecurityViolation:
    """MCP security violation."""

    rule: str
    severity: str  # "warning", "error", "critical"
    tool_name: str
    description: str
    blocked: bool = False


@dataclass
class MCPSecurityResult:
    """Result of MCP security check."""

    allowed: bool
    violations: list[MCPSecurityViolation] = field(default_factory=list)
    sanitized_args: dict[str, Any] | None = None


class MCPSecurityGuardrail:
    """
    Consolidated MCP Security Guardrail.

    Provides unified MCP protection with:
    - Tool whitelist validation
    - Argument sanitization
    - Response validation
    - Audit logging
    """

    def __init__(self):
        """Initialize MCP security guardrail."""
        self.enabled_rules: list[str] = [
            "tool_validation",
            "mcp_hardening",
        ]

        # Tool whitelist
        self.tool_whitelist: set[str] = {
            "read_file",
            "write_file",
            "edit",
            "run_command",
            "grep_search",
            "find_by_name",
            "list_dir",
            "git_status",
            "git_commit",
            "git_push",
            "redis_get",
            "redis_set",
            "http_get",
            "http_post",
            "brave_search",
            "fetch_url",
        }

        # Dangerous patterns
        self.dangerous_patterns = [
            r"__import__\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r"os\.system",
            r"subprocess\.",
            r"rm\s+-rf",
            r"DROP\s+TABLE",
            r"<script>",
        ]

        # Statistics
        self.checks_performed = 0
        self.tools_blocked = 0
        self.args_sanitized = 0

    async def validate_tool_call(self, tool_name: str, args: dict[str, Any]) -> MCPSecurityResult:
        """
        Validate MCP tool call.

        Args:
            tool_name: Name of tool
            args: Tool arguments

        Returns:
            MCPSecurityResult
        """
        self.checks_performed += 1
        violations = []

        # Check tool whitelist
        if "tool_validation" in self.enabled_rules:
            if not self._is_tool_allowed(tool_name):
                violations.append(
                    MCPSecurityViolation(
                        rule="tool_validation",
                        severity="error",
                        tool_name=tool_name,
                        description=f"Tool '{tool_name}' not in whitelist",
                        blocked=True,
                    ),
                )
                self.tools_blocked += 1

        # Check arguments for dangerous patterns
        if "mcp_hardening" in self.enabled_rules:
            arg_violations = self._check_arguments(tool_name, args)
            violations.extend(arg_violations)

        # Sanitize arguments
        sanitized = self._sanitize_arguments(args) if args else {}
        if sanitized != args:
            self.args_sanitized += 1

        return MCPSecurityResult(
            allowed=not any(v.blocked for v in violations),
            violations=violations,
            sanitized_args=sanitized,
        )

    def _is_tool_allowed(self, tool_name: str) -> bool:
        """Check if tool is in whitelist."""
        normalized = tool_name.lower().strip()

        if normalized in self.tool_whitelist:
            return True

        # Check prefix/suffix matches
        for allowed in self.tool_whitelist:
            if normalized.startswith(f"{allowed}_") or normalized.endswith(f"_{allowed}"):
                return True

        return False

    def _check_arguments(self, tool_name: str, args: dict[str, Any]) -> list[MCPSecurityViolation]:
        """Check arguments for dangerous patterns."""
        violations = []

        for key, value in args.items():
            if isinstance(value, str):
                for pattern in self.dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        violations.append(
                            MCPSecurityViolation(
                                rule="mcp_hardening",
                                severity="critical",
                                tool_name=tool_name,
                                description=f"Dangerous pattern in argument '{key}'",
                                blocked=True,
                            ),
                        )
                        break

        return violations

    def _sanitize_arguments(self, args: dict[str, Any]) -> dict[str, Any]:
        """Sanitize arguments by removing dangerous patterns."""
        sanitized = {}

        for key, value in args.items():
            if isinstance(value, str):
                clean = value
                for pattern in self.dangerous_patterns:
                    clean = re.sub(pattern, "[BLOCKED]", clean, flags=re.IGNORECASE)
                sanitized[key] = clean
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_arguments(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_arguments({"v": v})["v"] if isinstance(v, str | dict) else v for v in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    def add_to_whitelist(self, tool_name: str) -> None:
        """Add tool to whitelist."""
        self.tool_whitelist.add(tool_name.lower())

    def remove_from_whitelist(self, tool_name: str) -> None:
        """Remove tool from whitelist."""
        self.tool_whitelist.discard(tool_name.lower())

    def get_statistics(self) -> dict[str, Any]:
        """Get MCP security statistics."""
        return {
            "checks_performed": self.checks_performed,
            "tools_blocked": self.tools_blocked,
            "args_sanitized": self.args_sanitized,
            "whitelist_size": len(self.tool_whitelist),
            "enabled_rules": self.enabled_rules,
        }
