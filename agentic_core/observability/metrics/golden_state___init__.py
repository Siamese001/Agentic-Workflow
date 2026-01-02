from __future__ import annotations
"""Golden State Testing Infrastructure.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
Phase 2 - Pillar 12: Testing (Golden State)
Validation foundation with golden datasets and evaluators.
"""
import logging

from agentic_core.evaluators import (
    JudgeEvaluationResult,
    JudgeEvaluator,
    JudgeVerdict,
    JudgmentCriterion,
    JudgmentScore,
    create_judge_evaluator,
)

__all__ = [
    "JudgeEvaluator",
    "JudgeVerdict",
    "JudgeEvaluationResult",
    "JudgmentCriterion",
    "JudgmentScore",
    "create_judge_evaluator",
]