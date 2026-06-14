"""ask_user_question_calibration.py — precedent-calibrated confidence for AskUserQuestion.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W2.1). This is the CONSULT half of the
meta-learning loop: W1 captures each decision (recommended vs the user's selection + the stated
confidence); this module reads that history back so the *next* AskUserQuestion states a confidence
calibrated to how often the user has actually accepted the recommendation in the same context.

Given a telemetry ``context`` and the confidence the model is about to state, it:
  1. looks up prior decisions for that context (``AskUserQuestionConsulter``),
  2. computes empirical acceptance (selected == recommended) with a Wilson 95% lower bound
     (reusing ``tools.calibration.loop_metrics.wilson_interval`` — small-N safe),
  3. returns a calibrated-confidence suggestion that blends the stated number toward the
     conservative empirical lower bound, plus a strong/suggestive/none signal.

Pure-read — never mutates the ledger. Conservative by construction: with too little precedent it
returns the stated confidence unchanged (``signal="none"``).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.calibration.loop_metrics import wilson_interval
from tools.ledgers.consulter import AskUserQuestionConsulter

# Minimum prior decisions (with both recommended + selected indices) before precedent may move
# the number. Below this, calibration is a no-op (signal="none").
MIN_SAMPLES_FOR_SIGNAL = 5
# At/above this, precedent is treated as "strong" rather than "suggestive".
STRONG_SAMPLE_THRESHOLD = 12
# How strongly the empirical lower bound pulls the stated confidence (0..1).
DEFAULT_BLEND_WEIGHT = 0.5
# |stated - empirical_point| beyond this is flagged as a meaningful divergence.
DEFAULT_DIVERGENCE_THRESHOLD = 0.15


@dataclass
class ConfidenceCalibration:
    """Result of consulting precedent for one (context, stated_confidence)."""

    context: str
    stated_confidence: float
    n: int                       # prior decisions with both recommended + selected indices
    empirical_acceptance: float  # point estimate: P(selected == recommended)
    wilson_lower: float
    wilson_upper: float
    calibrated_confidence: float  # suggested number to state
    signal: str                   # "strong" | "suggestive" | "none"
    diverged: bool                # |stated - empirical_point| > threshold AND signal != none
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clamp(x: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, v))


def _acceptance_counts(matches: list[dict[str, Any]]) -> tuple[int, int]:
    """Return (aligned, n) over rows that have BOTH recommended_index and selected_index."""
    with_both = [
        m for m in matches
        if m.get("selected_index") is not None and m.get("recommended_index") is not None
    ]
    aligned = sum(1 for m in with_both if m["selected_index"] == m["recommended_index"])
    return aligned, len(with_both)


def lookup_calibrated_confidence(
    context: str,
    stated_confidence: float,
    *,
    db_path: Path | None = None,
    consulter: AskUserQuestionConsulter | None = None,
    min_samples: int = MIN_SAMPLES_FOR_SIGNAL,
    blend_weight: float = DEFAULT_BLEND_WEIGHT,
    divergence_threshold: float = DEFAULT_DIVERGENCE_THRESHOLD,
    limit: int = 50,
) -> ConfidenceCalibration:
    """Suggest a precedent-calibrated confidence for an AskUserQuestion in ``context``.

    Fail-open: any read error yields ``signal="none"`` and the stated confidence unchanged.
    """
    stated = _clamp(stated_confidence)
    try:
        c = consulter or AskUserQuestionConsulter(db_path=db_path)
        verdict = c.lookup(context=context, limit=limit)
        matches = verdict.matches or []
    except Exception:  # guardian: allow-broad-exception -- consult is best-effort, never wedge a call
        matches = []

    aligned, n = _acceptance_counts(matches)

    if n < max(1, min_samples):
        return ConfidenceCalibration(
            context=context,
            stated_confidence=stated,
            n=n,
            empirical_acceptance=0.0,
            wilson_lower=0.0,
            wilson_upper=0.0,
            calibrated_confidence=stated,
            signal="none",
            diverged=False,
            rationale=(
                f"insufficient precedent (n={n} < {min_samples}) — stated confidence unchanged"
            ),
        )

    point, low, high = wilson_interval(aligned, n)
    # Blend the stated number toward the conservative lower bound. Confidence should track how
    # often users actually accept the recommendation here; under-confidence is the safe error.
    calibrated = round((1.0 - blend_weight) * stated + blend_weight * low, 2)
    calibrated = _clamp(calibrated)
    signal = "strong" if n >= STRONG_SAMPLE_THRESHOLD else "suggestive"
    diverged = abs(stated - point) > divergence_threshold

    return ConfidenceCalibration(
        context=context,
        stated_confidence=stated,
        n=n,
        empirical_acceptance=round(point, 4),
        wilson_lower=round(low, 4),
        wilson_upper=round(high, 4),
        calibrated_confidence=calibrated,
        signal=signal,
        diverged=diverged,
        rationale=(
            f"{aligned}/{n} prior decisions in '{context}' took the recommendation "
            f"(acceptance {point:.0%}, Wilson95 lower {low:.0%}); "
            f"stated {stated:.2f} -> calibrated {calibrated:.2f}"
            + (" [DIVERGENT]" if diverged else "")
        ),
    )


def main() -> int:
    """CLI: report calibration for a context + stated confidence."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="AskUserQuestion confidence calibration")
    parser.add_argument("context", help="telemetry context (e.g. 'next-step')")
    parser.add_argument("stated", type=float, help="confidence the model is about to state (0..1)")
    args = parser.parse_args()
    result = lookup_calibrated_confidence(args.context, args.stated)
    print(json.dumps(result.as_dict(), indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
