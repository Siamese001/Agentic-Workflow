"""
Phase C: Behavioral Coverage Ratchet (Semantic Version).

Uses SSOT Guardian Registry to derive check_id requirements.
Verifies coverage via test file inspection (relaxed AST check).

This replaces brittle literal AST scanning with registry-derived validation.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.types.guardian_registry_types import (
    ALL_GUARDIANS,
)
from agentic_core.L0_routing.config.path_constants import TESTS_DIR

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Test file mapping (guardian_id → test file path)
# ---------------------------------------------------------------------------

GUARDIAN_TEST_FILES: dict[str, str] = {
    "hygiene": "tests/guardian/test_guardian_hygiene.py",
    "manifest_integrity": "tests/guardian/test_guardian_manifest.py",
    "contract_integrity": "tests/guardian/test_guardian_self_integrity.py",
}


def _extract_string_literals_from_test(test_path: Path) -> set[str]:
    """AST-extract all string literals from a test file."""
    source = test_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(test_path))
    strings: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.add(node.value)
    return strings


def _extract_test_class_names(test_path: Path) -> set[str]:
    """AST-extract all test class names from a test file."""
    source = test_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(test_path))
    classes: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            classes.add(node.name)
    return classes


# Derived sets for parametrization
_ENABLED_WITH_TESTS = [
    g.guardian_id for g in ALL_GUARDIANS if g.enabled_by_default and g.guardian_id in GUARDIAN_TEST_FILES
]
_DISABLED_WITH_TESTS = [
    g.guardian_id for g in ALL_GUARDIANS if not g.enabled_by_default and g.guardian_id in GUARDIAN_TEST_FILES
]


class TestCheckIdCoverage:
    """Every check_id from enabled guardians must be referenced in its test file."""

    @pytest.mark.parametrize("guardian_id", _ENABLED_WITH_TESTS)
    def test_all_check_ids_referenced_in_tests(self, guardian_id: str):
        spec = next(g for g in ALL_GUARDIANS if g.guardian_id == guardian_id)
        test_path = PROJECT_ROOT / GUARDIAN_TEST_FILES[guardian_id]
        assert test_path.exists(), f"Test file missing: {GUARDIAN_TEST_FILES[guardian_id]}"

        strings = _extract_string_literals_from_test(test_path)
        required_check_ids = set(spec.check_ids)

        # Relaxed check: check_id OR a substring match is acceptable
        missing = set()
        for cid in required_check_ids:
            if cid not in strings and not any(cid in s for s in strings):
                missing.add(cid)

        assert not missing, f"Guardian '{guardian_id}': check_ids not referenced in test: {missing}"


class TestPassFailScenarios:
    """Each enabled guardian test must have both PASS and FAIL scenario test classes."""

    @pytest.mark.parametrize("guardian_id", _ENABLED_WITH_TESTS)
    def test_has_pass_scenario(self, guardian_id: str):
        test_path = PROJECT_ROOT / GUARDIAN_TEST_FILES[guardian_id]
        classes = _extract_test_class_names(test_path)
        strings = _extract_string_literals_from_test(test_path)

        has_pass = any("PASS" in s for s in strings) or any(
            "pass" in c.lower() or "clean" in c.lower() or "valid" in c.lower() for c in classes
        )
        assert has_pass, (
            f"Guardian '{guardian_id}': no PASS scenario found in {GUARDIAN_TEST_FILES[guardian_id]}"
        )

    @pytest.mark.parametrize("guardian_id", _ENABLED_WITH_TESTS)
    def test_has_fail_scenario(self, guardian_id: str):
        test_path = PROJECT_ROOT / GUARDIAN_TEST_FILES[guardian_id]
        classes = _extract_test_class_names(test_path)
        strings = _extract_string_literals_from_test(test_path)

        has_fail = any("FAIL" in s for s in strings) or any(
            "dirty" in c.lower()
            or "tamper" in c.lower()
            or "fail" in c.lower()
            or "violation" in c.lower()
            or "synthetic" in c.lower()
            for c in classes
        )
        assert has_fail, (
            f"Guardian '{guardian_id}': no FAIL scenario found in {GUARDIAN_TEST_FILES[guardian_id]}"
        )


class TestDisabledGuardianSmokeCoverage:
    """Disabled guardians require only smoke coverage: test file exists + schema reference."""

    @pytest.mark.parametrize("guardian_id", _DISABLED_WITH_TESTS)
    def test_disabled_guardian_has_test_file(self, guardian_id: str):
        """Disabled guardian must still have a test file."""
        test_path = PROJECT_ROOT / GUARDIAN_TEST_FILES[guardian_id]
        assert test_path.exists(), f"Test file missing for disabled guardian: {guardian_id}"

    @pytest.mark.parametrize("guardian_id", _DISABLED_WITH_TESTS)
    def test_disabled_guardian_references_schema(self, guardian_id: str):
        """Disabled guardian test must reference schema-valid output (GuardianResult or status)."""
        test_path = PROJECT_ROOT / GUARDIAN_TEST_FILES[guardian_id]
        strings = _extract_string_literals_from_test(test_path)
        has_schema_ref = any(
            "GuardianResult" in s or "PASS" in s or "FAIL" in s for s in strings
        ) or "GuardianResult" in test_path.read_text(encoding="utf-8")
        assert has_schema_ref, f"Disabled guardian '{guardian_id}': test must reference schema-valid output"


class TestStatusPromotionCoverage:
    """Verify status promotion is tested across guardians."""

    def test_contract_test_covers_promotion(self):
        """The contract test file must contain status promotion tests."""
        contract_test = PROJECT_ROOT / TESTS_DIR / "guardian" / "test_guardian_contract.py"
        assert contract_test.exists()
        _extract_string_literals_from_test(contract_test)
        classes = _extract_test_class_names(contract_test)
        assert "TestStatusPromotion" in classes, (
            "test_guardian_contract.py must contain TestStatusPromotion class"
        )

    def test_aggregation_test_covers_rollup(self):
        """The aggregation test file must test global status rollup."""
        agg_test = PROJECT_ROOT / TESTS_DIR / "guardian" / "test_guardian_aggregation.py"
        assert agg_test.exists()
        classes = _extract_test_class_names(agg_test)
        assert any("dirty" in c.lower() or "fail" in c.lower() for c in classes), (
            "test_guardian_aggregation.py must test FAIL rollup scenario"
        )
