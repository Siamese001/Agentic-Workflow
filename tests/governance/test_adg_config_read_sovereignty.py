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
