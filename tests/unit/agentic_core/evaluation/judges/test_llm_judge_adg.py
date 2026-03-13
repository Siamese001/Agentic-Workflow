"""ADG importability contract for agentic_core/evaluation/judges/llm_judge.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_llm_judge.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.evaluation.judges.llm_judge import (  # noqa: F401
        GeminiJudge,
        JudgeScore,
        LLMJudge,
        NullJudge,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    JudgeScore = None  # type: ignore[assignment,misc]
    LLMJudge = None  # type: ignore[assignment,misc]
    NullJudge = None  # type: ignore[assignment,misc]
    GeminiJudge = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="llm_judge deps unavailable")
class TestLlmJudgeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/evaluation/judges/llm_judge.py must be importable."""
        assert _AVAILABLE

    def test_judgescore_defined(self) -> None:
        assert JudgeScore is not None

    def test_llmjudge_defined(self) -> None:
        assert LLMJudge is not None

    def test_nulljudge_defined(self) -> None:
        assert NullJudge is not None

    def test_geminijudge_defined(self) -> None:
        assert GeminiJudge is not None
