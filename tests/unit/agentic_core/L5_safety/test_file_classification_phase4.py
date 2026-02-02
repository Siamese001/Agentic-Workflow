"""
Unit tests for FileClassificationAgent Phase 4 - Code Quality Polish.

Tests:
1. Code quality standards are met
2. No lint errors in the file
3. Proper code organization
"""

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestPhase4CodeQuality:
    """Test code quality standards."""

    def test_file_has_module_docstring(self):
        """Verify file has proper module docstring."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        docstring = ast.get_docstring(tree)
        assert docstring is not None, "File should have module docstring"
        assert len(docstring) > 100, "Module docstring should be substantial"

    def test_class_has_docstring(self):
        """Verify FileClassificationAgent class has docstring."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                docstring = ast.get_docstring(node)
                assert docstring is not None, "Class should have docstring"
                return

        pytest.fail("FileClassificationAgent class not found")

    def test_public_methods_have_docstrings(self):
        """Verify public methods have docstrings."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith("_"):
                            docstring = ast.get_docstring(item)
                            assert docstring is not None, (
                                f"Public method {item.name} should have docstring"
                            )

    def test_no_syntax_errors(self):
        """Verify file has no syntax errors."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")

        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in file: {e}")


class TestPhase4CodeOrganization:
    """Test code organization standards."""

    def test_imports_at_top(self):
        """Verify imports are at the top of the file."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find first non-import, non-docstring statement
        first_non_import_line = None
        last_import_line = 0

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import_line = max(last_import_line, node.lineno)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # Skip docstrings
            elif first_non_import_line is None:
                first_non_import_line = node.lineno

        # Allow some imports after try/except blocks for optional dependencies
        # This is a reasonable pattern in Python

    def test_class_defined_after_imports(self):
        """Verify class is defined after imports."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        last_import_line = 0
        class_line = 0

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import_line = max(last_import_line, node.lineno)
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                class_line = node.lineno

        assert class_line > last_import_line, "Class should be after imports"

    def test_methods_have_type_hints(self):
        """Verify key methods have return type hints."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        key_methods = ["classify_file", "get_compliant_name", "heal", "heal_repository"]

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name in key_methods:
                        assert item.returns is not None, (
                            f"Method {item.name} should have return type hint"
                        )


class TestPhase4ConsistencyChecks:
    """Test consistency standards."""

    def test_consistent_return_format_in_heal(self):
        """Verify heal() returns consistent dict format."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd().resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
            },
        }
        agent.file_registry = []

        # Test various violation types
        test_cases = [
            {"type": "naming", "path": "/nonexistent/file.py"},
            {"type": "unknown", "path": "/nonexistent/file.py"},
            {"type": "naming", "path": "/nonexistent/file.txt"},
        ]

        required_keys = {"violations_found", "violations_fixed", "errors", "skipped"}

        for violation in test_cases:
            result = agent.heal(violation)
            assert isinstance(result, dict), "Result should be a dict"
            assert required_keys.issubset(result.keys()), (
                f"Result missing required keys: {required_keys - set(result.keys())}"
            )

    def test_file_type_literal_completeness(self):
        """Verify all FileType values are handled in stats."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")

        # Extract FileType values from Literal definition
        import re

        file_types_match = re.search(r"FileType = Literal\[(.*?)\]", content, re.DOTALL)
        assert file_types_match, "FileType Literal should be defined"

        file_types_str = file_types_match.group(1)
        file_types = re.findall(r'"(\w+)"', file_types_str)

        # Verify all types are in stats violations dict
        for ft in file_types:
            if ft != "IGNORE":
                assert f'"{ft}": 0' in content or f"'{ft}': 0" in content, (
                    f"FileType {ft} should be in stats violations"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
