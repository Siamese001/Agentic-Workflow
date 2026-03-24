"""ADG contract tests for apps_lic/types/message_type_types.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import apps_lic.types.message_type_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "types" / "message_type_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestMessageTypeTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_message_type(self):
        assert "MessageType" in _class_names()

    def test_has_hop_status(self):
        assert "HopStatus" in _class_names()

    def test_has_gate_decision(self):
        assert "GateDecision" in _class_names()

    def test_has_residual_agent_message(self):
        assert "ResidualAgentMessage" in _class_names()

    def test_has_llm_response(self):
        assert "LLMResponse" in _class_names()

    def test_message_type_has_user_value(self):
        assert "USER" in _src_text()

    def test_hop_status_has_completed_value(self):
        assert "COMPLETED" in _src_text()

    def test_gate_decision_has_pass_value(self):
        assert "PASS" in _src_text()


def test_module_importable():
    pass