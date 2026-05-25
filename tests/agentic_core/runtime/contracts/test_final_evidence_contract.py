"""P1 hotspot basename coverage — FinalEvidenceContract (C0 stage)."""
from tests._core_contract._spine_u0_exit_fixtures import L5_CERT


def test_final_evidence_contract_pass_support_status() -> None:
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        SUPPORT_STATUS_PASS,
        SUPPORT_STATUS_PASSING_VALUES,
    )

    fec = FinalEvidenceContract(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        l5_certification_ref=L5_CERT,
        support_status=SUPPORT_STATUS_PASS,
        support_target_met=True,
        final_evidence_digest="d1",
    )
    assert fec.support_status in SUPPORT_STATUS_PASSING_VALUES
