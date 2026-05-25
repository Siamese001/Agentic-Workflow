"""P1 hotspot basename coverage — runtime L1PlanContract (L1 stage)."""
import pytest

from tests._core_contract._spine_u0_exit_fixtures import L5_CERT


def test_l1_plan_contract_accepts_valid_l5_cert() -> None:
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    c = L1PlanContract(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        l5_certification_ref=L5_CERT,
    )
    assert c.l5_certification_ref == L5_CERT


def test_l1_plan_contract_rejects_empty_l5_cert() -> None:
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    with pytest.raises(ValueError, match="l5_certification_ref"):
        L1PlanContract(request_id="r1", run_id="run1", app_id="a", trace_id="t1")
