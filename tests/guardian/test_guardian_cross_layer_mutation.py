"""Runtime smoke tests for the cross-layer mutation Guardian runner."""

from __future__ import annotations

from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult
from ops_scripts.dev_tools.L0_routing_scripts.run_guardian_cross_layer_mutation import (
    run_cross_layer_mutation_guardian,
)


def test_cross_layer_mutation_guardian_emits_result_on_empty_repo(tmp_path) -> None:
    result = run_cross_layer_mutation_guardian(repo_root=tmp_path)

    assert isinstance(result, GuardianResult)
    assert result.guardian_id == "cross_layer_mutation_guard"
    assert {check.check_id for check in result.checks} == {
        "upward_layer_mutation",
        "L6_mutates_L4",
        "L4_invokes_L2",
        "C0_mutates_control_plane",
    }
