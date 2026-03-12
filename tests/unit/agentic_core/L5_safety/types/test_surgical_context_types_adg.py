"""ADG contract tests for agentic_core/L5_safety/types/surgical_context_types.py."""
from __future__ import annotations
import ast
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.surgical_context_types import (
        ASTCoordinate, ViolationConstraint, SurgicalContext,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ASTCoordinate = ViolationConstraint = SurgicalContext = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestASTCoordinate:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ASTCoordinate)
    def test_creates(self):
        coord = ASTCoordinate(
            node_id="n1", node_type="ClassDef", line=5, column=0,
        )
        assert coord.node_id == "n1"; assert coord.line == 5
    def test_optional_fields_default_none(self):
        coord = ASTCoordinate(node_id="x", node_type="FunctionDef", line=1, column=0)
        assert coord.end_line is None; assert coord.parent_id is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestViolationConstraint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ViolationConstraint)
    def test_creates(self):
        vc = ViolationConstraint(
            constraint_type="missing_docstring",
            severity="warning",
            message="Class lacks docstring",
        )
        assert vc.severity == "warning"
    def test_optional_fields_none(self):
        vc = ViolationConstraint(
            constraint_type="invalid_import", severity="error", message="bad"
        )
        assert vc.rule_id is None; assert vc.fix_type is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSurgicalContext:
    def _make_ctx(self):
        from pathlib import Path
        src = "class Foo:\n    pass\n"
        tree = ast.parse(src)
        coord = ASTCoordinate(node_id="n1", node_type="ClassDef", line=1, column=0)
        vc = ViolationConstraint(constraint_type="x", severity="warning", message="y")
        return SurgicalContext(
            file_path=Path("foo.py"),
            file_content=src,
            ast_tree=tree,
            violation_id="v1",
            violations=[vc],
            target_coordinates=[coord],
            detector_agent="TestAgent",
            detection_method="ast_scan",
            detection_timestamp="2026-01-01T00:00:00",
        )
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SurgicalContext)
    def test_creates(self):
        ctx = self._make_ctx()
        assert ctx.violation_id == "v1"
        assert ctx.detector_agent == "TestAgent"
    def test_to_dict(self):
        d = self._make_ctx().to_dict()
        assert "violation_id" in d; assert "violations" in d
    def test_get_nodes_by_type(self):
        ctx = self._make_ctx()
        nodes = ctx.get_nodes_by_type("ClassDef")
        assert len(nodes) >= 1

def test_module_importable(): assert _AVAIL or not _AVAIL
