"""
Tests for Phase Acceptance Enforcement Guard
==========================================

Tests the enforcement guard that prevents Phase 2 closeout transgressions.
"""

import shutil

# Add project root to path for imports
import sys
import tempfile
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.enforcement.phase_acceptance_guard import PhaseAcceptanceGuard

pytestmark = pytest.mark.unit_min_deps


class TestPhaseAcceptanceGuard:
    """Test the phase acceptance enforcement guard."""

    def setup_method(self):
        """Set up temporary directory for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.guard = PhaseAcceptanceGuard(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_missing_pytest_ini(self):
        """Test error when pytest.ini is missing."""
        assert not self.guard.validate()
        assert "pytest.ini not found" in self.guard.errors

    def test_testpaths_contract_sync_missing_contract(self):
        """Test error when contract test is missing."""
        pytest_ini = self.temp_dir / "pytest.ini"
        pytest_ini.write_text("[pytest]\ntestpaths = tests/example\n")

        assert not self.guard.validate()
        assert any("testpaths contract test not found" in error for error in self.guard.errors)

    def test_testpaths_contract_sync_mismatch(self):
        """Test error when testpaths don't match contract."""
        # Create pytest.ini
        pytest_ini = self.temp_dir / "pytest.ini"
        pytest_ini.write_text("""
[pytest]
testpaths =
    tests/unit_min_deps
    tests/integration/agentic_core
    tests/enforcement
    tests/governance
""")

        # Create contract test with outdated expectations
        contract_dir = self.temp_dir / "tests" / "unit_min_deps"
        contract_dir.mkdir(parents=True)
        contract_test = contract_dir / "test_testpaths_contract.py"
        contract_test.write_text("""
REQUIRED_TESTPATHS = {
    'tests/integration/agentic_core',
    'tests/unit_min_deps'
}
""")

        assert not self.guard.validate()
        assert "Testpaths contract mismatch" in self.guard.errors[0]
        assert "Missing in contract: ['tests/enforcement', 'tests/governance']" in self.guard.errors[0]

    def test_testpaths_contract_sync_match(self):
        """Test success when testpaths match contract."""
        # Create pytest.ini
        pytest_ini = self.temp_dir / "pytest.ini"
        pytest_ini.write_text("""
[pytest]
testpaths =
    tests/unit_min_deps
    tests/integration/agentic_core
""")

        # Create matching contract test
        contract_dir = self.temp_dir / "tests" / "unit_min_deps"
        contract_dir.mkdir(parents=True)
        contract_test = contract_dir / "test_testpaths_contract.py"
        contract_test.write_text("""
REQUIRED_TESTPATHS = {
    'tests/integration/agentic_core',
    'tests/unit_min_deps'
}
""")

        assert self.guard.validate()
        assert len(self.guard.errors) == 0

    def test_evidence_truncation_detection(self):
        """Test detection of truncation in evidence files."""
        # Create evidence directory
        evidence_dir = self.temp_dir / "docs" / "reports" / "governance"
        evidence_dir.mkdir(parents=True)

        # Create evidence file with truncation in pytest output
        evidence_file = evidence_dir / "test_evidence.md"
        evidence_file.write_text("""
# Test Evidence

## Pytest Output
```bash
pytest -q
===================== test session starts ======================
Full output truncated, 186 lines were hidden
```
""")

        self.guard.check_evidence_files_protocol()
        assert any("truncation" in w for w in self.guard.warnings)

    def test_evidence_missing_exit_code(self):
        """Test detection of missing exit codes in evidence."""
        # Create evidence directory
        evidence_dir = self.temp_dir / "docs" / "reports" / "governance"
        evidence_dir.mkdir(parents=True)

        # Create evidence file without exit code
        evidence_file = evidence_dir / "test_evidence.md"
        evidence_file.write_text("""
# Test Evidence

## Pytest Output
```bash
pytest -q
===================== test session starts ======================
19 tests collected in 0.03s
```
""")

        self.guard.check_evidence_files_protocol()
        warnings = [w for w in self.guard.warnings if "missing exit code" in w]
        assert len(warnings) > 0

    def test_phase_evidence_missing_git_history(self):
        """Test detection of missing git history analysis for failures."""
        # Create evidence directory
        evidence_dir = self.temp_dir / "docs" / "reports" / "governance"
        evidence_dir.mkdir(parents=True)

        # Create phase evidence with failures but no git history
        evidence_file = evidence_dir / "phase1_evidence.md"
        evidence_file.write_text("""
# Phase 1 Evidence

## Test Results
pytest -q failed with 16 errors
""")

        self.guard.check_phase_evidence_completeness()
        assert any("lacks git history analysis" in w for w in self.guard.warnings)

    def test_phase_evidence_missing_deterministic_command(self):
        """Test detection of missing deterministic command for pytest failures."""
        # Create evidence directory
        evidence_dir = self.temp_dir / "docs" / "reports" / "governance"
        evidence_dir.mkdir(parents=True)

        # Create phase evidence with pytest failure but no alternative
        evidence_file = evidence_dir / "phase1_evidence.md"
        evidence_file.write_text("""
# Phase 1 Evidence

## Test Results
```bash
pytest -q
===================== test session starts ======================
Exit code: 1
```
""")

        self.guard.check_phase_evidence_completeness()
        assert any("no deterministic command set" in w for w in self.guard.warnings)

    def test_phase_evidence_blocked_without_preexisting(self):
        """Test detection of BLOCKED status without pre-existing analysis."""
        # Create evidence directory
        evidence_dir = self.temp_dir / "docs" / "reports" / "governance"
        evidence_dir.mkdir(parents=True)

        # Create phase evidence marked BLOCKED but no analysis
        evidence_file = evidence_dir / "phase1_evidence.md"
        evidence_file.write_text("""
# Phase 1 Evidence

## Status: BLOCKED
No analysis provided.
""")

        self.guard.check_phase_evidence_completeness()
        assert any("lacks pre-existing analysis" in w for w in self.guard.warnings)

    def test_allowed_truncation_in_code_examples(self):
        """Test that truncation is allowed in non-evidence contexts."""
        # Create evidence directory
        evidence_dir = self.temp_dir / "docs" / "reports" / "governance"
        evidence_dir.mkdir(parents=True)

        # Create evidence file with ellipsis in code example (not evidence)
        evidence_file = evidence_dir / "test_evidence.md"
        evidence_file.write_text("""
# Test Evidence

## Code Example
Here's how to use the function:
```python
def example():
    # Some setup code here...
    return result
```

## Actual Evidence
```bash
pytest -q
===================== test session starts ======================
Exit code: 0
====================== 19 passed in 0.03s ======================
```
""")

        self.guard.check_evidence_files_protocol()
        truncation_warnings = [w for w in self.guard.warnings if "truncation pattern" in w]
        # Should not warn about truncation in code example
        # But the evidence block has "passed" so it shouldn't trigger exit code warning
        assert len(truncation_warnings) == 0
