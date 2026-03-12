"""ADG-driven tests for L2 execution healers — fan_in=1.

Covers: architecture_governor_healer, file_classification_healer,
        filesystem_ssot_healer, gravity_leak_healer.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus

# ---------------------------------------------------------------------------
# architecture_governor_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    CHECK_ID as ARCH_CHECK_ID,
    heal_architecture_governance,
)


class TestArchitectureGovernorHealer:
    def test_check_id_string(self):
        assert isinstance(ARCH_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_architecture_governance)

    def test_no_violations_returns_healed(self):
        result = heal_architecture_governance(
            {"violations_count": 0}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_architecture_governance(
            {"violations_count": 3, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)
        assert result.status != HealStatus.HEALED

    def test_check_id_matches(self):
        result = heal_architecture_governance({"violations_count": 0})
        assert result.check_id == ARCH_CHECK_ID


# ---------------------------------------------------------------------------
# file_classification_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.file_classification_healer import (
    CHECK_ID as FILE_CLASS_CHECK_ID,
    heal_file_classification,
)


class TestFileClassificationHealer:
    def test_check_id_string(self):
        assert isinstance(FILE_CLASS_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_file_classification)

    def test_no_violations_returns_healed(self):
        result = heal_file_classification(
            {"violations_count": 0}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_file_classification(
            {"violations_count": 2, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_file_classification({"violations_count": 0})
        assert result.check_id == FILE_CLASS_CHECK_ID


# ---------------------------------------------------------------------------
# filesystem_ssot_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    CHECK_ID as FS_CHECK_ID,
    heal_filesystem_ssot_drift,
)


class TestFilesystemSSOTHealer:
    def test_check_id_string(self):
        assert isinstance(FS_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_filesystem_ssot_drift)

    def test_no_evidence_returns_healed(self):
        result = heal_filesystem_ssot_drift({"evidence": {}}, apply=False)
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_forbidden_folders(self):
        result = heal_filesystem_ssot_drift(
            {"evidence": {"forbidden_folders": ["bad_folder"]}},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_filesystem_ssot_drift({"evidence": {}})
        assert result.check_id == FS_CHECK_ID


# ---------------------------------------------------------------------------
# gravity_leak_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    CHECK_ID as GRAVITY_CHECK_ID,
    heal_gravity_violations,
)


class TestGravityLeakHealer:
    def test_check_id_string(self):
        assert isinstance(GRAVITY_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_gravity_violations)

    def test_no_violations_returns_healed(self):
        result = heal_gravity_violations(
            {"violations_count": 0, "evidence": {}}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_gravity_violations(
            {
                "violations_count": 1,
                "evidence": {"violations": [{"file": "foo.py", "import": "L5.bar"}]},
            },
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_gravity_violations({"violations_count": 0, "evidence": {}})
        assert result.check_id == GRAVITY_CHECK_ID
