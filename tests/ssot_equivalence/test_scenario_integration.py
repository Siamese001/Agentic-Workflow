"""
Wave 7.1 — Scenario Integration Tests.

End-to-end tests wiring guardians → dispatcher → healers in a controlled
sandbox. Validates the full pipeline without requiring L3 approval bundles.

Scenarios:
1. Clean sandbox: all guardians pass, dispatcher produces all-SKIPPED results
2. Dispatcher dry-run: processes guardian aggregate, produces valid CombinedHealResult
3. Phase prefix mapping: new guardians are correctly mapped to phases
4. Healer invocation: registered healers are called for mapped check_ids
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L2_execution.scripts.remediation_dispatcher import (
    PHASE_CHECK_ID_PREFIXES,
    classify_check_ids,
    extract_check_ids,
)
from agentic_core.L2_execution.types.heal_contract import (
    CombinedHealResult,
    HealCheckResult,
    HealStatus,
)
from agentic_core.L2_execution.types.healer_registry import HEALER_REGISTRY

pytestmark = pytest.mark.ssot_equivalence

FIXED_UTC = "2026-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _build_guardian_aggregate(check_ids: list[str], status: str = "FAIL") -> dict:
    """Build a minimal guardian aggregate dict from check_id list."""
    checks = []
    for cid in check_ids:
        checks.append(
            {
                "check_id": cid,
                "status": status,
                "details": f"synthetic check {cid}",
                "evidence": {"violations": [], "violation_count": 0},
            },
        )
    return {
        "guardian_id": "aggregate",
        "version": 1,
        "status": status,
        "summary": "synthetic aggregate",
        "checks": checks,
        "artifacts": [],
        "metrics": {},
        "remediation_hints": [],
    }


@pytest.fixture()
def all_guardian_check_ids() -> list[str]:
    """All check_ids produced by a full guardian run (aggregate format)."""
    return [
        "guardian_architecture_governance",
        "guardian_classification_compliance",
        "guardian_contract_integrity",
        "guardian_drift_detection",
        "guardian_hierarchy_compliance",
        "guardian_location_alignment",
    ]


@pytest.fixture()
def aggregate_path(tmp_path: Path, all_guardian_check_ids: list[str]) -> Path:
    """Write a synthetic guardian aggregate to disk."""
    agg = _build_guardian_aggregate(all_guardian_check_ids)
    p = tmp_path / "combined_guardian_result.json"
    p.write_text(json.dumps(agg, indent=2), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 1. Phase prefix mapping
# ---------------------------------------------------------------------------


class TestPhasePrefixMapping:
    """Verify new guardians are correctly mapped to dispatcher phases."""

    def test_classification_maps_to_reconciliation(self) -> None:
        mapped, unmapped = classify_check_ids(["guardian_classification_compliance"])
        assert "guardian_classification_compliance" in mapped

    def test_hierarchy_maps_to_alignment(self) -> None:
        mapped, unmapped = classify_check_ids(["guardian_hierarchy_compliance"])
        assert "guardian_hierarchy_compliance" in mapped

    def test_architecture_maps_to_arch_validation(self) -> None:
        mapped, unmapped = classify_check_ids(["guardian_architecture_governance"])
        assert "guardian_architecture_governance" in mapped

    def test_all_wave5_guardians_mapped(self, all_guardian_check_ids: list[str]) -> None:
        mapped, unmapped = classify_check_ids(all_guardian_check_ids)
        # contract_integrity is not mapped to any phase
        expected_unmapped = {"guardian_contract_integrity"}
        assert unmapped == expected_unmapped
        assert len(mapped) == len(all_guardian_check_ids) - len(expected_unmapped)

    def test_no_phase_has_overlapping_prefixes(self) -> None:
        """Each check_id should map to at most one phase."""
        all_prefixes: list[str] = []
        for prefixes in PHASE_CHECK_ID_PREFIXES.values():
            all_prefixes.extend(prefixes)
        # No prefix should be a prefix of another prefix
        for i, p1 in enumerate(all_prefixes):
            for j, p2 in enumerate(all_prefixes):
                if i != j:
                    assert not p1.startswith(p2), f"Overlapping prefixes: {p1} vs {p2}"


# ---------------------------------------------------------------------------
# 2. Extract check_ids from aggregate
# ---------------------------------------------------------------------------


class TestExtractCheckIds:
    """Verify check_id extraction from guardian aggregate."""

    def test_extract_from_aggregate(self, all_guardian_check_ids: list[str]) -> None:
        agg = _build_guardian_aggregate(all_guardian_check_ids)
        extracted = extract_check_ids(agg)
        assert extracted == sorted(all_guardian_check_ids)

    def test_deduplication(self) -> None:
        agg = _build_guardian_aggregate(["guardian_drift_detection", "guardian_drift_detection"])
        extracted = extract_check_ids(agg)
        assert extracted == ["guardian_drift_detection"]


# ---------------------------------------------------------------------------
# 3. Healer registry coverage
# ---------------------------------------------------------------------------


class TestHealerRegistryCoverage:
    """Verify healer registry covers all Wave 5/6 check_ids."""

    WAVE6_CHECK_IDS = {
        "naming_compliance",
        "territory_compliance",
        "missing_structure",
        "subfolder_compliance",
        "import_compliance",
        "layer_gravity",
        "guardian_drift_detection",
    }

    def test_all_wave6_healers_registered(self) -> None:
        for cid in self.WAVE6_CHECK_IDS:
            assert cid in HEALER_REGISTRY, f"Missing healer for {cid}"

    def test_healer_dry_run_returns_valid_result(self) -> None:
        for cid, fn in HEALER_REGISTRY.items():
            check = {"check_id": cid, "status": "PASS", "evidence": {"violations": []}}
            result = fn(check)
            assert isinstance(result, HealCheckResult)
            assert isinstance(result.status, HealStatus)
            assert result.check_id == cid


# ---------------------------------------------------------------------------
# 4. Dispatcher dry-run integration (no approval needed)
# ---------------------------------------------------------------------------


class TestDispatcherDryRunIntegration:
    """Verify dispatcher produces valid CombinedHealResult from guardian aggregate."""

    def test_dry_run_produces_valid_json(self, aggregate_path: Path, tmp_path: Path) -> None:
        from agentic_core.L2_execution.scripts.remediation_dispatcher import run_dispatcher

        out_dir = tmp_path / "heal_output"
        result = run_dispatcher(
            guardian_result_path=aggregate_path,
            write_artifacts_dir=out_dir,
            created_utc=FIXED_UTC,
        )
        assert isinstance(result, CombinedHealResult)
        assert result.tool_id == "remediation_dispatcher"
        assert result.created_utc == FIXED_UTC

    def test_dry_run_all_skipped(self, aggregate_path: Path, tmp_path: Path) -> None:
        from agentic_core.L2_execution.scripts.remediation_dispatcher import run_dispatcher

        out_dir = tmp_path / "heal_output"
        result = run_dispatcher(
            guardian_result_path=aggregate_path,
            write_artifacts_dir=out_dir,
            created_utc=FIXED_UTC,
        )
        for check_result in result.results:
            assert check_result.status == HealStatus.SKIPPED, (
                f"{check_result.check_id} has status {check_result.status}, expected SKIPPED"
            )

    def test_dry_run_writes_artifact(self, aggregate_path: Path, tmp_path: Path) -> None:
        from agentic_core.L2_execution.scripts.remediation_dispatcher import run_dispatcher

        out_dir = tmp_path / "heal_output"
        run_dispatcher(
            guardian_result_path=aggregate_path,
            write_artifacts_dir=out_dir,
            created_utc=FIXED_UTC,
        )
        heal_path = out_dir / "combined_heal_result.json"
        assert heal_path.is_file()
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        assert data["tool_id"] == "remediation_dispatcher"
        assert isinstance(data["results"], list)

    def test_dry_run_schema_valid(self, aggregate_path: Path, tmp_path: Path) -> None:
        from agentic_core.L2_execution.scripts.remediation_dispatcher import run_dispatcher

        out_dir = tmp_path / "heal_output"
        result = run_dispatcher(
            guardian_result_path=aggregate_path,
            write_artifacts_dir=out_dir,
            created_utc=FIXED_UTC,
        )
        errors = result.validate()
        assert errors == [], f"CombinedHealResult validation errors: {errors}"
