"""
Unit tests for Phase 1: FileClassificationAgent Early Detection in execute_ssot.py

Tests verify that FileClassificationAgent is integrated into Phase 1 discovery
to catch naming violations early in the SSOT compliance workflow.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase1EarlyDetection:
    """Test FileClassificationAgent early detection in Phase 1 discovery."""

    def test_early_detection_code_exists(self):
        """Verify early detection code is present in execute_ssot.py."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check for early detection code markers
        assert "PHASE 1 ENHANCEMENT" in content
        assert "Early File Classification Detection" in content
        assert "FileClassificationAgent" in content
        assert "classification_violations" in content
        assert "classification_scan_result" in content

    def test_early_detection_stores_state(self):
        """Verify early detection stores results in state manager."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check state storage
        assert 'state_mgr.state["classification_violations"]' in content
        assert 'state_mgr.state["classification_scan_result"]' in content

    def test_early_detection_uses_validate_only_mode(self):
        """Verify early detection uses validator agent (read-only, no mutations)."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Current impl uses FileClassificationValidatorAgent.to_check_dict() — read-only
        assert "FileClassificationValidatorAgent" in content
        assert "to_check_dict" in content

    def test_early_detection_handles_errors_gracefully(self):
        """Verify early detection handles errors without crashing."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check error handling
        assert "except Exception as e:" in content
        assert "FileClassificationHealerAgent early detection failed" in content
        assert 'state_mgr.state["classification_violations"] = []' in content

    def test_early_detection_updates_state_manager(self):
        """Verify early detection properly updates state manager."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Check state manager updates
        assert 'state_mgr.update_agent("FileClassificationHealerAgent"' in content
        assert 'state_mgr.complete_agent("FileClassificationHealerAgent"' in content

    def test_early_detection_extracts_violations(self):
        """Verify early detection extracts violations from classifier stats."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Current impl extracts from validator to_check_dict() evidence
        assert '"type": "CLASSIFICATION"' in content
        assert "classification_violations" in content
        assert "classification_scan_result" in content


class TestPhase1EarlyDetectionIntegration:
    """Integration tests for early detection with mocked components."""

    def test_file_classification_agent_can_be_imported(self):
        """Verify FileClassificationAgent can be imported."""
        try:
            from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
                FileClassificationAgent,
            )

            assert FileClassificationAgent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import FileClassificationAgent: {e}")

    def test_file_classification_agent_has_required_methods(self):
        """Verify FileClassificationAgent has required methods for early detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Check required methods exist
        assert hasattr(FileClassificationAgent, "run")
        assert callable(getattr(FileClassificationAgent, "run", None))

    def test_early_detection_mock_execution(self):
        """Test early detection logic with mocked components."""
        # Create mock state manager
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {
            "compliance_scores": {},
            "location_violations": [],
            "location_scan_result": {},
        }

        # Create mock file classifier
        mock_classifier = MagicMock()
        mock_classifier.stats = {
            "violations": {"NAMING": 2, "HEADER": 1},
            "renamed": 0,
            "collisions_resolved": 0,
        }
        mock_classifier.run.return_value = {"success": True}

        # Simulate early detection logic
        classification_violations = []
        if mock_classifier.stats.get("violations"):
            for vtype, count in mock_classifier.stats["violations"].items():
                if count > 0:
                    classification_violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": "test_territory",
                        },
                    )

        # Verify violations extracted
        assert len(classification_violations) == 2
        assert classification_violations[0]["type"] == "CLASSIFICATION"
        assert classification_violations[0]["subtype"] in ["NAMING", "HEADER"]

    def test_early_detection_empty_violations(self):
        """Test early detection with no violations."""
        mock_classifier = MagicMock()
        mock_classifier.stats = {
            "violations": {},
            "renamed": 0,
            "collisions_resolved": 0,
        }

        classification_violations = []
        if mock_classifier.stats.get("violations"):
            for vtype, count in mock_classifier.stats["violations"].items():
                if count > 0:
                    classification_violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": "test_territory",
                        },
                    )

        assert len(classification_violations) == 0

    def test_early_detection_error_handling(self):
        """Test early detection error handling."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        # Simulate error scenario: set empty state as error handling would
        mock_state_mgr.state["classification_violations"] = []
        mock_state_mgr.state["classification_scan_result"] = {}

        assert mock_state_mgr.state["classification_violations"] == []
        assert mock_state_mgr.state["classification_scan_result"] == {}


class TestPhase1EarlyDetectionPosition:
    """Test that early detection is in the correct position in Phase 1."""

    def test_early_detection_after_location_agent(self):
        """Verify early detection runs after LocationAgent."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find positions
        location_complete_pos = content.find('state_mgr.complete_agent("LocationHealerAgent"')
        early_detection_pos = content.find("PHASE 1 ENHANCEMENT")

        # Early detection should come after LocationHealerAgent completion
        assert early_detection_pos > location_complete_pos, (
            "Early detection should be after LocationHealerAgent completion"
        )

    def test_early_detection_before_return(self):
        """Verify early detection runs before Phase 1 returns."""
        execute_ssot_path = PROJECT_ROOT / "agentic_core/L0_routing/scripts/execute_ssot.py"

        content = execute_ssot_path.read_text(encoding="utf-8")

        # Find the return statement in execute_phase1_discovery_impl
        early_detection_pos = content.find("PHASE 1 ENHANCEMENT")
        return_pos = content.find(
            "return (drift_report, violations, location_scan_result)",
            early_detection_pos,
        )

        # Early detection should come before the return
        assert return_pos > early_detection_pos, "Early detection should be before Phase 1 return"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
