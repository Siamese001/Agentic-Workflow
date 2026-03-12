"""ADG contract tests for agentic_core/runtime/config/contextual_router_config.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "runtime" / "config" / "contextual_router_config.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestContextualRouterConfigSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_routing_request_class(self):
        assert "RoutingRequest" in _class_names()

    def test_has_route_decision_class(self):
        assert "RoutingResult" in _class_names() or "RouteDecision" in _class_names()

    def test_has_request_id_field(self):
        assert "request_id" in _src_text()

    def test_has_action_type_field(self):
        assert "action_type" in _src_text()

    def test_has_target_files_field(self):
        assert "target_files" in _src_text()

    def test_has_agent_name_field(self):
        assert "agent_name" in _src_text()

    def test_has_payload_field(self):
        assert "payload" in _src_text()
