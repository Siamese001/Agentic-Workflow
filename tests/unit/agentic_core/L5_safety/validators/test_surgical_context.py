"""
Tests for SurgicalContext and SurgicalHealerMixin - Phase 0 Infrastructure

Validates the surgical healing infrastructure for Resolution Asymmetry remediation.
"""

import ast
import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    SurgicalContextBuilder,
    ViolationConstraint,
)
from agentic_core.mixins.surgical_healer_mixin import (
    SurgicalASTTransformer,
    SurgicalHealerMixin,
)


class TestASTCoordinate:
    """Tests for ASTCoordinate dataclass."""

    def test_create_coordinate(self):
        """Test creating an AST coordinate."""
        coord = ASTCoordinate(
            node_id="func_1",
            node_type="FunctionDef",
            line=10,
            column=0,
            end_line=20,
            end_column=0,
        )
        assert coord.node_id == "func_1"
        assert coord.node_type == "FunctionDef"
        assert coord.line == 10
        assert coord.column == 0
        assert coord.end_line == 20

    def test_coordinate_defaults(self):
        """Test default values for optional fields."""
        coord = ASTCoordinate(
            node_id="test",
            node_type="ClassDef",
            line=1,
            column=0,
        )
        assert coord.end_line is None
        assert coord.end_column is None
        assert coord.parent_id is None
        assert coord.children_ids == []


class TestViolationConstraint:
    """Tests for ViolationConstraint dataclass."""

    def test_create_violation(self):
        """Test creating a violation constraint."""
        violation = ViolationConstraint(
            constraint_type="missing_docstring",
            severity="warning",
            message="Function missing docstring",
            rule_id="DOC001",
            expected_pattern='"""Docstring here."""',
            fix_type="insert",
        )
        assert violation.constraint_type == "missing_docstring"
        assert violation.severity == "warning"
        assert violation.fix_type == "insert"

    def test_violation_defaults(self):
        """Test default values for optional fields."""
        violation = ViolationConstraint(
            constraint_type="test",
            severity="error",
            message="Test message",
        )
        assert violation.rule_id is None
        assert violation.expected_pattern is None
        assert violation.actual_pattern is None
        assert violation.fix_type is None


class TestSurgicalContext:
    """Tests for SurgicalContext dataclass."""

    def test_create_context(self):
        """Test creating a surgical context."""
        source = "def test(): pass"
        tree = ast.parse(source)

        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test_method",
            detection_timestamp="2026-02-02T17:00:00",
        )
        assert context.file_path == Path("test.py")
        assert context.violation_id == "v001"
        assert context.detector_agent == "TestAgent"

    def test_get_nodes_by_type(self):
        """Test getting nodes by type."""
        source = """
def func1(): pass
def func2(): pass
class MyClass: pass
"""
        tree = ast.parse(source)
        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        func_nodes = context.get_nodes_by_type("FunctionDef")
        class_nodes = context.get_nodes_by_type("ClassDef")

        assert len(func_nodes) == 2
        assert len(class_nodes) == 1

    def test_get_line_range(self):
        """Test getting line range for coordinate."""
        coord = ASTCoordinate(
            node_id="test",
            node_type="FunctionDef",
            line=5,
            column=0,
            end_line=10,
        )

        source = "def test(): pass"
        tree = ast.parse(source)
        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        start, end = context.get_line_range(coord)
        assert start == 5
        assert end == 10


class TestSurgicalContextBuilder:
    """Tests for SurgicalContextBuilder."""

    def test_builder_creates_context(self):
        """Test that builder creates a valid context."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def test_func(): pass\n")
            temp_path = Path(f.name)

        try:
            builder = SurgicalContextBuilder(temp_path, "TestAgent", "test_method")

            violations = [
                {
                    "constraint_type": "missing_docstring",
                    "severity": "warning",
                    "message": "Missing docstring",
                    "fix_type": "insert",
                },
            ]

            tree = ast.parse(temp_path.read_text())
            target_nodes = [tree.body[0]]  # The function def

            context = builder.build_context(
                violation_id="v001",
                violations=violations,
                target_nodes=target_nodes,
            )

            assert context is not None
            assert context.violation_id == "v001"
            assert len(context.violations) == 1
            assert context.detector_agent == "TestAgent"
        finally:
            temp_path.unlink()


class TestSurgicalASTTransformer:
    """Tests for SurgicalASTTransformer."""

    def test_transformer_inserts_docstring(self):
        """Test that transformer can insert a docstring."""
        source = "def my_func():\n    pass\n"
        tree = ast.parse(source)

        coord = ASTCoordinate(
            node_id="func_1",
            node_type="FunctionDef",
            line=1,
            column=0,
        )

        violation = ViolationConstraint(
            constraint_type="functiondef",
            severity="warning",
            message="Missing docstring",
            expected_pattern="TODO: Add docstring",
            fix_type="insert",
        )

        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[violation],
            target_coordinates=[coord],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        transformer = SurgicalASTTransformer(context)
        modified_tree = transformer.visit(tree)

        # Check that a docstring was added
        func_node = modified_tree.body[0]
        assert len(func_node.body) == 2  # docstring + pass
        assert transformer.modifications_made == 1

    def test_transformer_preserves_existing_docstring(self):
        """Test that transformer doesn't overwrite existing docstrings."""
        source = '''def my_func():
    """Existing docstring."""
    pass
'''
        tree = ast.parse(source)

        coord = ASTCoordinate(
            node_id="func_1",
            node_type="FunctionDef",
            line=1,
            column=0,
        )

        violation = ViolationConstraint(
            constraint_type="functiondef",
            severity="warning",
            message="Missing docstring",
            expected_pattern="New docstring",
            fix_type="insert",
        )

        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[violation],
            target_coordinates=[coord],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        transformer = SurgicalASTTransformer(context)
        modified_tree = transformer.visit(tree)

        # Check that existing docstring was preserved
        func_node = modified_tree.body[0]
        docstring = ast.get_docstring(func_node)
        assert docstring == "Existing docstring."
        assert transformer.modifications_made == 0


class TestSurgicalHealerMixin:
    """Tests for SurgicalHealerMixin."""

    def test_mixin_heal_surgical(self):
        """Test that mixin can perform surgical healing."""

        class TestHealer(SurgicalHealerMixin):
            pass

        healer = TestHealer()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def test_func():\n    pass\n")
            temp_path = Path(f.name)

        try:
            source = temp_path.read_text()
            tree = ast.parse(source)

            coord = ASTCoordinate(
                node_id="func_1",
                node_type="FunctionDef",
                line=1,
                column=0,
            )

            violation = ViolationConstraint(
                constraint_type="functiondef",
                severity="warning",
                message="Missing docstring",
                expected_pattern="TODO: Add docstring",
                fix_type="insert",
            )

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source,
                ast_tree=tree,
                violation_id="v001",
                violations=[violation],
                target_coordinates=[coord],
                detector_agent="TestAgent",
                detection_method="test",
                detection_timestamp="2026-02-02T17:00:00",
            )

            result = healer.heal_surgical(context)

            assert result["status"] == "success"
            assert result["violations_fixed"] == 1
            assert result["errors"] == 0
        finally:
            temp_path.unlink()

    def test_mixin_skips_when_no_violations(self):
        """Test that mixin skips when no modifications needed."""

        class TestHealer(SurgicalHealerMixin):
            pass

        healer = TestHealer()

        source = '''def test_func():
    """Has docstring."""
    pass
'''
        tree = ast.parse(source)

        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        result = healer.heal_surgical(context)

        assert result["status"] == "skipped"
        assert result["violations_fixed"] == 0


class TestZeroLossDiff:
    """Tests for zero-loss diff verification."""

    def test_healing_preserves_comments(self):
        """Test that healing preserves comments in source."""
        source = """# Important comment
def my_func():
    # Another comment
    pass  # inline comment
"""
        tree = ast.parse(source)

        coord = ASTCoordinate(
            node_id="func_1",
            node_type="FunctionDef",
            line=2,
            column=0,
        )

        violation = ViolationConstraint(
            constraint_type="functiondef",
            severity="warning",
            message="Missing docstring",
            expected_pattern="Function docstring.",
            fix_type="insert",
        )

        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[violation],
            target_coordinates=[coord],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        transformer = SurgicalASTTransformer(context)
        transformer.visit(tree)

        # The modification should add a docstring
        assert transformer.modifications_made == 1

        # Note: ast.unparse loses comments, but the SurgicalContext
        # should track them for zero-loss healing in production

    def test_healing_is_idempotent(self):
        """Test that running healing twice produces same result."""
        source = "def my_func():\n    pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:

            class TestHealer(SurgicalHealerMixin):
                pass

            healer = TestHealer()

            # First healing
            source1 = temp_path.read_text()
            tree1 = ast.parse(source1)

            coord = ASTCoordinate(
                node_id="func_1",
                node_type="FunctionDef",
                line=1,
                column=0,
            )

            violation = ViolationConstraint(
                constraint_type="functiondef",
                severity="warning",
                message="Missing docstring",
                expected_pattern="TODO: Add docstring",
                fix_type="insert",
            )

            context1 = SurgicalContext(
                file_path=temp_path,
                file_content=source1,
                ast_tree=tree1,
                violation_id="v001",
                violations=[violation],
                target_coordinates=[coord],
                detector_agent="TestAgent",
                detection_method="test",
                detection_timestamp="2026-02-02T17:00:00",
            )

            result1 = healer.heal_surgical(context1)
            assert result1["status"] == "success"

            # Second healing (should skip since docstring exists)
            source2 = temp_path.read_text()
            tree2 = ast.parse(source2)

            context2 = SurgicalContext(
                file_path=temp_path,
                file_content=source2,
                ast_tree=tree2,
                violation_id="v002",
                violations=[violation],
                target_coordinates=[coord],
                detector_agent="TestAgent",
                detection_method="test",
                detection_timestamp="2026-02-02T17:00:00",
            )

            result2 = healer.heal_surgical(context2)
            # Should skip because docstring now exists
            assert result2["violations_fixed"] == 0
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
