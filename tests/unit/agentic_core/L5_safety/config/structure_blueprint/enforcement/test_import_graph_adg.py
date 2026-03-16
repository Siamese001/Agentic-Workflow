"""ADG-driven tests for L5 structure_blueprint/enforcement/import_graph.py — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_import_graph_adg")
_emit_applies_guardrail("p0", "test_import_graph_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_import_graph_adg", "policy_binding")
_emit_snapshots_state("p0", "test_import_graph_adg", "state_snapshot")
emit_replay_key("p0", "test_import_graph_adg")
emit_determinism_digest("p0", "test_import_graph_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_import_graph_adg", "execution_auth")
_emit_validates_capability("p2", "test_import_graph_adg", "capability_check")
_emit_routes_to_capability("p2", "test_import_graph_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_import_graph_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_import_graph_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_import_graph_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_import_graph_adg", "exec_output")
_emit_dispatches_agent("p3", "test_import_graph_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_import_graph_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_import_graph_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_import_graph_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_import_graph_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_import_graph_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_import_graph_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_import_graph_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_import_graph_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_import_graph_adg", "eval_metric")
_emit_stores_embedding("p4", "test_import_graph_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_import_graph_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_import_graph_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import (
    INTERNAL_ROOTS,
    ImportEdge,
)


class TestInternalRoots:
    def test_is_frozenset(self):
        assert isinstance(INTERNAL_ROOTS, frozenset)

    def test_contains_agentic_core(self):
        assert "agentic_core" in INTERNAL_ROOTS

    def test_contains_apps_rg(self):
        assert "apps_rg" in INTERNAL_ROOTS

    def test_contains_apps_lic(self):
        assert "apps_lic" in INTERNAL_ROOTS


class TestImportEdge:
    def test_creates(self):
        edge = ImportEdge(
            source_file="foo.py",
            target_module="agentic_core.utils",
            imported_names=("helper",),
            lineno=5,
        )
        assert edge.source_file == "foo.py"
        assert edge.target_module == "agentic_core.utils"

    def test_lineno_stored(self):
        edge = ImportEdge("a.py", "b.module", ("x",), 10)
        assert edge.lineno == 10

    def test_is_star_default_false(self):
        edge = ImportEdge("a.py", "b", (), 1)
        assert edge.is_star is False

    def test_is_star_set(self):
        edge = ImportEdge("a.py", "b", (), 1, is_star=True)
        assert edge.is_star is True

    def test_repr_contains_source(self):
        edge = ImportEdge("foo.py", "bar.mod", (), 7)
        assert "foo.py" in repr(edge)
