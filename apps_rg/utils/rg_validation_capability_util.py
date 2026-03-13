"""
RGValidationCapability — Pure capability mixin for RG validation agents.

Extracts the shared validation harness that all RG validation agents repeat:
  - Log-prefixed execution entry
  - Issue collection via abstract collect_issues()
  - Pass/fail recording with signal management
  - Content-to-string conversion utility
  - Standard heal stub generation

The domain-specific check logic remains in each agent's collect_issues() override.
Agents compose this via multiple inheritance alongside RGAgentBase.

    @dataclass
    class SomeValidationAgent(RGValidationCapability, RGAgentBase):
        VALIDATION_SIGNAL = "SOME_FAILURE"
        VALIDATION_LOG_PREFIX = "Checking something..."
        VALIDATION_PASS_MESSAGE = "All checks passed"
        VALIDATION_FAIL_PREFIX = "Check issues"

        async def collect_issues(self) -> list[str]:
            ...  # domain-specific logic

RESPONSIBILITY COHESION: This capability must NOT contain domain-specific words.
It only knows about "checks", "issues", "scores", and "signals".

[CREATED 2026-02-08] Cluster 2 extraction per Pure Harness pattern.
"""

from __future__ import annotations

import json
from typing import Any, ClassVar


class RGValidationCapability:
    """Pure capability mixin for RG validation loop agents.

    Provides:
        - run_validation(): Template method with log → collect → record → signal
        - collect_issues(): Abstract — each agent implements domain checks
        - content_to_string(): Shared content-to-string converter
        - make_heal_result(): Standard heal stub generator

    Subclasses MUST:
        - Set VALIDATION_SIGNAL (e.g., "CHECK_FAILURE")
        - Set VALIDATION_LOG_PREFIX (e.g., "Running checks...")
        - Set VALIDATION_PASS_MESSAGE (e.g., "All checks passed")
        - Set VALIDATION_FAIL_PREFIX (e.g., "Check issues")
        - Override collect_issues() with domain-specific validation logic
    """

    VALIDATION_SIGNAL: ClassVar[str] = ""
    VALIDATION_LOG_PREFIX: ClassVar[str] = "Running validation..."
    VALIDATION_PASS_MESSAGE: ClassVar[str] = "Validation passed"
    VALIDATION_FAIL_PREFIX: ClassVar[str] = "Validation issues"

    async def run_validation(self) -> None:
        """Template method: log → collect issues → record pass/fail + signal.

        Calls self.log(), self.record_pass(), self.record_fail(),
        self.add_signal(), self.remove_signal() — all provided by RGAgentBase.
        """
        if not self.VALIDATION_SIGNAL:
            raise ValueError(f"{self.__class__.__name__} must set VALIDATION_SIGNAL")
        self.log(self.VALIDATION_LOG_PREFIX)
        issues = await self.collect_issues()
        if issues:
            self.record_fail(f"{self.VALIDATION_FAIL_PREFIX}: {len(issues)}", data=issues)
            self.add_signal(self.VALIDATION_SIGNAL)
        else:
            self.record_pass(self.VALIDATION_PASS_MESSAGE)
            self.remove_signal(self.VALIDATION_SIGNAL)

    async def collect_issues(self) -> list[str]:
        """Collect domain-specific validation issues. Must be overridden.

        Returns:
            List of issue description strings. Empty list means passed.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_issues()")

    @staticmethod
    def content_to_string(content: Any) -> str:
        """Convert heterogeneous content to a flat string for analysis.

        Handles str, list, dict, and other types uniformly.

        Args:
            content: Content to convert (str, list, dict, or other).

        Returns:
            String representation of content.
        """
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return " ".join(str(item) for item in content)
        if isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def make_heal_result(self, violation: dict[str, Any], *, status: str = "skipped") -> dict[str, Any]:
        """Generate a standard heal stub result.

        Args:
            violation: The violation dict being healed.
            status: Heal status (default "skipped").

        Returns:
            Canonical heal result dict.
        """
        violation_type = violation.get("type", "unknown")
        return {
            "status": status,
            "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }
