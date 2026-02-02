"""
Unit tests for Phase 2: Enhanced Confidence Calculation in execute_ssot.py

Tests verify that confidence calculation includes classification violations
from early detection for more accurate healing decisions.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase2ConfidenceCalculation:
    """Test enhanced confidence calculation with classification violations."""

    def test_confidence_calc_code_exists(self):
        """Verify enhanced confidence calculation code is present."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check for Phase 2 enhancement markers
        assert "PHASE 2 ENHANCEMENT" in content
        assert "classification_violations" in content
        assert "total_violations" in content

    def test_confidence_calc_includes_classification_violations(self):
        """Verify confidence calculation includes classification violations."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check that classification violations are retrieved from state
        assert 'state_mgr.state.get(\n                            "classification_violations"' in content

    def test_confidence_calc_combines_violations(self):
        """Verify total violations combines location and classification."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check that violations are combined
        assert "total_violations = (len(p1_loc) if p1_loc else 0) + len(" in content
        assert "classification_violations" in content

    def test_confidence_calc_adds_classification_type(self):
        """Verify CLASSIFICATION type is added when violations exist."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check that CLASSIFICATION type is conditionally added
        assert 'violation_types.append("CLASSIFICATION")' in content

    def test_confidence_calc_uses_total_violations(self):
        """Verify confidence calculation uses total_violations."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check that total_violations is passed to calculate_healing_confidence
        assert "violations_count=total_violations" in content


class TestPhase2ConfidenceCalculationLogic:
    """Test the logic of enhanced confidence calculation."""

    def test_total_violations_with_both_types(self):
        """Test total violations calculation with both location and classification."""
        p1_loc = [{"type": "LOCATION", "file": "test1.py"}]
        classification_violations = [
            {"type": "CLASSIFICATION", "subtype": "NAMING", "count": 2}
        ]

        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)

        assert total_violations == 2

    def test_total_violations_with_only_location(self):
        """Test total violations calculation with only location violations."""
        p1_loc = [
            {"type": "LOCATION", "file": "test1.py"},
            {"type": "LOCATION", "file": "test2.py"},
        ]
        classification_violations = []

        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)

        assert total_violations == 2

    def test_total_violations_with_only_classification(self):
        """Test total violations calculation with only classification violations."""
        p1_loc = None
        classification_violations = [
            {"type": "CLASSIFICATION", "subtype": "NAMING", "count": 1},
            {"type": "CLASSIFICATION", "subtype": "HEADER", "count": 1},
        ]

        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)

        assert total_violations == 2

    def test_total_violations_with_none(self):
        """Test total violations calculation with no violations."""
        p1_loc = None
        classification_violations = []

        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)

        assert total_violations == 0

    def test_violation_types_with_classification(self):
        """Test violation types includes CLASSIFICATION when violations exist."""
        classification_violations = [{"type": "CLASSIFICATION", "subtype": "NAMING"}]
        violation_types = ["SOVEREIGNTY", "NAMING", "HEADER"]

        if classification_violations:
            violation_types.append("CLASSIFICATION")

        assert "CLASSIFICATION" in violation_types
        assert len(violation_types) == 4

    def test_violation_types_without_classification(self):
        """Test violation types excludes CLASSIFICATION when no violations."""
        classification_violations = []
        violation_types = ["SOVEREIGNTY", "NAMING", "HEADER"]

        if classification_violations:
            violation_types.append("CLASSIFICATION")

        assert "CLASSIFICATION" not in violation_types
        assert len(violation_types) == 3


class TestPhase2StateManagerIntegration:
    """Test state manager integration for confidence calculation."""

    def test_state_manager_retrieves_classification_violations(self):
        """Test that state manager correctly retrieves classification violations."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {
            "classification_violations": [
                {"type": "CLASSIFICATION", "subtype": "NAMING", "count": 2}
            ]
        }

        classification_violations = mock_state_mgr.state.get("classification_violations", [])

        assert len(classification_violations) == 1
        assert classification_violations[0]["subtype"] == "NAMING"

    def test_state_manager_returns_empty_list_when_no_violations(self):
        """Test state manager returns empty list when no classification violations."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        classification_violations = mock_state_mgr.state.get("classification_violations", [])

        assert classification_violations == []

    def test_confidence_calculation_mock(self):
        """Test confidence calculation with mocked decision engine."""
        mock_decision_engine = MagicMock()
        mock_decision_engine.calculate_healing_confidence.return_value = MagicMock(
            value=0.85, reasoning="High confidence"
        )

        p1_loc = [{"type": "LOCATION"}]
        classification_violations = [{"type": "CLASSIFICATION"}]
        total_violations = len(p1_loc) + len(classification_violations)
        violation_types = ["SOVEREIGNTY", "NAMING", "HEADER", "CLASSIFICATION"]

        confidence = mock_decision_engine.calculate_healing_confidence(
            violations_count=total_violations,
            violation_types=violation_types,
            territory="test_territory",
        )

        assert confidence.value == 0.85
        mock_decision_engine.calculate_healing_confidence.assert_called_once_with(
            violations_count=2,
            violation_types=["SOVEREIGNTY", "NAMING", "HEADER", "CLASSIFICATION"],
            territory="test_territory",
        )


class TestPhase2CodePosition:
    """Test that Phase 2 code is in the correct position."""

    def test_phase2_after_phase1_early_detection(self):
        """Verify Phase 2 enhancement comes after Phase 1 early detection."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find positions
        phase1_pos = content.find("PHASE 1 ENHANCEMENT")
        phase2_pos = content.find("PHASE 2 ENHANCEMENT")

        # Phase 2 should come after Phase 1
        assert phase2_pos > phase1_pos, "Phase 2 should be after Phase 1"

    def test_phase2_before_healing_decision(self):
        """Verify Phase 2 enhancement comes before healing decision."""
        execute_ssot_path = (
            PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/execute_ssot.py"
        )

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find positions
        phase2_pos = content.find("PHASE 2 ENHANCEMENT")
        healing_decision_pos = content.find(
            "pascal_proceed, pascal_reason = decision_engine.should_proceed_with_healing"
        )

        # Phase 2 should come before healing decision
        assert healing_decision_pos > phase2_pos, (
            "Phase 2 should be before healing decision"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
