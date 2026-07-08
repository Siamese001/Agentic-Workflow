"""apps-test-model: EVAL."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.l5.egress_receipts import (
    SYMBOLIC_APPS_RG_PROVIDER_REF,
    receipt_from_provider_exchange,
)
from apps_rg.runtime.l5.packet_builder import build_l5_certification_packet

pytestmark = pytest.mark.apps_test_model("EVAL")


def _sealed() -> SealedL2Artifact:
    return SealedL2Artifact(
        request_id="req-lane-eval",
        run_id="run-lane-eval",
        app_id="apps_rg",
        trace_id="trace-lane-eval",
        execution_status="completed",
        generated_content="{}",
        compilation_hash="a" * 64,
        replay_key="replay-lane-eval",
        l5_certification_ref="l5:apps_rg:u0:lane-eval",
    )


def test_lane_eval_emits_l5_certified_packet_and_typed_egress_receipt() -> None:
    egress = receipt_from_provider_exchange(
        provider_profile=SimpleNamespace(profile_id="vendor-model-prod"),
        provider_request=SimpleNamespace(
            request_id="req-lane-eval",
            run_id="run-lane-eval",
            trace_root="trace-lane-eval",
            node_id="section:executive_summary",
            prompt_artifact_ref="prompt:lane-eval",
            max_tokens=256,
            temperature=0.1,
            top_p=1.0,
        ),
        provider_response=SimpleNamespace(
            success=True,
            text="redacted",
            receipt=SimpleNamespace(token_usage=SimpleNamespace(total_tokens=37)),
            error_message=None,
        ),
        latency_ms=18.25,
        call_purpose_ref="prompt:lane-eval",
    )
    result = build_l5_certification_packet(sealed=_sealed(), egress_receipts=(egress,))

    assert result.status == "L5_CERTIFIED"
    assert result.packet_ref.startswith("l5_packet:")
    assert result.packet.egress_receipts[0].provider_ref == SYMBOLIC_APPS_RG_PROVIDER_REF
    assert result.packet.egress_receipts[0].request_digest
    assert result.packet.egress_receipts[0].redaction_receipt_ref
    assert (
        result.packet.egress_receipts[0].l5_governance_context_digest
        == result.packet.l5_governance_context_digest
    )
