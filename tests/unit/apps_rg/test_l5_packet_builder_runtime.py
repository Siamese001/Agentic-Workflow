"""apps-test-model: SPINE BINDING."""

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

from apps_rg.runtime.l5.packet_builder import (
    attach_l5_packet_to_sealed,
    build_l5_certification_packet,
)


def _sealed(**overrides) -> SealedL2Artifact:
    base = {
        "request_id": "req-packet",
        "run_id": "run-packet",
        "app_id": "apps_rg",
        "trace_id": "trace-packet",
        "execution_status": "completed",
        "generated_content": "{}",
        "compilation_hash": "a" * 64,
        "replay_key": "replay-packet",
        "l5_certification_ref": "l5:apps_rg:u0:valid",
    }
    base.update(overrides)
    return SealedL2Artifact(**base)


def test_packet_builder_certifies_normal_governed_context() -> None:
    result = build_l5_certification_packet(sealed=_sealed())

    assert result.status == "L5_CERTIFIED"
    assert result.packet_digest == result.packet.digest_sha256
    assert result.packet.l5_governance_context_digest
    assert result.packet_ref.startswith("l5_packet:")


def test_packet_builder_missing_replay_key_not_certified() -> None:
    result = build_l5_certification_packet(sealed=_sealed(replay_key=""))

    assert result.status == "L5_NOT_CERTIFIED"
    assert any("missing_replay_key" in rc for rc in result.packet.reason_codes)


def test_packet_builder_rejects_placeholder_ref_without_test_flag() -> None:
    result = build_l5_certification_packet(
        sealed=_sealed(l5_certification_ref="test:valid:w6")
    )

    assert result.status == "L5_NOT_CERTIFIED"
    assert any("placeholder_l5_cert_ref_rejected" in rc for rc in result.packet.reason_codes)


def test_packet_builder_allows_placeholder_ref_only_with_test_flag() -> None:
    result = build_l5_certification_packet(
        sealed=_sealed(l5_certification_ref="test:valid:w6"),
        allow_test_l5_cert_ref=True,
    )

    assert result.status == "L5_CERTIFIED"


def test_attach_l5_packet_to_sealed_sets_packet_fields_without_gate_refs() -> None:
    sealed = _sealed(gate_verdict_refs=("G11:PASS",))
    result = build_l5_certification_packet(sealed=sealed)
    attached = attach_l5_packet_to_sealed(sealed, result)

    assert attached.l5_certification_packet_ref == result.packet_ref
    assert attached.l5_certification_packet_digest == result.packet_digest
    assert attached.l5_certification_status == "L5_CERTIFIED"
    assert attached.gate_verdict_refs == ("G11:PASS",)
