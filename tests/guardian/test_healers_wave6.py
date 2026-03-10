"""
Contract Tests: Wave 6 Healers (classification, hierarchy, architecture).

Tests:
1. Dry-run mode returns SKIPPED with planned actions
2. Apply mode for territory_compliance moves files
3. Apply mode for missing_structure creates directories
4. Human-review-only healers always return SKIPPED
5. HealCheckResult schema validity
6. Healer registry contains all expected entries
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    L1_COGNITION_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L2_execution.healers.architecture_governance_healer import (
    heal_import_compliance,
    heal_layer_gravity,
)
from agentic_core.L2_execution.healers.classification_compliance_healer import (
    heal_naming_compliance,
    heal_territory_compliance,
)
from agentic_core.L2_execution.healers.hierarchy_compliance_healer import (
    heal_missing_structure,
    heal_subfolder_compliance,
)
from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
from agentic_core.L2_execution.types.healer_registry_types import HEALER_REGISTRY

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures: synthetic check dicts (mimic guardian aggregate evidence)
# ---------------------------------------------------------------------------


@pytest.fixture()
def naming_check() -> dict:
    return {
        "check_id": "naming_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 2,
            "violations": [
                {"path": "agentic_core/L1_cognition/config/foo_config_types.py"},
                {"path": "agentic_core/L2_execution/utils/bar_util_mixin.py"},
            ],
        },
    }


@pytest.fixture()
def territory_check() -> dict:
    return {
        "check_id": "territory_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {
                    "path": "agentic_core/L1_cognition/config/SomeAgent.py",
                    "classified_as": "AGENT",
                    "expected_folder": "reasoning",
                    "actual_folder": "config",
                },
            ],
        },
    }


@pytest.fixture()
def missing_structure_check() -> dict:
    return {
        "check_id": "missing_structure",
        "status": "FAIL",
        "evidence": {
            "violation_count": 2,
            "violations": [
                {"level": "L2", "path": "agentic_core/L7_future"},
                {"level": "L3", "path": "agentic_core/L5_safety/new_subfolder", "parent_layer": "L5_safety"},
            ],
        },
    }


@pytest.fixture()
def subfolder_check() -> dict:
    return {
        "check_id": "subfolder_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {"path": "agentic_core/L5_safety/rogue", "parent_layer": "L5_safety", "folder_name": "rogue"},
            ],
        },
    }


@pytest.fixture()
def import_check() -> dict:
    return {
        "check_id": "import_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {
                    "path": "agentic_core/L0_routing/scripts/bad.py",
                    "source_layer": "L0",
                    "target_layer": "L5",
                    "import_line": "from agentic_core.L5_safety.reasoning import ...",
                    "line_number": 3,
                },
            ],
        },
    }


@pytest.fixture()
def gravity_check() -> dict:
    return {
        "check_id": "layer_gravity",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {
                    "path": "agentic_core/L0_routing/reasoning/WrongAgent.py",
                    "agent_name": "WrongAgent",
                    "actual_layer": "L0",
                    "assigned_layer": "L3",
                },
            ],
        },
    }


# ---------------------------------------------------------------------------
# 1. Healer registry completeness
# ---------------------------------------------------------------------------


class TestHealerRegistry:
    """Verify all Wave 6 healers are registered."""

    EXPECTED_IDS = {
        "naming_compliance",
        "territory_compliance",
        "missing_structure",
        "subfolder_compliance",
        "import_compliance",
        "layer_gravity",
    }

    def test_all_healers_registered(self) -> None:
        for cid in self.EXPECTED_IDS:
            assert cid in HEALER_REGISTRY, f"{cid} not in HEALER_REGISTRY"

    def test_registry_values_are_callable(self) -> None:
        for cid in self.EXPECTED_IDS:
            assert callable(HEALER_REGISTRY[cid])


# ---------------------------------------------------------------------------
# 2. Classification compliance healers
# ---------------------------------------------------------------------------


class TestNamingComplianceHealer:
    """Naming healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, naming_check: dict) -> None:
        result = heal_naming_compliance(naming_check)
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 2

    def test_apply_still_skipped(self, naming_check: dict, tmp_path: Path) -> None:
        result = heal_naming_compliance(naming_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED

    def test_planned_actions_sorted(self, naming_check: dict) -> None:
        result = heal_naming_compliance(naming_check)
        assert list(result.changes_made) == sorted(result.changes_made)


class TestTerritoryComplianceHealer:
    """Territory healer supports dry-run and apply."""

    def test_dry_run_returns_skipped(self, territory_check: dict) -> None:
        result = heal_territory_compliance(territory_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1
        assert "would_move" in result.changes_made[0]

    def test_apply_moves_file(self, territory_check: dict, tmp_path: Path) -> None:
        # Create source file
        src = tmp_path / L1_COGNITION_DIR / "config" / "SomeAgent.py"
        src.parent.mkdir(parents=True)
        src.write_text("class SomeAgent: pass\n", encoding="utf-8")

        result = heal_territory_compliance(territory_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.HEALED
        assert len(result.changes_made) == 1

        # Verify file moved
        target = tmp_path / L1_COGNITION_DIR / "reasoning" / "SomeAgent.py"
        assert target.is_file()
        assert not src.exists()

    def test_apply_without_repo_root_fails(self, territory_check: dict) -> None:
        result = heal_territory_compliance(territory_check, apply=True)
        assert result.status == HealStatus.FAILED


# ---------------------------------------------------------------------------
# 3. Hierarchy compliance healers
# ---------------------------------------------------------------------------


class TestMissingStructureHealer:
    """Missing structure healer supports dry-run and apply."""

    def test_dry_run_returns_skipped(self, missing_structure_check: dict) -> None:
        result = heal_missing_structure(missing_structure_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 2

    def test_apply_creates_directories(self, missing_structure_check: dict, tmp_path: Path) -> None:
        result = heal_missing_structure(missing_structure_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.HEALED
        assert len(result.changes_made) == 2

        assert (tmp_path / AGENTIC_CORE_DIR / "L7_future").is_dir()
        assert (tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "new_subfolder").is_dir()

    def test_apply_without_repo_root_fails(self, missing_structure_check: dict) -> None:
        result = heal_missing_structure(missing_structure_check, apply=True)
        assert result.status == HealStatus.FAILED

    def test_planned_actions_sorted(self, missing_structure_check: dict) -> None:
        result = heal_missing_structure(missing_structure_check)
        assert list(result.changes_made) == sorted(result.changes_made)


class TestSubfolderComplianceHealer:
    """Subfolder healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, subfolder_check: dict) -> None:
        result = heal_subfolder_compliance(subfolder_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1

    def test_apply_still_skipped(self, subfolder_check: dict, tmp_path: Path) -> None:
        result = heal_subfolder_compliance(subfolder_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED


# ---------------------------------------------------------------------------
# 4. Architecture governance healers (dry-run only)
# ---------------------------------------------------------------------------


class TestImportComplianceHealer:
    """Import compliance healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, import_check: dict) -> None:
        result = heal_import_compliance(import_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1
        assert "would_fix_import" in result.changes_made[0]

    def test_apply_still_skipped(self, import_check: dict, tmp_path: Path) -> None:
        result = heal_import_compliance(import_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED


class TestLayerGravityHealer:
    """Layer gravity healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, gravity_check: dict) -> None:
        result = heal_layer_gravity(gravity_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1
        assert "would_relocate_agent" in result.changes_made[0]

    def test_apply_still_skipped(self, gravity_check: dict, tmp_path: Path) -> None:
        result = heal_layer_gravity(gravity_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED


# ---------------------------------------------------------------------------
# 5. Schema validity (all healers return valid HealCheckResult)
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """Verify all healers produce valid HealCheckResult objects."""

    ALL_HEALER_FIXTURES = [
        "naming_check",
        "territory_check",
        "missing_structure_check",
        "subfolder_check",
        "import_check",
        "gravity_check",
    ]

    @pytest.mark.parametrize(
        "check_id",
        [
            "naming_compliance",
            "territory_compliance",
            "missing_structure",
            "subfolder_compliance",
            "import_compliance",
            "layer_gravity",
        ],
    )
    def test_healer_returns_valid_result(self, check_id: str) -> None:
        check = {"check_id": check_id, "status": "PASS", "evidence": {"violations": []}}
        healer_fn = HEALER_REGISTRY[check_id]
        result = healer_fn(check)
        assert isinstance(result, HealCheckResult)
        assert result.check_id == check_id
        assert isinstance(result.status, HealStatus)
        assert isinstance(result.changes_made, tuple)
