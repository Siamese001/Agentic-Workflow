import time
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent


@pytest.mark.asyncio
async def test_reconciler_isolation_v2(tmp_path: Path):
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "apps_lic").mkdir()
    (tmp_path / "apps_rg").mkdir()

    agent = FilesystemSSOTReconcilerAgent(tmp_path)

    with patch(
        "agentic_core.L5_safety.validators.structure_blueprint.SOVEREIGN_TERRITORIES",
        {"agentic_core": {}, "apps_lic": {}, "apps_rg": {}},
    ):
        await agent._scan_filesystem(target_territory="prompt_governance")

        assert "agentic_core" in agent.actual_folders
        assert "apps_lic" not in agent.actual_folders
        assert "apps_rg" not in agent.actual_folders


def test_governor_audit_bleed_prevention(tmp_path: Path):
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "apps_lic").mkdir()

    agent = ArchitectureGovernorAgent(project_root=tmp_path)

    with patch.object(ArchitectureGovernorAgent, "_get_structure_validator") as mock_validator:
        mock_validator.return_value.validate_structure.return_value.violations = []

        with patch(
            "agentic_core.L5_safety.validators.structure_blueprint.SOVEREIGN_TERRITORIES",
            {"agentic_core": {}, "apps_lic": {}},
        ):
            results = agent.heal_repository(dry_run=True, target_territory="apps_lic")

            roots_scanned = (results.get("_raw_result") or {}).get("roots_scanned")
            assert roots_scanned == ["apps_lic"]
            assert "agentic_core" not in (roots_scanned or [])


def test_performance_boundary_verification(tmp_path: Path):
    (tmp_path / "agentic_core").mkdir()

    agent = ArchitectureGovernorAgent(project_root=tmp_path)

    with patch.object(ArchitectureGovernorAgent, "_get_structure_validator") as mock_validator:
        mock_validator.return_value.validate_structure.return_value.violations = []

        start_time = time.time()
        agent.heal_repository(dry_run=True, target_territory="prompt_governance")
        execution_time = time.time() - start_time

        assert execution_time < 2.0
