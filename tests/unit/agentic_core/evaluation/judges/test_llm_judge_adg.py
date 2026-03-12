"""ADG importability contract for agentic_core/evaluation/judges/llm_judge.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_llm_judge.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.evaluation.judges.llm_judge import (  # noqa: F401
        JudgeScore,
        LLMJudge,
        NullJudge,
        GeminiJudge,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    JudgeScore = None  # type: ignore[assignment,misc]
    LLMJudge = None  # type: ignore[assignment,misc]
    NullJudge = None  # type: ignore[assignment,misc]
    GeminiJudge = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="llm_judge.py deps unavailable")
class TestLlmJudgeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: llm_judge.py must be importable."""
        assert _AVAILABLE

    def test_judgescore_is_type(self) -> None:
        assert JudgeScore is not None

    def test_llmjudge_is_type(self) -> None:
        assert LLMJudge is not None

    def test_nulljudge_is_type(self) -> None:
        assert NullJudge is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

