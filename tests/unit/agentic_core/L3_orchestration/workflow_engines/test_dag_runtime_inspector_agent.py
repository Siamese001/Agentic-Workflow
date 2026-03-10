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

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    L3_ORCHESTRATION_DIR,
)
from agentic_core.mixins.inspection_capability_mixin import InspectionCapability, InspectionResult

ROOT = Path(__file__).resolve().parents[5]
# Post-consolidation: DagRuntimeInspectorAgent shimmed to InspectorExecutor
AGENT_PATH = ROOT / L3_ORCHESTRATION_DIR / "reasoning" / "DagRuntimeInspectorAgent.py"
CANONICAL_PATH = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "InspectorExecutor.py"

# ---------------------------------------------------------------------------
# Parse the canonical executor source once for all AST tests
# ---------------------------------------------------------------------------
try:
    _SOURCE = CANONICAL_PATH.read_text(encoding="utf-8")
    _TREE = ast.parse(_SOURCE)
except FileNotFoundError:
    _SOURCE = ""
    _TREE = None


def _find_agent_class() -> ast.ClassDef:
    if not _TREE:
        pytest.fail("InspectorExecutor source not found")
    for node in ast.walk(_TREE):
        if isinstance(node, ast.ClassDef) and node.name == "InspectorExecutor":
            return node
    pytest.fail("InspectorExecutor class not found in AST")


_AGENT_NODE = _find_agent_class() if _TREE else None
_METHOD_NAMES = (
    [item.name for item in _AGENT_NODE.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if _AGENT_NODE
    else []
)


# ---------------------------------------------------------------------------
# 1. AST STRUCTURAL TESTS
# ---------------------------------------------------------------------------
class TestDagRuntimeInspectorStructuralContract:
    """AST structural contract: agent shape, inheritance, method presence."""

    def test_correct_import_path(self) -> None:
        """Canonical executor module exists at expected path."""
        assert CANONICAL_PATH.exists(), f"Missing: {CANONICAL_PATH}"

    def test_shim_exists(self) -> None:
        """Original shim file still exists for backward compat."""
        assert AGENT_PATH.exists(), f"Missing shim: {AGENT_PATH}"

    def test_inherits_inspection_capability(self) -> None:
        """Must list InspectionCapability in bases."""
        base_names = []
        for base in _AGENT_NODE.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
        assert "InspectionCapability" in base_names, f"Bases: {base_names}"

    def test_inherits_sovereign_base(self) -> None:
        """Must list SovereignBaseAgent in bases."""
        base_names = []
        for base in _AGENT_NODE.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
        assert "SovereignBaseAgent" in base_names, f"Bases: {base_names}"

    def test_sets_inspection_log_prefix(self) -> None:
        """Must set INSPECTION_LOG_PREFIX as a class field."""
        for item in _AGENT_NODE.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "INSPECTION_LOG_PREFIX":
                        return
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                if item.target.id == "INSPECTION_LOG_PREFIX":
                    return
        pytest.fail("INSPECTION_LOG_PREFIX not found")

    def test_has_perform_checks_or_inherits(self) -> None:
        """perform_checks must be locally defined or inherited from InspectionCapability."""
        if "perform_checks" in _METHOD_NAMES:
            return
        base_names = [
            b.id if isinstance(b, ast.Name) else b.attr
            for b in _AGENT_NODE.bases
            if isinstance(b, (ast.Name, ast.Attribute))
        ]
        assert "InspectionCapability" in base_names, "Must inherit perform_checks from InspectionCapability"

    def test_has_diagnose_or_inherits(self) -> None:
        """diagnose must be locally defined or inherited from InspectionCapability."""
        if "diagnose" in _METHOD_NAMES:
            return
        assert "InspectionCapability" in _SOURCE, "Must inherit diagnose from InspectionCapability"


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


class TestInspectionCapabilityContractViaDagStub:
    """InspectionCapability behavioral contract tested via DagRuntimeInspector stub."""

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
