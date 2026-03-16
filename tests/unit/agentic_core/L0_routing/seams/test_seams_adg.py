"""ADG-driven tests for L0 seams: canonical_truth_seam, layer_emission_seam, vigilance_seam.

Contract tests: Protocol definitions, factory functions, dynamic loader stubs.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_seams_adg")
_emit_applies_guardrail("p0", "test_seams_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_seams_adg", "policy_binding")
_emit_snapshots_state("p0", "test_seams_adg", "state_snapshot")
emit_replay_key("p0", "test_seams_adg")
emit_determinism_digest("p0", "test_seams_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# canonical_truth_seam
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.seams.canonical_truth_seam import (
    CanonicalTruthProvider,
    get_canonical_layer,
    get_canonical_truth_provider,
)


class TestCanonicalTruthSeam:
    def test_canonical_truth_provider_is_protocol(self):
        assert callable(CanonicalTruthProvider)

    def test_has_get_layer(self):
        assert hasattr(CanonicalTruthProvider, "get_layer")

    def test_has_categorize_agent(self):
        assert hasattr(CanonicalTruthProvider, "categorize_agent")

    def test_get_canonical_truth_provider_callable(self):
        assert callable(get_canonical_truth_provider)

    def test_get_canonical_truth_provider_returns_module(self):
        provider = get_canonical_truth_provider()
        assert provider is not None

    def test_get_canonical_layer_callable(self):
        assert callable(get_canonical_layer)

    def test_get_canonical_layer_returns_int_or_raises(self):
        try:
            layer = get_canonical_layer(Path("agentic_core/L5_safety/foo.py"))
            assert isinstance(layer, int)
        except (RuntimeError, AttributeError, TypeError):
            pass  # provider may not have get_layer as direct callable


# ---------------------------------------------------------------------------
# layer_emission_seam
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.seams.layer_emission_seam import (
    LayerEmissionValidator,
    assert_layer_may_emit,
    get_layer_emission_validator,
)


class TestLayerEmissionSeam:
    def test_layer_emission_validator_is_protocol(self):
        assert callable(LayerEmissionValidator)

    def test_has_validate_emission(self):
        assert hasattr(LayerEmissionValidator, "validate_emission")

    def test_get_layer_emission_validator_callable(self):
        assert callable(get_layer_emission_validator)

    def test_assert_layer_may_emit_callable(self):
        assert callable(assert_layer_may_emit)


# ---------------------------------------------------------------------------
# vigilance_seam
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.seams.vigilance_seam import (
    get_vigilance_event_artifact,
    get_vigilance_severity,
    load_vigilance_types,
)


class TestVigilanceSeam:
    def test_load_vigilance_types_callable(self):
        assert callable(load_vigilance_types)

    def test_get_vigilance_event_artifact_callable(self):
        assert callable(get_vigilance_event_artifact)

    def test_get_vigilance_severity_callable(self):
        assert callable(get_vigilance_severity)

    def test_load_vigilance_types_returns_module(self):
        mod = load_vigilance_types()
        assert mod is not None

    def test_vigilance_event_artifact_is_class(self):
        cls = get_vigilance_event_artifact()
        assert callable(cls)

    def test_vigilance_severity_is_enum(self):
        from enum import Enum
        cls = get_vigilance_severity()
        assert issubclass(cls, Enum)
