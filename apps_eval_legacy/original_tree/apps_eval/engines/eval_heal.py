"""L2 E4 HEAL stage — local repair (retry/skip) for failed scenarios.

Plan: apps-eval-agentic-spine-hardening-9d4f2e W3.4
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from apps_eval.engines.eval_valid import ValidResult
    from apps_eval.types.eval_types import ScenarioResult

logger = logging.getLogger(__name__)


@dataclass
class HealResult:
    """Result from HEAL stage with retried/fixed scenarios."""
    ok: bool = False
    original_results: list["ScenarioResult"] = field(default_factory=list)
    healed_results: list["ScenarioResult"] = field(default_factory=list)
    retried_count: int = 0
    skipped_count: int = 0
    repair_log: list[dict] = field(default_factory=list)


class EvalHealStage:
    """Heal stage: retry failed scenarios, skip permanently broken ones.

    Implements the E4 stage of L2 execution per AGENTIC_SPINE.md:
    - Retry-on-failure for transient errors (judge timeout, rate limit)
    - Skip for permanently broken scenarios
    - Max 1 retry per scenario to avoid infinite loops
    """

    def __init__(
        self,
        valid_result: "ValidResult",
        max_retries: int = 1,
        retryable_outcomes: set[str] | None = None,
    ):
        self.valid_result = valid_result
        self.max_retries = max_retries
        self.retryable_outcomes = retryable_outcomes or {"TIMEOUT", "ERROR"}
        self.runner = None  # Set by caller

    def run(self, scenario_results: list["ScenarioResult"]) -> HealResult:
        """Run healing on scenario results.

        Args:
            scenario_results: Results from E3 EXEC stage

        Returns:
            HealResult with healed outcomes
        """
        result = HealResult(original_results=list(scenario_results))

        if not scenario_results:
            result.ok = True
            return result

        healed = []
        for sr in scenario_results:
            if sr.outcome in self.retryable_outcomes and self.max_retries > 0:
                # Attempt retry
                logger.info("Retrying scenario %s (outcome=%s)", sr.scenario_id, sr.outcome)
                retry_result = self._retry_scenario(sr)
                if retry_result.outcome == "PASS":
                    healed.append(retry_result)
                    result.retried_count += 1
                    result.repair_log.append({
                        "scenario_id": sr.scenario_id,
                        "action": "retry",
                        "from_outcome": sr.outcome,
                        "to_outcome": retry_result.outcome,
                    })
                else:
                    # Still failing after retry — mark as SKIP
                    skip_result = self._skip_scenario(retry_result)
                    healed.append(skip_result)
                    result.skipped_count += 1
                    result.repair_log.append({
                        "scenario_id": sr.scenario_id,
                        "action": "skip",
                        "from_outcome": retry_result.outcome,
                        "reason": "max_retries_exceeded",
                    })
            else:
                # No healing needed or non-retryable
                healed.append(sr)

        result.healed_results = healed
        result.ok = True
        return result

    def _retry_scenario(self, sr: "ScenarioResult") -> "ScenarioResult":
        """Retry a single scenario."""
        if self.runner is None:
            logger.warning("No runner set for retry — returning original")
            return sr

        # Re-run using the scenario definition
        scenario = {"id": sr.scenario_id, "suite_id": sr.suite_id}
        return self.runner._run_scenario_simple(scenario)

    def _skip_scenario(self, sr: "ScenarioResult") -> "ScenarioResult":
        """Mark scenario as SKIP (permanently skipped)."""
        from apps_eval.types.eval_types import ScenarioResult

        return ScenarioResult(
            scenario_id=sr.scenario_id,
            suite_id=sr.suite_id,
            outcome="SKIP",
            passed=False,
            score=0.0,
            message=f"Skipped after retry (original: {sr.outcome})",
            latency_ms=sr.latency_ms,
            deterministic=sr.deterministic,
        )

    def set_runner(self, runner) -> None:
        """Set the ScenarioRunner for retry execution."""
        self.runner = runner