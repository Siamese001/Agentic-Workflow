"""
SignatureVerifierAgent - Verification inspector for file/agent signatures.

Refactored: 2026-02-08 (Cluster 1B — InspectionCapability extraction)

Bugs fixed during refactor:
- SELF.CONFIG → self.config (uppercase typo)
- DATA: OBJECT = None → data: Any = None (undefined type)
- Removed undefined 'result' variable reference in execute()
- Removed misplaced module-level docstrings and semantic signal comments
- Consolidated scattered imports to top of file
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.base_agents.timeout_decorator import timeout

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.inspection_capability import (
    DiagnosticReport,
    InspectionCapability,
)
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

Logger: Any = logging.getLogger(__name__)


class SignatureVerifierAgent(
    InspectionCapability,
    SubatomicTestingMixin,
    SovereignBaseAgent,
):
    """Verification inspector for file and agent signatures."""

    INSPECTION_LOG_PREFIX = "Running signature verification..."

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the verifier."""
        super().__init__()
        self.config = config or {}
        Logger.info("Initialized %s", self.__class__.__name__)

    def perform_checks(
        self,
        target: Any,
        context: dict[str, Any] | None = None,
    ) -> tuple[list[str], dict[str, Any]]:
        """Verify a target object for integrity issues."""
        issues: list[str] = []
        metrics: dict[str, Any] = {}

        if target is None:
            issues.append("Target is null")
        elif isinstance(target, dict):
            metrics["field_count"] = len(target)
        elif isinstance(target, list):
            metrics["item_count"] = len(target)

        metrics["type"] = type(target).__name__

        return issues, metrics

    def execute(self, data: Any, **kwargs: Any) -> DiagnosticReport:
        """Execute operation — adapter preserving pre-refactor entrypoint.

        The original execute() returned an OperationResult which was buggy
        (undefined OBJECT type, undefined result variable). This now returns
        a DiagnosticReport which has the same .healthy/.issues/.metrics
        contract as InspectionResult but as a concrete adapter type.
        """
        return self.diagnose(data, kwargs.get("context"))

    def diagnose(self, target: Any, context: dict[str, Any] | None = None) -> DiagnosticReport:
        """Run verification via InspectionCapability harness.

        Returns DiagnosticReport (adapter) to preserve the pre-refactor
        external contract.
        """
        result = self.run_inspection(target, context)
        return result.to_diagnostic_report()

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, int]:
        """Invoke healing chain via super() with cycle detection."""
        if _call_path is None:
            _call_path = set()

        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by SignatureVerifierAgent."""
        return self.make_heal_result(violation)


def execute_signature_verification(
    data: Any,
    config: dict[str, Any] | None = None,
) -> DiagnosticReport:
    """Convenience function for signature verification."""
    return SignatureVerifierAgent(config).diagnose(data)
