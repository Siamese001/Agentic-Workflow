"""
Tests for Phase 2: High Tier Remediation

Tests surgical healing integration for:
- ASTValidatorAgent (6 violations)
- FilesystemSSOTReconcilerAgent (6 violations)
- StructureHealerAgent (6 violations)
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.core.surgical_healing_adapter import (
    SurgicalHealingAdapter,
)


class TestASTValidatorAgentIntegration:
    """Tests for ASTValidatorAgent surgical healing integration."""

    def test_adapter_with_bare_except_detection(self):
        """Test detecting and preparing to fix bare except clauses."""
        source = """
try:
    risky_operation()
except:
    pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ASTValidatorAgent")

            detection_result = {
                "type": "bare_except",
                "line": 4,
                "message": "Bare except clause detected",
                "severity": "error",
                "expected_pattern": "except Exception:",
                "actual_pattern": "except:",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_bare_except",
            )

            assert context is not None
            assert context.detector_agent == "ASTValidatorAgent"
            assert context.violations[0].constraint_type == "bare_except"
        finally:
            temp_path.unlink()

    def test_adapter_with_eval_exec_detection(self):
        """Test detecting dangerous eval/exec usage."""
        source = """
def dangerous_func(user_input):
    result = eval(user_input)
    return result
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ASTValidatorAgent")

            detection_result = {
                "type": "dangerous_eval",
                "line": 3,
                "message": "Use of eval() detected",
                "severity": "error",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_eval_exec",
            )

            assert context is not None
            assert context.violations[0].constraint_type == "dangerous_eval"
        finally:
            temp_path.unlink()

    def test_adapter_with_debugger_detection(self):
        """Test detecting leftover debugger statements."""
        source = """
def my_func():
    import pdb; pdb.set_trace()
    return 42
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ASTValidatorAgent")

            detection_result = {
                "type": "debugger_statement",
                "line": 3,
                "message": "Debugger statement detected",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_debugger",
            )

            assert context is not None
            # debugger_statement infers to "replace" since it doesn't contain
            # "unused" or "remove" keywords
            assert context.violations[0].fix_type == "replace"
        finally:
            temp_path.unlink()

    def test_batch_ast_violations(self):
        """Test batch processing of multiple AST violations."""
        source = """
try:
    eval(user_input)
except:
    import pdb; pdb.set_trace()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ASTValidatorAgent")

            detection_results = [
                {"type": "dangerous_eval", "line": 3, "message": "eval detected"},
                {"type": "bare_except", "line": 4, "message": "bare except"},
                {"type": "debugger_statement", "line": 5, "message": "debugger"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="validate_all",
            )

            assert context is not None
            assert len(context.violations) == 3
        finally:
            temp_path.unlink()


class TestFilesystemSSOTReconcilerIntegration:
    """Tests for FilesystemSSOTReconcilerAgent surgical healing integration."""

    def test_adapter_with_drift_detection(self):
        """Test detecting SSOT drift."""
        source = """
class MisplacedAgent:
    def run(self):
        pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FilesystemSSOTReconcilerAgent")

            detection_result = {
                "type": "ssot_drift",
                "line": 1,
                "message": "File not in SSOT-approved location",
                "severity": "error",
                "expected_pattern": "agentic_core/L5_safety/validators/",
                "actual_pattern": str(temp_path.parent),
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_detect_drift",
            )

            assert context is not None
            assert context.detector_agent == "FilesystemSSOTReconcilerAgent"
        finally:
            temp_path.unlink()

    def test_adapter_with_root_drift_detection(self):
        """Test detecting root-level drift."""
        source = "# Misplaced file\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FilesystemSSOTReconcilerAgent")

            detection_result = {
                "type": "root_drift",
                "line": 1,
                "message": "Python file in project root",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="detect_root_drift",
            )

            assert context is not None
            assert context.violations[0].constraint_type == "root_drift"
        finally:
            temp_path.unlink()

    def test_batch_ssot_violations(self):
        """Test batch SSOT drift violations."""
        source = "class TestClass: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FilesystemSSOTReconcilerAgent")

            detection_results = [
                {"type": "ssot_drift", "line": 1, "message": "Location drift"},
                {"type": "naming_convention", "line": 1, "message": "Invalid name"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="scan_root_folders",
            )

            assert context is not None
            assert len(context.violations) == 2
        finally:
            temp_path.unlink()


class TestStructureHealerAgentIntegration:
    """Tests for StructureHealerAgent surgical healing integration."""

    def test_adapter_with_missing_init_detection(self):
        """Test detecting missing __init__.py files."""
        source = "# Package marker\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="StructureHealerAgent")

            detection_result = {
                "type": "missing_init",
                "line": 1,
                "message": "Directory missing __init__.py",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="detect_missing_init",
            )

            assert context is not None
            assert context.violations[0].fix_type == "insert"
        finally:
            temp_path.unlink()

    def test_adapter_with_structure_violation(self):
        """Test detecting structural violations."""
        source = """
class MyClass:
    def method(self):
        pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="StructureHealerAgent")

            detection_result = {
                "type": "structural_violation",
                "line": 2,
                "message": "Class missing required base class",
                "severity": "error",
                "expected_pattern": "class MyClass(SovereignBaseAgent):",
                "actual_pattern": "class MyClass:",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_structure",
            )

            assert context is not None
            assert context.violations[0].expected_pattern is not None
        finally:
            temp_path.unlink()

    def test_surgical_healing_for_structure(self):
        """Test applying surgical healing for structural issues."""
        source = "def my_func():\n    pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="StructureHealerAgent")

            detection_result = {
                "type": "functiondef",
                "line": 1,
                "message": "Function missing docstring",
                "severity": "warning",
                "expected_pattern": "TODO: Add docstring",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_structure",
            )

            # Update fix type
            context.violations[0].fix_type = "insert"

            result = adapter.apply_surgical_healing(context)

            assert result.status == "success"
            assert result.violations_fixed >= 1
        finally:
            temp_path.unlink()


class TestHighTierZeroLossDiff:
    """Tests verifying zero-loss diffs for High Tier agents."""

    def test_ast_validator_preserves_content(self):
        """Test that AST validation preserves unrelated content."""
        source = """# Important header comment
\"\"\"Module docstring.\"\"\"

import os
import sys

def valid_function():
    \"\"\"Docstring.\"\"\"
    return 42

class ValidClass:
    \"\"\"Class docstring.\"\"\"
    pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ASTValidatorAgent")

            # No violations - should preserve everything
            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result={
                    "type": "valid",
                    "line": 1,
                    "message": "No issues",
                },
                detection_method="validate_all",
            )

            assert context is not None
            assert context.file_content == source
        finally:
            temp_path.unlink()

    def test_filesystem_reconciler_tracks_coordinates(self):
        """Test that filesystem reconciler tracks AST coordinates."""
        source = """
class AgentOne:
    pass

class AgentTwo:
    pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FilesystemSSOTReconcilerAgent")

            detection_results = [
                {"type": "missing_docstring", "line": 2, "message": "AgentOne"},
                {"type": "missing_docstring", "line": 5, "message": "AgentTwo"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="_detect_drift",
            )

            assert context is not None
            assert len(context.target_coordinates) == 2
            assert context.target_coordinates[0].line == 2
            assert context.target_coordinates[1].line == 5
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
