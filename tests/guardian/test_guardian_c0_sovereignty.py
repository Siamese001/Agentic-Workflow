"""Runtime smoke tests for the C0 sovereignty Guardian runner."""

from __future__ import annotations

from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult
from ops_scripts.dev_tools.L0_routing_scripts.run_guardian_c0_sovereignty import (
    run_c0_sovereignty_guardian,
)


def test_c0_sovereignty_guardian_emits_result_on_empty_repo(tmp_path) -> None:
    result = run_c0_sovereignty_guardian(repo_root=tmp_path)

    assert isinstance(result, GuardianResult)
    assert result.guardian_id == "c0_sovereignty_enforcement"
    assert {check.check_id for check in result.checks} == {
        "embedding_drives_routing",
        "embedding_drives_tier_selection",
        "embedding_mutates_threshold",
    }
