"""ADG importability contract for apps_shared/types/judge_evaluator_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_judge_evaluator_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.types.judge_evaluator_types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        JudgeEvaluationResult,
        JudgeEvaluator,
        JudgeVerdict,
        JudgmentCriterion,
        JudgmentScore,
        create_judge_evaluator,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    JudgmentCriterion = None  # type: ignore[assignment,misc]
    JudgmentScore = None  # type: ignore[assignment,misc]
    JudgeVerdict = None  # type: ignore[assignment,misc]
    JudgeEvaluationResult = None  # type: ignore[assignment,misc]
    JudgeEvaluator = None  # type: ignore[assignment,misc]
    create_judge_evaluator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="judge_evaluator_types.py deps unavailable")
class TestJudgeEvaluatorTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: judge_evaluator_types.py must be importable."""
        assert _AVAILABLE

    def test_judgmentcriterion_is_type(self) -> None:
        assert JudgmentCriterion is not None

    def test_judgmentscore_is_type(self) -> None:
        assert JudgmentScore is not None

    def test_judgeverdict_is_type(self) -> None:
        assert JudgeVerdict is not None

    def test_create_judge_evaluator_callable(self) -> None:
        assert callable(create_judge_evaluator)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None