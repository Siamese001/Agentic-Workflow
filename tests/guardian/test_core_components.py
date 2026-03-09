#!/usr/bin/env python3
"""
Guardian Test for Critical Core Components
Comprehensive tests for critical system file existence and accessibility.

Merged from:
- test_core_components.py (core validation logic)
- test_core_components_comprehensive.py (test cases)
"""

import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CRITICAL_FILES = [
    "agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py",
    "agentic_core/base_agents/SovereignBaseAgent.py",
]


class CoreComponentsValidator:
    """Validates critical system file existence."""

    def __init__(self, critical_files: list[str] | None = None):
        """Initialize with list of critical files."""
        self.critical_files = critical_files if critical_files is not None else CRITICAL_FILES

    def validate(self) -> dict[str, Any]:
        """
        Validate all critical files exist.

        Returns:
            Dict with validation results
        """
        result = {
            "compliant": True,
            "total_files": len(self.critical_files),
            "found": [],
            "missing": [],
        }

        for filepath in self.critical_files:
            file_path = Path(filepath)
            if file_path.exists() and file_path.is_file():
                result["found"].append(filepath)
            else:
                result["missing"].append(filepath)

        result["compliant"] = len(result["missing"]) == 0
        return result


class TestCoreComponents:
    """Comprehensive core components validation tests."""

    @pytest.fixture
    def validator(self):
        """Provide validator instance."""
        return CoreComponentsValidator()

    def test_all_critical_files_exist(self, validator):
        """TC-CC-01: All critical files exist."""
        result = validator.validate()

        if result["missing"]:
            pytest.fail(f"Some critical files don't exist: {result['missing']}")

        assert result["compliant"]

    def test_missing_file_detection(self):
        """TC-CC-02: Missing file is detected."""
        validator = CoreComponentsValidator(
            critical_files=[
                "nonexistent_file.py",
                "tests/guardian/test_core_components.py",
            ],
        )

        result = validator.validate()
        assert not result["compliant"]
        assert "nonexistent_file.py" in result["missing"]

    def test_empty_critical_files_list(self):
        """TC-CC-03: Empty critical files list passes."""
        validator = CoreComponentsValidator(critical_files=[])
        result = validator.validate()
        assert result["compliant"]
        assert result["total_files"] == 0

    def test_partial_file_existence(self):
        """TC-CC-04: Partial file existence detected correctly."""
        validator = CoreComponentsValidator(
            critical_files=[
                "nonexistent_file_1.py",
                "tests/guardian/test_core_components.py",
                "nonexistent_file_2.py",
            ],
        )

        result = validator.validate()
        assert not result["compliant"]
        assert len(result["found"]) == 1
        assert len(result["missing"]) == 2

    def test_directory_instead_of_file(self, tmp_path):
        """TC-CC-06: Directory instead of file handled correctly."""
        temp_dir = tmp_path / "test_dir"
        temp_dir.mkdir()

        validator = CoreComponentsValidator(critical_files=[str(temp_dir)])
        result = validator.validate()

        assert not result["compliant"]
        assert str(temp_dir) in result["missing"]

    def test_large_file_list_performance(self):
        """TC-CC-08: Performance with large file lists."""
        import time

        large_list = [f"nonexistent_file_{i}.py" for i in range(1000)]
        large_list.append("tests/guardian/test_core_components.py")

        validator = CoreComponentsValidator(critical_files=large_list)

        start_time = time.time()
        result = validator.validate()
        elapsed_time = time.time() - start_time

        assert not result["compliant"]
        assert len(result["found"]) == 1
        assert len(result["missing"]) == 1000
        assert elapsed_time < 5.0, f"Validation took too long: {elapsed_time:.2f}s"


def test_critical_files_exist() -> None:
    """
    Test that all critical system files exist.

    This is the main guardian test for critical components.
    """
    validator = CoreComponentsValidator()
    result = validator.validate()

    if result["missing"]:
        for filepath in result["missing"]:
            print(f"[MISSING] {filepath}")
        pytest.fail(f"Missing {len(result['missing'])} critical files")
    else:
        print(f"[PASS] All {result['total_files']} critical files exist")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
