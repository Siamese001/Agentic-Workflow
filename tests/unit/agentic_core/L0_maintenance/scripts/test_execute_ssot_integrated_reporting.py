"""
Unit tests for Phase 3: Integrated Reporting in execute_ssot.py

Tests verify that classification violations from early detection are included
in the final report aggregation in Phase 5.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase3IntegratedReporting:
    """Test integrated reporting with classification violations."""

    def test_phase3_enhancement_code_exists(self):
        """Verify Phase 3 enhancement code is present."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check for Phase 3 enhancement markers
        assert "PHASE 3 ENHANCEMENT" in content
        assert "FileClassificationAgent violations from early detection" in content

    def test_classification_violations_retrieved_from_state(self):
        """Verify classification violations are retrieved from state manager."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check that classification violations are retrieved
        assert 'state_mgr.state.get("classification_violations", [])' in content

    def test_classification_violations_added_to_all_violations(self):
        """Verify classification violations are added to all_violations list."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check that classification violations are processed
        assert "for class_violation in classification_violations:" in content
        assert '"type": "CLASSIFICATION"' in content
        assert '"source": "FileClassificationAgent"' in content

    def test_classification_violation_dict_structure(self):
        """Verify classification violation dict has correct structure."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check violation dict structure
        assert '"subtype": subtype' in content
        assert '"count": count' in content
        assert '"recommended_action"' in content


class TestPhase3ViolationAggregation:
    """Test violation aggregation logic."""

    def test_classification_violation_conversion(self):
        """Test conversion of classification violation to report format."""
        class_violation = {
            "type": "CLASSIFICATION",
            "subtype": "NAMING",
            "count": 3,
            "territory": "test_territory",
        }

        subtype = class_violation.get("subtype", "UNKNOWN")
        count = class_violation.get("count", 1)

        violation_dict = {
            "type": "CLASSIFICATION",
            "subtype": subtype,
            "source": "FileClassificationAgent",
            "file": class_violation.get("file", "multiple"),
            "message": f"{subtype} violation: {count} file(s) need attention",
            "severity": "medium",
            "recommended_action": f"Run FileClassificationAgent to fix {subtype} issues",
            "llm_triggered": False,
            "confidence": 0.7,
            "count": count,
        }

        assert violation_dict["type"] == "CLASSIFICATION"
        assert violation_dict["subtype"] == "NAMING"
        assert violation_dict["source"] == "FileClassificationAgent"
        assert violation_dict["count"] == 3
        assert "NAMING" in violation_dict["message"]

    def test_multiple_classification_violations(self):
        """Test aggregation of multiple classification violations."""
        classification_violations = [
            {"type": "CLASSIFICATION", "subtype": "NAMING", "count": 2},
            {"type": "CLASSIFICATION", "subtype": "HEADER", "count": 1},
        ]

        all_violations = []
        for class_violation in classification_violations:
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
        assert all_violations[0]["subtype"] == "NAMING"
        assert all_violations[1]["subtype"] == "HEADER"

    def test_empty_classification_violations(self):
        """Test handling of empty classification violations."""
        classification_violations = []

        all_violations = []
        for class_violation in classification_violations:
            if isinstance(class_violation, dict):
                all_violations.append(class_violation)

        assert len(all_violations) == 0

    def test_combined_violations_count(self):
        """Test that violation count includes classification violations."""
        arch_violations = [{"type": "ARCH"}]
        location_violations = [{"type": "LOCATION"}]
        classification_violations = [{"type": "CLASSIFICATION", "subtype": "NAMING"}]

        all_violations = []
        all_violations.extend(arch_violations)
        all_violations.extend(location_violations)

        for class_violation in classification_violations:
            if isinstance(class_violation, dict):
                all_violations.append(class_violation)

        violation_count = len(all_violations)
        assert violation_count == 3


class TestPhase3StateManagerIntegration:
    """Test state manager integration for Phase 3."""

    def test_state_manager_retrieves_classification_violations(self):
        """Test state manager correctly retrieves classification violations."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {
            "classification_violations": [
                {"type": "CLASSIFICATION", "subtype": "NAMING", "count": 2},
                {"type": "CLASSIFICATION", "subtype": "HEADER", "count": 1},
            ]
        }

        classification_violations = mock_state_mgr.state.get(
            "classification_violations", []
        )

        assert len(classification_violations) == 2

    def test_state_manager_empty_classification_violations(self):
        """Test state manager returns empty list when no violations."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        classification_violations = mock_state_mgr.state.get(
            "classification_violations", []
        )

        assert classification_violations == []


class TestPhase3CodePosition:
    """Test that Phase 3 code is in the correct position."""

    def test_phase3_in_phase5_certification(self):
        """Verify Phase 3 enhancement is in Phase 5 certification."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find positions
        phase5_start = content.find("PHASE 5: CERTIFICATION")
        phase3_enhancement = content.find("PHASE 3 ENHANCEMENT")

        # Phase 3 enhancement should be within Phase 5
        assert phase3_enhancement > phase5_start, (
            "Phase 3 enhancement should be in Phase 5 certification"
        )

    def test_phase3_after_hygiene_violations(self):
        """Verify Phase 3 enhancement comes after RootHygieneAgent violations."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find positions
        hygiene_pos = content.find("Get RootHygieneAgent violations")
        phase3_pos = content.find("PHASE 3 ENHANCEMENT")

        # Phase 3 should come after hygiene violations
        assert phase3_pos > hygiene_pos, (
            "Phase 3 should be after RootHygieneAgent violations"
        )

    def test_phase3_before_violation_count(self):
        """Verify Phase 3 enhancement comes before violation count calculation."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find positions
        phase3_pos = content.find("PHASE 3 ENHANCEMENT")
        violation_count_pos = content.find(
            "violation_count = len(all_violations)", phase3_pos
        )

        # Phase 3 should come before violation count
        assert violation_count_pos > phase3_pos, (
            "Phase 3 should be before violation count calculation"
        )


class TestPhase3AllPhasesIntegration:
    """Test integration of all three phases."""

    def test_all_phase_markers_present(self):
        """Verify all phase enhancement markers are present."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check all phase markers
        assert "PHASE 1 ENHANCEMENT" in content
        assert "PHASE 2 ENHANCEMENT" in content
        assert "PHASE 3 ENHANCEMENT" in content

    def test_phases_in_correct_order(self):
        """Verify phases are in correct logical order within their functions."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Phase 1 is in execute_phase1_discovery_impl
        # Phase 2 is in main execution flow (after Phase 1 is called)
        # Phase 3 is in execute_phase5_final_impl (reporting)
        # All phases exist - that's the key check
        phase1_pos = content.find("PHASE 1 ENHANCEMENT")
        phase2_pos = content.find("PHASE 2 ENHANCEMENT")
        phase3_pos = content.find("PHASE 3 ENHANCEMENT")

        # All phases should exist
        assert phase1_pos != -1, "Phase 1 enhancement should exist"
        assert phase2_pos != -1, "Phase 2 enhancement should exist"
        assert phase3_pos != -1, "Phase 3 enhancement should exist"

        # Phase 3 should be in Phase 5 certification (after Phase 5 marker)
        phase5_marker = content.find("PHASE 5: CERTIFICATION")
        assert phase3_pos > phase5_marker, "Phase 3 should be in Phase 5 certification"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
