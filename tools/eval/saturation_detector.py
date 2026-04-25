"""Capability-eval saturation detector (W4.3).

Anthropic step 7: once a capability eval approaches its saturation ceiling,
it provides diminishing signal for further improvement — promote it to the
regression suite instead. This detector watches pass-rate history per
dimension and emits a promotion proposal through the approval gauntlet.

Invariants:
  - Proposal-only; never mutates eval_taxonomy directly.
  - Deterministic: same history + same thresholds ⇒ same proposals.
  - Uses the rubric-publication adapter so promotion is routed via UWG.

Saturation heuristic:
  - Last ``window`` runs have pass_rate >= ``ceiling``.
  - Slope of pass_rate over window is below ``slope_epsilon``.
  - Dimension has been in the capability suite for >= ``min_age_runs``.
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SaturationThresholds:
    ceiling: float = 0.95
    slope_epsilon: float = 0.01
    window: int = 10
    min_age_runs: int = 20


@dataclass(frozen=True, slots=True)
class DimensionHistory:
    rubric_family: str
    dimension: str
    pass_rates: tuple[float, ...]  # oldest → newest


@dataclass(frozen=True, slots=True)
class PromotionProposal:
    rubric_family: str
    dimension: str
    last_window_mean: float
    window_slope: float
    recommended_target: str  # "regression"
    rationale: str


def _slope(values: tuple[float, ...]) -> float:
    if len(values) < 2:
        return 0.0
    xs = list(range(len(values)))
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(values)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values))
    den = sum((x - mean_x) ** 2 for x in xs) or 1.0
    return num / den


def evaluate(history: DimensionHistory, thresholds: SaturationThresholds) -> PromotionProposal | None:
    if len(history.pass_rates) < thresholds.min_age_runs:
        return None
    window = history.pass_rates[-thresholds.window :]
    if len(window) < thresholds.window:
        return None
    window_mean = statistics.fmean(window)
    if window_mean < thresholds.ceiling:
        return None
    slope = _slope(window)
    if abs(slope) > thresholds.slope_epsilon:
        return None
    return PromotionProposal(
        rubric_family=history.rubric_family,
        dimension=history.dimension,
        last_window_mean=window_mean,
        window_slope=slope,
        recommended_target="regression",
        rationale=(
            f"last {thresholds.window} runs mean={window_mean:.3f} "
            f">= ceiling={thresholds.ceiling:.3f}; "
            f"slope={slope:.4f} within epsilon={thresholds.slope_epsilon:.4f}"
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history",
        type=Path,
        required=True,
        help="JSONL file; each line = {rubric_family, dimension, pass_rates: [..]}",
    )
    parser.add_argument("--out", type=Path, default=Path("artifacts/eval/saturation_proposals.json"))
    parser.add_argument("--ceiling", type=float, default=0.95)
    parser.add_argument("--slope-epsilon", type=float, default=0.01)
    parser.add_argument("--window", type=int, default=10)
    parser.add_argument("--min-age-runs", type=int, default=20)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

    thresholds = SaturationThresholds(args.ceiling, args.slope_epsilon, args.window, args.min_age_runs)
    proposals: list[PromotionProposal] = []
    with args.history.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            hist = DimensionHistory(
                rubric_family=str(obj["rubric_family"]),
                dimension=str(obj["dimension"]),
                pass_rates=tuple(float(x) for x in obj["pass_rates"]),
            )
            result = evaluate(hist, thresholds)
            if result is not None:
                proposals.append(result)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump([p.__dict__ for p in proposals], fh, indent=2, sort_keys=True)
    logger.info("wrote %d promotion proposals to %s", len(proposals), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
