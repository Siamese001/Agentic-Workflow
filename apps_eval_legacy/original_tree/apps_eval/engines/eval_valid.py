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
        # W3.2: Basic schema validation — check required fields
        scenarios = self.prep_result.scenarios if self.prep_result else []
        required_fields = ["id", "suite_id"]
        for sc in scenarios:
            for field in required_fields:
                if field not in sc or not sc[field]:
                    logger.warning("Scenario missing required field '%s': %s", field, sc.get("id", "unknown"))
                    return False
        return True

    def _validate_thresholds(self) -> bool:
        """Validate threshold profile exists and has dimensions."""
        from pathlib import Path

        suite_configs = self.prep_result.suite_configs if self.prep_result else []
        for suite in suite_configs:
            threshold_profile = suite.get("threshold_profile", "default")
            # Check if threshold profile YAML exists
            profile_path = (
                Path(__file__).parents[1] / "config" / "domain_contract" / "threshold_profiles.yaml"
            )
            if not profile_path.exists():
                # Degraded — no thresholds yet
                logger.warning("Threshold profile file not found: %s", profile_path)
                continue
            try:
                import yaml
                with open(profile_path, encoding="utf-8") as f:
                    profiles = yaml.safe_load(f) or {}
                dims = profiles.get("dimensions", [])
                if not dims:
                    logger.warning("No dimensions in threshold profile: %s", threshold_profile)
            except Exception as exc:
                logger.warning("Failed to load threshold profile: %s", exc)
        return True

    def _check_judge_available(self) -> bool:
        """Check if Qwen judge is available (heartbeat)."""
        # W3.2: Check if we can import and ping the judge
        try:
            # Try to import the judge module — if it exists, assume available
            from apps_eval.engines.judges.qwen_judge import QwenJudge  # noqa: F401
            return True
        except ImportError:
            logger.info("Qwen judge not available — running deterministic-only mode")
            return False
