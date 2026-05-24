"""Provider-neutral score normalization for panel judges."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class NormalizedScore:
    score: float
    score_scale: str
    threshold: float
    pass_: bool
    decisive_failure: bool


def normalize_panel_score(body: Mapping[str, Any]) -> NormalizedScore:
    """Single pass math for all providers (identical JSON => identical pass)."""
    scale = str(body.get("score_scale") or "0_to_5")
    raw_score = float(body.get("score", 0))
    raw_threshold = float(body.get("threshold", 4.0 if scale == "0_to_5" else 0.8))
    decisive = bool(body.get("decisive_failure", False))

    if scale == "0_to_1":
        norm_score = raw_score
        norm_threshold = raw_threshold
    else:
        norm_score = raw_score
        norm_threshold = raw_threshold

    model_pass_flag = body.get("pass")
    if decisive:
        passed = False
    elif model_pass_flag is not None:
        passed = bool(model_pass_flag)
    else:
        passed = norm_score >= norm_threshold

    return NormalizedScore(
        score=norm_score,
        score_scale=scale,
        threshold=norm_threshold,
        pass_=passed,
        decisive_failure=decisive,
    )


__all__ = ["NormalizedScore", "normalize_panel_score"]
