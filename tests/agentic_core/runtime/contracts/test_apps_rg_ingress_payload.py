"""P1 hotspot basename coverage — AppsRgIngressPayload / RequestEnvelope (U0 ingress)."""
from tests._core_contract._spine_u0_exit_fixtures import thin_apps_rg_ingress_kwargs


def test_apps_rg_ingress_payload_accepts_minimal_spine_fixture() -> None:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import AppsRgIngressPayload

    p = AppsRgIngressPayload(**thin_apps_rg_ingress_kwargs())
    assert p.target_company == "Acme Corp"
