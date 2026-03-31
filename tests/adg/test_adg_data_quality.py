"""Test ADG data quality functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgDataQuality:
    """Test ADG data quality functionality."""

    def test_adg_schema_validation_exists(self):
        """Test ADG schema validation module exists."""
        from agentic_core.adg.schema import validate_node, validate_edge

        assert callable(validate_node)
        assert callable(validate_edge)

    def test_adg_data_quality_checks_exist(self):
        """Test ADG data quality check functions exist."""
        from tools.adg.adg_lifecycle import check_data_quality

        assert callable(check_data_quality)

    def test_adg_duplicate_detection_exists(self):
        """Test ADG duplicate detection exists."""
        from tools.adg.adg_lifecycle import detect_duplicates

        assert callable(detect_duplicates)

    def test_adg_orphan_detection_exists(self):
        """Test ADG orphan node detection exists."""
        from tools.adg.adg_lifecycle import detect_orphan_nodes

        assert callable(detect_orphan_nodes)

    def test_adg_integrity_check_exists(self):
        """Test ADG integrity check exists."""
        from tools.adg.adg_lifecycle import verify_integrity

        assert callable(verify_integrity)

    def test_adg_validation_rules_defined(self):
        """Test ADG validation rules are defined."""
        from agentic_core.adg.schema import VALIDATION_RULES

        assert isinstance(VALIDATION_RULES, dict)
        assert len(VALIDATION_RULES) > 0


if __name__ == '__main__':
    unittest.main()
