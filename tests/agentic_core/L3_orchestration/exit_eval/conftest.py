"""Fixtures for exit_eval tests."""

from __future__ import annotations

from typing import Any, Mapping

import pytest

from agentic_core.L3_orchestration.exit_eval.dimension import Dimension
from agentic_core.L3_orchestration.exit_eval.graders.base import (
    Grader,
    GraderOutput,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    JudgeProtocol,
    JudgeResponse,
)


class FakeCodeGrader(Grader):
    """Returns a pre-programmed score; used to test gate composition."""

    from agentic_core.L3_orchestration.exit_eval.dimension import GraderClass

    grader_class = GraderClass.CODE_BASED

    def __init__(self, score: float = 1.0, *, raise_exc: Exception | None = None) -> None:
        self._score = score
        self._raise = raise_exc

    def grade(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> GraderOutput:
        if self._raise is not None:
            raise self._raise
        return GraderOutput(score=self._score, abstain=False)


class FakeJudge(JudgeProtocol):
    """Deterministic judge stub for tests."""

    def __init__(
        self,
        score: float = 1.0,
        abstain: bool = False,
        *,
        raise_exc: Exception | None = None,
    ) -> None:
        self._score = score
        self._abstain = abstain
        self._raise = raise_exc

    def judge(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> JudgeResponse:
        if self._raise is not None:
            raise self._raise
        return JudgeResponse(score=self._score, abstain=self._abstain, reasoning="test")


@pytest.fixture
def rubrics_dir(tmp_path_factory: pytest.TempPathFactory) -> "Any":
    """Path to the packaged golden rubrics."""
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "config" / "exit_eval_rubrics"
