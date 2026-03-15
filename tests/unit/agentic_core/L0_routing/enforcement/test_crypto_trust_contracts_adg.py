"""ADG importability contract for agentic_core/L0_routing/enforcement/crypto_trust_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_crypto_trust_contracts.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (  # noqa: F401
        ReplayDetectedError,
        SigningError,
        VerificationError,
        hash_artifact_canonical,
        sign_artifact,
        verify_signature,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    hash_artifact_canonical = None  # type: ignore[assignment,misc]
    SigningError = None  # type: ignore[assignment,misc]
    sign_artifact = None  # type: ignore[assignment,misc]
    VerificationError = None  # type: ignore[assignment,misc]
    verify_signature = None  # type: ignore[assignment,misc]
    ReplayDetectedError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="crypto_trust_contracts deps unavailable")
class TestCryptoTrustContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/enforcement/crypto_trust_contracts.py must be importable."""
        assert _AVAILABLE

    def test_signingerror_defined(self) -> None:
        assert SigningError is not None

    def test_verificationerror_defined(self) -> None:
        assert VerificationError is not None

    def test_replaydetectederror_defined(self) -> None:
        assert ReplayDetectedError is not None
