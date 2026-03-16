"""H4 — ADG config-read sovereignty tests.

Verifies that Graph 5 (reads_from edges) correctly detects env/config reads
and that production sovereign layers have expected config read patterns.

Plan ref: tests/governance/test_adg_config_read_sovereignty.py
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import (
    ADGStaticScanner,
    Edge,
    _AttributeVisitor,
)
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

_emit_records_execution_trace("p0", "evidence", "test_adg_config_read_sovereignty")
_emit_applies_guardrail("p0", "test_adg_config_read_sovereignty", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_config_read_sovereignty", "policy_binding")
_emit_snapshots_state("p0", "test_adg_config_read_sovereignty", "state_snapshot")
emit_replay_key("p0", "test_adg_config_read_sovereignty")
emit_determinism_digest("p0", "test_adg_config_read_sovereignty")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_config_read_sovereignty", "execution_auth")
_emit_validates_capability("p2", "test_adg_config_read_sovereignty", "capability_check")
_emit_routes_to_capability("p2", "test_adg_config_read_sovereignty", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_config_read_sovereignty", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_config_read_sovereignty", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_config_read_sovereignty", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_config_read_sovereignty", "exec_output")
_emit_dispatches_agent("p3", "test_adg_config_read_sovereignty", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_config_read_sovereignty", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_config_read_sovereignty", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_config_read_sovereignty", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_config_read_sovereignty", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_config_read_sovereignty", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_config_read_sovereignty", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_config_read_sovereignty", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_config_read_sovereignty", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_config_read_sovereignty", "eval_metric")
_emit_stores_embedding("p4", "test_adg_config_read_sovereignty", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_config_read_sovereignty", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_config_read_sovereignty", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _visit(source: str) -> list[Edge]:
    tree = ast.parse(source)
    visitor = _AttributeVisitor("ADG::Module::test", "test.py")
    visitor.visit(tree)
    return visitor.edges


class TestConfigReadVisitor:
    """Unit-level: _AttributeVisitor correctly classifies reads."""

    def test_os_getenv_is_reads_env(self):
        edges = _visit("x = os.getenv('KEY')\n")
        assert any(e.edge_kind == "reads_env" for e in edges)

    def test_os_environ_get_is_reads_env(self):
        edges = _visit("x = os.environ.get('KEY', 'default')\n")
        assert any(e.edge_kind == "reads_env" for e in edges)

    def test_os_environ_subscript_via_attr(self):
        edges = _visit("x = os.environ\n")
        assert any(e.edge_kind == "reads_env" for e in edges)

    def test_secret_symbol_is_reads_secret(self):
        edges = _visit("val = get_secret('DB_PASS')\n")
        assert any(e.edge_kind == "reads_secret" for e in edges)

    def test_policy_symbol_is_reads_policy_state(self):
        edges = _visit("v = get_policy_value('ALLOW_X')\n")
        assert any(e.edge_kind == "reads_policy_state" for e in edges)

    def test_config_get_is_reads_config(self):
        edges = _visit("x = config.get('key')\n")
        assert any(e.edge_kind == "reads_config" for e in edges)

    def test_non_config_call_not_flagged(self):
        edges = _visit("x = some_other_function()\n")
        assert edges == []

    def test_multiple_reads_in_file(self):
        src = "a = os.getenv('A')\nb = os.environ.get('B')\n"
        edges = _visit(src)
        env_edges = [e for e in edges if e.edge_kind == "reads_env"]
        assert len(env_edges) >= 1


class TestConfigReadSovereignty:
    """Integration: sovereign layers must not bypass config reads."""

    def test_reads_from_edges_exist_in_full_scan(self):
        """A full scan must produce at minimum 50 reads_from edges (evidence floor)."""
        scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=False)
        result = scanner.scan()
        counts = result.edge_counts_by_relation()
        actual = counts.get("reads_from", 0)
        assert actual >= 50, (
            f"reads_from edge count {actual} below evidence floor 50. "
            "Graph 5 may not be extracting correctly."
        )

    def test_reads_from_edges_have_correct_sub_types(self):
        """All reads_from edges must have a valid sub-type."""
        scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=False)
        result = scanner.scan()
        valid_sub_types = {
            "reads_env",
            "reads_config",
            "reads_secret",
            "reads_runtime_state",
            "reads_policy_state",
        }
        reads_edges = [e for e in result.edges if e.relation_type == "reads_from"]
        invalid = [e for e in reads_edges if e.edge_kind not in valid_sub_types]
        assert invalid == [], f"reads_from edges with invalid edge_kind: {invalid[:5]}"
