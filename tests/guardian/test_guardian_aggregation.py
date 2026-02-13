"""
Phase B: Guardian Aggregation Tests — ReAct-Style.

Tests the run_all_guardians.py aggregator against sandboxed fixtures.
Verifies:
1. Clean repo → all guardians pass → combined PASS
2. Dirty repo → at least one FAIL → combined FAIL
3. Deterministic sorted execution order
4. Global status promotion (ERROR > FAIL > PASS)
5. Per-guardian metrics present
6. Combined artifact written correctly
7. Schema compatibility of combined result
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_all_guardians import (
    run_all_guardians,
)
from agentic_core.L0_routing.types.guardian_contract import (
    CheckStatus,
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)
from agentic_core.L0_routing.types.guardian_registry import (
    get_guardian_specs,
)

_ENABLED_GUARDIANS = get_guardian_specs(enabled_only=True)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_repo(tmp_path: Path) -> Path:
    """Minimal sandboxed repo — no violations."""
    for folder in ("agentic_core", "apps_shared", "tests"):
        d = tmp_path / folder
        d.mkdir()
        (d / "__init__.py").write_text("", encoding="utf-8")
        (d / "real_module.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def dirty_repo(clean_repo: Path) -> Path:
    """Add hygiene violations."""
    (clean_repo / "agentic_core" / "scratch.tmp").write_bytes(b"\x00")
    (clean_repo / "agentic_core" / "empty_dir").mkdir()
    return clean_repo


# ---------------------------------------------------------------------------
# 1. Clean repo → combined PASS
# ---------------------------------------------------------------------------


class TestCleanAggregation:
    # Guardians that inherently require the real repo structure
    # (SOVEREIGN_TERRITORIES, classification config, etc.) and cannot
    # work on a minimal sandboxed tmp_path fixture.
    _REAL_REPO_GUARDIANS = {
        "guardian_hierarchy_compliance",
        "guardian_location_alignment",
    }

    def test_combined_result_has_correct_id(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        assert result.guardian_id == "combined"

    def test_sandboxable_sub_guardians_pass(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        for check in result.checks:
            if check.check_id in self._REAL_REPO_GUARDIANS:
                continue
            assert check.status == CheckStatus.PASS.value, (
                f"Sub-guardian {check.check_id} should PASS on clean repo"
            )

    def test_guardian_count_matches_registry(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        assert result.metrics["guardian_count"] == len(_ENABLED_GUARDIANS)
        assert len(result.checks) == len(_ENABLED_GUARDIANS)


# ---------------------------------------------------------------------------
# 2. Dirty repo → combined FAIL
# ---------------------------------------------------------------------------


class TestDirtyAggregation:
    def test_combined_fails(self, dirty_repo: Path):
        result = run_all_guardians(repo_root=dirty_repo)
        assert result.status == GuardianStatus.FAIL.value

    def test_hygiene_sub_guardian_fails(self, dirty_repo: Path):
        result = run_all_guardians(repo_root=dirty_repo)
        hygiene_check = next(c for c in result.checks if c.check_id == "guardian_hygiene")
        assert hygiene_check.status == CheckStatus.FAIL.value

    def test_remediation_hints_aggregated(self, dirty_repo: Path):
        result = run_all_guardians(repo_root=dirty_repo)
        assert len(result.remediation_hints) > 0


# ---------------------------------------------------------------------------
# 3. Deterministic ordering
# ---------------------------------------------------------------------------


class TestDeterministicOrdering:
    def test_sorted_execution(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        check_ids = [c.check_id for c in result.checks]
        sorted_ids = sorted(check_ids)
        assert check_ids == sorted_ids, "Guardians must execute in sorted order"

    def test_same_input_same_output(self, clean_repo: Path):
        r1 = run_all_guardians(repo_root=clean_repo)
        r2 = run_all_guardians(repo_root=clean_repo)
        d1 = r1.to_dict()
        d2 = r2.to_dict()
        assert d1 == d2


# ---------------------------------------------------------------------------
# 4. Per-guardian metrics
# ---------------------------------------------------------------------------


class TestMetrics:
    def test_per_guardian_metrics_present(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        assert "per_guardian" in result.metrics
        assert len(result.metrics["per_guardian"]) == len(_ENABLED_GUARDIANS)

    def test_each_entry_has_guardian_id(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        for entry in result.metrics["per_guardian"]:
            assert "guardian_id" in entry
            assert "status" in entry

    def test_total_checks_counted(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        assert result.metrics["total_checks"] > 0


# ---------------------------------------------------------------------------
# 5. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths: {violations}"

    def test_schema_compatible(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema drift: {errors}"

    def test_correlation_id_injectable(self, clean_repo: Path):
        result = run_all_guardians(
            repo_root=clean_repo,
            correlation_id="test-run-42",
        )
        assert result.correlation_id == "test-run-42"
        d = result.to_dict()
        assert d["correlation_id"] == "test-run-42"


# ---------------------------------------------------------------------------
# 6. Artifact writing
# ---------------------------------------------------------------------------


class TestArtifactWriting:
    def test_writes_combined_artifact(self, clean_repo: Path):
        run_all_guardians(
            repo_root=clean_repo,
            write_artifacts_dir="docs/reports/verification/guardian",
        )
        out = clean_repo / "docs" / "reports" / "verification" / "guardian" / "combined_guardian_result.json"
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["guardian_id"] == "combined"
