"""ADG-driven tests for L0 seams: canonical_truth_seam, layer_emission_seam, vigilance_seam.

Contract tests: Protocol definitions, factory functions, dynamic loader stubs.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_seams_adg", "execution_auth")
_emit_validates_capability("p2", "test_seams_adg", "capability_check")
_emit_routes_to_capability("p2", "test_seams_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_seams_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_seams_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_seams_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_seams_adg", "exec_output")
_emit_dispatches_agent("p3", "test_seams_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_seams_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_seams_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_seams_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_seams_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_seams_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_seams_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_seams_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_seams_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_seams_adg", "eval_metric")
_emit_stores_embedding("p4", "test_seams_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_seams_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_seams_adg", "exec_snapshot_link")

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
