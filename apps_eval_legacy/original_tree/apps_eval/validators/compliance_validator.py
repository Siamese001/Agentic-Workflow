"""
Compliance Validator — Ensures evaluation runs meet policy requirements.

SVP Standards:
- Explicit error handling
- No silent exceptions
- Evidence-based validation
"""

from __future__ import annotations

import logging
from typing import Any

from apps_eval.types import EvalRequest, EvalResult, SuiteResult

_log = logging.getLogger(__name__)


class ComplianceValidator:
    """Validates evaluation runs against compliance policies."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._violations: list[str] = []

    def validate(self, request: EvalRequest, result: EvalResult) -> tuple[bool, list[str]]:
        """
        Validate evaluation result against compliance policies.

        Returns:
            (passed, violations) tuple
        """
        self._violations = []

        # Validate minimum pass rate
        if result.overall_score < request.config.min_pass_rate:
            self._violations.append(
                f"COMPLIANCE: Overall score {result.overall_score:.2f} below minimum "
                f"{request.config.min_pass_rate:.2f}",
            )

        # Validate deterministic results requirement
        if request.config.require_deterministic:
            for suite in result.suite_results:
                if not self._validate_deterministic(suite):
                    break

        # Validate no critical failures
        for suite in result.suite_results:
            for scenario in suite.scenarios:
                if scenario.outcome == "ERROR":
                    self._violations.append(
                        f"COMPLIANCE: Critical error in {scenario.scenario_id}: {scenario.message}",
                    )

        passed = len(self._violations) == 0
        return passed, self._violations

    def _validate_deterministic(self, suite: SuiteResult) -> bool:
        """Validate that suite results are deterministic."""
        for scenario in suite.scenarios:
            if not scenario.deterministic:
                self._violations.append(
                    f"COMPLIANCE: Non-deterministic result in {scenario.scenario_id}",
                )
                return False
        return True
