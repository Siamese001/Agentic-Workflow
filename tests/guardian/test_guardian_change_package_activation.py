"""Runtime smoke tests for the change-package activation Guardian runner."""

from __future__ import annotations

from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult
from ops_scripts.dev_tools.L0_routing_scripts.run_guardian_change_package_activation import (
    run_change_package_activation_guardian,
)


def test_change_package_activation_guardian_emits_result_on_empty_repo(tmp_path) -> None:
    result = run_change_package_activation_guardian(repo_root=tmp_path)

    assert isinstance(result, GuardianResult)
    assert result.guardian_id == "change_package_activation_guard"
    assert {check.check_id for check in result.checks} == {
        "proposal_only_bypass",
        "direct_version_store_commit",
        "activation_without_approval_gate",
    }
