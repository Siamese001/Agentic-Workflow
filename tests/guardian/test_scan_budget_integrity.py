"""
Scan Budget Integrity Enforcement.

Verifies that the contract integrity checker correctly detects:
1. Scanning guardians that raise RuntimeError for scan caps (violation)
2. Scanning guardians that import cap constants but NOT guard_scan_budget (violation)
3. Scanning guardians that correctly use guard_scan_budget (pass)

Uses synthetic AST fixtures — no actual files created.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_contract_integrity import (
    _check_imports_scan_caps,
    _check_no_raise_exception_for_caps,
    _check_no_raise_runtime_error_for_caps,
    _check_uses_guard_scan_budget,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Synthetic source fixtures
# ---------------------------------------------------------------------------

GOOD_GUARDIAN_SOURCE = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
    guard_scan_budget,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        breach = guard_scan_budget(count)
        if breach is not None:
            return breach
    return []
"""

BAD_GUARDIAN_RAISES_RUNTIME_ERROR = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > 10000:
            raise RuntimeError("Exceeded MAX_FILES_PER_SCAN limit")
    return []
"""

BAD_GUARDIAN_NO_BUDGET_HELPER = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > MAX_FILES_PER_SCAN:
            return "too many files"
    return []
"""

NON_SCANNING_GUARDIAN_SOURCE = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    CheckStatus,
)

def run_guardian(repo_root):
    result = GuardianResult(guardian_id="simple")
    return result
"""

BAD_GUARDIAN_RAISES_VALUE_ERROR = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > 10000:
            raise ValueError("MAX_FILES_PER_SCAN exceeded")
    return []
"""

BAD_GUARDIAN_RAISES_CUSTOM_EXCEPTION = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > 10000:
            raise ScanBudgetError("Breached MAX_FILES_PER_SCAN")
    return []
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestScanCapImportDetection:
    """AST correctly identifies guardians that import scan cap constants."""

    def test_detects_scan_cap_imports(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        assert _check_imports_scan_caps(tree) is True

    def test_non_scanning_guardian_has_no_caps(self):
        tree = ast.parse(NON_SCANNING_GUARDIAN_SOURCE)
        assert _check_imports_scan_caps(tree) is False


class TestGuardScanBudgetUsage:
    """AST correctly identifies guard_scan_budget import."""

    def test_detects_guard_scan_budget_import(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        assert _check_uses_guard_scan_budget(tree) is True

    def test_missing_guard_scan_budget_detected(self):
        tree = ast.parse(BAD_GUARDIAN_NO_BUDGET_HELPER)
        assert _check_uses_guard_scan_budget(tree) is False


class TestRuntimeErrorForCapsDetection:
    """AST correctly flags raise RuntimeError mentioning scan cap names."""

    def test_detects_raise_runtime_error_with_cap_name(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_RUNTIME_ERROR)
        violations = _check_no_raise_runtime_error_for_caps(tree)
        assert len(violations) > 0, "Should detect RuntimeError mentioning MAX_FILES_PER_SCAN"

    def test_no_false_positive_on_correct_guardian(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        violations = _check_no_raise_runtime_error_for_caps(tree)
        assert violations == [], f"Good guardian should have no violations: {violations}"

    def test_no_false_positive_on_non_scanning_guardian(self):
        tree = ast.parse(NON_SCANNING_GUARDIAN_SOURCE)
        violations = _check_no_raise_runtime_error_for_caps(tree)
        assert violations == []


class TestAnyExceptionForCapsDetection:
    """Broadened check flags any raise <Exception> mentioning scan cap names."""

    def test_detects_value_error_with_cap_name(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_VALUE_ERROR)
        violations = _check_no_raise_exception_for_caps(tree)
        assert len(violations) > 0, "Should detect ValueError mentioning MAX_FILES_PER_SCAN"
        assert violations[0][1] == "ValueError"

    def test_detects_custom_exception_with_cap_name(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_CUSTOM_EXCEPTION)
        violations = _check_no_raise_exception_for_caps(tree)
        assert len(violations) > 0, "Should detect ScanBudgetError mentioning MAX_FILES_PER_SCAN"
        assert violations[0][1] == "ScanBudgetError"

    def test_detects_runtime_error_with_cap_name(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_RUNTIME_ERROR)
        violations = _check_no_raise_exception_for_caps(tree)
        assert len(violations) > 0
        assert violations[0][1] == "RuntimeError"

    def test_no_false_positive_on_correct_guardian(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        violations = _check_no_raise_exception_for_caps(tree)
        assert violations == []

    def test_no_false_positive_on_non_scanning_guardian(self):
        tree = ast.parse(NON_SCANNING_GUARDIAN_SOURCE)
        violations = _check_no_raise_exception_for_caps(tree)
        assert violations == []


class TestEndToEndIntegrityPattern:
    """Full pattern: scanning guardian → must import guard_scan_budget, must not raise RuntimeError."""

    def test_good_guardian_passes_all_checks(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        assert _check_imports_scan_caps(tree) is True
        assert _check_uses_guard_scan_budget(tree) is True
        assert _check_no_raise_runtime_error_for_caps(tree) == []

    def test_bad_guardian_raising_error_fails(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_RUNTIME_ERROR)
        assert _check_imports_scan_caps(tree) is True
        assert _check_no_raise_runtime_error_for_caps(tree) != []

    def test_bad_guardian_missing_helper_fails(self):
        tree = ast.parse(BAD_GUARDIAN_NO_BUDGET_HELPER)
        assert _check_imports_scan_caps(tree) is True
        assert _check_uses_guard_scan_budget(tree) is False
