"""ADG contract tests for agentic_core/runtime/utils/discovery_util.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.runtime.utils.discovery_util as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "runtime" / "utils" / "discovery_util.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestDiscoveryUtilSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_discovered_agent_record_class(self):
        assert "DiscoveredAgentRecord" in _class_names()

    def test_has_agent_registry_class(self):
        assert "AgentRegistry" in _class_names()

    def test_has_name_field(self):
        assert "name" in _src_text()

    def test_has_layer_field(self):
        assert "layer" in _src_text()

    def test_has_file_path_field(self):
        assert "file_path" in _src_text()

    def test_has_discover_all_method(self):
        assert "discover_all" in _methods_of("AgentRegistry")

    def test_agent_registry_has_discovered_agents(self):
        assert "discovered_agents" in _src_text()
