"""apps_qna.engines.judges — RAG evaluation judges.

D1.2: Three deterministic heuristic judges for the RAG dims declared in
eval_rubrics.yaml (context_recall, context_precision, answer_relevancy).

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-deferred-e9c5b3.md D1.2
"""

from __future__ import annotations

from .answer_relevancy_judge import AnswerRelevancyJudge, grade as grade_answer_relevancy
from .context_precision_judge import ContextPrecisionJudge, grade as grade_context_precision
from .context_recall_judge import ContextRecallJudge, grade as grade_context_recall
from .interview_card_quality_judge import InterviewCardQualityJudge, grade as grade_interview_card_quality

__all__ = [
    "AnswerRelevancyJudge",
    "ContextPrecisionJudge",
    "ContextRecallJudge",
    "InterviewCardQualityJudge",
    "grade_answer_relevancy",
    "grade_context_precision",
    "grade_context_recall",
    "grade_interview_card_quality",
]
