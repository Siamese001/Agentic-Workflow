"""Scorecard & Regression — aggregate scoring and cross-digest comparison.

Provides:
- ``JudgeScorecard``    — weighted multi-dimension scorecard from JudgeReports
- ``RegressionAnalyzer`` — compare two evaluation runs and flag regressions

Usage::

    scorecard = JudgeScorecard()
    result = scorecard.compute([report1, report2, report3])
    print(result["overall_score"], result["dimension_scores"])

    analyzer = RegressionAnalyzer(verdict_store)
    regressions = analyzer.compare("new_digest", "old_digest")
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from agentic_core.evaluation.judges.types import (
    JudgeReport,
    VerdictOutcome,
)
from agentic_core.evaluation.judges.verdict_store import VerdictStore
from tqdm import tqdm

_log = logging.getLogger(__name__)

# Default dimension weights for overall scoring
_DEFAULT_WEIGHTS: dict[str, float] = {
    "architecture": 1.5,
    "code_quality": 1.0,
    "dependency_health": 1.2,
    "governance_coverage": 1.5,
    "governance_quality": 1.3,
    "security": 2.0,
}


class JudgeScorecard:
    """Weighted multi-dimension scorecard computed from JudgeReports.

    Aggregates verdicts across multiple modules and dimensions,
    applying configurable weights to produce an overall quality score.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self._weights = weights or dict(_DEFAULT_WEIGHTS)

    def compute(self, reports: list[JudgeReport]) -> dict[str, Any]:
        """Compute a weighted scorecard from multiple JudgeReports.

        Returns:
            Dict with overall_score, dimension_scores, fail_summary,
            module_scores, and metadata.
        """
        if not reports:
            return {
                "overall_score": 0.0,
                "dimension_scores": {},
                "fail_summary": [],
                "module_scores": [],
                "total_verdicts": 0,
                "total_modules": 0,
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }

        # Collect all verdicts grouped by dimension
        dim_scores: dict[str, list[float]] = {}
        dim_outcomes: dict[str, list[str]] = {}
        module_scores: list[dict[str, Any]] = []
        fail_summary: list[dict[str, Any]] = []
        total_verdicts = 0

        for report in tqdm(reports, desc="Processing", unit="item"):
            mod_score = {
                "target": report.target,
                "overall_score": report.overall_score,
                "passed": report.passed,
                "fail_count": report.fail_count,
                "warn_count": report.warn_count,
                "verdict_count": len(report.verdicts),
            }
            module_scores.append(mod_score)

            for verdict in tqdm(report.verdicts, desc="Processing", unit="item"):
                if verdict.outcome == VerdictOutcome.SKIP.value:
                    continue
                total_verdicts += 1
                dim_scores.setdefault(verdict.dimension, []).append(verdict.score)
                dim_outcomes.setdefault(verdict.dimension, []).append(verdict.outcome)

                if verdict.outcome == VerdictOutcome.FAIL.value:
                    fail_summary.append(
                        {
                            "target": report.target,
                            "dimension": verdict.dimension,
                            "rubric_id": verdict.rubric_id,
                            "score": verdict.score,
                            "severity": verdict.severity,
                            "reasoning": verdict.reasoning[:200],
                        },
                    )

        # Compute dimension averages
        dimension_results: dict[str, dict[str, Any]] = {}
        for dim, scores in tqdm(sorted(dim_scores.items()), desc="Processing", unit="item"):
            avg = round(sum(scores) / len(scores), 4)
            outcomes = dim_outcomes.get(dim, [])
            fail_count = outcomes.count(VerdictOutcome.FAIL.value)
            warn_count = outcomes.count(VerdictOutcome.WARN.value)

            if fail_count > 0:
                outcome = VerdictOutcome.FAIL.value
            elif warn_count > 0:
                outcome = VerdictOutcome.WARN.value
            else:
                outcome = VerdictOutcome.PASS.value

            dimension_results[dim] = {
                "average_score": avg,
                "outcome": outcome,
                "verdict_count": len(scores),
                "fail_count": fail_count,
                "warn_count": warn_count,
                "weight": self._weights.get(dim, 1.0),
            }

        # Weighted overall score
        weighted_sum = 0.0
        total_weight = 0.0
        for dim, data in dimension_results.items():
            w = data["weight"]
            weighted_sum += data["average_score"] * w
            total_weight += w

        overall = round(weighted_sum / total_weight, 4) if total_weight > 0 else 0.0

        # Sort failures by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        fail_summary.sort(key=lambda f: severity_order.get(f["severity"], 99))

        return {
            "overall_score": overall,
            "dimension_scores": dimension_results,
            "fail_summary": fail_summary,
            "module_scores": sorted(module_scores, key=lambda m: m["overall_score"]),
            "total_verdicts": total_verdicts,
            "total_modules": len(reports),
            "passed": all(r.passed for r in reports),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    def render_text(self, result: dict[str, Any]) -> str:
        """Render scorecard result as human-readable text."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("  LLM-as-Judge Scorecard")
        lines.append("=" * 60)
        lines.append(f"  Overall Score: {result['overall_score']:.4f}")
        lines.append(f"  Status: {'PASS' if result.get('passed') else 'FAIL'}")
        lines.append(
            f"  Modules: {result['total_modules']}  |  Verdicts: {result['total_verdicts']}",
        )
        lines.append("-" * 60)

        for dim, data in sorted(
            result.get("dimension_scores", {}).items(),
            key=lambda x: x[1]["average_score"],
        ):
            icon = "PASS" if data["outcome"] == "PASS" else "WARN" if data["outcome"] == "WARN" else "FAIL"
            lines.append(
                f"  [{icon}] {dim:<25} {data['average_score']:.4f}  "
                f"(w={data['weight']:.1f}, n={data['verdict_count']})",
            )

        if result.get("fail_summary"):
            lines.append("-" * 60)
            lines.append("  Failures:")
            for f in result["fail_summary"][:10]:
                lines.append(
                    f"    [{f['severity']}] {f['rubric_id']} @ {f['target']}: {f['reasoning'][:80]}",
                )

        lines.append("=" * 60)
        return "\n".join(lines)


class RegressionAnalyzer:
    """Compare two evaluation runs and flag regressions.

    Uses VerdictStore to compare verdicts between two ADG digests.
    """

    def __init__(
        self,
        verdict_store: VerdictStore,
        regression_threshold: float = 0.05,
    ) -> None:
        self._store = verdict_store
        self._threshold = regression_threshold

    def compare(
        self,
        current_digest: str,
        previous_digest: str,
    ) -> dict[str, Any]:
        """Compare verdicts between two ADG digests.

        Returns:
            Dict with regressions, improvements, stable counts, and summary.
        """
        raw_regressions = self._store.regressions(current_digest, previous_digest)

        # Filter by threshold
        significant = [r for r in raw_regressions if abs(r["delta"]) >= self._threshold]

        # Also check for improvements (score increased)
        current_verdicts = self._store.query_by_digest(current_digest)
        previous_verdicts = self._store.query_by_digest(previous_digest)

        current_map = {(v.target, v.rubric_id): v for v in current_verdicts}
        previous_map = {(v.target, v.rubric_id): v for v in previous_verdicts}

        improvements: list[dict[str, Any]] = []
        stable = 0

        for key, curr in tqdm(current_map.items(), desc="Processing", unit="item"):
            prev = previous_map.get(key)
            if prev is None:
                continue
            delta = curr.score - prev.score
            if delta > self._threshold:
                improvements.append(
                    {
                        "target": curr.target,
                        "rubric_id": curr.rubric_id,
                        "dimension": curr.dimension,
                        "current_score": curr.score,
                        "previous_score": prev.score,
                        "delta": round(delta, 4),
                    },
                )
            elif abs(delta) <= self._threshold:
                stable += 1

        new_failures = [
            r
            for r in significant
            if r["current_outcome"] == VerdictOutcome.FAIL.value
            and r["previous_outcome"] != VerdictOutcome.FAIL.value
        ]

        return {
            "current_digest": current_digest,
            "previous_digest": previous_digest,
            "regressions": significant,
            "regression_count": len(significant),
            "new_failures": new_failures,
            "new_failure_count": len(new_failures),
            "improvements": improvements,
            "improvement_count": len(improvements),
            "stable_count": stable,
            "threshold": self._threshold,
            "has_regressions": len(significant) > 0,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def render_text(self, result: dict[str, Any]) -> str:
        """Render regression analysis as human-readable text."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("  Regression Analysis")
        lines.append("=" * 60)
        lines.append(f"  Current:  {result['current_digest']}")
        lines.append(f"  Previous: {result['previous_digest']}")
        lines.append(
            f"  Regressions: {result['regression_count']}  |  "
            f"Improvements: {result['improvement_count']}  |  "
            f"Stable: {result['stable_count']}",
        )

        if result["regressions"]:
            lines.append("-" * 60)
            lines.append("  Regressions:")
            for r in result["regressions"]:
                lines.append(
                    f"    {r['rubric_id']} @ {r['target']}: "
                    f"{r['previous_score']:.4f} -> {r['current_score']:.4f} "
                    f"(delta={r['delta']:+.4f})",
                )

        if result["new_failures"]:
            lines.append("-" * 60)
            lines.append("  NEW FAILURES (was not FAIL before):")
            for f in result["new_failures"]:
                lines.append(
                    f"    {f['rubric_id']} @ {f['target']}: "
                    f"{f['previous_outcome']} -> {f['current_outcome']}",
                )

        if result["improvements"]:
            lines.append("-" * 60)
            lines.append("  Improvements:")
            for i in result["improvements"][:5]:
                lines.append(
                    f"    {i['rubric_id']} @ {i['target']}: "
                    f"{i['previous_score']:.4f} -> {i['current_score']:.4f} "
                    f"(delta={i['delta']:+.4f})",
                )

        lines.append("=" * 60)
        return "\n".join(lines)


__all__ = ["JudgeScorecard", "RegressionAnalyzer"]
