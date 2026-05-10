"""Heuristic scorer calibration - compare predictions to actual outcomes.

Plan: author-gate-ask-ui-deferred-scope-a2e3f8 D6.

Analyzes historical decisions to validate and improve confidence scoring.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import statistics

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"


@dataclass
class CalibrationResult:
    """Calibration analysis result."""
    
    n_samples: int = 0
    mean_error: float = 0.0
    std_error: float = 0.0
    correlation: float = 0.0
    calibration_bias: float = 0.0  # Positive = overconfident
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "n_samples": self.n_samples,
            "mean_error": round(self.mean_error, 3),
            "std_error": round(self.std_error, 3),
            "correlation": round(self.correlation, 3) if self.n_samples >= 3 else None,
            "calibration_bias": round(self.calibration_bias, 3),
        }


def load_historical_decisions(
    min_confidence: float = 0.60,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Load historical decisions with outcomes for calibration.
    
    Returns decisions from ask_user_question ledger that have outcomes recorded.
    """
    if not LEDGER_PATH.exists():
        return []
    
    since = (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)).isoformat()
    
    conn = sqlite3.connect(LEDGER_PATH)
    try:
        # Query decisions with their outcomes
        rows = conn.execute(
            """SELECT 
                d.decision_id, d.confidence_score, d.decision_type,
                o.execution_completed, o.tests_passed, o.regression_found
            FROM ask_user_question_decisions d
            LEFT JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.created_at >= ? AND d.confidence_score >= ?
            """,
            (since, min_confidence),
        ).fetchall()
        
        decisions = []
        for row in rows:
            decision_id, confidence, dec_type, executed, tests_passed, regression = row
            
            # Determine actual outcome (1.0 = success, 0.0 = failure)
            if executed and tests_passed and not regression:
                actual = 1.0
            elif executed and (not tests_passed or regression):
                actual = 0.0
            else:
                continue  # Skip unresolved decisions
            
            decisions.append({
                "decision_id": decision_id,
                "predicted": confidence,
                "actual": actual,
                "decision_type": dec_type or "unknown",
            })
        
        return decisions
    finally:
        conn.close()


def compute_calibration(decisions: list[dict[str, Any]]) -> CalibrationResult:
    """Compute calibration metrics from historical decisions.
    
    Compares predicted confidence vs actual success rate.
    """
    if len(decisions) < 2:
        return CalibrationResult(n_samples=len(decisions))
    
    predicted = [d["predicted"] for d in decisions]
    actual = [d["actual"] for d in decisions]
    
    # Prediction errors (positive = overconfident)
    errors = [p - a for p, a in zip(predicted, actual)]
    
    mean_error = statistics.mean(errors)
    std_error = statistics.stdev(errors) if len(errors) >= 2 else 0.0
    
    # Pearson correlation
    try:
        n = len(predicted)
        mean_p = statistics.mean(predicted)
        mean_a = statistics.mean(actual)
        
        numerator = sum((p - mean_p) * (a - mean_a) for p, a in zip(predicted, actual))
        denom_p = sum((p - mean_p) ** 2 for p in predicted) ** 0.5
        denom_a = sum((a - mean_a) ** 2 for a in actual) ** 0.5
        
        correlation = numerator / (denom_p * denom_a) if denom_p * denom_a > 0 else 0.0
    except Exception:
        correlation = 0.0
    
    return CalibrationResult(
        n_samples=len(decisions),
        mean_error=mean_error,
        std_error=std_error,
        correlation=correlation,
        calibration_bias=mean_error,  # Positive = overconfident
    )


def suggest_weight_adjustments(calibration: CalibrationResult) -> dict[str, Any]:
    """Suggest weight adjustments based on calibration results."""
    suggestions = {
        "bias_direction": "overconfident" if calibration.calibration_bias > 0.05 else 
                         "underconfident" if calibration.calibration_bias < -0.05 else "neutral",
        "recommendations": [],
    }
    
    if calibration.calibration_bias > 0.10:
        suggestions["recommendations"].append(
            "Scorer is overconfident. Consider reducing base confidence or increasing blast radius penalty."
        )
    elif calibration.calibration_bias < -0.10:
        suggestions["recommendations"].append(
            "Scorer is underconfident. Consider increasing weights on positive signals (tests, precedent)."
        )
    
    if calibration.correlation is not None and calibration.correlation < 0.3:
        suggestions["recommendations"].append(
            "Low correlation between confidence and outcomes. Review scoring formula."
        )
    
    if calibration.std_error > 0.20:
        suggestions["recommendations"].append(
            "High variance in predictions. Consider adding more signal components."
        )
    
    if not suggestions["recommendations"]:
        suggestions["recommendations"].append("Calibration is acceptable. No changes recommended.")
    
    return suggestions


def generate_calibration_report(days: int = 30) -> dict[str, Any]:
    """Generate full calibration report."""
    decisions = load_historical_decisions(days=days)
    calibration = compute_calibration(decisions)
    suggestions = suggest_weight_adjustments(calibration)
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "sample_size": len(decisions),
        "calibration": calibration.to_dict(),
        "suggestions": suggestions,
    }


def main() -> int:
    """CLI for calibration report."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Heuristic scorer calibration")
    parser.add_argument("--report", action="store_true", help="Generate calibration report")
    parser.add_argument("--days", type=int, default=30, help="Analysis period")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.report:
        report = generate_calibration_report(days=args.days)
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("Heuristic Scorer Calibration Report")
            print(f"Generated: {report['generated_at']}")
            print(f"Period: Last {report['period_days']} days")
            print(f"Sample size: {report['sample_size']} decisions")
            print()
            
            cal = report["calibration"]
            print(f"Calibration Metrics:")
            print(f"  Mean error: {cal['mean_error']:+.3f} (positive = overconfident)")
            print(f"  Std error: {cal['std_error']:.3f}")
            print(f"  Correlation: {cal['correlation'] or 'N/A'}")
            print()
            
            print("Recommendations:")
            for rec in report["suggestions"]["recommendations"]:
                print(f"  - {rec}")
        
        return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
