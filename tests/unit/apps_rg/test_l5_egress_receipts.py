"""apps-test-model: LAW."""

from dataclasses import asdict
from types import SimpleNamespace

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.l5.packet_builder import build_l5_certification_packet
from apps_rg.runtime.l5.egress_receipts import (
    SYMBOLIC_APPS_RG_PROVIDER_REF,
    build_apps_rg_egress_receipt,
    receipt_digest,
    receipt_from_provider_exchange,
)


def test_apps_rg_egress_receipt_uses_typed_fields() -> None:
    receipt = build_apps_rg_egress_receipt(
        request_metadata={"request_id": "req", "prompt_artifact_ref": "pa"},
        response_metadata={"success": True, "has_text": True},
        call_purpose_ref="pa",
        egress_policy_ref="policy",
    )

    assert receipt.provider_ref == SYMBOLIC_APPS_RG_PROVIDER_REF
    assert receipt.request_digest
    assert receipt.call_purpose_ref == "pa"
    assert receipt.redaction_receipt_ref
    assert receipt.egress_status == "EGRESS_CERTIFIED"
    assert receipt.certified is True


def test_apps_rg_egress_receipt_has_no_raw_prompt_or_response_fields() -> None:
    receipt = build_apps_rg_egress_receipt(
        request_metadata={"request_id": "req", "prompt_chars": 12},
        response_metadata={"success": True, "has_text": True},
        call_purpose_ref="pa",
    )
    payload = asdict(receipt)
    joined = " ".join(str(v) for v in payload.values())

    assert "raw prompt" not in joined.lower()
    assert "raw response" not in joined.lower()
    assert "prompt_text" not in payload
    assert "response_text" not in payload


def test_apps_rg_egress_receipt_digest_is_stable() -> None:
    kwargs = dict(
        request_metadata={"request_id": "req", "prompt_artifact_ref": "pa"},
        response_metadata={"success": True, "has_text": True},
        call_purpose_ref="pa",
    )
    first = build_apps_rg_egress_receipt(**kwargs)
    second = build_apps_rg_egress_receipt(**kwargs)

    assert receipt_digest(first) == receipt_digest(second)


def test_provider_exchange_uses_symbolic_provider_ref_not_vendor_model() -> None:
    receipt = receipt_from_provider_exchange(
        provider_profile=SimpleNamespace(profile_id="anthropic-claude-prod"),
        provider_request=SimpleNamespace(
            request_id="req",
            run_id="run",
            trace_root="trace",
            node_id="node",
            prompt_artifact_ref="prompt-ref",
            max_tokens=128,
            temperature=0.2,
            top_p=1.0,
        ),
        provider_response=SimpleNamespace(
            success=True,
            text="redacted generated output",
            receipt=SimpleNamespace(token_usage=SimpleNamespace(total_tokens=42)),
            error_message=None,
        ),
        latency_ms=12.3,
        call_purpose_ref="prompt-ref",
    )

    assert receipt.provider_ref == SYMBOLIC_APPS_RG_PROVIDER_REF
    assert "anthropic" not in receipt.provider_ref
    assert "claude" not in receipt.provider_ref
    assert receipt.request_digest
    assert receipt.response_digest


def test_egress_receipt_is_attached_to_final_packet() -> None:
    receipt = build_apps_rg_egress_receipt(
        request_metadata={"request_id": "req", "prompt_artifact_ref": "pa"},
        response_metadata={"success": True, "has_text": True},
        call_purpose_ref="pa",
    )
    sealed = SealedL2Artifact(
        request_id="req-egress",
        run_id="run-egress",
        app_id="apps_rg",
        trace_id="trace-egress",
        execution_status="completed",
        generated_content="{}",
        compilation_hash="a" * 64,
        replay_key="replay-egress",
        l5_certification_ref="l5:apps_rg:u0:egress",
    )

    result = build_l5_certification_packet(sealed=sealed, egress_receipts=(receipt,))

    assert result.status == "L5_CERTIFIED"
    assert len(result.packet.egress_receipts) == 1
    assert (
        result.packet.egress_receipts[0].l5_governance_context_digest
        == result.packet.l5_governance_context_digest
    )
