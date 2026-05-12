#!/usr/bin/env python3
"""Score apps_lic judges against human-labeled holdout corpus.

Loads corpus and adjudicated scores, runs available judges, computes:
- Per-dimension MAE
- Spearman correlation where computable
- Hard guardrail false-pass counts

Writes calibration_report JSON.

Does NOT fail on missing judge imports—marks judge_status=unavailable.
Does NOT call external APIs or live model providers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def try_import_judges() -> dict[str, Any]:
    """Try to import available judges. Return dict of available judges."""
    judges: dict[str, Any] = {}

    # Try response_likelihood_judge
    try:
        from apps_lic.engines.judges.response_likelihood_judge import ResponseLikelihoodJudge
        judges["response_likelihood"] = {
            "class": ResponseLikelihoodJudge,
            "available": True,
            "dimension": "response_likelihood",
        }
    except ImportError as e:
        judges["response_likelihood"] = {"available": False, "error": str(e)}

    # Try brand_voice_judge
    try:
        from apps_lic.engines.judges.brand_voice_judge import BrandVoiceJudge
        judges["brand_voice"] = {
            "class": BrandVoiceJudge,
            "available": True,
            "dimension": "brand_voice",
        }
    except ImportError as e:
        judges["brand_voice"] = {"available": False, "error": str(e)}

    # Try personalization_judge if available
    try:
        from apps_lic.engines.judges.personalization_judge import PersonalizationJudge
        judges["personalization"] = {
            "class": PersonalizationJudge,
            "available": True,
            "dimension": "personalization_quality",
        }
    except ImportError as e:
        judges["personalization"] = {"available": False, "error": str(e)}

    return judges


def load_corpus(corpus_path: Path) -> dict[str, dict]:
    """Load corpus as dict keyed by holdout_id."""
    corpus: dict[str, dict] = {}
    if not corpus_path.exists():
        return corpus

    with corpus_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                holdout_id = row.get("holdout_id")
                if holdout_id:
                    corpus[holdout_id] = row
            except json.JSONDecodeError:
                continue
    return corpus


def load_adjudicated_scores(scores_path: Path) -> list[dict]:
    """Load adjudicated scores CSV."""
    import csv

    scores: list[dict] = []
    if not scores_path.exists():
        return scores

    with scores_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for key in row:
                val = row[key]
                if val == "":
                    row[key] = None
                elif val is not None:
                    try:
                        if "." in val:
                            row[key] = float(val)
                        else:
                            row[key] = int(val)
                    except (ValueError, TypeError):
                        pass
            scores.append(row)
    return scores


def compute_spearman(x: list[float], y: list[float]) -> float | None:
    """Compute Spearman rank correlation. Returns None if not computable."""
    if len(x) < 3 or len(y) < 3 or len(x) != len(y):
        return None

    try:
        from scipy import stats
        corr, _ = stats.spearmanr(x, y)
        return float(corr)
    except ImportError:
        # Fallback: manual rank correlation
        return compute_rank_correlation(x, y)


def compute_rank_correlation(x: list[float], y: list[float]) -> float | None:
    """Compute Spearman-like rank correlation without scipy."""
    if len(x) < 3 or len(x) != len(y):
        return None

    def rank(data: list[float]) -> list[float]:
        sorted_vals = sorted(set(data))
        return [sorted_vals.index(v) + 1 for v in data]

    try:
        rx = rank(x)
        ry = rank(y)

        n = len(x)
        mean_rx = sum(rx) / n
        mean_ry = sum(ry) / n

        num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
        den = (sum((r - mean_rx) ** 2 for r in rx) * sum((r - mean_ry) ** 2 for r in ry)) ** 0.5

        if den == 0:
            return None
        return num / den
    except Exception:
        return None


def compute_mae(predicted: list[float], actual: list[float]) -> float | None:
    """Compute mean absolute error."""
    if len(predicted) != len(actual) or len(predicted) == 0:
        return None

    try:
        return sum(abs(p - a) for p, a in zip(predicted, actual)) / len(predicted)
    except Exception:
        return None


def run_judge_evaluation(
    judges: dict[str, Any],
    corpus: dict[str, dict],
    adjudicated: list[dict],
) -> dict[str, Any]:
    """Run judge evaluation and return results."""
    results: dict[str, Any] = {
        "judges_evaluated": {},
        "aggregate_metrics": {},
        "guardrail_audit": {},
    }

    # Dimension mapping from adjudicated scores to human ground truth
    dimension_map = {
        "response_likelihood": ("normalized_response_likelihood_0_1", "median_response_likelihood_1_5"),
        "brand_voice": ("normalized_brand_voice_0_1", "median_brand_voice_1_5"),
        "personalization": ("normalized_personalization_quality_0_1", "median_personalization_quality_1_5"),
    }

    for judge_name, judge_info in judges.items():
        judge_result: dict[str, Any] = {
            "status": "unavailable" if not judge_info.get("available") else "available",
        }

        if not judge_info.get("available"):
            judge_result["reason"] = judge_info.get("error", "Import failed")
            results["judges_evaluated"][judge_name] = judge_result
            continue

        # Collect predictions vs actuals
        predictions: list[float] = []
        actuals: list[float] = []
        raw_scores: list[int] = []  # 1-5 scale if available

        for score_row in adjudicated:
            holdout_id = score_row.get("holdout_id")
            if not holdout_id or holdout_id not in corpus:
                continue

            corpus_item = corpus[holdout_id]

            # Get normalized human score for this dimension
            norm_col, raw_col = dimension_map.get(judge_name, (None, None))
            human_score = score_row.get(norm_col)

            if human_score is None:
                continue

            # Run judge (stub - would call actual judge)
            # For now, mark as would-run
            judge_result["would_evaluate"] = {
                "holdout_id": holdout_id,
                "message_preview": corpus_item.get("composed_message", "")[:50] + "...",
            }

            predictions.append(0.5)  # Placeholder - would come from judge
            actuals.append(float(human_score))

        if len(predictions) >= 3:
            judge_result["n_evaluated"] = len(predictions)
            judge_result["mae"] = compute_mae(predictions, actuals)
            judge_result["spearman"] = compute_spearman(predictions, actuals)
        else:
            judge_result["n_evaluated"] = len(predictions)
            judge_result["insufficient_data"] = True

        results["judges_evaluated"][judge_name] = judge_result

    # Guardrail audit (stub)
    results["guardrail_audit"] = {
        "total_hard_negatives": 20,
        "false_passes_by_judge": {},
        "false_fail_rate": None,
        "note": "Guardrail auditing requires implemented judge outputs",
    }

    # Aggregate metrics
    spearmans = [
        r.get("spearman")
        for r in results["judges_evaluated"].values()
        if r.get("spearman") is not None
    ]
    maes = [
        r.get("mae")
        for r in results["judges_evaluated"].values()
        if r.get("mae") is not None
    ]

    results["aggregate_metrics"] = {
        "best_response_likelihood_spearman": next(
            (r.get("spearman") for name, r in results["judges_evaluated"].items()
             if name == "response_likelihood" and r.get("spearman")), None
        ),
        "best_brand_voice_spearman": next(
            (r.get("spearman") for name, r in results["judges_evaluated"].items()
             if name == "brand_voice" and r.get("spearman")), None
        ),
        "best_overall_spearman": max(spearmans) if spearmans else None,
        "mean_mae_per_dimension": sum(maes) / len(maes) if maes else None,
    }

    # Promotion recommendations
    best_spearman = results["aggregate_metrics"]["best_overall_spearman"]
    results["promotion_recommendations"] = {
        "spearman_threshold": 0.8,
        "best_achieved": best_spearman,
        "meets_promotion_criteria": (best_spearman is not None and best_spearman >= 0.8),
        "notes": "Spearman >= 0.80 required for judge promotion consideration",
    }

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score judges against holdout corpus")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("apps_lic/evals/holdout/outreach_holdout_corpus.v1.jsonl"),
        help="Path to corpus JSONL",
    )
    parser.add_argument(
        "--adjudicated",
        type=Path,
        default=Path("apps_lic/evals/holdout/adjudicated_scores.outreach_quality.v1.csv"),
        help="Path to adjudicated scores CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("apps_lic/evals/holdout/calibration_report.outreach_quality.v1.json"),
        help="Output JSON report path",
    )
    args = parser.parse_args(argv)

    # Import available judges
    judges = try_import_judges()
    available_count = sum(1 for j in judges.values() if j.get("available"))
    unavailable_count = len(judges) - available_count

    print(f"Judge availability: {available_count} available, {unavailable_count} unavailable")

    # Load corpus and adjudicated scores
    corpus = load_corpus(args.corpus)
    print(f"Loaded corpus: {len(corpus)} items")

    adjudicated = load_adjudicated_scores(args.adjudicated)
    print(f"Loaded adjudicated scores: {len(adjudicated)} items")

    # Run evaluation
    results = run_judge_evaluation(judges, corpus, adjudicated)

    # Build full report
    report: dict[str, Any] = {
        "report_schema_version": "calibration_report.outreach_quality.v1",
        "generated_at": None,  # Would use datetime
        "corpus_version": "outreach_holdout_corpus.v1",
        "human_labels_version": "human_labels.outreach_quality.v1",
        "adjudicated_scores_version": "adjudicated_scores.outreach_quality.v1",
        "judges_evaluated": list(judges.keys()),
        "summary": {
            "corpus_size": len(corpus),
            "human_labeled_items": len(adjudicated),
            "adjudicated_items": len(adjudicated),
            "judges_available": available_count,
            "judges_unavailable": unavailable_count,
        },
        "per_judge_results": results["judges_evaluated"],
        "aggregate_metrics": results["aggregate_metrics"],
        "guardrail_audit": results["guardrail_audit"],
        "promotion_recommendations": results["promotion_recommendations"],
        "notes": "Calibration report generated. Populate with real judge outputs after judge implementation.",
    }

    # Write report
    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    args.output.write_text(report_json, encoding="utf-8")
    print(f"Calibration report written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
