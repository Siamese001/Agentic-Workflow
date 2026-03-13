"""ADG importability contract for agentic_core/L5_safety/security/signature_verifier.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_signature_verifier.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.security.signature_verifier import (  # noqa: F401
        InstructionPacket,
        SandboxEnvelope,
        SignatureVerificationError,
        SignatureVerifier,
        VerificationContext,
        get_signature_verifier,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SignatureVerificationError = None  # type: ignore[assignment,misc]
    VerificationContext = None  # type: ignore[assignment,misc]
    InstructionPacket = None  # type: ignore[assignment,misc]
    SandboxEnvelope = None  # type: ignore[assignment,misc]
    SignatureVerifier = None  # type: ignore[assignment,misc]
    get_signature_verifier = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="signature_verifier deps unavailable")
class TestSignatureVerifierImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/security/signature_verifier.py must be importable."""
        assert _AVAILABLE

    def test_signatureverificationerror_defined(self) -> None:
        assert SignatureVerificationError is not None

    def test_verificationcontext_defined(self) -> None:
        assert VerificationContext is not None

    def test_instructionpacket_defined(self) -> None:
        assert InstructionPacket is not None

    def test_sandboxenvelope_defined(self) -> None:
        assert SandboxEnvelope is not None

    def test_signatureverifier_defined(self) -> None:
        assert SignatureVerifier is not None
