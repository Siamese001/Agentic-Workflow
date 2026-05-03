"""W3 verification — canonical Anthropic grader types + trajectory match mode.

Plan: ``.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`` W3.P1-P4.

Proves:

- `GRADER_TYPE_VOCAB` includes the 4 new types (`tool_calls`,
  `state_check`, `transcript`, `trajectory_match`) plus the 3 legacy.
- `TRAJECTORY_MATCH_MODE_VOCAB` defines the 5 modes + empty.
- `ScoreDimension` accepts the new types and validates trajectory_match_mode.
- `grade_tool_calls` dispatches correctly across modes.
- `grade_state_check` validates dotted-path assertions.
- `grade_transcript` reads the metric bundle.
- Gate surfaces INVALID_GRADER_TYPE for unknown types.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_TYPE_DISPATCH,
    grade_state_check,
    grade_tool_calls,
    grade_transcript,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    GRADER_UNKNOWN_SENTINEL,
)
from agentic_core.L4_state.contracts.app_domain import (
    GRADER_TYPE_VOCAB,
    TRAJECTORY_MATCH_MODE_VOCAB,
    AppDomainContractError,
    ScoreDimension,
)


class TestGraderTypeVocab:
    def test_all_legacy_types_kept(self) -> None:
        assert "deterministic" in GRADER_TYPE_VOCAB
        assert "llm_as_judge" in GRADER_TYPE_VOCAB
        assert "hybrid" in GRADER_TYPE_VOCAB

    def test_new_types_present(self) -> None:
        assert "tool_calls" in GRADER_TYPE_VOCAB
        assert "state_check" in GRADER_TYPE_VOCAB
        assert "transcript" in GRADER_TYPE_VOCAB
        assert "trajectory_match" in GRADER_TYPE_VOCAB

    def test_trajectory_mode_vocab(self) -> None:
        assert TRAJECTORY_MATCH_MODE_VOCAB == frozenset(
            {"strict", "unordered", "subset", "superset", "none"}
        )


class TestScoreDimensionAcceptsNewTypes:
    @pytest.mark.parametrize("gtype", ["tool_calls", "state_check", "transcript", "trajectory_match"])
    def test_accepts_new_grader_type(self, gtype: str) -> None:
        dim = ScoreDimension(
            dimension_id="t", description="test", weight=0.1, grader_type=gtype,
        )
        assert dim.grader_type == gtype

    @pytest.mark.parametrize("mode", ["strict", "unordered", "subset", "superset", "none"])
    def test_accepts_trajectory_mode(self, mode: str) -> None:
        dim = ScoreDimension(
            dimension_id="t", description="t", weight=0.1,
            grader_type="tool_calls", trajectory_match_mode=mode,
        )
        assert dim.trajectory_match_mode == mode

    def test_rejects_invalid_trajectory_mode(self) -> None:
        with pytest.raises(AppDomainContractError, match="trajectory_match_mode"):
            ScoreDimension(
                dimension_id="t", description="t", weight=0.1,
                grader_type="tool_calls", trajectory_match_mode="bogus",
            )

    def test_empty_trajectory_mode_ok(self) -> None:
        """Empty string means "not applicable" — accepted."""
        dim = ScoreDimension(
            dimension_id="t", description="t", weight=0.1, grader_type="deterministic",
        )
        assert dim.trajectory_match_mode == ""

    def test_score_bands_default_empty(self) -> None:
        dim = ScoreDimension(
            dimension_id="t", description="t", weight=0.1, grader_type="deterministic",
        )
        assert dim.score_bands == ()

    def test_score_bands_accepted(self) -> None:
        dim = ScoreDimension(
            dimension_id="t", description="t", weight=0.1, grader_type="llm_as_judge",
            score_bands=("BAD", "WEAK", "OK", "GOOD"),
        )
        assert dim.score_bands == ("BAD", "WEAK", "OK", "GOOD")


class TestToolCallsGrader:
    def _dim(self, mode: str = "unordered") -> ScoreDimension:
        return ScoreDimension(
            dimension_id="trajectory", description="t", weight=0.2,
            grader_type="tool_calls", trajectory_match_mode=mode,
        )

    def test_strict_match(self) -> None:
        score, _ev = grade_tool_calls(
            self._dim("strict"),
            {"output": {"tool_calls": ["a", "b"], "expected_tool_calls": ["a", "b"]}},
        )
        assert score == 1.0

    def test_strict_mismatch(self) -> None:
        score, _ev = grade_tool_calls(
            self._dim("strict"),
            {"output": {"tool_calls": ["b", "a"], "expected_tool_calls": ["a", "b"]}},
        )
        assert score == 0.0

    def test_unordered_partial(self) -> None:
        score, _ev = grade_tool_calls(
            self._dim("unordered"),
            {"output": {"tool_calls": ["a", "c"], "expected_tool_calls": ["a", "b"]}},
        )
        assert score == 0.5

    def test_subset(self) -> None:
        score, _ev = grade_tool_calls(
            self._dim("subset"),
            {"output": {"tool_calls": ["a"], "expected_tool_calls": ["a", "b"]}},
        )
        assert score == 1.0
        score2, _ = grade_tool_calls(
            self._dim("subset"),
            {"output": {"tool_calls": ["c"], "expected_tool_calls": ["a", "b"]}},
        )
        assert score2 == 0.0

    def test_superset(self) -> None:
        score, _ev = grade_tool_calls(
            self._dim("superset"),
            {"output": {"tool_calls": ["a", "b", "c"], "expected_tool_calls": ["a", "b"]}},
        )
        assert score == 1.0

    def test_unknown_when_missing(self) -> None:
        score, _ev = grade_tool_calls(self._dim(), {"output": {}})
        assert score == GRADER_UNKNOWN_SENTINEL


class TestStateCheckGrader:
    def _dim(self) -> ScoreDimension:
        return ScoreDimension(
            dimension_id="state_dim", description="t", weight=0.1,
            grader_type="state_check",
        )

    def test_pass_on_match(self) -> None:
        score, _ev = grade_state_check(
            self._dim(),
            {
                "state_diff": {"ledger": {"rows_added": 1}, "counter": {"incremented": True}},
                "output": {"expected_state": {"state_dim": {"ledger.rows_added": 1, "counter.incremented": True}}},
            },
        )
        assert score == 1.0

    def test_fail_on_mismatch(self) -> None:
        score, ev = grade_state_check(
            self._dim(),
            {
                "state_diff": {"ledger": {"rows_added": 2}},
                "output": {"expected_state": {"state_dim": {"ledger.rows_added": 1}}},
            },
        )
        assert score == 0.0
        assert any("mismatch::ledger.rows_added" in e for e in ev)

    def test_unknown_when_no_assertion(self) -> None:
        score, _ev = grade_state_check(self._dim(), {"state_diff": {}, "output": {}})
        assert score == GRADER_UNKNOWN_SENTINEL


class TestTranscriptGrader:
    def _dim(self) -> ScoreDimension:
        return ScoreDimension(
            dimension_id="ttfb", description="t", weight=0.1,
            grader_type="transcript",
        )

    def test_reads_metric(self) -> None:
        score, _ev = grade_transcript(
            self._dim(),
            {"output": {"transcript_metrics": {"ttfb": 0.42}}},
        )
        assert score == 0.42

    def test_unknown_when_absent(self) -> None:
        score, _ev = grade_transcript(self._dim(), {"output": {}})
        assert score == GRADER_UNKNOWN_SENTINEL


class TestDispatchTable:
    def test_all_vocab_types_routed(self) -> None:
        for gtype in GRADER_TYPE_VOCAB:
            assert gtype in GRADER_TYPE_DISPATCH, f"{gtype} missing from dispatch"

    def test_legacy_types_route_to_generic(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            read_dim_score_from_output,
        )
        assert GRADER_TYPE_DISPATCH["deterministic"] is read_dim_score_from_output
        assert GRADER_TYPE_DISPATCH["llm_as_judge"] is read_dim_score_from_output

    def test_tool_calls_and_trajectory_match_share_grader(self) -> None:
        assert GRADER_TYPE_DISPATCH["tool_calls"] is GRADER_TYPE_DISPATCH["trajectory_match"]


class TestGateInvalidGraderTypeCheck:
    def test_gate_has_invalid_grader_type_check(self) -> None:
        """Structural check: gate source has INVALID_GRADER_TYPE logic."""
        src = (
            Path(__file__).resolve().parents[2]
            / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"
        ).read_text(encoding="utf-8")
        assert "INVALID_GRADER_TYPE" in src
        assert "VALID_GRADER_TYPES" in src
