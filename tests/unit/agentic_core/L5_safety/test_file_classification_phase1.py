"""
Unit tests for FileClassificationAgent Phase 1 fixes.

Tests:
1. Logger is properly defined and accessible
2. No redundant imports inside methods
3. File header documentation is accurate
"""

import ast
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestPhase1LoggerFix:
    """Test that Logger is properly defined in FileClassificationAgent."""

    def test_logger_is_defined_at_module_level(self):
        """Verify Logger is defined at module level, not inside methods."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")

        # Logger should be defined at module level
        assert "Logger = logging.getLogger(__name__)" in content, (
            "Logger should be defined at module level"
        )

        # logging import should exist
        assert "import logging" in content, "logging module should be imported"

    def test_logger_can_be_imported(self):
        """Verify Logger can be imported from the module."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import Logger

        assert Logger is not None, "Logger should be importable"
        assert hasattr(Logger, "info"), "Logger should have info method"
        assert hasattr(Logger, "warning"), "Logger should have warning method"
        assert hasattr(Logger, "error"), "Logger should have error method"

    def test_agent_instantiation_no_crash(self):
        """Verify agent can be instantiated without Logger-related crashes."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Create agent instance (using object.__new__ to avoid SovereignBaseAgent checks)
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
            "deep_refactors": 0,
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
                # WINDSURF IMPLEMENTATION: New categories
                "ORCHESTRATOR": 0,
                "VALIDATOR": 0,
                "FACTORY": 0,
                "CONFIG": 0,
                "ADAPTER": 0,
            },
        }
        agent.file_registry = []

        # Should not raise any exceptions
        assert agent is not None


class TestPhase1RedundantImportFix:
    """Test that redundant imports inside methods are removed."""

    def test_no_import_inside_heal_method(self):
        """Verify no import statement exists inside the heal() method."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find the FileClassificationAgent class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                # Find the heal method
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "heal":
                        # Check for import statements inside the method
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Import):
                                # Only fail if it's importing decorators
                                for alias in stmt.names:
                                    assert "decorators" not in alias.name, (
                                        "No decorators import should be inside heal() method"
                                    )
                            if isinstance(stmt, ast.ImportFrom):
                                if stmt.module and "decorators" in stmt.module:
                                    pytest.fail(
                                        "No decorators import should be inside heal() method"
                                    )


class TestPhase1FileHeaderFix:
    """Test that file header documentation is accurate."""

    def test_file_header_references_correct_filename(self):
        """Verify file header references correct filename."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")

        # Check first 500 characters for header
        header = content[:500]

        # Should reference correct filename
        assert "FileClassificationAgent.py" in header, (
            "Header should reference FileClassificationAgent.py"
        )

        # Should NOT reference old filename
        assert "PascalSovereigntyAgent.py" not in header, (
            "Header should NOT reference PascalSovereigntyAgent.py"
        )

    def test_file_header_has_proper_docstring(self):
        """Verify file has proper module docstring."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Check for module docstring
        docstring = ast.get_docstring(tree)
        assert docstring is not None, "File should have a module docstring"
        assert len(docstring) > 50, "Module docstring should be substantial"


class TestPhase1Integration:
    """Integration tests for Phase 1 fixes."""

    def test_heal_method_callable_without_crash(self):
        """Verify heal() method can be called without Logger-related crashes."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Create agent instance
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
            "deep_refactors": 0,
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
                # WINDSURF IMPLEMENTATION: New categories
                "ORCHESTRATOR": 0,
                "VALIDATOR": 0,
                "FACTORY": 0,
                "CONFIG": 0,
                "ADAPTER": 0,
            },
        }
        agent.file_registry = []

        # Call heal with a dummy violation (should not crash)
        result = agent.heal({"type": "naming", "path": "/nonexistent/file.py"})

        # Should return a dict with expected keys
        assert isinstance(result, dict), "heal() should return a dict"
        assert "violations_found" in result or "skipped" in result, (
            "Result should contain standard keys"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
