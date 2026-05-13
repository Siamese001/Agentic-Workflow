"""Cross-app platform contract — every domain app round-trips uniformly.

This is the framework-driven counterpart to per-app `test_contract.py`
files. Adding a new app means registering it in
`tests/_apps_contract/fixtures.py` — no new test file required.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.4)
"""
from __future__ import annotations

import pytest

from tests._apps_contract.fixtures import (
    APP_CONTRACT_REGISTRY,
    AppContract,
    build_config,
    build_request,
    build_result,
)


@pytest.mark.parametrize(
    "contract",
    APP_CONTRACT_REGISTRY.contracts,
    ids=[c.app_id for c in APP_CONTRACT_REGISTRY.contracts],
)
def test_request_round_trip(contract: AppContract) -> None:
    req = build_request(contract)
    rebuilt = type(req).model_validate(req.model_dump())
    assert req.model_dump() == rebuilt.model_dump()


@pytest.mark.parametrize(
    "contract",
    APP_CONTRACT_REGISTRY.contracts,
    ids=[c.app_id for c in APP_CONTRACT_REGISTRY.contracts],
)
def test_config_round_trip(contract: AppContract) -> None:
    cfg = build_config(contract)
    rebuilt = type(cfg).model_validate(cfg.model_dump())
    assert cfg.model_dump() == rebuilt.model_dump()


@pytest.mark.parametrize(
    "contract",
    APP_CONTRACT_REGISTRY.contracts,
    ids=[c.app_id for c in APP_CONTRACT_REGISTRY.contracts],
)
def test_result_exposes_gate_violations(contract: AppContract) -> None:
    """Platform invariant: every Result type exposes `gate_violations: list[str]`.

    apps_lic uses `CampaignResult` which has `validation_errors` instead;
    we accept either as the platform contract is "expose a list-of-violations
    field by SOME canonical name."
    """
    result = build_result(contract)
    candidate_fields = ("gate_violations", "validation_errors", "violations")
    found = [f for f in candidate_fields if hasattr(result, f)]
    assert found, (
        f"{contract.app_id}.{contract.result_class} exposes none of "
        f"{candidate_fields}; platform contract requires one."
    )
    for f in found:
        value = getattr(result, f)
        assert isinstance(value, list), (
            f"{contract.app_id}.{f} must be a list, got {type(value).__name__}"
        )


@pytest.mark.parametrize(
    "contract",
    APP_CONTRACT_REGISTRY.contracts,
    ids=[c.app_id for c in APP_CONTRACT_REGISTRY.contracts],
)
def test_result_round_trip(contract: AppContract) -> None:
    result = build_result(contract)
    rebuilt = type(result).model_validate(result.model_dump())
    assert result.model_dump() == rebuilt.model_dump()
