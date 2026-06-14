"""Runtime smoke tests for the gateway-bypass Guardian runner."""

from __future__ import annotations

from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult
from ops_scripts.dev_tools.L0_routing_scripts.run_guardian_gateway_bypass import (
    run_gateway_bypass_guardian,
)


def test_gateway_bypass_guardian_emits_result_on_empty_repo(tmp_path) -> None:
    result = run_gateway_bypass_guardian(repo_root=tmp_path)

    assert isinstance(result, GuardianResult)
    assert result.guardian_id == "gateway_bypass"
    assert {check.check_id for check in result.checks} == {
        "provider_sdk_import",
        "direct_model_call",
        "bypass_tier_router",
        "bypass_embedding_factory",
    }
