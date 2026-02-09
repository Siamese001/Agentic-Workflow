"""
Tests for Phase 3: Medium Tier Remediation

Tests surgical healing integration for agents with 3-5 violations:
- AgentCategory (5 violations)
- ArchitectureGovernorAgent (3 violations)
- AutonomyGuardianAgent (3 violations)
- FileClassificationAgent (3 violations)
- GovernanceAgent (3 violations)
- HierarchyAgent (3 violations)
- input_validation_guardrail_agent_config (4 violations)
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.SurgicalHealingAdapter import (
    SurgicalHealingAdapter,
)


class TestAgentCategoryIntegration:
    """Tests for AgentCategory surgical healing integration."""

    def test_adapter_with_scan_violations(self):
        """Test detecting scan violations in AgentCategory."""
        source = """
class AgentCategory:
    def _scan_violations(self):
        return [{"type": "test", "line": 1}]
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AgentCategory")

            detection_result = {
                "type": "detection_healing_mismatch",
                "line": 3,
                "message": "Detection returns structured data but healing is unstructured",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_scan_violations",
            )

            assert context is not None
            assert context.detector_agent == "AgentCategory"
        finally:
            temp_path.unlink()

    def test_batch_category_violations(self):
        """Test batch category violations."""
        source = "class AgentCategory: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AgentCategory")

            detection_results = [
                {"type": "mismatch", "line": 1, "message": "Violation 1"},
                {"type": "mismatch", "line": 1, "message": "Violation 2"},
                {"type": "mismatch", "line": 1, "message": "Violation 3"},
                {"type": "mismatch", "line": 1, "message": "Violation 4"},
                {"type": "mismatch", "line": 1, "message": "Violation 5"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="_scan_violations",
            )

            assert context is not None
            assert len(context.violations) == 5
        finally:
            temp_path.unlink()


class TestArchitectureGovernorAgentIntegration:
    """Tests for ArchitectureGovernorAgent surgical healing integration."""

    def test_adapter_with_guardian_scan(self):
        """Test detecting guardian scan issues."""
        source = """
class ArchitectureGovernorAgent:
    def _orchestrate_guardian_scan(self):
        return {"status": "ok"}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ArchitectureGovernorAgent")

            detection_result = {
                "type": "pattern_validation",
                "line": 3,
                "message": "Pattern validation mismatch",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_orchestrate_guardian_scan",
            )

            assert context is not None
            assert context.detection_method == "_orchestrate_guardian_scan"
        finally:
            temp_path.unlink()

    def test_adapter_with_baseline_drift(self):
        """Test detecting baseline drift."""
        source = "class ArchitectureGovernorAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ArchitectureGovernorAgent")

            detection_result = {
                "type": "baseline_drift",
                "line": 1,
                "message": "Baseline drift detected",
                "severity": "error",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_check_baseline_drift",
            )

            assert context is not None
            assert context.violations[0].severity == "error"
        finally:
            temp_path.unlink()


class TestAutonomyGuardianAgentIntegration:
    """Tests for AutonomyGuardianAgent surgical healing integration."""

    def test_adapter_with_string_operations(self):
        """Test detecting string-based operations."""
        source = """
class AutonomyGuardianAgent:
    def heal_repository(self, path):
        content = path.read_text()
        fixed = content.replace("bad", "good")
        return fixed
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AutonomyGuardianAgent")

            detection_results = [
                {
                    "type": "string_operation_replace",
                    "line": 5,
                    "message": "Uses string replace",
                },
                {
                    "type": "string_operation_split",
                    "line": 5,
                    "message": "Uses string split",
                },
                {
                    "type": "string_operation_join",
                    "line": 5,
                    "message": "Uses string join",
                },
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="heal_repository",
            )

            assert context is not None
            assert len(context.violations) == 3
        finally:
            temp_path.unlink()


class TestFileClassificationAgentIntegration:
    """Tests for FileClassificationAgent surgical healing integration."""

    def test_adapter_with_pattern_detection(self):
        """Test detecting pattern classification."""
        source = """
class FileClassificationAgent:
    def _detect_test_patterns(self, path):
        return {"is_test": True}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FileClassificationAgent")

            detection_result = {
                "type": "pattern_mismatch",
                "line": 3,
                "message": "Pattern detection returns dict but healer expects different",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_detect_test_patterns",
            )

            assert context is not None
            assert context.detector_agent == "FileClassificationAgent"
        finally:
            temp_path.unlink()

    def test_batch_pattern_violations(self):
        """Test batch pattern violations."""
        source = "class FileClassificationAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FileClassificationAgent")

            detection_results = [
                {"type": "test_pattern", "line": 1, "message": "Test pattern"},
                {"type": "script_pattern", "line": 1, "message": "Script pattern"},
                {"type": "type_pattern", "line": 1, "message": "Type pattern"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="_detect_patterns",
            )

            assert context is not None
            assert len(context.violations) == 3
        finally:
            temp_path.unlink()


class TestGovernanceAgentIntegration:
    """Tests for GovernanceAgent surgical healing integration."""

    def test_adapter_with_governance_validation(self):
        """Test governance validation detection."""
        source = """
class GovernanceAgent:
    def validate_governance(self):
        return {"compliant": True}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="GovernanceAgent")

            detection_result = {
                "type": "governance_mismatch",
                "line": 3,
                "message": "Governance validation mismatch",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_governance",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestHierarchyAgentIntegration:
    """Tests for HierarchyAgent surgical healing integration."""

    def test_adapter_with_hierarchy_detection(self):
        """Test hierarchy detection."""
        source = """
class HierarchyAgent:
    def detect_hierarchy_issues(self):
        return [{"level": 1, "issue": "test"}]
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="HierarchyAgent")

            detection_result = {
                "type": "hierarchy_mismatch",
                "line": 3,
                "message": "Hierarchy detection/healing mismatch",
                "severity": "warning",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="detect_hierarchy_issues",
            )

            assert context is not None
            assert context.detector_agent == "HierarchyAgent"
        finally:
            temp_path.unlink()


class TestInputValidationGuardrailIntegration:
    """Tests for input_validation_guardrail_agent_config integration."""

    def test_adapter_with_validation_config(self):
        """Test input validation config detection."""
        source = """
INPUT_VALIDATION_CONFIG = {
    "required_fields": ["name", "type"],
    "validators": {}
}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="input_validation_guardrail_agent_config")

            detection_results = [
                {"type": "string_operation", "line": 2, "message": "String op 1"},
                {"type": "string_operation", "line": 3, "message": "String op 2"},
                {"type": "string_operation", "line": 4, "message": "String op 3"},
                {"type": "string_operation", "line": 4, "message": "String op 4"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="validate_input",
            )

            assert context is not None
            assert len(context.violations) == 4
        finally:
            temp_path.unlink()


class TestMediumTierSurgicalHealing:
    """Integration tests for medium tier surgical healing."""

    def test_surgical_healing_applies_correctly(self):
        """Test that surgical healing applies correctly."""
        source = "def my_func():\n    pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AgentCategory")

            detection_result = {
                "type": "functiondef",
                "line": 1,
                "message": "Missing docstring",
                "expected_pattern": "TODO: Add docstring",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="scan",
            )

            context.violations[0].fix_type = "insert"

            result = adapter.apply_surgical_healing(context)

            assert result.status == "success"
            assert result.violations_fixed >= 1
        finally:
            temp_path.unlink()

    def test_batch_healing_multiple_agents(self):
        """Test batch healing across multiple agent patterns."""
        source = """
class TestAgent:
    def method1(self):
        pass

    def method2(self):
        pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            # Test that adapter works for multiple agents
            agents = [
                "AgentCategory",
                "ArchitectureGovernorAgent",
                "AutonomyGuardianAgent",
                "FileClassificationAgent",
                "GovernanceAgent",
                "HierarchyAgent",
            ]

            for agent_name in agents:
                adapter = SurgicalHealingAdapter(agent_name=agent_name)

                detection_result = {
                    "type": "test",
                    "line": 2,
                    "message": f"Test for {agent_name}",
                }

                context = adapter.create_context_from_detection(
                    file_path=temp_path,
                    detection_result=detection_result,
                    detection_method="test",
                )

                assert context is not None
                assert context.detector_agent == agent_name
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
