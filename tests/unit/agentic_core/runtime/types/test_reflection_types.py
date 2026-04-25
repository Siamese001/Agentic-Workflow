"""Tests for shared reflection types (W4.2 binding)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentic_core.runtime.types.reflection_types import (
    L1_RETRIEVAL_ACTIONS,
    L3_ORCHESTRATION_ACTIONS,
    ReflectionNextAction,
    ReflectionTrace,
    ReflectionVerdict,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TestReflectionVerdict:
    def test_three_states(self) -> None:
        assert {v.value for v in ReflectionVerdict} == {"accept", "revise", "abort"}


class TestReflectionNextAction:
    def test_l1_excludes_l3_actions(self) -> None:
        assert ReflectionNextAction.REPLAN not in L1_RETRIEVAL_ACTIONS
        assert ReflectionNextAction.RETRY_TOOL not in L1_RETRIEVAL_ACTIONS

    def test_l3_excludes_l1_actions(self) -> None:
        assert ReflectionNextAction.REWRITE_QUERY not in L3_ORCHESTRATION_ACTIONS
        assert ReflectionNextAction.GRAPH_HOP not in L3_ORCHESTRATION_ACTIONS
        assert ReflectionNextAction.TRANSFORM_SWAP not in L3_ORCHESTRATION_ACTIONS

    def test_abstain_and_accept_in_both(self) -> None:
        for action in (ReflectionNextAction.ABSTAIN, ReflectionNextAction.ACCEPT_AS_IS):
            assert action in L1_RETRIEVAL_ACTIONS
            assert action in L3_ORCHESTRATION_ACTIONS


class TestReflectionTrace:
    def test_minimal_construction(self) -> None:
        trace = ReflectionTrace(
            iteration=0,
            evidence_in="x",
            verdict=ReflectionVerdict.ACCEPT,
            rationale="ok",
            next_action=None,
            grader_identity="heuristic/v1",
            emitted_at=_now(),
        )
        assert trace.iteration == 0
        assert trace.extras == {}

    def test_negative_iteration_rejected(self) -> None:
        with pytest.raises(ValueError, match="iteration must be"):
            ReflectionTrace(
                iteration=-1,
                evidence_in="x",
                verdict=ReflectionVerdict.ACCEPT,
                rationale="ok",
                next_action=None,
                grader_identity="g",
                emitted_at=_now(),
            )

    def test_wrong_verdict_type_rejected(self) -> None:
        with pytest.raises(TypeError, match="verdict must be"):
            ReflectionTrace(
                iteration=0,
                evidence_in="x",
                verdict="accept",  # type: ignore[arg-type]
                rationale="ok",
                next_action=None,
                grader_identity="g",
                emitted_at=_now(),
            )

    def test_wrong_action_type_rejected(self) -> None:
        with pytest.raises(TypeError, match="next_action must be"):
            ReflectionTrace(
                iteration=0,
                evidence_in="x",
                verdict=ReflectionVerdict.ACCEPT,
                rationale="ok",
                next_action="abstain",  # type: ignore[arg-type]
                grader_identity="g",
                emitted_at=_now(),
            )

    def test_long_rationale_rejected(self) -> None:
        with pytest.raises(ValueError, match="rationale must be"):
            ReflectionTrace(
                iteration=0,
                evidence_in="x",
                verdict=ReflectionVerdict.ACCEPT,
                rationale="x" * 300,
                next_action=None,
                grader_identity="g",
                emitted_at=_now(),
            )

    def test_frozen_immutable(self) -> None:
        trace = ReflectionTrace(
            iteration=0,
            evidence_in="x",
            verdict=ReflectionVerdict.ACCEPT,
            rationale="ok",
            next_action=None,
            grader_identity="g",
            emitted_at=_now(),
        )
        with pytest.raises((AttributeError, Exception)):
            trace.iteration = 5  # type: ignore[misc]
