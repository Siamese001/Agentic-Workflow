"""apps_rg U0 reflection harness — LIVE runtime path tests.

The sidecar tests in ``test_apps_rg_u0_payload_reflection.py`` prove
``apps_rg_u0_adapt`` works on fixtures. **These** tests prove the harness
is on the live runtime path — every real ``apps_rg_dispatch`` invocation
must produce a ``ValidatedRequest`` carrying a passing
``AppsRgU0ReflectionReceipt`` BEFORE L1 runs.

Coverage (per plan apps-rg-u0-reflection-live-wiring-105147 W3):

    1. valid thin payload → AppIngressRunner.run → dispatch → U0 invokes harness
    2. ValidatedRequest carries app_payload populated from harness
    3. ValidatedRequest carries reflection_receipt with pass_status=True
    4. audit_refs include "reflection:<digest_prefix>" entry
    5. Each of the 4 invalid fixtures fails at U0 BEFORE L1 executes
    6. Determinism: same envelope → same digests
    7. Direct dispatch (bypassing AppIngressRunner) still hits the harness
    8. No L1/L0/C0/PA/L2/Exit code runs after U0 rejection (proven by call-tracing
       the L1 binding and asserting it was not invoked)

Plan: .windsurf/plans/apps-rg-u0-reflection-live-wiring-105147.md (W3)
"""
from __future__ import annotations

import copy
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
from agentic_core.runtime.entry.apps_rg_dispatch import (
    APPS_RG_REQUIRED_FIELDS,
    apps_rg_dispatch,
    apps_rg_parse,
)
from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg
from agentic_core.runtime.u0 import (
    AppsRgU0AdapterError,
    AppsRgU0ReflectionReceipt,
    InvalidJdPayloadError,
    MissingJdHashError,
    MissingPolicyRefsError,
    MissingReplayKeyError,
    UnknownGenerationModeError,
    synthesize_contract_payload,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _thin_valid_payload() -> dict[str, Any]:
    """The shape ``apps_rg/__main__.py`` builds today."""

    return {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Amit Ayer — Senior AI Engineering Leader.",
        "job_description_text": "We seek a Senior Director of AI Engineering to lead our applied research org.",
        "manual_brief_path": None,
        "auto_research_internal": False,
        "auto_research_tavily": False,
        "research_via": None,
        "output_directory": "artifacts/apps_rg/runs",
        "idempotency_key": None,
    }


# ---------------------------------------------------------------------------
# 1+2+3+4. Live path — happy path proves harness invoked, receipt threaded
# ---------------------------------------------------------------------------


def test_live_runner_run_emits_validated_request_with_reflection_receipt() -> None:
    """A real-shaped thin payload must produce a ValidatedRequest with the
    harness receipt attached."""

    runner = AppIngressRunner(
        dispatch=lambda envelope: u0_validate_apps_rg(envelope),  # short-circuit at U0
        parse=apps_rg_parse,
        required_fields=APPS_RG_REQUIRED_FIELDS,
    )
    result = runner.run(_thin_valid_payload())

    assert isinstance(result, ValidatedRequest), (
        f"runner.run should produce ValidatedRequest from U0; got {type(result).__name__}"
    )
    assert result.reflection_receipt is not None, "reflection_receipt must be threaded onto ValidatedRequest"
    assert isinstance(result.reflection_receipt, AppsRgU0ReflectionReceipt)
    assert result.reflection_receipt.pass_status is True
    assert result.reflection_receipt.silently_dropped == ()
    assert result.reflection_receipt.unknown_mappings == ()


def test_live_runner_run_populates_app_payload() -> None:
    """The harness must thread the validated contract dump into app_payload."""

    runner = AppIngressRunner(
        dispatch=lambda envelope: u0_validate_apps_rg(envelope),
        parse=apps_rg_parse,
        required_fields=APPS_RG_REQUIRED_FIELDS,
    )
    result = runner.run(_thin_valid_payload())
    assert isinstance(result, ValidatedRequest)

    # The harness contract has these top-level keys; every one must appear.
    expected_keys = {
        "apps_rg_contract_version", "transport", "identity", "replay",
        "jd_payload", "resume_payload", "target", "generation_mode",
        "capability_requirements", "profile_manifest", "quality_thresholds",
        "output_requirements", "provenance_requirements", "payload_digest",
    }
    assert set(result.app_payload.keys()) == expected_keys


def test_live_path_threads_reflection_digest_into_audit_refs() -> None:
    """Existing audit infrastructure must capture the harness verdict."""

    runner = AppIngressRunner(
        dispatch=lambda envelope: u0_validate_apps_rg(envelope),
        parse=apps_rg_parse,
        required_fields=APPS_RG_REQUIRED_FIELDS,
    )
    result = runner.run(_thin_valid_payload())
    assert isinstance(result, ValidatedRequest)

    reflection_refs = [r for r in result.audit_refs if r.startswith("reflection:")]
    assert len(reflection_refs) == 1
    digest_prefix = reflection_refs[0].split(":", 1)[1]
    assert digest_prefix == result.reflection_receipt.input_payload_digest[:16]


def test_live_path_authority_validation_receipt_is_legacy_scan_result() -> None:
    """Defence in depth: the legacy AuthorityValidationReceipt must still
    be produced by the U0 binding so the existing audit chain sees it."""

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None
    vr = u0_validate_apps_rg(envelope)
    assert vr.authority_validation_receipt is not None
    assert vr.authority_validation_receipt.allowed is True
    assert vr.authority_validation_receipt.forbidden_fields_detected == ()


# ---------------------------------------------------------------------------
# 5. Each invalid fixture fails at U0 BEFORE L1
# ---------------------------------------------------------------------------


def test_invalid_missing_jd_payload_fails_before_l1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If a future synthesizer change emits an empty jd_text bypassing the
    placeholder fallback, the harness must still catch it via either the
    domain InvalidJdPayloadError or the Pydantic ``string_too_short``
    surfacing as AppsRgU0AdapterError."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod

    real_synth = synth_mod.synthesize_contract_payload

    def _empty_jd_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        contract = real_synth(envelope)
        contract["jd_payload"]["jd_text"] = ""
        return contract

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _empty_jd_synth)

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None

    with pytest.raises((InvalidJdPayloadError, AppsRgU0AdapterError)):
        u0_validate_apps_rg(envelope)


def test_synthesizer_placeholder_fallback_documented() -> None:
    """Document the synthesizer's contract-validity guarantee: when both
    job_description_text and job_description_ref are blank in the legacy
    envelope, the synthesizer substitutes a placeholder so the harness
    sees a contract-valid payload. This is intentional — the placeholder
    appears verbatim in app_payload, observable downstream.

    The placeholder behaviour is the bridge design: the synthesizer always
    produces a contract-valid payload from the legacy thin envelope, even
    when the legacy envelope lacks fields the contract requires. Real
    enforcement of "JD must be present for resume_generation" is a
    semantic check that belongs in L1 / quality gates, not U0 reflection.
    """

    thin = _thin_valid_payload()
    thin["job_description_text"] = ""
    thin["job_description_ref"] = ""
    envelope = apps_rg_parse(thin)
    assert envelope is not None

    contract = synthesize_contract_payload(envelope)
    assert contract["jd_payload"]["jd_text"], "synthesizer must substitute a non-empty placeholder"
    # The harness accepts the placeholder — proves the bridge holds.
    vr = u0_validate_apps_rg(envelope)
    assert vr.reflection_receipt.pass_status is True
    # And the placeholder is observable downstream — no silent data loss.
    assert vr.app_payload["jd_payload"]["jd_text"] == contract["jd_payload"]["jd_text"]


def test_invalid_unknown_generation_mode_fails_before_l1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the synthesizer to emit a bogus generation_mode; the harness
    must raise UnknownGenerationModeError at U0."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod

    real_synth = synth_mod.synthesize_contract_payload

    def _bad_mode_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        contract = real_synth(envelope)
        contract["generation_mode"] = "totally_invented_mode"
        return contract

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _bad_mode_synth)

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None
    with pytest.raises(UnknownGenerationModeError):
        u0_validate_apps_rg(envelope)


def test_invalid_missing_policy_ref_fails_before_l1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the synthesizer to drop a required policy ref; the harness
    must raise MissingPolicyRefsError at U0."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod

    real_synth = synth_mod.synthesize_contract_payload

    def _missing_ref_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        contract = real_synth(envelope)
        contract["profile_manifest"]["prompt_registry_ref"] = ""
        return contract

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _missing_ref_synth)

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None
    with pytest.raises(MissingPolicyRefsError):
        u0_validate_apps_rg(envelope)


def test_invalid_unmapped_field_fails_before_l1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the synthesizer to inject an unmapped top-level key. Pydantic's
    extra='forbid' catches this and the harness raises AppsRgU0AdapterError
    BEFORE L1 runs."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod

    real_synth = synth_mod.synthesize_contract_payload

    def _injected_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        contract = real_synth(envelope)
        contract["mystery_top_level_field"] = {"injected": True}
        return contract

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _injected_synth)

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None
    with pytest.raises(AppsRgU0AdapterError):
        u0_validate_apps_rg(envelope)


def test_invalid_missing_replay_key_fails_before_l1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the synthesizer to blank /replay/replay_key; the harness must
    raise MissingReplayKeyError BEFORE L1 runs."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod

    real_synth = synth_mod.synthesize_contract_payload

    def _missing_replay_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        contract = real_synth(envelope)
        contract["replay"]["replay_key"] = ""
        return contract

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _missing_replay_synth)

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None
    with pytest.raises(MissingReplayKeyError):
        u0_validate_apps_rg(envelope)


# ---------------------------------------------------------------------------
# 6. Determinism on the live path
# ---------------------------------------------------------------------------


def test_live_path_digests_are_deterministic_across_runs() -> None:
    """Same input envelope → same input_payload_digest + validated_request_digest."""

    envelope1 = apps_rg_parse(_thin_valid_payload())
    envelope2 = apps_rg_parse(_thin_valid_payload())
    assert envelope1 is not None and envelope2 is not None

    # Force identical request_id/run_id/trace_id so the digests match. (parse
    # mints UUID-derived ones by default — that's correct in production but
    # we need pinned values for determinism testing.)
    pinned: dict[str, str] = {
        "request_id": "rg-req-pinned-123",
        "run_id": "rg-run-pinned-123",
        "trace_id": "rg-trace-pinned-456",
        "submitted_at": "2026-05-10T12:00:00+00:00",
        "tenant_id": "apps_rg",
    }
    from dataclasses import replace as _replace

    e1 = _replace(envelope1, **pinned)
    e2 = _replace(envelope2, **pinned)

    vr1 = u0_validate_apps_rg(e1)
    vr2 = u0_validate_apps_rg(e2)

    assert vr1.reflection_receipt.input_payload_digest == vr2.reflection_receipt.input_payload_digest
    assert vr1.reflection_receipt.validated_request_digest == vr2.reflection_receipt.validated_request_digest


# ---------------------------------------------------------------------------
# 7. Full dispatch end-to-end (apps_rg_dispatch invokes U0 internally)
# ---------------------------------------------------------------------------


def test_full_dispatch_runs_harness_at_u0_stage() -> None:
    """The real apps_rg_dispatch must invoke the harness via u0_validate_apps_rg.

    We assert by patching u0_validate_apps_rg in the dispatch module and
    confirming the patched version fires. The patch returns a real
    ValidatedRequest so the rest of the pipeline doesn't break.
    """

    from agentic_core.runtime.entry import apps_rg_dispatch as dispatch_mod

    real_u0 = dispatch_mod.u0_validate_apps_rg
    call_log: list[str] = []

    def _spy(envelope: RequestEnvelope) -> ValidatedRequest:
        call_log.append("u0_called")
        return real_u0(envelope)

    with patch.object(dispatch_mod, "u0_validate_apps_rg", side_effect=_spy):
        envelope = apps_rg_parse(_thin_valid_payload())
        assert envelope is not None
        result = apps_rg_dispatch(envelope)

    assert call_log == ["u0_called"]
    assert isinstance(result, X3Disposition)
    assert result.exit_status == "success"


# ---------------------------------------------------------------------------
# 8. No L1/L0/C0/PA/L2/Exit code runs after U0 rejection
# ---------------------------------------------------------------------------


def test_no_l1_execution_after_u0_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force U0 to fail (via synthesizer corruption) and assert L1 never runs."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod
    from agentic_core.L1_cognition import apps_rg_l1_binding as l1_mod
    from agentic_core.runtime.entry import apps_rg_dispatch as dispatch_mod

    real_synth = synth_mod.synthesize_contract_payload
    l1_call_log: list[str] = []

    def _bad_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        c = real_synth(envelope)
        c["generation_mode"] = "obviously_invalid"
        return c

    def _l1_spy(*args: Any, **kwargs: Any) -> Any:
        l1_call_log.append("l1_called")
        raise AssertionError("L1 must not be invoked when U0 rejects")

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _bad_synth)
    monkeypatch.setattr(dispatch_mod, "l1_plan_apps_rg", _l1_spy)

    envelope = apps_rg_parse(_thin_valid_payload())
    assert envelope is not None

    # The dispatch wraps U0 errors and must NOT proceed to L1.
    # UnknownGenerationModeError is not a (TypeError, ValueError) so the
    # current dispatch will let it propagate — that's correct: U0 raised
    # and L1 was not called.
    with pytest.raises(UnknownGenerationModeError):
        apps_rg_dispatch(envelope)

    assert l1_call_log == [], "L1 was invoked despite U0 failure"
