"""P1 hotspot basename coverage — SealedL2Artifact (L2 stage)."""
from tests._core_contract._spine_u0_exit_fixtures import L5_CERT


def test_sealed_l2_artifact_completed_with_cert() -> None:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    art = SealedL2Artifact(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        execution_status="completed",
        l5_certification_ref=L5_CERT,
    )
    assert art.execution_status == "completed"
