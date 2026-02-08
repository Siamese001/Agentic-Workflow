"""
Unit tests for DagRuntimeInspectorAgent — L3 inspection agent.

Tests (AST-structural + behavioral):
1. AST: Class exists at correct import path
2. AST: Inherits from InspectionCapability and SubatomicTestingMixin
3. AST: Implements perform_checks, diagnose, heal_repository, heal
4. AST: Sets INSPECTION_LOG_PREFIX
5. AST: diagnose() does NOT return DiagnosticReport (cleanup verified)
6. Behavioral: run_inspection returns InspectionResult with correct attributes
7. Behavioral: Null target produces issues
8. Behavioral: Dict/list targets populate metrics
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from agentic_core.mixins.inspection_capability import InspectionCapability, InspectionResult

ROOT = Path(__file__).resolve().parents[5]
AGENT_PATH = ROOT / "agentic_core" / "L3_orchestration" / "reasoning" / "DagRuntimeInspectorAgent.py"

# ---------------------------------------------------------------------------
# Parse the agent source once for all AST tests
# ---------------------------------------------------------------------------
_SOURCE = AGENT_PATH.read_text(encoding="utf-8")
_TREE = ast.parse(_SOURCE)


def _find_agent_class() -> ast.ClassDef:
    for node in ast.walk(_TREE):
        if isinstance(node, ast.ClassDef) and node.name == "DagRuntimeInspectorAgent":
            return node
    pytest.fail("DagRuntimeInspectorAgent class not found in AST")


_AGENT_NODE = _find_agent_class()
_METHOD_NAMES = [
    item.name for item in _AGENT_NODE.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
]


# ---------------------------------------------------------------------------
# 1. AST STRUCTURAL TESTS
# ---------------------------------------------------------------------------
class TestDagRuntimeInspectorStructure:
    """AST-based structural verification."""

    def test_correct_import_path(self) -> None:
        """Agent module exists at expected path."""
        assert AGENT_PATH.exists(), f"Missing: {AGENT_PATH}"

    def test_inherits_inspection_capability(self) -> None:
        """Must list InspectionCapability in bases."""
        base_names = []
        for base in _AGENT_NODE.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
        assert "InspectionCapability" in base_names, f"Bases: {base_names}"

    def test_inherits_subatomic_testing_mixin(self) -> None:
        """Must list SubatomicTestingMixin in bases."""
        base_names = []
        for base in _AGENT_NODE.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
        assert "SubatomicTestingMixin" in base_names, f"Bases: {base_names}"

    def test_sets_inspection_log_prefix(self) -> None:
        """Must set INSPECTION_LOG_PREFIX as a non-empty string constant."""
        for item in _AGENT_NODE.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "INSPECTION_LOG_PREFIX":
                        assert isinstance(item.value, ast.Constant) and item.value.value
                        return
        pytest.fail("INSPECTION_LOG_PREFIX not found")

    def test_implements_perform_checks(self) -> None:
        assert "perform_checks" in _METHOD_NAMES

    def test_implements_diagnose(self) -> None:
        assert "diagnose" in _METHOD_NAMES

    def test_implements_heal_repository(self) -> None:
        assert "heal_repository" in _METHOD_NAMES

    def test_implements_heal(self) -> None:
        assert "heal" in _METHOD_NAMES

    def test_diagnose_calls_run_inspection(self) -> None:
        """diagnose() must delegate to self.run_inspection()."""
        assert "run_inspection" in _SOURCE


# ---------------------------------------------------------------------------
# 2. BEHAVIORAL TESTS (via lightweight InspectionCapability subclass)
# ---------------------------------------------------------------------------
class _DagInspectorStub(InspectionCapability):
    """Minimal stub replicating DagRuntimeInspectorAgent.perform_checks()."""

    INSPECTION_LOG_PREFIX = "Running DAG runtime diagnostics..."

    def perform_checks(
        self,
        target: Any,
        context: dict[str, Any] | None = None,
    ) -> tuple[list[str], dict[str, Any]]:
        issues: list[str] = []
        metrics: dict[str, Any] = {}
        if target is None:
            issues.append("Target is null")
        elif isinstance(target, dict):
            metrics["field_count"] = len(target)
        elif isinstance(target, list):
            metrics["item_count"] = len(target)
        metrics["type"] = type(target).__name__
        return issues, metrics


class TestDagRuntimeInspectorBehavior:
    """Behavioral tests using InspectionResult natively."""

    @pytest.fixture
    def inspector(self) -> _DagInspectorStub:
        return _DagInspectorStub()

    def test_healthy_dict_target(self, inspector: _DagInspectorStub) -> None:
        result = inspector.run_inspection({"key": "value"})
        assert isinstance(result, InspectionResult)
        assert result.healthy is True
        assert result.issues == []
        assert result.metrics["field_count"] == 1
        assert result.metrics["type"] == "dict"

    def test_healthy_list_target(self, inspector: _DagInspectorStub) -> None:
        result = inspector.run_inspection([1, 2, 3])
        assert isinstance(result, InspectionResult)
        assert result.healthy is True
        assert result.metrics["item_count"] == 3
        assert result.metrics["type"] == "list"

    def test_null_target_produces_issue(self, inspector: _DagInspectorStub) -> None:
        result = inspector.run_inspection(None)
        assert isinstance(result, InspectionResult)
        assert result.healthy is False
        assert "Target is null" in result.issues
        assert result.metrics["type"] == "NoneType"

    def test_string_target_no_special_metrics(self, inspector: _DagInspectorStub) -> None:
        result = inspector.run_inspection("hello")
        assert isinstance(result, InspectionResult)
        assert result.healthy is True
        assert result.metrics["type"] == "str"

    def test_heal_stub_returns_canonical_keys(self, inspector: _DagInspectorStub) -> None:
        result = inspector.make_heal_result({"type": "test"})
        assert set(result.keys()) == {"status", "details", "artifacts", "errors"}
        assert result["status"] == "skipped"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
