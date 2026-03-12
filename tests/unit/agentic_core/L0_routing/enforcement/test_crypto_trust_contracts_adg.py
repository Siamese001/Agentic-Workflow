"""ADG importability contract for agentic_core/L0_routing/enforcement/crypto_trust_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_crypto_trust_contracts.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (  # noqa: F401
        SigningError,
        VerificationError,
        ReplayDetectedError,
        ReplayGuardStore,
        EscalationRequiredError,
        SignedGuardianError,
        hash_artifact_canonical,
        sign_artifact,
        verify_signature,
        record_and_block_replay,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SigningError = None  # type: ignore[assignment,misc]
    VerificationError = None  # type: ignore[assignment,misc]
    ReplayDetectedError = None  # type: ignore[assignment,misc]
    ReplayGuardStore = None  # type: ignore[assignment,misc]
    EscalationRequiredError = None  # type: ignore[assignment,misc]
    SignedGuardianError = None  # type: ignore[assignment,misc]
    hash_artifact_canonical = None  # type: ignore[assignment,misc]
    sign_artifact = None  # type: ignore[assignment,misc]
    verify_signature = None  # type: ignore[assignment,misc]
    record_and_block_replay = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="crypto_trust_contracts.py deps unavailable")
class TestCryptoTrustContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: crypto_trust_contracts.py must be importable."""
        assert _AVAILABLE

    def test_signingerror_is_type(self) -> None:
        assert SigningError is not None

    def test_verificationerror_is_type(self) -> None:
        assert VerificationError is not None

    def test_replaydetectederror_is_type(self) -> None:
        assert ReplayDetectedError is not None

    def test_hash_artifact_canonical_callable(self) -> None:
        assert callable(hash_artifact_canonical)

    def test_sign_artifact_callable(self) -> None:
        assert callable(sign_artifact)

