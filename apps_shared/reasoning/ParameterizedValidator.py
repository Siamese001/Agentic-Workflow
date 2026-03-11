"""ParameterizedValidator — Shared parameterized validation base for LIC and RG domains.

Extracted from LICValidationExecutor and RGValidationExecutor (2026-03-11, P3-A).
Both app validation executors share the same execute()/collect_issues() skeleton
with a rule-registry dispatch pattern. This base captures that skeleton.

Usage:
    class MyValidator(ParameterizedValidator):
        pass

    @MyValidator.register_rule("my_rule")
    def _my_rule_handler(self, data, **kwargs):
        return [{"type": "violation", ...}]

    v = MyValidator(rule_set="my_rule")
    result = v.execute(data)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


@dataclass
class ParameterizedValidator(SovereignBaseAgent):
    """Generic parameterized validator with rule-registry dispatch.

    Subclasses register rule handlers via `@SubClass.register_rule("name")`
    or by populating `_RULE_REGISTRY` at class level.

    The `execute()` method calls `collect_issues()` and wraps the result
    in a standard dict with keys: rule_set, issues, issue_count, passed.
    """

    rule_set: str = "generic"

    # Per-subclass rule registry. Subclasses should define their own
    # class-level dict OR use the register_rule() classmethod decorator.
    _RULE_REGISTRY: dict[str, Callable] = {}

    @classmethod
    def register_rule(cls, name: str) -> Callable:
        """Decorator to register a collect_issues implementation under `name`."""

        def decorator(func: Callable) -> Callable:
            cls._RULE_REGISTRY[name] = func
            return func

        return decorator

    def execute(self, data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Execute validation and return a standard result dict."""
        issues = self.collect_issues(data, **kwargs)
        return {
            "rule_set": self.rule_set,
            "issues": issues,
            "issue_count": len(issues),
            "passed": len(issues) == 0,
        }

    def collect_issues(self, data: dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        """Dispatch to the registered rule handler for self.rule_set."""
        handler = self._RULE_REGISTRY.get(self.rule_set)
        if handler is None:
            return [
                {
                    "type": "unknown_rule_set",
                    "severity": "high",
                    "message": f"No handler for rule_set={self.rule_set!r}",
                },
            ]
        return handler(self, data, **kwargs)

    def heal_repository(self) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Heal violations — not yet implemented at base level."""
        violation_type = violation.get("type", "unknown")
        return {
            "status": "skipped",
            "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }
