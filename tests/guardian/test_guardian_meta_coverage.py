"""
Guardian Meta-Coverage Test — Ensures every Guardian script has test coverage.

This is the "test that tests the tests" — it enumerates all guardian scripts
and asserts that a corresponding test module exists in tests/guardian/.

ReAct pattern: Observe (discover scripts) → Verify (check coverage map) → Report.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.types.guardian_registry import (
    ALL_GUARDIANS,
    get_guardian_specs,
)

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# Coverage map: guardian_id → test module(s) that cover it
# Derived from registry guardian_ids, with test file paths added here
# ---------------------------------------------------------------------------

GUARDIAN_COVERAGE_MAP: dict[str, list[str]] = {
    "hygiene": [
        "tests/guardian/test_guardian_hygiene.py",
    ],
    "manifest_integrity": [
        "tests/guardian/test_guardian_manifest.py",
    ],
    "contract_integrity": [
        "tests/guardian/test_guardian_self_integrity.py",
    ],
}

# Additional non-script coverage (contract module tests, aggregator tests)
AUXILIARY_COVERAGE: dict[str, list[str]] = {
    "guardian_contract": [
        "tests/guardian/test_guardian_contract.py",
        "tests/guardian/test_contract_compatibility.py",
    ],
    "combined": [
        "tests/guardian/test_guardian_aggregation.py",
    ],
}


class TestGuardianMetaCoverage:
    """Ensure every guardian in SSOT registry has test coverage."""

    def test_every_registered_guardian_has_test_coverage(self):
        """Every guardian in ALL_GUARDIANS must appear in GUARDIAN_COVERAGE_MAP."""
        uncovered = []
        for spec in ALL_GUARDIANS:
            if spec.guardian_id not in GUARDIAN_COVERAGE_MAP:
                uncovered.append(f"{spec.guardian_id} ({spec.entrypoint_module})")

        assert not uncovered, f"Registered guardians without test coverage: {uncovered}"

    def test_all_test_files_exist(self):
        """Every test file in the coverage map must actually exist."""
        missing = []
        all_coverage = {**GUARDIAN_COVERAGE_MAP, **AUXILIARY_COVERAGE}
        for guardian_id, test_files in all_coverage.items():
            for tf in test_files:
                full_path = PROJECT_ROOT / tf
                if not full_path.exists():
                    missing.append(f"{guardian_id}: {tf}")

        assert not missing, f"Test files in coverage map do not exist: {missing}"

    def test_all_registered_entrypoints_exist(self):
        """Every entrypoint module in registry must be importable."""
        import importlib

        errors = []
        for spec in ALL_GUARDIANS:
            try:
                mod = importlib.import_module(spec.entrypoint_module)
                if not hasattr(mod, spec.entrypoint_fn):
                    errors.append(
                        f"{spec.guardian_id}: {spec.entrypoint_fn} not found in {spec.entrypoint_module}",
                    )
            except ImportError as exc:
                errors.append(f"{spec.guardian_id}: ImportError {exc}")

        assert not errors, f"Registry entrypoint errors: {errors}"

    def test_contract_module_exists(self):
        """The canonical contract module must exist."""
        contract_path = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "types" / "guardian_contract.py"
        assert contract_path.exists(), f"Contract module missing: {contract_path}"

    def test_registry_module_exists(self):
        """The SSOT registry module must exist."""
        registry_path = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "types" / "guardian_registry.py"
        assert registry_path.exists(), f"Registry module missing: {registry_path}"

    def test_registry_not_empty(self):
        """Registry must have at least one guardian."""
        assert len(ALL_GUARDIANS) > 0
        assert len(get_guardian_specs(enabled_only=True)) > 0

    def test_registry_order_is_deterministic(self):
        """ALL_GUARDIANS must be sorted by guardian_id."""
        ids = [spec.guardian_id for spec in ALL_GUARDIANS]
        assert ids == sorted(ids), f"Registry not sorted: {ids}"
