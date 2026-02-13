"""
Guardian Contract Tests: Hierarchy Compliance.

Tests:
1. Schema validity (GuardianResult fields, types)
2. Check IDs match registry spec
3. Deterministic evidence ordering
4. Missing structure scan detects missing L2/L3 dirs
5. Subfolder compliance scan detects non-approved folders
6. Clean synthetic repo produces PASS
7. No mutations (scan-only)
8. Timestamp injection for determinism
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.scripts.run_guardian_hierarchy_compliance import (
    GUARDIAN_ID,
    _get_l3_subfolders,
    run_hierarchy_compliance_guardian,
    scan_missing_structure,
    scan_subfolder_compliance,
)
from agentic_core.L0_maintenance.types.guardian_contract import (
    GuardianResult,
    GuardianStatus,
)
from agentic_core.L0_maintenance.types.guardian_registry import get_guardian_by_id

pytestmark = pytest.mark.guardian

FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def real_result() -> GuardianResult:
    """Run hierarchy compliance guardian on the real repo."""
    return run_hierarchy_compliance_guardian(
        repo_root=PROJECT_ROOT,
        timestamp=FIXED_TIMESTAMP,
    )


@pytest.fixture()
def synthetic_repo(tmp_path: Path) -> Path:
    """Create a minimal synthetic repo with complete hierarchy."""
    from agentic_core.L5_safety.config.structure_blueprint_config import (
        SOVEREIGN_TERRITORIES,
    )

    ac = tmp_path / "agentic_core"
    agentic_core_def = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    l2_subfolders = agentic_core_def.get("subfolders", {})
    approved_l2 = list(l2_subfolders.keys()) if hasattr(l2_subfolders, "keys") else []

    for layer_name in approved_l2:
        layer_path = ac / layer_name
        layer_path.mkdir(parents=True, exist_ok=True)
        layer_def = l2_subfolders.get(layer_name, {})
        for sub_name in _get_l3_subfolders(layer_def):
            (layer_path / sub_name).mkdir(parents=True, exist_ok=True)

    return tmp_path


@pytest.fixture()
def synthetic_repo_with_violations(tmp_path: Path) -> Path:
    """Create a synthetic repo with known hierarchy violations."""
    ac = tmp_path / "agentic_core"

    # Create L5_safety with only 'config' — others (reasoning, types, etc.) will be missing
    layer = ac / "L5_safety"
    layer.mkdir(parents=True)
    (layer / "config").mkdir()

    # Create a non-approved subfolder
    (layer / "rogue_folder").mkdir()

    return tmp_path


# ---------------------------------------------------------------------------
# 1. Schema validity
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """Verify guardian result conforms to contract schema."""

    def test_guardian_id(self, real_result: GuardianResult) -> None:
        assert real_result.guardian_id == GUARDIAN_ID

    def test_timestamp_injected(self, real_result: GuardianResult) -> None:
        assert real_result.timestamp == FIXED_TIMESTAMP

    def test_status_is_valid(self, real_result: GuardianResult) -> None:
        valid_statuses = {s.value for s in GuardianStatus}
        assert real_result.status in valid_statuses

    def test_checks_nonempty(self, real_result: GuardianResult) -> None:
        assert len(real_result.checks) >= 2

    def test_check_ids_match_registry(self, real_result: GuardianResult) -> None:
        spec = get_guardian_by_id(GUARDIAN_ID)
        assert spec is not None
        emitted_ids = {c.check_id for c in real_result.checks}
        registered_ids = set(spec.check_ids)
        assert emitted_ids == registered_ids

    def test_metrics_present(self, real_result: GuardianResult) -> None:
        assert "total_checks" in real_result.metrics
        assert "passed_checks" in real_result.metrics
        assert "failed_checks" in real_result.metrics

    def test_serialization_roundtrip(self, real_result: GuardianResult) -> None:
        json_str = real_result.to_json()
        data = json.loads(json_str)
        assert data["guardian_id"] == GUARDIAN_ID
        assert isinstance(data["checks"], list)
        assert len(data["checks"]) >= 2


# ---------------------------------------------------------------------------
# 2. Deterministic evidence ordering
# ---------------------------------------------------------------------------


class TestDeterministicEvidence:
    """Verify evidence is deterministically ordered."""

    def test_missing_structure_sorted(self, real_result: GuardianResult) -> None:
        check = next(
            (c for c in real_result.checks if c.check_id == "missing_structure"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)

    def test_subfolder_compliance_sorted(self, real_result: GuardianResult) -> None:
        check = next(
            (c for c in real_result.checks if c.check_id == "subfolder_compliance"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 3. Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanMissingStructure:
    """Unit tests for missing structure scan."""

    def test_complete_repo_no_violations(self, synthetic_repo: Path) -> None:
        violations = scan_missing_structure(synthetic_repo)
        assert violations == []

    def test_missing_l2_detected(self, tmp_path: Path) -> None:
        """A missing L2 layer directory should be detected."""
        # Create agentic_core with no subdirectories
        (tmp_path / "agentic_core").mkdir()
        violations = scan_missing_structure(tmp_path)
        # Should detect all expected L2 layers as missing
        assert len(violations) > 0
        l2_violations = [v for v in violations if v["level"] == "L2"]
        assert len(l2_violations) > 0

    def test_missing_l3_detected(self, synthetic_repo_with_violations: Path) -> None:
        """Missing L3 subfolders should be detected."""
        violations = scan_missing_structure(synthetic_repo_with_violations)
        l3_violations = [v for v in violations if v["level"] == "L3"]
        # L5_safety has config/ but is missing other LCD subfolders (reasoning, types, etc.)
        assert len(l3_violations) > 0


class TestScanSubfolderCompliance:
    """Unit tests for subfolder compliance scan."""

    def test_clean_repo_no_violations(self, synthetic_repo: Path) -> None:
        violations = scan_subfolder_compliance(synthetic_repo)
        assert violations == []

    def test_rogue_folder_detected(self, synthetic_repo_with_violations: Path) -> None:
        """A non-approved subfolder should be detected."""
        violations = scan_subfolder_compliance(synthetic_repo_with_violations)
        rogue = [v for v in violations if v["folder_name"] == "rogue_folder"]
        assert len(rogue) == 1
        assert rogue[0]["parent_layer"] == "L5_safety"


# ---------------------------------------------------------------------------
# 4. No mutations (scan-only)
# ---------------------------------------------------------------------------


class TestNoMutations:
    """Verify guardian does not mutate the repo."""

    def test_no_files_created_or_deleted(self, synthetic_repo: Path) -> None:
        before = set()
        for dirpath, dirnames, filenames in os.walk(synthetic_repo):
            before.add(dirpath)
            for fname in filenames:
                before.add(os.path.join(dirpath, fname))

        run_hierarchy_compliance_guardian(
            repo_root=synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )

        after = set()
        for dirpath, dirnames, filenames in os.walk(synthetic_repo):
            after.add(dirpath)
            for fname in filenames:
                after.add(os.path.join(dirpath, fname))

        assert before == after, (
            f"Guardian mutated filesystem: created={after - before}, deleted={before - after}"
        )
