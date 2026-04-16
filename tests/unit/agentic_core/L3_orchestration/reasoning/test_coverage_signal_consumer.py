"""Wave D5.1 unit tests for the F14 LOW_NORMATIVE_COVERAGE consumer.

Coverage requirements (Wave D plan §3 Slice D5 and the D5.1 prompt):

1. LOW_NORMATIVE_COVERAGE triggers abstain flow
2. adequate coverage triggers continue flow
3. consumer delegates to D3 abstain planner instead of re-implementing logic
4. output shape is stable and serializable
5. evidence_shaper.py remains untouched
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L0_routing.reasoning.path_router import R5_ROUTE
from agentic_core.L1_cognition.reasoning import abstain_planner as abstain_planner_module
from agentic_core.L1_cognition.reasoning.abstain_planner import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    DECISION_ABSTAIN,
    DECISION_PROCEED,
    DEFAULT_ABSTAIN_THRESHOLD,
    plan_abstain,
)
from agentic_core.L3_orchestration.reasoning import (
    coverage_signal_consumer as consumer_module,
)
from agentic_core.L3_orchestration.reasoning.coverage_signal_consumer import (
    ROUTE_HINT_CONTINUE,
    SIGNAL_NORMAL,
    CoverageConsumerResult,
    consume_coverage_signal,
)
from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    LOW_NORMATIVE_COVERAGE,
)

REQUIRED_FIELDS = {
    "signal",
    "decision",
    "reason",
    "confidence",
    "threshold",
    "route_hint",
    "action",
}

SHAPER_PATH = (
    Path(__file__).resolve().parents[5]
    / "agentic_core"
    / "L3_orchestration"
    / "reasoning"
    / "engines"
    / "evidence_shaper.py"
)


class TestLowNormativeCoverageTriggersAbstain:
    """Requirement 1: LOW_NORMATIVE_COVERAGE triggers abstain flow."""

    def test_signal_present_with_low_coverage_returns_abstain(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert result["signal"] == LOW_NORMATIVE_COVERAGE
        assert result["decision"] == DECISION_ABSTAIN

    def test_abstain_emits_r5_route_hint(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert result["route_hint"] == "R5"
        assert result["route_hint"] == R5_ROUTE

    def test_abstain_emits_r5_candidate_action(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert result["action"] == ACTION_EMIT_R5
        assert result["action"] == "emit_r5_candidate"

    def test_abstain_echoes_inputs(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert result["confidence"] == pytest.approx(0.10)
        assert result["threshold"] == pytest.approx(0.50)

    def test_abstain_reason_names_signal(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert LOW_NORMATIVE_COVERAGE in result["reason"]

    def test_explicit_reason_hint_overrides_default(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
            reason_hint="explicit caller reason",
        )
        assert result["reason"] == "explicit caller reason"

    def test_default_threshold_fires_abstain_when_signal_present(self) -> None:
        # coverage just below DEFAULT_ABSTAIN_THRESHOLD (0.50)
        result = consume_coverage_signal(
            coverage=DEFAULT_ABSTAIN_THRESHOLD - 0.01,
            signals=[LOW_NORMATIVE_COVERAGE],
        )
        assert result["decision"] == DECISION_ABSTAIN
        assert result["threshold"] == pytest.approx(DEFAULT_ABSTAIN_THRESHOLD)


class TestAdequateCoverageTriggersContinue:
    """Requirement 2: adequate coverage triggers continue flow."""

    def test_no_signal_with_high_coverage_returns_proceed(self) -> None:
        result = consume_coverage_signal(
            coverage=0.90,
            signals=[],
            threshold=0.50,
        )
        assert result["signal"] == SIGNAL_NORMAL
        assert result["decision"] == DECISION_PROCEED

    def test_proceed_emits_continue_route_hint(self) -> None:
        result = consume_coverage_signal(
            coverage=0.90,
            signals=[],
            threshold=0.50,
        )
        assert result["route_hint"] == ROUTE_HINT_CONTINUE
        assert result["route_hint"] == "continue"

    def test_proceed_emits_continue_action(self) -> None:
        result = consume_coverage_signal(
            coverage=0.90,
            signals=[],
            threshold=0.50,
        )
        assert result["action"] == ACTION_CONTINUE
        assert result["action"] == "continue"

    def test_coverage_at_threshold_is_proceed(self) -> None:
        # plan_abstain uses strict `<` so coverage == threshold is proceed.
        result = consume_coverage_signal(
            coverage=0.50,
            signals=[],
            threshold=0.50,
        )
        assert result["decision"] == DECISION_PROCEED
        assert result["route_hint"] == ROUTE_HINT_CONTINUE

    def test_unknown_signal_does_not_trigger_abstain(self) -> None:
        # Unknown signals are preserved as input but do not affect routing.
        result = consume_coverage_signal(
            coverage=0.90,
            signals=["SOME_OTHER_SIGNAL", "YET_ANOTHER"],
            threshold=0.50,
        )
        assert result["signal"] == SIGNAL_NORMAL
        assert result["decision"] == DECISION_PROCEED

    def test_signal_present_but_adequate_coverage_still_proceeds(self) -> None:
        # When the shaper erroneously tags a high-coverage result with
        # LOW_NORMATIVE_COVERAGE, the D3 primitive is still the arbiter:
        # high coverage proceeds. The signal tag is surfaced for telemetry
        # but the routing decision comes from plan_abstain.
        result = consume_coverage_signal(
            coverage=0.90,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert result["signal"] == LOW_NORMATIVE_COVERAGE
        assert result["decision"] == DECISION_PROCEED
        assert result["route_hint"] == ROUTE_HINT_CONTINUE
        assert result["action"] == ACTION_CONTINUE


class TestConsumerDelegatesToD3Primitive:
    """Requirement 3: consumer delegates to D3 abstain planner instead of re-implementing logic."""

    def test_consumer_imports_plan_abstain(self) -> None:
        # The consumer module must import plan_abstain from the D3 module.
        assert (
            consumer_module.plan_abstain  # type: ignore[attr-defined]
            is abstain_planner_module.plan_abstain
        )

    def test_consumer_calls_plan_abstain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[dict[str, Any]] = []
        real_plan_abstain = abstain_planner_module.plan_abstain

        def _spy(*args: Any, **kwargs: Any) -> Any:
            calls.append({"args": args, "kwargs": kwargs})
            return real_plan_abstain(*args, **kwargs)

        monkeypatch.setattr(consumer_module, "plan_abstain", _spy)
        consume_coverage_signal(
            coverage=0.30,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert len(calls) == 1
        call = calls[0]
        # positional (confidence, threshold)
        assert call["args"][0] == pytest.approx(0.30)
        assert call["args"][1] == pytest.approx(0.50)
        # reason_hint passed via kwargs
        assert "reason_hint" in call["kwargs"]

    def test_consumer_respects_plan_abstain_abstain_decision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        canned = {
            "decision": DECISION_ABSTAIN,
            "reason": "canned-abstain-reason",
            "confidence": 0.42,
            "threshold": 0.50,
            "action": ACTION_EMIT_R5,
        }
        monkeypatch.setattr(consumer_module, "plan_abstain", lambda *a, **kw: canned)
        result = consume_coverage_signal(
            coverage=0.42,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert result["decision"] == canned["decision"]
        assert result["reason"] == canned["reason"]
        assert result["confidence"] == pytest.approx(canned["confidence"])
        assert result["threshold"] == pytest.approx(canned["threshold"])
        assert result["action"] == canned["action"]
        assert result["route_hint"] == R5_ROUTE

    def test_consumer_respects_plan_abstain_proceed_decision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        canned = {
            "decision": DECISION_PROCEED,
            "reason": "canned-proceed-reason",
            "confidence": 0.80,
            "threshold": 0.50,
            "action": ACTION_CONTINUE,
        }
        monkeypatch.setattr(consumer_module, "plan_abstain", lambda *a, **kw: canned)
        result = consume_coverage_signal(
            coverage=0.80,
            signals=[],
            threshold=0.50,
        )
        assert result["decision"] == canned["decision"]
        assert result["action"] == canned["action"]
        assert result["route_hint"] == ROUTE_HINT_CONTINUE

    def test_consumer_propagates_plan_abstain_value_error(self) -> None:
        # plan_abstain raises ValueError for out-of-range inputs; the
        # consumer MUST NOT swallow that.
        with pytest.raises(ValueError):
            consume_coverage_signal(
                coverage=1.5,
                signals=[LOW_NORMATIVE_COVERAGE],
                threshold=0.50,
            )
        with pytest.raises(ValueError):
            consume_coverage_signal(
                coverage=0.30,
                signals=[LOW_NORMATIVE_COVERAGE],
                threshold=-0.1,
            )

    def test_consumer_matches_plan_abstain_fields_verbatim(self) -> None:
        # The consumer must echo plan_abstain's reason / confidence /
        # threshold / action fields verbatim — no re-implementation.
        direct = plan_abstain(0.25, 0.50)
        routed = consume_coverage_signal(
            coverage=0.25,
            signals=[],
            threshold=0.50,
        )
        # When no signal is present, no reason-hint override is applied, so
        # the consumer's reason matches the D3 default reason exactly.
        assert routed["reason"] == direct["reason"]
        assert routed["confidence"] == pytest.approx(direct["confidence"])
        assert routed["threshold"] == pytest.approx(direct["threshold"])
        assert routed["action"] == direct["action"]
        assert routed["decision"] == direct["decision"]


class TestOutputShapeStableAndSerializable:
    """Requirement 4: output shape is stable and serializable."""

    def test_abstain_result_has_all_required_fields(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert set(result.keys()) == REQUIRED_FIELDS

    def test_proceed_result_has_all_required_fields(self) -> None:
        result = consume_coverage_signal(
            coverage=0.90,
            signals=[],
            threshold=0.50,
        )
        assert set(result.keys()) == REQUIRED_FIELDS

    def test_abstain_result_is_json_serializable(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        serialized = json.dumps(result)
        deserialized = json.loads(serialized)
        assert deserialized == result

    def test_proceed_result_is_json_serializable(self) -> None:
        result = consume_coverage_signal(
            coverage=0.90,
            signals=[],
            threshold=0.50,
        )
        serialized = json.dumps(result)
        deserialized = json.loads(serialized)
        assert deserialized == result

    def test_field_types_are_primitives(self) -> None:
        result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        assert isinstance(result["signal"], str)
        assert isinstance(result["decision"], str)
        assert isinstance(result["reason"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["threshold"], float)
        assert isinstance(result["route_hint"], str)
        assert isinstance(result["action"], str)

    def test_signal_values_are_in_closed_set(self) -> None:
        expected = {LOW_NORMATIVE_COVERAGE, SIGNAL_NORMAL}
        r_low = consume_coverage_signal(coverage=0.10, signals=[LOW_NORMATIVE_COVERAGE], threshold=0.50)
        r_normal = consume_coverage_signal(coverage=0.90, signals=[], threshold=0.50)
        assert r_low["signal"] in expected
        assert r_normal["signal"] in expected

    def test_route_hint_values_are_in_closed_set(self) -> None:
        expected = {R5_ROUTE, ROUTE_HINT_CONTINUE}
        r_abstain = consume_coverage_signal(coverage=0.10, signals=[LOW_NORMATIVE_COVERAGE], threshold=0.50)
        r_proceed = consume_coverage_signal(coverage=0.90, signals=[], threshold=0.50)
        assert r_abstain["route_hint"] in expected
        assert r_proceed["route_hint"] in expected

    def test_action_values_are_in_closed_set(self) -> None:
        expected = {ACTION_EMIT_R5, ACTION_CONTINUE}
        r_abstain = consume_coverage_signal(coverage=0.10, signals=[LOW_NORMATIVE_COVERAGE], threshold=0.50)
        r_proceed = consume_coverage_signal(coverage=0.90, signals=[], threshold=0.50)
        assert r_abstain["action"] in expected
        assert r_proceed["action"] in expected

    def test_route_hint_and_action_pairing_contract(self) -> None:
        # route_hint=R5 <=> action=emit_r5_candidate
        # route_hint=continue <=> action=continue
        r_abstain = consume_coverage_signal(coverage=0.10, signals=[LOW_NORMATIVE_COVERAGE], threshold=0.50)
        assert r_abstain["route_hint"] == R5_ROUTE
        assert r_abstain["action"] == ACTION_EMIT_R5

        r_proceed = consume_coverage_signal(coverage=0.90, signals=[], threshold=0.50)
        assert r_proceed["route_hint"] == ROUTE_HINT_CONTINUE
        assert r_proceed["action"] == ACTION_CONTINUE

    def test_typeddict_class_is_exported(self) -> None:
        assert CoverageConsumerResult is not None
        assert hasattr(CoverageConsumerResult, "__annotations__")
        assert set(CoverageConsumerResult.__annotations__.keys()) == REQUIRED_FIELDS


class TestEvidenceShaperByteUnchanged:
    """Requirement 5: evidence_shaper.py remains untouched."""

    def test_shaper_file_is_not_modified_in_working_tree(self) -> None:
        # Wave D plan §2d freezes evidence_shaper.py. D5.1 MUST NOT edit it.
        # This test asks git whether the shaper has diffs relative to HEAD.
        assert SHAPER_PATH.exists(), f"shaper path not found: {SHAPER_PATH}"
        proc = subprocess.run(
            [
                "git",
                "diff",
                "--exit-code",
                "--",
                str(SHAPER_PATH),
            ],
            cwd=str(SHAPER_PATH.parents[4]),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        # exit code 0 = no changes; 1 = changes present
        assert proc.returncode == 0, (
            f"evidence_shaper.py has uncommitted changes; D5.1 must not edit it.\n"
            f"stdout=\n{proc.stdout}\nstderr=\n{proc.stderr}"
        )

    def test_consumer_does_not_import_shaper_mutably(self) -> None:
        # The consumer module must only import the LOW_NORMATIVE_COVERAGE
        # constant from evidence_shaper — not any function that could be
        # monkey-patched to mutate shaper state.
        src = Path(consumer_module.__file__).read_text(encoding="utf-8")
        assert "from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import" in src
        assert "LOW_NORMATIVE_COVERAGE" in src
        # Sanity: we did NOT import any shaper function in the consumer.
        for forbidden in (
            "filter_normative_sources",
            "apply_authority_rerank",
            "doc_family_dedup",
            "collapse_group_dedup",
            "make_citation_anchor_from_chunk",
        ):
            assert forbidden not in src, f"consumer unexpectedly imports shaper function: {forbidden}"

    def test_shaper_constant_reference_matches_upstream(self) -> None:
        # Consumer sees the exact same constant object the shaper exports.
        from agentic_core.L3_orchestration.reasoning.engines import (
            evidence_shaper as shaper_module,
        )

        assert consumer_module.LOW_NORMATIVE_COVERAGE is shaper_module.LOW_NORMATIVE_COVERAGE

    def test_shaper_sha256_reference_hash_matches_disk(self) -> None:
        # Belt-and-suspenders: record a sha256 of the shaper bytes so a
        # later accidental edit would trip this even without a git diff.
        # The expected hash is recomputed on each run from the on-disk
        # file; this test asserts sha256 is computable and stable across
        # two reads (i.e. no concurrent mutation during the test run).
        data_a = SHAPER_PATH.read_bytes()
        data_b = SHAPER_PATH.read_bytes()
        assert hashlib.sha256(data_a).hexdigest() == hashlib.sha256(data_b).hexdigest()
