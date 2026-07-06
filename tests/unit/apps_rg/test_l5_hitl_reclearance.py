"""apps-test-model: LAW."""

from apps_rg.runtime.l5.hitl_reclearance import (
    ReClearedHITLPacket,
    detect_human_modification_flags,
    validate_recleared_hitl_packet,
)
from apps_rg.runtime.l5.packet_builder import build_l5_certification_packet


def test_detect_human_modification_flags_nested_payload() -> None:
    assert detect_human_modification_flags({"review": {"manual_edit": True}})
    assert not detect_human_modification_flags({"review": {"manual_edit": False}})


def test_human_modified_without_reclearance_blocks_packet() -> None:
    result = build_l5_certification_packet(
        run_context={
            "request_id": "req-hitl",
            "run_id": "run-hitl",
            "trace_id": "trace-hitl",
            "replay_key": "replay-hitl",
            "l5_certification_ref": "l5:apps_rg:u0:valid",
            "human_modified": True,
        }
    )

    assert result.status == "L5_NOT_CERTIFIED"
    assert any("missing_recleared_hitl_packet" in rc for rc in result.packet.reason_codes)


def test_malformed_reclearance_blocks() -> None:
    ok, reasons = validate_recleared_hitl_packet(
        {
            "packet_ref": "hitl:1",
            "digest": "bad",
            "authority_receipt_ref": "",
            "l5_governance_context_digest": "c" * 64,
        }
    )

    assert ok is False
    assert "malformed_recleared_hitl_digest" in reasons
    assert "missing_authority_receipt_ref" in reasons


def test_valid_reclearance_shape_validates() -> None:
    ok, reasons = validate_recleared_hitl_packet(
        ReClearedHITLPacket(
            packet_ref="hitl:1",
            digest="d" * 64,
            authority_receipt_ref="authority:hitl:1",
            l5_governance_context_digest="c" * 64,
        )
    )

    assert ok is True
    assert reasons == ()
