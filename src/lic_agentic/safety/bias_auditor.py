"""Minimal bias auditor stub used for safety-aware routing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class BiasAssessment:
    score: float
    notes: str


def audit_bias(inputs) -> BiasAssessment:
    """Return a light-weight bias score for *inputs*."""

    prompt = getattr(inputs, "prompt", getattr(inputs, "prompt", ""))
    if not prompt:
        return BiasAssessment(0.0, "Empty prompt, no bias risk")
    score = 0.1 if "diversity" in prompt.lower() else 0.0
    notes = "Detected inclusive language" if score else "No flagged bias"
    return BiasAssessment(score, notes)
