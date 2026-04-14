"""ADG contract tests for StateManagementAgent source structure."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "agentic_core" / "L3_orchestration" / "reasoning" / "StateManagementAgent.py"


def _tree() -> ast.AST:
    return ast.parse(SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names() -> set[str]:
    return {node.name for node in ast.walk(_tree()) if isinstance(node, ast.ClassDef)}


def _methods_of(class_name: str) -> set[str]:
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {child.name for child in node.body if isinstance(child, ast.FunctionDef)}
    return set()


def _src_text() -> str:
    return SRC.read_text(encoding="utf-8", errors="replace")


class TestStateManagementAgentSource:
    def test_source_exists(self):
        assert SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_state_entry_class(self):
        assert "StateEntry" in _class_names()

    def test_has_state_management_agent_class(self):
        assert "StateManagementAgent" in _class_names()

    def test_state_entry_has_key_field(self):
        assert "key" in _src_text()

    def test_state_entry_has_file_path_field(self):
        assert "file_path" in _src_text()

    def test_state_management_agent_has_run_or_execute(self):
        methods = _methods_of("StateManagementAgent")
        assert "run" in methods or "execute" in methods
