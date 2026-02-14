"""Wave 7.0.1 — Meta-Learning Proposal Contract Tests.

Tests deterministic serialization, immutable-target rejection,
semantic-clock enforcement, delta consistency, forbidden-key absence,
and trace-id determinism.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L7_meta_learning.types.meta_learning_types import (
    IMMUTABLE_COMPONENTS,
    MetaLearningProposalArtifact,
    ObjectiveSignal,
    ProposedChange,
    build_meta_learning_proposal,
)

# =============================================================================
# Helpers
# =============================================================================

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))
_EVIDENCE = "abc123"


def _build_sample(**overrides) -> MetaLearningProposalArtifact:
    """Build a sample proposal with sensible defaults, accepting overrides."""
    defaults = {
        "semantic_clock": _CLOCK,
        "proposer": "test_subsystem",
        "target_component": "routing_thresholds",
        "before": {"threshold": 0.5},
        "after": {"threshold": 0.7},
        "metric_name": "accuracy",
        "baseline": 0.80,
        "candidate": 0.85,
        "evidence_hash": _EVIDENCE,
        "policy_config_hash": None,
    }
    defaults.update(overrides)
    return build_meta_learning_proposal(**defaults)


# =============================================================================
# §1 — Deterministic Serialization
# =============================================================================


class TestDeterministicSerialization:
    def test_deterministic_serialization(self) -> None:
        """Two identical proposals → byte-identical JSON."""
        a = _build_sample()
        b = _build_sample()
        assert a.to_json() == b.to_json()
        assert json.loads(a.to_json()) == json.loads(b.to_json())


# =============================================================================
# §2 — Missing Semantic Clock Rejected
# =============================================================================


class TestSemanticClockEnforcement:
    def test_missing_semantic_clock_rejected(self) -> None:
        """Raises ValueError when semantic_clock is None."""
        with pytest.raises(ValueError, match="semantic_clock is required"):
            MetaLearningProposalArtifact(
                artifact_type="META_LEARNING_PROPOSAL",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="dummy",
                proposer="test",
                target_component="routing_thresholds",
                proposed_change=ProposedChange.from_dicts({}, {}),
                objective_signal=ObjectiveSignal(metric_name="m", baseline=0.0, candidate=0.0, delta=0.0),
                evidence_hash="x",
                policy_config_hash=None,
            )


# =============================================================================
# §3 — Immutable Component Rejected
# =============================================================================


class TestImmutableComponentRejection:
    def test_immutable_component_rejected(self) -> None:
        """target_component='guardian_contract' → ValueError('IMMUTABLE_TARGET')."""
        with pytest.raises(ValueError, match="IMMUTABLE_TARGET"):
            _build_sample(target_component="guardian_contract")

    @pytest.mark.parametrize("component", sorted(IMMUTABLE_COMPONENTS))
    def test_all_immutable_components_rejected(self, component: str) -> None:
        """Every member of IMMUTABLE_COMPONENTS must be rejected."""
        with pytest.raises(ValueError, match="IMMUTABLE_TARGET"):
            _build_sample(target_component=component)


# =============================================================================
# §4 — Delta Calculation Consistent
# =============================================================================


class TestDeltaCalculation:
    def test_delta_calculation_consistent(self) -> None:
        """delta == candidate - baseline (float stable)."""
        proposal = _build_sample(baseline=0.80, candidate=0.85)
        assert proposal.objective_signal.delta == pytest.approx(0.05)
        assert proposal.objective_signal.delta == pytest.approx(
            proposal.objective_signal.candidate - proposal.objective_signal.baseline
        )

    def test_negative_delta(self) -> None:
        """Negative delta is correctly computed."""
        proposal = _build_sample(baseline=0.90, candidate=0.80)
        assert proposal.objective_signal.delta == pytest.approx(-0.10)


# =============================================================================
# §5 — No Runtime Fields Present
# =============================================================================

FORBIDDEN_KEYS = {"exec", "import", "path", "file", "code"}


class TestNoRuntimeFields:
    def test_no_runtime_fields_present(self) -> None:
        """Assert forbidden keys not in artifact JSON."""
        proposal = _build_sample()
        raw = proposal.to_json()
        payload = json.loads(raw)
        self._assert_no_forbidden_keys(payload)

    def _assert_no_forbidden_keys(self, obj: object, path: str = "") -> None:
        """Recursively check no forbidden top-level or nested keys."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in FORBIDDEN_KEYS, f"Forbidden key '{key}' found at {path}.{key}"
                self._assert_no_forbidden_keys(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._assert_no_forbidden_keys(item, f"{path}[{i}]")


# =============================================================================
# §6 — Trace ID Deterministic
# =============================================================================


class TestTraceIdDeterminism:
    def test_trace_id_deterministic(self) -> None:
        """Same input → identical trace_id."""
        a = _build_sample()
        b = _build_sample()
        assert a.trace_id == b.trace_id
        assert len(a.trace_id) == 64  # SHA-256 hex

    def test_trace_id_stable_under_dict_reorder(self) -> None:
        """Shuffled dict order → identical trace_id."""
        before_a = {"x": 1, "y": 2, "z": 3}
        after_a = {"a": 10, "b": 20}

        before_b = {"z": 3, "x": 1, "y": 2}
        after_b = {"b": 20, "a": 10}

        a = _build_sample(before=before_a, after=after_a)
        b = _build_sample(before=before_b, after=after_b)
        assert a.trace_id == b.trace_id

    def test_different_input_different_trace_id(self) -> None:
        """Different inputs must produce different trace_ids."""
        a = _build_sample(baseline=0.80, candidate=0.85)
        b = _build_sample(baseline=0.70, candidate=0.75)
        assert a.trace_id != b.trace_id
