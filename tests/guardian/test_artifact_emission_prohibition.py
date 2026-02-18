"""G-2-6 — Artifact Emission Prohibition Tests.

Negative tests proving L0/L5/L6 cannot emit RESULT or HEALING_PLAN artifacts.
Positive control: L2 emission is permitted.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.routing_artifact_types import (
    HealingPlan,
    ResultArtifact,
)
from agentic_core.L5_safety.enforcement.artifact_emission_prohibition import (
    FORBIDDEN_ARTIFACT_KINDS,
    FORBIDDEN_EMISSION_LAYERS,
    assert_layer_may_emit,
)

# =============================================================================
# NEGATIVE: RESULT emission from L0 raises
# =============================================================================


class TestResultEmissionBlocked:
    def test_l0_result_raises(self):
        with pytest.raises(PermissionError, match="ARTIFACT_EMISSION_PROHIBITED.*layer=L0.*RESULT"):
            ResultArtifact(
                trace_id="t-001",
                execution_outcome="success",
                final_state_hash="abc123",
                artifact_class="heal",
                emitting_layer="L0",
            )

    def test_l5_result_raises(self):
        with pytest.raises(PermissionError, match="ARTIFACT_EMISSION_PROHIBITED.*layer=L5.*RESULT"):
            ResultArtifact(
                trace_id="t-002",
                execution_outcome="success",
                final_state_hash="abc123",
                artifact_class="heal",
                emitting_layer="L5",
            )

    def test_l6_result_raises(self):
        with pytest.raises(PermissionError, match="ARTIFACT_EMISSION_PROHIBITED.*layer=L6.*RESULT"):
            ResultArtifact(
                trace_id="t-003",
                execution_outcome="success",
                final_state_hash="abc123",
                artifact_class="heal",
                emitting_layer="L6",
            )


# =============================================================================
# NEGATIVE: HEALING_PLAN emission from L0/L5/L6 raises
# =============================================================================


class TestHealingPlanEmissionBlocked:
    def test_l0_healing_plan_raises(self):
        with pytest.raises(PermissionError, match="ARTIFACT_EMISSION_PROHIBITED.*layer=L0.*HEALING_PLAN"):
            HealingPlan(
                trace_id="t-010",
                plan_id="p-001",
                manifests=("m1",),
                semantic_clock_tick=1,
                policy_liaison_node="node-1",
                emitting_layer="L0",
            )

    def test_l6_healing_plan_raises(self):
        with pytest.raises(PermissionError, match="ARTIFACT_EMISSION_PROHIBITED.*layer=L6.*HEALING_PLAN"):
            HealingPlan(
                trace_id="t-011",
                plan_id="p-002",
                manifests=("m1",),
                semantic_clock_tick=1,
                policy_liaison_node="node-1",
                emitting_layer="L6",
            )

    def test_l5_healing_plan_raises(self):
        with pytest.raises(PermissionError, match="ARTIFACT_EMISSION_PROHIBITED.*layer=L5.*HEALING_PLAN"):
            HealingPlan(
                trace_id="t-012",
                plan_id="p-003",
                manifests=("m1",),
                semantic_clock_tick=1,
                policy_liaison_node="node-1",
                emitting_layer="L5",
            )


# =============================================================================
# POSITIVE: L2 emission permitted
# =============================================================================


class TestL2EmissionPermitted:
    def test_l2_result_ok(self):
        r = ResultArtifact(
            trace_id="t-100",
            execution_outcome="success",
            final_state_hash="abc123",
            artifact_class="heal",
            emitting_layer="L2",
        )
        assert r.trace_id == "t-100"
        assert r.emitting_layer == "L2"

    def test_l2_healing_plan_ok(self):
        hp = HealingPlan(
            trace_id="t-101",
            plan_id="p-100",
            manifests=("m1", "m2"),
            semantic_clock_tick=5,
            policy_liaison_node="node-x",
            emitting_layer="L2",
        )
        assert hp.trace_id == "t-101"
        assert hp.emitting_layer == "L2"

    def test_default_layer_is_l2(self):
        r = ResultArtifact(
            trace_id="t-102",
            execution_outcome="ok",
            final_state_hash="h",
            artifact_class="c",
        )
        assert r.emitting_layer == "L2"

    def test_l3_result_ok(self):
        """L3 is not in the forbidden set."""
        r = ResultArtifact(
            trace_id="t-103",
            execution_outcome="ok",
            final_state_hash="h",
            artifact_class="c",
            emitting_layer="L3",
        )
        assert r.emitting_layer == "L3"


# =============================================================================
# DETERMINISTIC ERROR MESSAGE
# =============================================================================


class TestDeterministicMessage:
    def test_result_error_contains_trace_id(self):
        try:
            ResultArtifact(
                trace_id="my-trace-42",
                execution_outcome="ok",
                final_state_hash="h",
                artifact_class="c",
                emitting_layer="L0",
            )
        except PermissionError as e:
            msg = str(e)
            assert "layer=L0" in msg
            assert "artifact_kind=RESULT" in msg
            assert "trace_id=my-trace-42" in msg

    def test_healing_plan_error_contains_trace_id(self):
        try:
            HealingPlan(
                trace_id="hp-trace-99",
                plan_id="p-1",
                manifests=(),
                semantic_clock_tick=0,
                policy_liaison_node="n",
                emitting_layer="L6",
            )
        except PermissionError as e:
            msg = str(e)
            assert "layer=L6" in msg
            assert "artifact_kind=HEALING_PLAN" in msg
            assert "trace_id=hp-trace-99" in msg


# =============================================================================
# STRUCTURAL: guard function + constants
# =============================================================================


class TestStructural:
    def test_forbidden_layers_complete(self):
        assert FORBIDDEN_EMISSION_LAYERS == frozenset({"L0", "L5", "L6"})

    def test_forbidden_artifacts_complete(self):
        assert FORBIDDEN_ARTIFACT_KINDS == frozenset({"RESULT", "HEALING_PLAN"})

    def test_assert_layer_may_emit_allows_non_forbidden_combo(self):
        assert_layer_may_emit("INCIDENT", "L0")
        assert_layer_may_emit("RESULT", "L2")
        assert_layer_may_emit("HEALING_PLAN", "L2")
        assert_layer_may_emit("ROUTE_DECISION", "L0")

    def test_single_emission_module(self):
        import pathlib

        matches = list(pathlib.Path("agentic_core").rglob("artifact_emission_prohibition.py"))
        assert len(matches) == 1, f"Expected 1 module, found {len(matches)}: {matches}"
        assert "L5_safety" in str(matches[0])
