"""ADG burndown gate surface tests.

Kept in a SEPARATE file from test_execute_ssot_adg_surfaces.py because
ops_scripts.ci.adg_burndown_gate replaces sys.stdout/sys.stderr at module-import
time on Windows (to force UTF-8), which destroys pytest's capture handles if the
module is imported inside a test that runs alongside capture-dependent tests.

The ``restore_stdio`` autouse fixture in this file saves and restores
sys.stdout/sys.stderr around every test so pytest capture stays intact.

Coverage:
  [ADG-1a] _resolve_adg_file_graph — picks latest by sorted glob
  [ADG-1b] _resolve_adg_file_graph — sentinel fallback when no candidates
  [ADG-1c] stale hardcoded path 03122026 no longer present in source
  [ADG-1d] _ADG_FILE_GRAPH is a Path produced by _resolve_adg_file_graph
  [ADG-1e] _load_adg_importer_counts degrades on missing file
  [ADG-1f] _load_adg_importer_counts parses edges and counts correctly
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
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

_emit_records_execution_trace("p0", "evidence", "test_adg_burndown_gate_surfaces")
_emit_applies_guardrail("p0", "test_adg_burndown_gate_surfaces", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_burndown_gate_surfaces", "policy_binding")
_emit_snapshots_state("p0", "test_adg_burndown_gate_surfaces", "state_snapshot")
emit_replay_key("p0", "test_adg_burndown_gate_surfaces")
emit_determinism_digest("p0", "test_adg_burndown_gate_surfaces")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_burndown_gate_surfaces", "execution_auth")
_emit_validates_capability("p2", "test_adg_burndown_gate_surfaces", "capability_check")
_emit_routes_to_capability("p2", "test_adg_burndown_gate_surfaces", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_burndown_gate_surfaces", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_burndown_gate_surfaces", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_burndown_gate_surfaces", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_burndown_gate_surfaces", "exec_output")
_emit_dispatches_agent("p3", "test_adg_burndown_gate_surfaces", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_burndown_gate_surfaces", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_burndown_gate_surfaces", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_burndown_gate_surfaces", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_burndown_gate_surfaces", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_burndown_gate_surfaces", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_burndown_gate_surfaces", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_burndown_gate_surfaces", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_burndown_gate_surfaces", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_burndown_gate_surfaces", "eval_metric")
_emit_stores_embedding("p4", "test_adg_burndown_gate_surfaces", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_burndown_gate_surfaces", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_burndown_gate_surfaces", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture(autouse=True)
def restore_stdio():
    """Save and restore sys.stdout/sys.stderr around every test.

    adg_burndown_gate replaces both at module-import time on Windows.
    Without this fixture pytest's capture tmpfile handle is destroyed and
    every subsequent test in the session raises:
        ValueError: I/O operation on closed file
    """
    orig_out = sys.stdout
    orig_err = sys.stderr
    yield
    sys.stdout = orig_out
    sys.stderr = orig_err


@pytest.mark.unit
def test_resolve_adg_file_graph_latest_by_sorted_name() -> None:
    """Sorted descending glob → lexicographically last file is chosen."""
    from ops_scripts.ci.adg_burndown_gate import _resolve_adg_file_graph

    tmp = Path(tempfile.mkdtemp())
    try:
        adg_dir = tmp / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        (adg_dir / "adg_file_graph_03122026.json").write_text("{}")
        (adg_dir / "adg_file_graph_03132026_0840.json").write_text("{}")
        result = _resolve_adg_file_graph(tmp)
        assert result.name == "adg_file_graph_03132026_0840.json"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.mark.unit
def test_resolve_adg_file_graph_fallback_when_no_candidates() -> None:
    """When no adg_file_graph_*.json exists, a sentinel path is returned."""
    from ops_scripts.ci.adg_burndown_gate import _resolve_adg_file_graph

    tmp = Path(tempfile.mkdtemp())
    try:
        adg_dir = tmp / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        result = _resolve_adg_file_graph(tmp)
        assert result.name == "adg_file_graph.json"
        assert not result.exists()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.mark.unit
def test_stale_hardcoded_path_03122026_absent_from_source() -> None:
    """The old hardcoded path must not appear anywhere in adg_burndown_gate.py."""
    gate_src = (_REPO_ROOT / "ops_scripts" / "ci" / "adg_burndown_gate.py").read_text(encoding="utf-8")
    assert "adg_file_graph_03122026.json" not in gate_src, (
        "Stale hardcoded path 'adg_file_graph_03122026.json' still present"
    )


@pytest.mark.unit
def test_adg_file_graph_constant_is_path_not_string() -> None:
    """_ADG_FILE_GRAPH must be a Path produced by _resolve_adg_file_graph."""
    import ops_scripts.ci.adg_burndown_gate as gate

    assert callable(gate._resolve_adg_file_graph)
    assert isinstance(gate._ADG_FILE_GRAPH, Path)


@pytest.mark.unit
def test_load_adg_importer_counts_returns_empty_on_missing_file() -> None:
    """_load_adg_importer_counts must degrade gracefully when the file is absent."""
    import ops_scripts.ci.adg_burndown_gate as gate
    from ops_scripts.ci.adg_burndown_gate import _load_adg_importer_counts

    tmp = Path(tempfile.mkdtemp())
    original = gate._ADG_FILE_GRAPH
    try:
        gate._ADG_FILE_GRAPH = tmp / "nonexistent.json"
        result = _load_adg_importer_counts()
        assert result == {}
    finally:
        gate._ADG_FILE_GRAPH = original
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.mark.unit
def test_load_adg_importer_counts_parses_edges_correctly() -> None:
    """_load_adg_importer_counts counts unique edge sym entries per module path."""
    import ops_scripts.ci.adg_burndown_gate as gate
    from ops_scripts.ci.adg_burndown_gate import _load_adg_importer_counts

    # The sym->path conversion drops the LAST dotted segment (it's the symbol name,
    # not the module name): "a.b.c.D" -> "a/b/c.py"
    graph = {
        "edges": [
            {"sym": "agentic_core.L0_routing.scripts.execute_ssot.SomeClass"},
            {"sym": "agentic_core.L0_routing.scripts.execute_ssot.OtherClass"},
            {"sym": "agentic_core.L5_safety.reasoning.LocationHealerAgent.heal"},
        ]
    }
    tmp = Path(tempfile.mkdtemp())
    original = gate._ADG_FILE_GRAPH
    try:
        adg_file = tmp / "adg_file_graph_test.json"
        adg_file.write_text(json.dumps(graph), encoding="utf-8")
        gate._ADG_FILE_GRAPH = adg_file
        counts = _load_adg_importer_counts()
        assert counts.get("agentic_core/L0_routing/scripts/execute_ssot.py", 0) == 2
        assert counts.get("agentic_core/L5_safety/reasoning/LocationHealerAgent.py", 0) == 1
    finally:
        gate._ADG_FILE_GRAPH = original
        shutil.rmtree(tmp, ignore_errors=True)
