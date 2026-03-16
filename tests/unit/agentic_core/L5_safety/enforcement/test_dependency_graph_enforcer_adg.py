"""ADG-driven tests for L5_safety/enforcement/dependency_graph_enforcer.py — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_dependency_graph_enforcer_adg")
_emit_applies_guardrail("p0", "test_dependency_graph_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_dependency_graph_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_dependency_graph_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_dependency_graph_enforcer_adg")
emit_determinism_digest("p0", "test_dependency_graph_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.dependency_graph_enforcer import DependencyGraph


class TestDependencyGraph:
    def test_creates(self):
        g = DependencyGraph()
        assert g is not None

    def test_graph_starts_empty(self):
        g = DependencyGraph()
        assert g.graph == {}

    def test_reverse_graph_starts_empty(self):
        g = DependencyGraph()
        assert g.reverse_graph == {}

    def test_has_build(self):
        assert hasattr(DependencyGraph, "build")

    def test_build_empty_list(self):
        g = DependencyGraph()
        g.build([])
        assert g.graph == {}

    def test_build_existing_file(self, tmp_path):
        src = tmp_path / "sample.py"
        src.write_text("import os\nfrom pathlib import Path\n", encoding="utf-8")
        g = DependencyGraph()
        g.build([str(src)])
        assert str(src) in g.graph
        assert "os" in g.graph[str(src)]["imports"]
