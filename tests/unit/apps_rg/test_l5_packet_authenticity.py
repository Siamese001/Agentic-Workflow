"""Regression tests for authenticated apps_rg L5 packet consumption."""

from __future__ import annotations

from dataclasses import asdict, replace
from types import SimpleNamespace

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.bindings.exit_binding import _exit_finalize_apps_rg_impl
from apps_rg.runtime.l5.egress_receipts import receipt_from_provider_exchange
from apps_rg.runtime.l5.packet_builder import (
    attach_l5_packet_to_sealed,
    build_l5_certification_packet,
    verify_l5_packet_against_runtime,
)


def _sealed(**overrides: object) -> SealedL2Artifact:
    values = {
        "request_id": "req-auth",
        "run_id": "run-auth",
        "app_id": "apps_rg",
        "trace_id": "trace-auth",
        "execution_status": "completed",
        "generated_content": "{}",
        "compilation_hash": "a" * 64,
        "replay_key": "replay-auth",
        "l5_certification_ref": "l5:apps_rg:u0:auth",
    }
    values.update(overrides)
    return SealedL2Artifact(**values)


def _prompt(**overrides: object) -> SimpleNamespace:
    values = {
        "request_id": "req-auth",
        "run_id": "run-auth",
        "app_id": "apps_rg",
        "trace_id": "trace-auth",
        "tenant_id": "apps_rg",
        "replay_key": "replay-auth",
        "l5_certification_ref": "l5:apps_rg:u0:auth",
        "compilation_hash": "b" * 64,
        "evidence_digest": "c" * 64,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_attached_packet_is_recomputed_and_verified() -> None:
    sealed = _sealed()
    prompt = _prompt()
    result = build_l5_certification_packet(sealed=sealed, prompt_artifact=prompt)
    attached = attach_l5_packet_to_sealed(sealed, result, prompt_artifact=prompt)

    verification = verify_l5_packet_against_runtime(
        attached,
        prompt_artifact=prompt,
        require_stored_verification=True,
    )

    assert verification.verified is True
    assert attached.l5_certification_verified is True
    assert attached.l5_certification_packet is result.packet


def test_forged_hex_status_without_packet_object_is_blocked() -> None:
    forged = _sealed(
        l5_certification_packet_ref="l5_packet:" + "d" * 64,
        l5_certification_packet_digest="d" * 64,
        l5_certification_status="L5_CERTIFIED",
        l5_runtime_binding_digest="e" * 64,
        l5_certification_verified=True,
        l5_certification_verification_digest="f" * 64,
    )

    result = _exit_finalize_apps_rg_impl(forged, fec=None)

    assert result.disposition.outcome_authorized is False
    assert result.cache_write_proposals == ()
    assert (
        "missing_or_invalid_l5_certification_packet"
        in result.disposition.blocking_reason
    )


def test_packet_from_another_run_is_blocked() -> None:
    prompt = _prompt()
    result = build_l5_certification_packet(sealed=_sealed(), prompt_artifact=prompt)
    attached = attach_l5_packet_to_sealed(_sealed(), result, prompt_artifact=prompt)
    replayed_under_other_run = replace(attached, run_id="run-other")

    verification = verify_l5_packet_against_runtime(
        replayed_under_other_run,
        prompt_artifact=_prompt(run_id="run-other"),
        require_stored_verification=True,
    )

    assert verification.verified is False
    assert "packet_run_id_mismatch" in verification.reason_codes


def test_prompt_or_evidence_binding_change_is_detected() -> None:
    prompt = _prompt()
    result = build_l5_certification_packet(sealed=_sealed(), prompt_artifact=prompt)
    attached = attach_l5_packet_to_sealed(_sealed(), result, prompt_artifact=prompt)

    verification = verify_l5_packet_against_runtime(
        attached,
        prompt_artifact=_prompt(evidence_digest="9" * 64),
        require_stored_verification=True,
    )

    assert verification.verified is False
    assert "runtime_binding_digest_mismatch" in verification.reason_codes


def test_egress_digest_changes_when_response_content_changes() -> None:
    profile = SimpleNamespace(profile_id="provider-profile")
    request = SimpleNamespace(
        request_id="req-egress",
        run_id="run-egress",
        trace_root="trace-egress",
        node_id="node",
        prompt_artifact_ref="prompt:1",
        max_tokens=100,
        temperature=0.1,
        top_p=1.0,
    )

    def response(text: str) -> SimpleNamespace:
        return SimpleNamespace(
            success=True,
            text=text,
            error_message=None,
            receipt=SimpleNamespace(token_usage=SimpleNamespace(total_tokens=10)),
        )

    first = receipt_from_provider_exchange(
        provider_profile=profile,
        provider_request=request,
        provider_response=response('{"answer":"alpha"}'),
        latency_ms=1.0,
        call_purpose_ref="prompt:1",
    )
    second = receipt_from_provider_exchange(
        provider_profile=profile,
        provider_request=request,
        provider_response=response('{"answer":"beta"}'),
        latency_ms=1.0,
        call_purpose_ref="prompt:1",
    )

    assert first.response_digest != second.response_digest
    serialized = str(asdict(first))
    assert "alpha" not in serialized
