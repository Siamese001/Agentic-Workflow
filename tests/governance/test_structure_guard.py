"""
file: tests/governance/test_structure_guard.py
description: |
    Meta-Test: Verifies that the governance script actually detects violations.
    Prevents 'Silent Failure' of the enforcement tool.
    Mandatory Pass: 100%
"""
import pytest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_SCRIPT = PROJECT_ROOT / "ops_scripts/governance/check_test_structure.py"

def run_governance():
    return subprocess.run(
        ["python", str(GOVERNANCE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )

def test_tc_5_1_clean_state_pass():
    """
    TC-5.1: The current repo state (post-migration) MUST pass the check.
    """
    result = run_governance()
    assert result.returncode == 0, f"Governance Check Failed on 'Clean' Repo:\n{result.stdout}"
    assert "[PASSED]" in result.stdout

def test_tc_5_2_detect_root_violation(tmp_path):
    """
    TC-5.2: Creating a test file in tests/ root must trigger failure.
    """
    # Create a dummy bad test file
    bad_file = PROJECT_ROOT / "tests/test_illegal_root_file.py"
    bad_file.touch()
    
    try:
        result = run_governance()
        assert result.returncode == 1, "Governance script failed to detect root file violation"
        assert "[ROOT VIOLATION]" in result.stdout
        assert "test_illegal_root_file.py" in result.stdout
    finally:
        # Cleanup
        if bad_file.exists():
            bad_file.unlink()

def test_tc_5_3_detect_shallow_nesting(tmp_path):
    """
    TC-5.3: Creating a test file directly in tests/unit/ (no domain) must fail.
    """
    bad_file = PROJECT_ROOT / "tests/unit/test_shallow.py"
    bad_file.touch()
    
    try:
        result = run_governance()
        assert result.returncode == 1, "Governance script failed to detect shallow nesting"
        assert "[DEPTH VIOLATION]" in result.stdout
        assert "test_shallow.py" in result.stdout
    finally:
        if bad_file.exists():
            bad_file.unlink()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])