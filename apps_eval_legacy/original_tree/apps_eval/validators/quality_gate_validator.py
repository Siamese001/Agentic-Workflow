"""
Quality Gate Validator — Enforces evaluation quality standards.

SVP Standards:
- Explicit threshold enforcement
- No silent degradation
- Evidence-based decisions
"""

from __future__ import annotations

import logging
from typing import Any

from apps_eval.types import EvalResult

_log = logging.getLogger(__name__)


class QualityGateValidator:
    """Enforces quality gates for evaluation results."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._violations: list[str] = []

    def validate(self, result: EvalResult) -> tuple[bool, list[str]]:
        """
        Validate evaluation result against quality gates.

        Returns:
            (passed, violations) tuple
        """
        self._violations = []

        # Gate 1: Minimum scenarios executed
        min_scenarios = self.config.get("min_scenarios", 1)
        total_scenarios = sum(len(suite.scenarios) for suite in result.suite_results)
        if total_scenarios < min_scenarios:
            self._violations.append(
                f"QUALITY: Only {total_scenarios} scenarios executed, minimum {min_scenarios} required",
            )

        # Gate 2: Maximum latency
        max_latency = self.config.get("max_latency_ms", 30000)
        for suite in result.suite_results:
            if suite.mean_latency_ms > max_latency:
                self._violations.append(
                    f"QUALITY: Suite {suite.suite_id} latency {suite.mean_latency_ms:.0f}ms "
                    f"exceeds maximum {max_latency}ms",
                )

        # Gate 3: Regression detection
        if result.regression_records:
            for record in result.regression_records:
                if record.verdict == "REGRESSION":
                    self._violations.append(
                        f"QUALITY: Regression detected in {record.dimension_id}: "
                        f"{record.baseline_score:.2f} → {record.current_score:.2f}",
                    )

        # Gate 4: Completeness check
        for suite in result.suite_results:
            if suite.error:
                self._violations.append(
                    f"QUALITY: Suite {suite.suite_id} incomplete: {suite.error}",
                )

        passed = len(self._violations) == 0
        return passed, self._violations
