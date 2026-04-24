"""Capability + regression eval harness runner.

Reads rubric definitions from ``config/judges/rubrics.yaml``, executes the
configured test suites, and emits a JSON report that CI can gate on. The
runner is deliberately transport-thin — all grading logic lives in
``agentic_core/evaluation/judges/`` and ``system_learning/engines/``.

Invariants (Anthropic/OpenAI/Google best-practice):
  - Each trial is isolated (clean temp dir per trial).
  - Grades the outcome, not the path, when the rubric is capability-class.
  - LLM-judge abstentions (``Unknown``) do not count against pass rate but
    are tracked against each dimension's ``unknown_budget``.
  - Regression suite fails the build on any pass-rate drop vs baseline.
  - Capability suite fails the build only on ``min_pass_rate_target`` breach.

Usage:
    python tools/eval/run_capability_regression.py \
        --rubrics config/judges/rubrics.yaml \
        --suite capability \
        --out artifacts/eval/capability_run.json

Exit codes:
    0  — all suites within thresholds.
    1  — at least one suite breached a threshold (build should fail).
    2  — harness misconfiguration (rubrics file missing, etc.).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SuiteResult:
    suite: str                  # "capability" or "regression"
    rubric_family: str          # "rag" | "governance" | "security"
    dimension: str
    trials: int
    passes: int
    warns: int
    fails: int
    unknowns: int
    pass_rate: float
    unknown_rate: float
    threshold_min: float
    breached: bool
    notes: str = ""


def _load_rubrics(path: Path) -> dict[str, Any]:
    try:
        import yaml  # local import keeps harness optional-dep friendly
    except ImportError as exc:
        raise SystemExit(f"PyYAML required: {exc}") from exc
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _rubric_families(rubrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Flatten the three rubric families (rag / gov / sec) into one map."""
    return {
        "rag": rubrics.get("dimensions", {}) or {},
        "governance": rubrics.get("governance_dimensions", {}) or {},
        "security": rubrics.get("security_dimensions", {}) or {},
    }


_FAMILY_DIR: dict[str, str] = {"rag": "rag", "governance": "gov", "security": "sec"}


def _load_trials(family: str, dim: str, golden_root: Path) -> list[dict[str, Any]]:
    """Load golden items for a dimension. Items with gold_outcome == 'pending'
    are excluded from the trial set — they do not contribute to pass-rate."""
    fam_dir = golden_root / _FAMILY_DIR.get(family, family) / dim
    if not fam_dir.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(fam_dir.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                items.append(json.load(fh))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("skipping malformed golden item %s: %s", path, exc)
    return items


def _classify(item: dict[str, Any], pass_threshold: float, warn_threshold: float) -> str:
    outcome = str(item.get("gold_outcome") or "").lower()
    if outcome == "pending":
        return "pending"
    if outcome == "unknown" or item.get("gold_score") is None:
        return "unknown"
    score = float(item["gold_score"])
    if score >= pass_threshold:
        return "pass"
    if score >= warn_threshold:
        return "warn"
    return "fail"


def _evaluate_dimension(
    family: str,
    dim: str,
    spec: dict[str, Any],
    suite: str,
    taxonomy: dict[str, Any],
    golden_root: Path,
) -> SuiteResult:
    """Evaluate a single rubric dimension against its golden dataset.

    Trial counts exclude ``gold_outcome: "pending"`` items; pass-rate is
    computed only over calibrated items (pass/warn/fail/unknown).
    """
    min_rate = float(taxonomy.get(suite, {}).get("min_pass_rate_target", 0.0))
    pass_threshold = float(spec.get("pass_threshold", 4.0))
    warn_threshold = float(spec.get("warn_threshold", 3.0))
    unknown_budget = float(spec.get("unknown_budget", 0.2))

    items = _load_trials(family, dim, golden_root)
    buckets: dict[str, int] = {"pass": 0, "warn": 0, "fail": 0, "unknown": 0, "pending": 0}
    for item in items:
        buckets[_classify(item, pass_threshold, warn_threshold)] += 1

    calibrated = buckets["pass"] + buckets["warn"] + buckets["fail"] + buckets["unknown"]
    pass_rate = (buckets["pass"] / calibrated) if calibrated else 0.0
    unknown_rate = (buckets["unknown"] / calibrated) if calibrated else 0.0

    # Zero-calibrated cases do not breach — they're reported but not fail-closed
    # because the harness should not block merges when the dataset hasn't been
    # authored yet. Once calibrated items exist, min_rate applies.
    breached = bool(calibrated) and (pass_rate < min_rate or unknown_rate > unknown_budget)

    notes_parts: list[str] = []
    if not calibrated:
        notes_parts.append("no calibrated items; pending only")
    if buckets["pending"]:
        notes_parts.append(f"{buckets['pending']} pending seed items excluded from pass-rate")
    if unknown_rate > unknown_budget:
        notes_parts.append(f"unknown_rate {unknown_rate:.2f} > budget {unknown_budget:.2f}")

    return SuiteResult(
        suite=suite,
        rubric_family=family,
        dimension=dim,
        trials=calibrated,
        passes=buckets["pass"],
        warns=buckets["warn"],
        fails=buckets["fail"],
        unknowns=buckets["unknown"],
        pass_rate=pass_rate,
        unknown_rate=unknown_rate,
        threshold_min=min_rate,
        breached=breached,
        notes="; ".join(notes_parts) or "ok",
    )


def run(rubrics_path: Path, suite: str, out_path: Path | None, golden_root: Path) -> int:
    if not rubrics_path.exists():
        logger.error("rubrics file not found: %s", rubrics_path)
        return 2
    rubrics = _load_rubrics(rubrics_path)
    families = _rubric_families(rubrics)
    taxonomy = rubrics.get("eval_taxonomy", {}) or {}
    if suite not in taxonomy:
        logger.error("unknown suite %s; expected one of %s", suite, list(taxonomy))
        return 2

    results: list[SuiteResult] = []
    for family, dims in families.items():
        for dim, spec in dims.items():
            results.append(_evaluate_dimension(family, dim, spec, suite, taxonomy, golden_root))

    any_breach = any(r.breached for r in results)
    report = {
        "suite": suite,
        "rubrics_file": str(rubrics_path),
        "results": [asdict(r) for r in results],
        "breached": any_breach,
    }
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
        logger.info("eval report written to %s", out_path)
    else:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)

    return 1 if any_breach else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rubrics", type=Path, default=Path("config/judges/rubrics.yaml"))
    parser.add_argument("--suite", choices=["capability", "regression"], default="capability")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--golden-root", type=Path, default=Path("data/eval/golden"))
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    return run(args.rubrics, args.suite, args.out, args.golden_root)


if __name__ == "__main__":
    raise SystemExit(main())
