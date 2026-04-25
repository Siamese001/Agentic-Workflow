"""Unit tests for agentic_core.L2_execution.reasoning.compiled_artifact.

Targets Wave-4 / Phase P12. Source: 480 lines, fan_in=58 (L2, impact 58.0).
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import date

import pytest

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
    InjectionScanResult,
    PromptBOM,
    RoutingDecision,
    TemplateManifest,
    _shim_active,
    classify_artifact_dict,
    get_v1_verification_count,
    reset_v1_verification_count,
)


SECRET = b"test-secret-key-32-bytes-padding!"


from collections.abc import Iterator


@pytest.fixture(autouse=True)
def _reset_shim() -> Iterator[None]:
    reset_v1_verification_count()
    yield
    reset_v1_verification_count()


class TestAuthorityLevel:
    def test_from_slot_code_maps_all(self) -> None:
        assert AuthorityLevel.from_slot_code("S0") == AuthorityLevel.ABSOLUTE
        assert AuthorityLevel.from_slot_code("I0") == AuthorityLevel.GOVERNED
        assert AuthorityLevel.from_slot_code("D0") == AuthorityLevel.BINDING
        assert AuthorityLevel.from_slot_code("C0") == AuthorityLevel.INFO
        assert AuthorityLevel.from_slot_code("E0") == AuthorityLevel.EXEMPLAR
        assert AuthorityLevel.from_slot_code("M0") == AuthorityLevel.META_COGNITIVE
        assert AuthorityLevel.from_slot_code("H0") == AuthorityLevel.HEALING
        assert AuthorityLevel.from_slot_code("Y0") == AuthorityLevel.META_LEARNING
        assert AuthorityLevel.from_slot_code("R0") == AuthorityLevel.SCHEMA
        assert AuthorityLevel.from_slot_code("U0") == AuthorityLevel.ZERO

    def test_from_slot_code_case_insensitive(self) -> None:
        assert AuthorityLevel.from_slot_code("s0") == AuthorityLevel.ABSOLUTE

    def test_unknown_code_defaults_zero(self) -> None:
        assert AuthorityLevel.from_slot_code("XX") == AuthorityLevel.ZERO


class TestAuthoritySlot:
    def test_valid_slot_roundtrip(self) -> None:
        s = AuthoritySlot(
            slot_type="S0",
            content="constitution",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L5",
        )
        assert s.slot_code == "S0"
        assert s.content == "constitution"

    def test_mismatched_authority_level_raises(self) -> None:
        with pytest.raises(ValueError, match="does not match"):
            AuthoritySlot(
                slot_type="S0",
                content="x",
                authority_level=AuthorityLevel.ZERO,
                source_layer="L5",
            )

    def test_c0_slot_rejects_forbidden_metadata(self) -> None:
        with pytest.raises(ValueError, match="cannot carry"):
            AuthoritySlot(
                slot_type="C0",
                content="",
                authority_level=AuthorityLevel.INFO,
                source_layer="L4",
                metadata={"route_mode": "direct"},
            )

    def test_u0_rejects_auth_token(self) -> None:
        with pytest.raises(ValueError, match="auth_token"):
            AuthoritySlot(
                slot_type="U0",
                content="intent",
                authority_level=AuthorityLevel.ZERO,
                source_layer="L0",
                metadata={"auth_token": "secret"},
            )

    def test_s0_allows_arbitrary_metadata(self) -> None:
        # S0 isn't in the forbidden set — any metadata OK
        s = AuthoritySlot(
            slot_type="S0",
            content="",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L5",
            metadata={"route_mode": "safe", "auth_token": "x"},
        )
        assert s.metadata["auth_token"] == "x"

    def test_y0_rejects_forbidden_metadata(self) -> None:
        with pytest.raises(ValueError, match="cannot carry"):
            AuthoritySlot(
                slot_type="Y0",
                content="telemetry",
                authority_level=AuthorityLevel.META_LEARNING,
                source_layer="L4",
                metadata={"execution_tier": "T3"},
            )

    def test_r0_rejects_forbidden_metadata(self) -> None:
        with pytest.raises(ValueError, match="cannot carry"):
            AuthoritySlot(
                slot_type="R0",
                content="json schema",
                authority_level=AuthorityLevel.SCHEMA,
                source_layer="L_PG",
                metadata={"safety_threshold": 0.5},
            )

    def test_r0_slot_roundtrip(self) -> None:
        s = AuthoritySlot(
            slot_type="R0",
            content="json: {answer: str}",
            authority_level=AuthorityLevel.SCHEMA,
            source_layer="L_PG",
        )
        assert s.slot_code == "R0"
        assert s.authority_level is AuthorityLevel.SCHEMA

    def test_y0_slot_roundtrip(self) -> None:
        s = AuthoritySlot(
            slot_type="Y0",
            content="pattern summary",
            authority_level=AuthorityLevel.META_LEARNING,
            source_layer="L4",
        )
        assert s.slot_code == "Y0"
        assert s.authority_level is AuthorityLevel.META_LEARNING

    def test_frozen(self) -> None:
        s = AuthoritySlot(slot_type="U0", content="", authority_level=AuthorityLevel.ZERO, source_layer="L0")
        with pytest.raises(AttributeError):
            s.content = "changed"  # type: ignore[misc]


def _mint_v2_artifact(secret: bytes = SECRET) -> CompiledPromptArtifact:
    """Build an artifact with a valid v2 signature."""
    from datetime import datetime, timezone

    _utc = timezone.utc
    artifact = CompiledPromptArtifact(
        trace_id="t-123",
        system_version_hash="sysv1",
        final_system_string="SYSTEM",
        final_user_string="USER",
        allowed_tools_schema=[{"name": "x"}],
        tokens=100,
        slots_used=["S0", "U0"],
        signature="",  # placeholder
        timestamp=datetime.now(_utc).isoformat(),
    )
    # Compute and embed real signature
    sig = artifact._compute_signature(secret)
    return CompiledPromptArtifact(
        trace_id=artifact.trace_id,
        system_version_hash=artifact.system_version_hash,
        final_system_string=artifact.final_system_string,
        final_user_string=artifact.final_user_string,
        allowed_tools_schema=artifact.allowed_tools_schema,
        tokens=artifact.tokens,
        slots_used=artifact.slots_used,
        signature=sig,
        timestamp=artifact.timestamp,
        idempotency_nonce=artifact.idempotency_nonce,
    )


class TestCompiledPromptArtifactValidation:
    def test_empty_trace_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="trace_id must not be empty"):
            CompiledPromptArtifact(
                trace_id="",
                system_version_hash="h",
                final_system_string="s",
                final_user_string="u",
                allowed_tools_schema=[],
                tokens=0,
                slots_used=[],
                signature="sig",
            )

    def test_negative_tokens_rejected(self) -> None:
        with pytest.raises(ValueError, match="tokens must be >= 0"):
            CompiledPromptArtifact(
                trace_id="t",
                system_version_hash="h",
                final_system_string="s",
                final_user_string="u",
                allowed_tools_schema=[],
                tokens=-1,
                slots_used=[],
                signature="sig",
            )

    def test_default_schema_version_is_2(self) -> None:
        a = _mint_v2_artifact()
        assert a.schema_version == 2

    def test_idempotency_nonce_defaults_to_uuid(self) -> None:
        a = _mint_v2_artifact()
        assert len(a.idempotency_nonce) == 32  # uuid4 hex
        # Two artifacts have different nonces
        b = _mint_v2_artifact()
        assert a.idempotency_nonce != b.idempotency_nonce


class TestManifestHash:
    def test_manifest_hash_stable(self) -> None:
        a1 = _mint_v2_artifact()
        # Manufacture a second artifact with same logical content but different nonce
        a2 = CompiledPromptArtifact(
            trace_id=a1.trace_id,
            system_version_hash=a1.system_version_hash,
            final_system_string=a1.final_system_string,
            final_user_string=a1.final_user_string,
            allowed_tools_schema=a1.allowed_tools_schema,
            tokens=a1.tokens,
            slots_used=a1.slots_used,
            signature="ignored",
            timestamp=a1.timestamp,
        )
        # Different nonces but identical logical content → same manifest_hash
        assert a1.idempotency_nonce != a2.idempotency_nonce
        assert a1.manifest_hash == a2.manifest_hash

    def test_manifest_hash_order_invariant_for_slots_used(self) -> None:
        a = _mint_v2_artifact()
        b = CompiledPromptArtifact(
            trace_id=a.trace_id,
            system_version_hash=a.system_version_hash,
            final_system_string=a.final_system_string,
            final_user_string=a.final_user_string,
            allowed_tools_schema=a.allowed_tools_schema,
            tokens=a.tokens,
            slots_used=list(reversed(a.slots_used)),
            signature="x",
            timestamp=a.timestamp,
        )
        assert a.manifest_hash == b.manifest_hash


class TestVerifySignature:
    def test_v2_signature_verifies(self) -> None:
        a = _mint_v2_artifact()
        assert a.verify_signature(SECRET) is True

    def test_v2_wrong_secret_fails(self) -> None:
        a = _mint_v2_artifact()
        assert a.verify_signature(b"wrong-secret-key") is False

    def test_forged_signature_fails(self) -> None:
        a = _mint_v2_artifact()
        forged = CompiledPromptArtifact(
            trace_id=a.trace_id,
            system_version_hash=a.system_version_hash,
            final_system_string=a.final_system_string,
            final_user_string=a.final_user_string,
            allowed_tools_schema=a.allowed_tools_schema,
            tokens=a.tokens,
            slots_used=a.slots_used,
            signature="a" * 64,  # wrong
            timestamp=a.timestamp,
            idempotency_nonce=a.idempotency_nonce,
        )
        assert forged.verify_signature(SECRET) is False


class TestShimActiveAndTelemetry:
    def test_shim_active_before_sunset(self) -> None:
        # Date in the past — shim should be active
        assert _shim_active(today=date(2026, 1, 1)) is True

    def test_shim_inactive_after_sunset(self) -> None:
        assert _shim_active(today=date(2026, 7, 24)) is False

    def test_override_env_keeps_shim_active(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("EQ6_SHIM_FORCE_ACTIVE", "1")
        assert _shim_active(today=date(2030, 1, 1)) is True

    def test_v1_count_starts_zero(self) -> None:
        assert get_v1_verification_count() == 0

    def test_reset_helper_clears_counter(self) -> None:
        # Internal mutation — just ensure reset restores 0
        import agentic_core.L2_execution.reasoning.compiled_artifact as mod

        mod._v1_verifications = 5
        reset_v1_verification_count()
        assert get_v1_verification_count() == 0


class TestClassifyArtifactDict:
    def test_schema_version_2_returned(self) -> None:
        assert classify_artifact_dict({"schema_version": 2}) == 2

    def test_schema_version_higher_returned_as_2(self) -> None:
        assert classify_artifact_dict({"schema_version": 5}) == 2

    def test_nonce_implies_v2(self) -> None:
        assert classify_artifact_dict({"idempotency_nonce": "abc"}) == 2

    def test_default_is_v1(self) -> None:
        assert classify_artifact_dict({}) == 1

    def test_empty_nonce_is_v1(self) -> None:
        assert classify_artifact_dict({"idempotency_nonce": ""}) == 1

    def test_string_schema_version_ignored(self) -> None:
        # Only int schema_version >= 2 triggers v2
        assert classify_artifact_dict({"schema_version": "2"}) == 1


class TestSerialization:
    def test_to_dict_contains_all_fields(self) -> None:
        a = _mint_v2_artifact()
        d = a.to_dict()
        assert d["trace_id"] == "t-123"
        assert d["tokens"] == 100
        assert "signature" in d

    def test_from_dict_roundtrip(self) -> None:
        a = _mint_v2_artifact()
        d = a.to_dict()
        restored = CompiledPromptArtifact.from_dict(d)
        assert restored.trace_id == a.trace_id
        assert restored.signature == a.signature

    def test_from_dict_ignores_extra_keys(self) -> None:
        a = _mint_v2_artifact()
        d = a.to_dict()
        d["future_field"] = "ignored"
        restored = CompiledPromptArtifact.from_dict(d)
        assert restored.trace_id == a.trace_id


class TestAncillaryDataclasses:
    def test_prompt_bom_roundtrip(self) -> None:
        bom = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=["m1"],
            raw_u0="u",
            raw_c0="c",
            template_args={"k": "v"},
        )
        d = bom.to_dict()
        assert d["trace_id"] == "t"

    def test_template_manifest_validate(self) -> None:
        m = TemplateManifest(
            template_id="T1",
            version="1",
            git_commit_hash="abc",
            required_variables=["a", "b"],
        )
        missing = m.validate({"a": 1})
        assert missing == ["b"]
        assert m.validate({"a": 1, "b": 2}) == []

    def test_routing_decision_fields(self) -> None:
        r = RoutingDecision(path="A", risk="H", rationale="why", confidence=0.9)
        assert r.path == "A"
        assert r.confidence == 0.9

    def test_injection_scan_result_fields(self) -> None:
        r = InjectionScanResult(detected=True, override_attempts=["x"], risk_score=0.5, blocked=True)
        assert r.detected is True
        assert r.blocked is True


# ---------------------------------------------------------------------------
# Property-based tests (hypothesis) — HMAC signing invariants
# ---------------------------------------------------------------------------

from hypothesis import given, strategies as st


_secret_strat = st.binary(min_size=16, max_size=64)
_nonempty_text = st.text(min_size=1, max_size=40)


class TestHMACSigningProperties:
    """The v2 signature scheme must satisfy standard HMAC invariants."""

    @given(secret=_secret_strat, trace_id=_nonempty_text, tokens=st.integers(0, 10000))
    def test_verify_roundtrip(self, secret: bytes, trace_id: str, tokens: int) -> None:
        # Build an artifact with a freshly-computed v2 signature; it must verify.
        from datetime import datetime, timezone

        stub = CompiledPromptArtifact(
            trace_id=trace_id,
            system_version_hash="h",
            final_system_string="sys",
            final_user_string="usr",
            allowed_tools_schema=[],
            tokens=tokens,
            slots_used=["S0"],
            signature="placeholder",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        sig = stub._compute_signature(secret)
        signed = CompiledPromptArtifact(
            trace_id=stub.trace_id,
            system_version_hash=stub.system_version_hash,
            final_system_string=stub.final_system_string,
            final_user_string=stub.final_user_string,
            allowed_tools_schema=stub.allowed_tools_schema,
            tokens=stub.tokens,
            slots_used=stub.slots_used,
            signature=sig,
            timestamp=stub.timestamp,
            idempotency_nonce=stub.idempotency_nonce,
        )
        assert signed.verify_signature(secret) is True

    @given(
        secret_a=_secret_strat,
        secret_b=_secret_strat,
        trace_id=_nonempty_text,
    )
    def test_wrong_secret_never_verifies(self, secret_a: bytes, secret_b: bytes, trace_id: str) -> None:
        # If secrets differ, signature must not verify.
        if secret_a == secret_b:
            return  # trivially equal — skip this iteration
        a = _mint_v2_artifact(secret_a)
        # re-build with the same artifact but verifying with wrong secret
        assert a.verify_signature(secret_b) is False

    @given(secret=_secret_strat)
    def test_manifest_hash_excludes_nonce(self, secret: bytes) -> None:
        # EQ-1 invariant: two artifacts with identical logical content but
        # different nonces share the same manifest_hash.
        a = _mint_v2_artifact(secret)
        import uuid as _uuid

        b = CompiledPromptArtifact(
            trace_id=a.trace_id,
            system_version_hash=a.system_version_hash,
            final_system_string=a.final_system_string,
            final_user_string=a.final_user_string,
            allowed_tools_schema=a.allowed_tools_schema,
            tokens=a.tokens,
            slots_used=a.slots_used,
            signature="ignored",
            timestamp=a.timestamp,
            idempotency_nonce=_uuid.uuid4().hex,  # different nonce
        )
        assert a.idempotency_nonce != b.idempotency_nonce
        assert a.manifest_hash == b.manifest_hash

    @given(
        secret=_secret_strat,
        slots=st.lists(
            st.sampled_from(["S0", "I0", "D0", "C0", "U0"]),
            min_size=1,
            max_size=5,
            unique=True,
        ),
    )
    def test_manifest_hash_invariant_under_slots_used_order(self, secret: bytes, slots: list[str]) -> None:
        # EQ-9: manifest_hash must be invariant under slots_used permutation.
        import random

        shuffled = list(slots)
        random.Random(0).shuffle(shuffled)
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
        a = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=0,
            slots_used=slots,
            signature="x",
            timestamp=ts,
        )
        b = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=0,
            slots_used=shuffled,
            signature="x",
            timestamp=ts,
        )
        assert a.manifest_hash == b.manifest_hash

    @given(
        secret=_secret_strat,
        tamper_field=st.sampled_from(["final_system_string", "final_user_string", "system_version_hash"]),
        new_value=_nonempty_text,
    )
    def test_tampering_breaks_signature(self, secret: bytes, tamper_field: str, new_value: str) -> None:
        # Modify any signed field → signature must no longer verify.
        a = _mint_v2_artifact(secret)
        kwargs = dict(
            trace_id=a.trace_id,
            system_version_hash=a.system_version_hash,
            final_system_string=a.final_system_string,
            final_user_string=a.final_user_string,
            allowed_tools_schema=a.allowed_tools_schema,
            tokens=a.tokens,
            slots_used=a.slots_used,
            signature=a.signature,
            timestamp=a.timestamp,
            idempotency_nonce=a.idempotency_nonce,
        )
        if kwargs[tamper_field] == new_value:
            return  # coincidentally equal — skip
        kwargs[tamper_field] = new_value
        tampered = CompiledPromptArtifact(**kwargs)  # type: ignore[arg-type]
        assert tampered.verify_signature(secret) is False
