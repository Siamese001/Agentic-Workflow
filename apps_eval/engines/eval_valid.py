"""L2 E2 VALID stage — validate schema, thresholds, judge availability."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps_eval.engines.eval_prep import PrepResult

logger = logging.getLogger(__name__)


@dataclass
class ValidResult:
    ok: bool = False
    failure_reason: str | None = None
    prep_result: "PrepResult | None" = None
    schema_valid: bool = False
    thresholds_valid: bool = False
    judge_available: bool = True

    @property
    def deterministic_only(self) -> bool:
        """Pass through from prep_result for FEC resolution."""
        if self.prep_result:
            return self.prep_result.deterministic_only
        return False


class EvalValidStage:
    """Validate evaluation inputs before execution."""

    def __init__(self, prep_result: "PrepResult"):
        self.prep_result = prep_result

    def run(self) -> ValidResult:
        result = ValidResult(prep_result=self.prep_result)

        # Validate scenario JSON schema
        result.schema_valid = self._validate_scenario_schema()
        if not result.schema_valid:
            result.failure_reason = "schema_validation_failed"
            return result

        # Validate threshold profile exists and has dimensions
        result.thresholds_valid = self._validate_thresholds()
        if not result.thresholds_valid:
            result.failure_reason = "threshold_validation_failed"
            return result

        # Validate judge availability (unless deterministic-only)
        if not self.prep_result.deterministic_only:
            result.judge_available = self._check_judge_available()
            if not result.judge_available:
                # Degraded mode - still ok but skip judge dims
                logger.warning("Judge unavailable; running deterministic-only")

        result.ok = True
        return result

    def _validate_scenario_schema(self) -> bool:
        """Validate scenario JSON against schema."""
        # TODO: Implement JSON schema validation (deferred)
        return True

    def _validate_thresholds(self) -> bool:
        """Validate threshold profile exists and has dimensions."""
        # TODO: Implement threshold profile validation (deferred)
        return True

    def _check_judge_available(self) -> bool:
        """Check if Qwen judge is available (heartbeat)."""
        # TODO: Implement Qwen heartbeat check (deferred)
        return True
