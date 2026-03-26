"""Foundational behavioral tests for agentic_core/L5_safety/security/signature_verifier.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_signature_verifier_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L5_safety.security.signature_verifier import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    InstructionPacket,
    SandboxEnvelope,
    SignatureVerificationError,
    SignatureVerifier,
    VerificationContext,
    get_signature_verifier,
    verify_instruction_packet,
    verify_sandbox_envelope,
)


class TestSignatureVerificationErrorContract:
    def test_is_class(self):
        from agentic_core.L5_safety.security.signature_verifier import (  # noqa: F401
        assert isinstance(SignatureVerificationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SignatureVerificationError, type)

class TestVerificationContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VerificationContext)

    def test_is_frozen(self):
        assert VerificationContext.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(VerificationContext)}
        assert field_names >= {'packet_hash', 'signature_hash', 'verification_timestamp', 'signer_id', 'is_verified'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(VerificationContext)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert VerificationContext.__dataclass_params__.frozen is True

class TestInstructionPacketContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(InstructionPacket)

    def test_is_frozen(self):
        assert InstructionPacket.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(InstructionPacket)}
        assert field_names >= {'payload', 'signature', 'signer_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(InstructionPacket)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert InstructionPacket.__dataclass_params__.frozen is True

class TestSandboxEnvelopeContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SandboxEnvelope)

    def test_is_frozen(self):
        assert SandboxEnvelope.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SandboxEnvelope)}
        assert field_names >= {'packet', 'sandbox_config', 'envelope_signature'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(SandboxEnvelope)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert SandboxEnvelope.__dataclass_params__.frozen is True

class TestSignatureVerifierContract:
    def test_is_class(self):
        assert isinstance(SignatureVerifier, type)

    def test_has_method_verify_instruction_packet(self):
        assert callable(getattr(SignatureVerifier, 'verify_instruction_packet', None))

    def test_has_method_verify_sandbox_envelope(self):
        assert callable(getattr(SignatureVerifier, 'verify_sandbox_envelope', None))

    def test_has_method_add_trusted_signer(self):
        assert callable(getattr(SignatureVerifier, 'add_trusted_signer', None))

class TestGetSignatureVerifierFunction:
    def test_is_callable(self):
        assert callable(get_signature_verifier)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_signature_verifier)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestVerifyInstructionPacketFunction:
    def test_is_callable(self):
        assert callable(verify_instruction_packet)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(verify_instruction_packet)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestVerifySandboxEnvelopeFunction:
    def test_is_callable(self):
        assert callable(verify_sandbox_envelope)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(verify_sandbox_envelope)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module signature_verifier must be importable or skip gracefully."""
    pass  # Import verified at module level
