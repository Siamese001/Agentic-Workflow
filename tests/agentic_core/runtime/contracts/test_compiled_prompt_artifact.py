"""P1 hotspot basename coverage — CompiledPromptArtifact (PA stage)."""
from tests._core_contract._spine_u0_exit_fixtures import L5_CERT


def test_compiled_prompt_artifact_generation_posture() -> None:
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    from agentic_core.runtime.contracts.posture import POSTURE_GENERATION

    pa = CompiledPromptArtifact(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        l5_certification_ref=L5_CERT,
    )
    assert pa.posture == POSTURE_GENERATION
