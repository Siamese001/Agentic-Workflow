"""Behavioral tests for ``agentic_core.L5_safety.types.surgical_context_types``.

Covers:
- ASTCoordinate / ViolationConstraint dataclass construction + defaults.
- SurgicalContext.get_target_node finds by (line, col); returns None on miss.
- SurgicalContext.get_nodes_by_type filters by AST class name.
- SurgicalContext.get_line_range end-line fallback to start.
- SurgicalContext.extract_source_segment single-line and multi-line.
- SurgicalContext.to_dict / from_dict round-trip preserves fields.
- SurgicalContextBuilder.build_context assembles coordinates from AST nodes.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    SurgicalContextBuilder,
    ViolationConstraint,
)


SAMPLE = "x = 1\ny = 2\n\ndef foo():\n    return x + y\n"


def _build_ctx(content: str = SAMPLE) -> SurgicalContext:
    return SurgicalContext(
        file_path=Path("test.py"),
        file_content=content,
        ast_tree=ast.parse(content),
        violation_id="v1",
        violations=[],
        target_coordinates=[],
        detector_agent="detector",
        detection_method="scan",
        detection_timestamp="2026-01-01T00:00:00",
    )


# ---- ASTCoordinate -------------------------------------------------------


class TestASTCoordinate:
    def test_required_fields(self) -> None:
        c = ASTCoordinate(node_id="n1", node_type="Name", line=1, column=0)
        assert c.end_line is None
        assert c.children_ids == []
        assert c.parent_id is None

    def test_all_fields(self) -> None:
        c = ASTCoordinate(
            node_id="n1",
            node_type="Call",
            line=5,
            column=4,
            end_line=5,
            end_column=15,
            parent_id="p1",
            children_ids=["c1", "c2"],
        )
        assert c.children_ids == ["c1", "c2"]
        assert c.parent_id == "p1"


# ---- ViolationConstraint -------------------------------------------------


class TestViolationConstraint:
    def test_minimal(self) -> None:
        v = ViolationConstraint(
            constraint_type="no-bare-except",
            severity="high",
            message="bad catch",
        )
        assert v.rule_id is None
        assert v.fix_type is None

    def test_full(self) -> None:
        v = ViolationConstraint(
            constraint_type="t",
            severity="low",
            message="m",
            rule_id="R1",
            expected_pattern="ok",
            actual_pattern="bad",
            fix_type="replace",
        )
        assert v.rule_id == "R1"


# ---- SurgicalContext queries ---------------------------------------------


class TestSurgicalContextQueries:
    def test_get_target_node_hit(self) -> None:
        ctx = _build_ctx()
        # line 1 col 0 is the Assign node for "x = 1"
        coord = ASTCoordinate(node_id="n", node_type="Assign", line=1, column=0)
        node = ctx.get_target_node(coord)
        assert isinstance(node, ast.Assign)

    def test_get_target_node_miss(self) -> None:
        ctx = _build_ctx()
        coord = ASTCoordinate(node_id="n", node_type="x", line=999, column=999)
        assert ctx.get_target_node(coord) is None

    def test_get_nodes_by_type_functiondef(self) -> None:
        ctx = _build_ctx()
        fns = ctx.get_nodes_by_type("FunctionDef")
        assert len(fns) == 1
        assert isinstance(fns[0], ast.FunctionDef)
        assert fns[0].name == "foo"

    def test_get_nodes_by_type_miss(self) -> None:
        ctx = _build_ctx()
        assert ctx.get_nodes_by_type("NoSuchNode") == []

    def test_line_range_single(self) -> None:
        ctx = _build_ctx()
        coord = ASTCoordinate(node_id="n", node_type="x", line=3, column=0)
        assert ctx.get_line_range(coord) == (3, 3)

    def test_line_range_multi(self) -> None:
        ctx = _build_ctx()
        coord = ASTCoordinate(
            node_id="n",
            node_type="x",
            line=4,
            column=0,
            end_line=5,
        )
        assert ctx.get_line_range(coord) == (4, 5)


# ---- SurgicalContext.extract_source_segment ------------------------------


class TestExtractSourceSegment:
    def test_single_line(self) -> None:
        ctx = _build_ctx()
        coord = ASTCoordinate(node_id="n", node_type="x", line=1, column=0)
        assert ctx.extract_source_segment(coord) == "x = 1\n"

    def test_multi_line(self) -> None:
        ctx = _build_ctx()
        coord = ASTCoordinate(
            node_id="n",
            node_type="x",
            line=4,
            column=0,
            end_line=5,
        )
        segment = ctx.extract_source_segment(coord)
        assert "def foo" in segment
        assert "return x + y" in segment


# ---- to_dict / from_dict round-trip --------------------------------------


class TestSerialization:
    def test_to_dict_shape(self) -> None:
        ctx = _build_ctx()
        ctx.violations.append(
            ViolationConstraint(constraint_type="t", severity="s", message="m"),
        )
        ctx.target_coordinates.append(
            ASTCoordinate(node_id="n", node_type="Assign", line=1, column=0),
        )
        d = ctx.to_dict()
        assert d["file_path"] == "test.py"
        assert d["violation_id"] == "v1"
        assert len(d["violations"]) == 1
        assert len(d["target_coordinates"]) == 1
        assert d["violations"][0]["constraint_type"] == "t"

    def test_from_dict_roundtrip(self) -> None:
        ctx = _build_ctx()
        ctx.violations.append(
            ViolationConstraint(constraint_type="t", severity="s", message="m"),
        )
        ctx.target_coordinates.append(
            ASTCoordinate(node_id="n", node_type="Assign", line=1, column=0),
        )
        d = ctx.to_dict()
        d["file_content"] = ctx.file_content  # required by from_dict
        restored = SurgicalContext.from_dict(d)
        assert restored.violation_id == ctx.violation_id
        assert restored.file_path == ctx.file_path
        assert len(restored.violations) == 1
        assert restored.violations[0].constraint_type == "t"
        assert len(restored.target_coordinates) == 1


# ---- SurgicalContextBuilder ---------------------------------------------


class TestSurgicalContextBuilder:
    def test_reads_file_and_parses(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(SAMPLE, encoding="utf-8")
        b = SurgicalContextBuilder(
            file_path=f,
            detector_agent="detector",
            detection_method="scan",
        )
        assert b.file_content == SAMPLE
        assert isinstance(b.ast_tree, ast.Module)

    def test_build_context_from_nodes(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(SAMPLE, encoding="utf-8")
        b = SurgicalContextBuilder(
            file_path=f,
            detector_agent="d",
            detection_method="ast_walk",
        )
        fn_nodes = [n for n in ast.walk(b.ast_tree) if isinstance(n, ast.FunctionDef)]
        ctx = b.build_context(
            violation_id="v42",
            violations=[{"constraint_type": "t", "severity": "s", "message": "m"}],
            target_nodes=fn_nodes,
        )
        assert ctx.violation_id == "v42"
        assert ctx.file_path == f
        assert len(ctx.violations) == 1
        assert len(ctx.target_coordinates) == len(fn_nodes)
        coord = ctx.target_coordinates[0]
        assert coord.node_type == "FunctionDef"
        assert coord.line == fn_nodes[0].lineno
        assert coord.column == fn_nodes[0].col_offset
        assert coord.node_id.startswith("ast_walk_0_")
        assert ctx.detection_timestamp  # non-empty ISO string

    def test_build_context_empty_nodes(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(SAMPLE, encoding="utf-8")
        b = SurgicalContextBuilder(
            file_path=f,
            detector_agent="d",
            detection_method="m",
        )
        ctx = b.build_context(violation_id="v", violations=[], target_nodes=[])
        assert ctx.target_coordinates == []
        assert ctx.violations == []
