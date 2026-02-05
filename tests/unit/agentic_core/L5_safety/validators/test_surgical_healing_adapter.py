"""
Tests for SurgicalHealingAdapter - Phase 1 Critical Tier

Tests the adapter that bridges legacy healing methods to surgical healing.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.core.surgical_healing_adapter import (
    SurgicalHealingAdapter,
    SurgicalHealingResult,
)


class TestSurgicalHealingAdapter:
    """Tests for SurgicalHealingAdapter."""

    def test_create_adapter(self):
        """Test creating an adapter."""
        adapter = SurgicalHealingAdapter(agent_name="TestAgent")
        assert adapter.agent_name == "TestAgent"

    def test_create_context_from_detection(self):
        """Test creating SurgicalContext from detection result."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("def test_func():\n    pass\n")
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            detection_result = {
                "type": "missing_docstring",
                "line": 1,
                "message": "Function missing docstring",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="heal_imports",
            )

            assert context is not None
            assert context.file_path == temp_path
            assert context.detector_agent == "CodeHealerAgent"
            assert len(context.violations) == 1
            assert context.violations[0].constraint_type == "missing_docstring"
        finally:
            temp_path.unlink()

    def test_create_context_nonexistent_file(self):
        """Test that context creation returns None for nonexistent files."""
        adapter = SurgicalHealingAdapter(agent_name="TestAgent")

        context = adapter.create_context_from_detection(
            file_path=Path("/nonexistent/file.py"),
            detection_result={"type": "test", "line": 1, "message": "test"},
            detection_method="test",
        )

        assert context is None

    def test_create_batch_context(self):
        """Test creating batch context for multiple violations."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("def func1():\n    pass\n\ndef func2():\n    pass\n")
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            detection_results = [
                {"type": "missing_docstring", "line": 1, "message": "Missing docstring"},
                {"type": "missing_docstring", "line": 4, "message": "Missing docstring"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="heal_all",
            )

            assert context is not None
            assert len(context.violations) == 2
            assert len(context.target_coordinates) == 2
        finally:
            temp_path.unlink()

    def test_apply_surgical_healing(self):
        """Test applying surgical healing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("def test_func():\n    pass\n")
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            detection_result = {
                "type": "functiondef",
                "line": 1,
                "message": "Missing docstring",
                "severity": "warning",
                "expected_pattern": "TODO: Add docstring",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="heal_imports",
            )

            # Update fix_type to insert
            context.violations[0].fix_type = "insert"

            result = adapter.apply_surgical_healing(context)

            assert result.status == "success"
            assert result.violations_fixed >= 1
            assert result.errors == 0
        finally:
            temp_path.unlink()

    def test_apply_surgical_healing_no_context(self):
        """Test that healing with no context returns error."""
        adapter = SurgicalHealingAdapter(agent_name="TestAgent")

        result = adapter.apply_surgical_healing(None)

        assert result.status == "error"
        assert result.errors == 1

    def test_infer_fix_type(self):
        """Test fix type inference."""
        adapter = SurgicalHealingAdapter(agent_name="TestAgent")

        assert adapter._infer_fix_type("missing_docstring") == "insert"
        assert adapter._infer_fix_type("unused_import") == "delete"
        assert adapter._infer_fix_type("remove_unused") == "delete"
        assert adapter._infer_fix_type("invalid_syntax") == "replace"


class TestSurgicalHealingResult:
    """Tests for SurgicalHealingResult dataclass."""

    def test_create_result(self):
        """Test creating a healing result."""
        result = SurgicalHealingResult(
            status="success",
            violations_found=5,
            violations_fixed=3,
            errors=0,
            skipped=2,
            details="Fixed 3 violations",
        )

        assert result.status == "success"
        assert result.violations_found == 5
        assert result.violations_fixed == 3

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = SurgicalHealingResult(
            status="success",
            violations_found=5,
            violations_fixed=3,
            errors=0,
            skipped=2,
        )

        result_dict = result.to_dict()

        assert result_dict["status"] == "success"
        assert result_dict["violations_found"] == 5
        assert result_dict["violations_fixed"] == 3

    def test_result_default_artifacts(self):
        """Test that artifacts default to empty list."""
        result = SurgicalHealingResult(
            status="success",
            violations_found=1,
            violations_fixed=1,
            errors=0,
            skipped=0,
        )

        assert result.artifacts == []


class TestCodeHealerAgentIntegration:
    """Integration tests for CodeHealerAgent with surgical adapter."""

    def test_adapter_with_import_detection(self):
        """Test adapter with import-style detection results."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("import os\nimport sys\n\ndef main():\n    print(os.getcwd())\n")
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            # Simulate detection of unused import
            detection_result = {
                "type": "unused_import",
                "line": 2,
                "message": "Unused import: sys",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="heal_imports",
            )

            assert context is not None
            assert context.violations[0].constraint_type == "unused_import"
            assert context.violations[0].fix_type == "delete"
        finally:
            temp_path.unlink()

    def test_adapter_with_canon_detection(self):
        """Test adapter with canon-style detection results."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("try:\n    pass\nexcept:\n    pass\n")
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            # Simulate detection of bare except
            detection_result = {
                "type": "bare_except",
                "line": 3,
                "message": "Bare except clause",
                "severity": "error",
                "expected_pattern": "except Exception:",
                "actual_pattern": "except:",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="heal_canon",
            )

            assert context is not None
            assert context.violations[0].expected_pattern == "except Exception:"
            assert context.violations[0].actual_pattern == "except:"
        finally:
            temp_path.unlink()

    def test_adapter_with_structural_detection(self):
        """Test adapter with structural-style detection results."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("def main():  \n    pass\n")  # trailing whitespace
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            # Simulate detection of trailing whitespace
            detection_result = {
                "type": "trailing_whitespace",
                "line": 1,
                "message": "Trailing whitespace",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="heal_structural",
            )

            assert context is not None
            assert context.violations[0].constraint_type == "trailing_whitespace"
        finally:
            temp_path.unlink()


class TestCompositeGuardrailIntegration:
    """Integration tests for CompositeGuardrailAgent with surgical adapter."""

    def test_adapter_with_guardrail_detection(self):
        """Test adapter with guardrail-style detection results."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("class MyAgent:\n    def run(self):\n        pass\n")
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CompositeGuardrailAgent")

            # Simulate detection of missing guardrail
            detection_result = {
                "type": "missing_guardrail",
                "line": 2,
                "message": "Method missing input validation guardrail",
                "severity": "error",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="check_guardrails",
            )

            assert context is not None
            assert context.detector_agent == "CompositeGuardrailAgent"
            assert context.violations[0].fix_type == "insert"
        finally:
            temp_path.unlink()

    def test_batch_guardrail_violations(self):
        """Test batch processing of guardrail violations."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "class MyAgent:\n"
                "    def method1(self):\n"
                "        pass\n"
                "    def method2(self):\n"
                "        pass\n"
            )
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CompositeGuardrailAgent")

            detection_results = [
                {
                    "type": "missing_guardrail",
                    "line": 2,
                    "message": "Missing guardrail on method1",
                },
                {
                    "type": "missing_guardrail",
                    "line": 4,
                    "message": "Missing guardrail on method2",
                },
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="check_guardrails",
            )

            assert context is not None
            assert len(context.violations) == 2
            assert all(v.fix_type == "insert" for v in context.violations)
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
