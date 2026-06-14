"""Runtime smoke tests for the escalation-determinism Guardian runner."""

from __future__ import annotations

from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult
from ops_scripts.dev_tools.L0_routing_scripts.run_guardian_escalation_determinism import (
    run_escalation_determinism_guardian,
)


def test_escalation_determinism_guardian_emits_result_on_empty_repo(tmp_path) -> None:
    result = run_escalation_determinism_guardian(repo_root=tmp_path)

    assert isinstance(result, GuardianResult)
    assert result.guardian_id == "escalation_determinism"
    assert {check.check_id for check in result.checks} == {
        "failure_signal_built_from_raw_notes",
        "alternate_escalation_context_construction",
        "escalation_context_mutation",
    }
