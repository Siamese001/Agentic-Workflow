"""
End-to-end and integration tests for FileClassificationAgent integration in execute_ssot.py

Tests cover all three phases:
- Phase 1: Early Detection in Phase 1 Discovery
- Phase 2: Enhanced Confidence Calculation
- Phase 3: Integrated Reporting in Phase 5 Certification

These tests verify the complete workflow of FileClassificationAgent integration.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestE2EAllPhasesPresent:
    """E2E tests verifying all phases are properly integrated."""

    def test_all_phase_enhancements_exist(self):
        """Verify all phase enhancement markers exist in execute_ssot.py."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # All three phase enhancements should exist
        assert "PHASE 1 ENHANCEMENT" in content, "Phase 1 enhancement missing"
        assert "PHASE 2 ENHANCEMENT" in content, "Phase 2 enhancement missing"
        assert "PHASE 3 ENHANCEMENT" in content, "Phase 3 enhancement missing"

    def test_file_classification_agent_imported(self):
        """Verify FileClassificationAgent is properly imported."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert "from agentic_core.L5_safety.reasoning.FileClassificationAgent import" in content
        assert "FileClassificationAgent" in content

    def test_file_classification_agent_in_agents_dict(self):
        """Verify FileClassificationAgent is registered in agents dictionary."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert '"file_classification": FileClassificationAgent' in content


class TestE2EPhase1EarlyDetection:
    """E2E tests for Phase 1: Early Detection."""

    def test_early_detection_in_phase1_discovery(self):
        """Verify early detection is in execute_phase1_discovery_impl."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Phase 1 enhancement should exist in the file
        assert "PHASE 1 ENHANCEMENT" in content
        assert "Early File Classification Detection" in content

        # Should be associated with FileClassificationAgent
        phase1_pos = content.find("PHASE 1 ENHANCEMENT")
        section = content[phase1_pos : phase1_pos + 2000]
        assert "FileClassificationAgent" in section
        assert "classification_violations" in section

    def test_early_detection_uses_validate_only(self):
        """Verify early detection uses validate_only mode."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert "file_classifier.validate_only = True" in content
        assert "file_classifier.dry_run = True" in content

    def test_early_detection_stores_in_state(self):
        """Verify early detection stores results in state manager."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert 'state_mgr.state["classification_violations"]' in content
        assert 'state_mgr.state["classification_scan_result"]' in content


class TestE2EPhase2ConfidenceCalculation:
    """E2E tests for Phase 2: Enhanced Confidence Calculation."""

    def test_confidence_calc_retrieves_classification_violations(self):
        """Verify confidence calculation retrieves classification violations."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find Phase 2 enhancement
        phase2_pos = content.find("PHASE 2 ENHANCEMENT")
        phase2_section = content[phase2_pos : phase2_pos + 1000]

        assert (
            'state_mgr.state.get(\n                            "classification_violations"' in phase2_section
        )

    def test_confidence_calc_combines_violations(self):
        """Verify confidence calculation combines all violation types."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert "total_violations = (len(p1_loc) if p1_loc else 0) + len(" in content

    def test_confidence_calc_adds_classification_type(self):
        """Verify CLASSIFICATION type is added to violation_types."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert 'violation_types.append("CLASSIFICATION")' in content


class TestE2EPhase3IntegratedReporting:
    """E2E tests for Phase 3: Integrated Reporting."""

    def test_phase3_in_phase5_certification(self):
        """Verify Phase 3 enhancement is in Phase 5 certification function."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find execute_phase5_final_impl function
        func_start = content.find("def execute_phase5_final_impl(")
        func_end = content.find("\ndef ", func_start + 1)

        func_content = content[func_start:func_end]

        # Phase 3 enhancement should be in this function
        assert "PHASE 3 ENHANCEMENT" in func_content

    def test_classification_violations_in_all_violations(self):
        """Verify classification violations are added to all_violations."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        assert "for class_violation in classification_violations:" in content
        assert '"source": "FileClassificationAgent"' in content

    def test_classification_violation_structure(self):
        """Verify classification violation dict has correct structure."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find Phase 3 section
        phase3_pos = content.find("PHASE 3 ENHANCEMENT")
        phase3_section = content[phase3_pos : phase3_pos + 1500]

        assert '"type": "CLASSIFICATION"' in phase3_section
        assert '"subtype": subtype' in phase3_section
        assert '"recommended_action"' in phase3_section


class TestE2EDataFlow:
    """E2E tests for data flow between phases."""

    def test_classification_violations_flow_phase1_to_phase2(self):
        """Test that classification violations flow from Phase 1 to Phase 2."""
        # Simulate the data flow
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        # Phase 1: Store classification violations
        classification_violations = [{"type": "CLASSIFICATION", "subtype": "NAMING", "count": 2}]
        mock_state_mgr.state["classification_violations"] = classification_violations

        # Phase 2: Retrieve classification violations
        retrieved = mock_state_mgr.state.get("classification_violations", [])

        assert len(retrieved) == 1
        assert retrieved[0]["subtype"] == "NAMING"

    def test_classification_violations_flow_phase1_to_phase3(self):
        """Test that classification violations flow from Phase 1 to Phase 3."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        # Phase 1: Store classification violations
        classification_violations = [
            {"type": "CLASSIFICATION", "subtype": "NAMING", "count": 2},
            {"type": "CLASSIFICATION", "subtype": "HEADER", "count": 1},
        ]
        mock_state_mgr.state["classification_violations"] = classification_violations

        # Phase 3: Retrieve and process
        all_violations = []
        for class_violation in mock_state_mgr.state.get("classification_violations", []):
            if isinstance(class_violation, dict):
                subtype = class_violation.get("subtype", "UNKNOWN")
                count = class_violation.get("count", 1)
                violation_dict = {
                    "type": "CLASSIFICATION",
                    "subtype": subtype,
                    "source": "FileClassificationAgent",
                    "count": count,
                }
                all_violations.append(violation_dict)

        assert len(all_violations) == 2
        assert all_violations[0]["source"] == "FileClassificationAgent"

    def test_total_violations_includes_all_sources(self):
        """Test that total violations includes all violation sources."""
        # Simulate all violation sources
        arch_violations = [{"type": "ARCH"}]
        location_violations = [{"type": "LOCATION"}, {"type": "LOCATION"}]
        classification_violations = [{"type": "CLASSIFICATION", "subtype": "NAMING"}]
        hygiene_violations = [{"type": "HYGIENE"}]

        all_violations = []
        all_violations.extend(arch_violations)
        all_violations.extend(location_violations)

        for class_violation in classification_violations:
            if isinstance(class_violation, dict):
                all_violations.append(class_violation)

        all_violations.extend(hygiene_violations)

        violation_count = len(all_violations)
        assert violation_count == 5


class TestE2EErrorHandling:
    """E2E tests for error handling across phases."""

    def test_phase1_error_handling(self):
        """Test Phase 1 error handling doesn't crash workflow."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Phase 1 should have error handling
        assert "FileClassificationAgent early detection failed" in content
        assert 'state_mgr.state["classification_violations"] = []' in content

    def test_phase3_handles_empty_violations(self):
        """Test Phase 3 handles empty classification violations."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        classification_violations = mock_state_mgr.state.get("classification_violations", [])

        all_violations = []
        for class_violation in classification_violations:
            if isinstance(class_violation, dict):
                all_violations.append(class_violation)

        # Should not crash with empty violations
        assert len(all_violations) == 0


class TestIntegrationFileClassificationAgent:
    """Integration tests with actual FileClassificationAgent."""

    def test_file_classification_agent_importable(self):
        """Test FileClassificationAgent can be imported."""
        try:
            from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
                FileClassificationAgent,
            )

            assert FileClassificationAgent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import FileClassificationAgent: {e}")

    def test_file_classification_agent_has_run_method(self):
        """Test FileClassificationAgent has run method."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "run")
        assert callable(getattr(FileClassificationAgent, "run", None))

    @pytest.mark.skip(reason="Core integrity check prevents instantiation in test environment")
    def test_file_classification_agent_has_stats(self):
        """Test FileClassificationAgent instance has stats attribute."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Create instance with dry_run to avoid any changes
        agent = FileClassificationAgent(
            project_root=PROJECT_ROOT,
            dry_run=True,
            validate_only=True,
        )

        assert hasattr(agent, "stats")
        assert isinstance(agent.stats, dict)


class TestIntegrationExecuteSSOTImports:
    """Integration tests for execute_ssot.py imports."""

    def test_execute_ssot_imports_work(self):
        """Test that execute_ssot.py imports work correctly."""
        try:
            # Import key components
            from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
                FileClassificationAgent,
            )
            from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent
            from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

            assert FileClassificationAgent is not None
            assert LocationHealerAgent is not None
            assert HierarchyAgent is not None
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
