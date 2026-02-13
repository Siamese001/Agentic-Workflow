"""
§Wave4.2 — L3CognitiveDiffBundle tests.

1. Contract/serialization: stable JSON, sorted diff ops
2. SemanticClock enforcement: None → ValueError
3. Determinism/idempotency: same inputs → identical JSON + trace_id
4. Integration seam: before/after snapshots → expected diff ops
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_maintenance.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L3_orchestration.types.cognitive_diff_types import (
    CognitiveStateSnapshot,
    DiffOp,
    L3CognitiveDiffBundle,
    compute_cognitive_diff,
    emit_cognitive_diff_bundle,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clock() -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=7, vector_clock=(("L0", 3), ("L3", 4)))


@pytest.fixture
def before_state() -> CognitiveStateSnapshot:
    return CognitiveStateSnapshot(
        route_context="user_request_heal",
        candidate_paths=("human_escalation", "low_risk_bypass", "standard_validation"),
        selected_path="",
        rationale_enum="pending",
        risk_score=0.0,
        budget_est=0.0,
    )


@pytest.fixture
def after_state() -> CognitiveStateSnapshot:
    return CognitiveStateSnapshot(
        route_context="user_request_heal",
        candidate_paths=("human_escalation", "low_risk_bypass", "standard_validation"),
        selected_path="standard_validation",
        rationale_enum="low_risk_deterministic",
        risk_score=0.15,
        budget_est=0.3,
    )


# ===========================================================================
# 1. Contract / serialization
# ===========================================================================


class TestContractSerialization:
    def test_to_dict_stable_json(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        j = json.dumps(bundle.to_dict(), sort_keys=True, separators=(",", ":"))
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["artifact_type"] == "COGNITIVE_DIFF_BUNDLE"
        assert parsed["semantic_clock"]["tick"] == 7

    def test_diff_ops_sorted_by_path(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        paths = [op.path for op in bundle.diff]
        assert paths == sorted(paths)

    def test_to_dict_has_all_top_level_keys(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        d = bundle.to_dict()
        assert set(d.keys()) == {
            "artifact_type",
            "semantic_clock",
            "trace_id",
            "before",
            "after",
            "diff",
            "policy_config_hash",
        }

    def test_frozen_immutable(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        with pytest.raises(AttributeError):
            bundle.trace_id = "mutated"  # type: ignore[misc]

    def test_wrong_artifact_type_raises(self, clock, before_state, after_state):
        with pytest.raises(ValueError, match="artifact_type must be"):
            L3CognitiveDiffBundle(
                artifact_type="WRONG",
                semantic_clock=clock,
                trace_id="t1",
                before=before_state,
                after=after_state,
                diff=(),
            )

    def test_unsorted_diff_raises(self, clock, before_state, after_state):
        with pytest.raises(ValueError, match="diff ops must be sorted"):
            L3CognitiveDiffBundle(
                artifact_type="COGNITIVE_DIFF_BUNDLE",
                semantic_clock=clock,
                trace_id="t1",
                before=before_state,
                after=after_state,
                diff=(
                    DiffOp(path="z_field", before="a", after="b"),
                    DiffOp(path="a_field", before="x", after="y"),
                ),
            )


# ===========================================================================
# 2. SemanticClock enforcement
# ===========================================================================


class TestSemanticClockEnforcement:
    def test_none_semantic_clock_raises_on_bundle(self, before_state, after_state):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            L3CognitiveDiffBundle(
                artifact_type="COGNITIVE_DIFF_BUNDLE",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="t1",
                before=before_state,
                after=after_state,
                diff=(),
            )

    def test_none_semantic_clock_raises_on_emit(self, before_state, after_state):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            emit_cognitive_diff_bundle(
                before=before_state,
                after=after_state,
                semantic_clock=None,  # type: ignore[arg-type]
            )


# ===========================================================================
# 3. Determinism / idempotency
# ===========================================================================


class TestDeterminismIdempotency:
    def test_same_inputs_byte_identical_json(
        self,
        clock,
        before_state,
        after_state,
    ):
        def _make():
            return emit_cognitive_diff_bundle(
                before=before_state,
                after=after_state,
                semantic_clock=clock,
                policy_config_hash="hash_abc",
            )

        j1 = json.dumps(_make().to_dict(), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(_make().to_dict(), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_trace_id_deterministic_across_calls(
        self,
        clock,
        before_state,
        after_state,
    ):
        a = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        b = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        assert a.trace_id == b.trace_id

    def test_different_tick_different_trace_id(self, before_state, after_state):
        c1 = SemanticClockSnapshot(tick=1)
        c2 = SemanticClockSnapshot(tick=2)
        a = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=c1,
        )
        b = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=c2,
        )
        assert a.trace_id != b.trace_id

    def test_no_diff_produces_empty_ops(self, clock, before_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=before_state,
            semantic_clock=clock,
        )
        assert bundle.diff == ()


# ===========================================================================
# 4. Integration seam: before/after → expected diff ops
# ===========================================================================


class TestIntegrationSeam:
    def test_changed_fields_produce_diff_ops(self, before_state, after_state):
        diff = compute_cognitive_diff(before_state, after_state)
        diff_paths = {op.path for op in diff}
        assert "selected_path" in diff_paths
        assert "rationale_enum" in diff_paths
        assert "risk_score" in diff_paths
        assert "budget_est" in diff_paths

    def test_unchanged_fields_not_in_diff(self, before_state, after_state):
        diff = compute_cognitive_diff(before_state, after_state)
        diff_paths = {op.path for op in diff}
        assert "route_context" not in diff_paths
        assert "candidate_paths" not in diff_paths

    def test_diff_op_values_correct(self, before_state, after_state):
        diff = compute_cognitive_diff(before_state, after_state)
        sp_op = next(op for op in diff if op.path == "selected_path")
        assert sp_op.before == ""
        assert sp_op.after == "standard_validation"

    def test_full_bundle_contains_expected_diff(
        self,
        clock,
        before_state,
        after_state,
    ):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        d = bundle.to_dict()
        diff_paths = [op["path"] for op in d["diff"]]
        assert diff_paths == sorted(diff_paths)
        assert "selected_path" in diff_paths

    def test_snapshot_unsorted_candidates_raises(self):
        with pytest.raises(ValueError, match="candidate_paths must be sorted"):
            CognitiveStateSnapshot(
                route_context="ctx",
                candidate_paths=("z_path", "a_path"),
                selected_path="z_path",
                rationale_enum="test",
                risk_score=0.0,
                budget_est=0.0,
            )

    def test_diff_op_empty_path_raises(self):
        with pytest.raises(ValueError, match="path must be non-empty"):
            DiffOp(path="", before="a", after="b")

    def test_policy_config_hash_propagated(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
            policy_config_hash="policy_xyz",
        )
        assert bundle.policy_config_hash == "policy_xyz"
        assert bundle.to_dict()["policy_config_hash"] == "policy_xyz"
