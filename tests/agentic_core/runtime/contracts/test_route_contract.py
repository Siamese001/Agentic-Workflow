"""P1 hotspot basename coverage — RouteContract (L0 stage)."""
from tests._core_contract._spine_u0_exit_fixtures import L5_CERT


def test_route_contract_read_only_posture() -> None:
    from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY
    from agentic_core.runtime.contracts.route_contract import RouteContract

    rc = RouteContract(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        route_id="R4",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        l5_certification_ref=L5_CERT,
    )
    assert rc.posture == POSTURE_READ_ONLY
