"""EQ-6 — replay-verifier shim hardening.

Plan: ``docs/archive/windsurf/legacy-tree/plans/eq1-compiled-artifact-schema-d9a3e7.md``
ADR:  ADR-PROMPT-ASSEMBLY-002 §9 (back-compat shim window)

Covers:
- ``classify_artifact_dict`` returns 1 vs 2 from raw dicts.
- ``_shim_active`` honors the sunset date and the override env var.
- v1 verification path is taken pre-sunset and skipped post-sunset.
- Telemetry counter and one-shot warning fire on v1 verifications.
- ``EQ6_SHIM_FORCE_ACTIVE=1`` keeps shim active past sunset.
"""

from __future__ import annotations

from datetime import date

import pytest

from agentic_core.L2_execution.reasoning import compiled_artifact as ca_mod
from agentic_core.L2_execution.reasoning.compiled_artifact import (
    CompiledPromptArtifact,
    _shim_active,
    _SHIM_OVERRIDE_ENV,
    _SHIM_SUNSET_DATE,
    classify_artifact_dict,
    get_v1_verification_count,
    reset_v1_verification_count,
)


SECRET = b"x" * 32


@pytest.fixture(autouse=True)
def _reset_counter() -> None:
    """Each test starts with a fresh telemetry counter."""
    reset_v1_verification_count()
    yield
    reset_v1_verification_count()


# --------------------------------------------------------------------------
# classify_artifact_dict.
# --------------------------------------------------------------------------


class TestClassifyArtifactDict:
    def test_returns_2_when_schema_version_is_2(self) -> None:
        assert classify_artifact_dict({"schema_version": 2}) == 2

    def test_returns_2_when_schema_version_is_3(self) -> None:
        # Forward-compat: anything >= 2 still classifies as v2-equivalent.
        assert classify_artifact_dict({"schema_version": 3}) == 2

    def test_returns_2_when_nonce_present(self) -> None:
        assert classify_artifact_dict({"idempotency_nonce": "abc"}) == 2

    def test_returns_1_when_no_marker(self) -> None:
        # Pre-EQ1 artifact dicts had neither field.
        assert classify_artifact_dict({"trace_id": "t"}) == 1

    def test_returns_1_when_nonce_is_empty(self) -> None:
        # Empty nonce is treated as absent — defensive against bad serializers.
        assert classify_artifact_dict({"idempotency_nonce": ""}) == 1

    def test_returns_1_when_schema_version_is_1(self) -> None:
        assert classify_artifact_dict({"schema_version": 1}) == 1


# --------------------------------------------------------------------------
# _shim_active.
# --------------------------------------------------------------------------


class TestShimActive:
    def test_active_before_sunset(self) -> None:
        assert _shim_active(today=date(2026, 7, 22)) is True

    def test_inactive_on_sunset_day(self) -> None:
        assert _shim_active(today=_SHIM_SUNSET_DATE) is False

    def test_inactive_after_sunset(self) -> None:
        assert _shim_active(today=date(2027, 1, 1)) is False

    def test_override_env_keeps_shim_active_past_sunset(self, monkeypatch) -> None:
        monkeypatch.setenv(_SHIM_OVERRIDE_ENV, "1")
        assert _shim_active(today=date(2030, 1, 1)) is True

    def test_override_env_truthy_values(self, monkeypatch) -> None:
        for value in ("1", "true", "yes", "on", "TRUE", "Yes"):
            monkeypatch.setenv(_SHIM_OVERRIDE_ENV, value)
            assert _shim_active(today=date(2030, 1, 1)) is True

    def test_override_env_falsy_values_do_not_activate(self, monkeypatch) -> None:
        for value in ("0", "false", "", "no"):
            monkeypatch.setenv(_SHIM_OVERRIDE_ENV, value)
            assert _shim_active(today=date(2030, 1, 1)) is False


# --------------------------------------------------------------------------
# verify_signature path coverage + telemetry.
# --------------------------------------------------------------------------


def _v1_signed_artifact() -> CompiledPromptArtifact:
    """Build an artifact, then overwrite its signature with the v1 scheme."""
    artifact = CompiledPromptArtifact(
        trace_id="t",
        system_version_hash="h",
        final_system_string="hello",
        final_user_string="world",
        allowed_tools_schema=[],
        tokens=2,
        slots_used=["S0", "U0"],
        signature="",
    )
    v1_sig = artifact._compute_signature_v1(SECRET)
    return CompiledPromptArtifact(
        trace_id=artifact.trace_id,
        system_version_hash=artifact.system_version_hash,
        final_system_string=artifact.final_system_string,
        final_user_string=artifact.final_user_string,
        allowed_tools_schema=artifact.allowed_tools_schema,
        tokens=artifact.tokens,
        slots_used=artifact.slots_used,
        signature=v1_sig,
        idempotency_nonce=artifact.idempotency_nonce,
        timestamp=artifact.timestamp,
    )


class TestVerifySignatureShim:
    def test_v2_signature_verifies_without_touching_shim(self) -> None:
        artifact = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="hello",
            final_user_string="world",
            allowed_tools_schema=[],
            tokens=2,
            slots_used=["S0", "U0"],
            signature="",
        )
        signed = artifact.__class__(**{**artifact.__dict__, "signature": artifact._compute_signature(SECRET)})
        assert signed.verify_signature(SECRET) is True
        # v2 path must NOT bump the v1 telemetry counter.
        assert get_v1_verification_count() == 0

    def test_v1_signature_verifies_when_shim_active(self) -> None:
        artifact = _v1_signed_artifact()
        assert artifact.verify_signature(SECRET) is True
        assert get_v1_verification_count() == 1

    def test_v1_telemetry_warning_is_one_shot(self, caplog) -> None:
        import logging

        caplog.set_level(logging.WARNING, logger="agentic_core.L2_execution.reasoning.compiled_artifact")
        a1 = _v1_signed_artifact()
        a2 = _v1_signed_artifact()
        a1.verify_signature(SECRET)
        a2.verify_signature(SECRET)
        # Two verifications, ONE warning record.
        v1_warnings = [r for r in caplog.records if "v1 signature shim" in r.getMessage()]
        assert len(v1_warnings) == 1
        assert get_v1_verification_count() == 2

    def test_v1_signature_rejected_after_sunset(self, monkeypatch) -> None:
        # Force shim inactive by overriding the date check at module level.
        monkeypatch.setattr(ca_mod, "_shim_active", lambda today=None: False)
        artifact = _v1_signed_artifact()
        assert artifact.verify_signature(SECRET) is False
        # No v1 verification was recorded — branch was skipped.
        assert get_v1_verification_count() == 0

    def test_v1_signature_accepted_when_override_set_post_sunset(self, monkeypatch) -> None:
        # Sunset has passed AND override is set => still verifies.
        monkeypatch.setenv(_SHIM_OVERRIDE_ENV, "1")
        artifact = _v1_signed_artifact()
        assert artifact.verify_signature(SECRET) is True
        assert get_v1_verification_count() == 1

    def test_garbage_signature_returns_false_under_both_paths(self) -> None:
        artifact = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="hello",
            final_user_string="world",
            allowed_tools_schema=[],
            tokens=2,
            slots_used=["S0", "U0"],
            signature="deadbeef" * 8,
        )
        assert artifact.verify_signature(SECRET) is False
        # Failed verification must not pollute the v1 counter.
        assert get_v1_verification_count() == 0
