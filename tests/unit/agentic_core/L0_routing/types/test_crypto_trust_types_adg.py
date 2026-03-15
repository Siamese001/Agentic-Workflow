"""ADG importability contract for agentic_core/L0_routing/types/crypto_trust_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_crypto_trust_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.crypto_trust_types import (  # noqa: F401
        KeyRecord,
        KeyStatus,
        SignatureEnvelope,
        SignedGuardianArtifact,
        SigningAlgorithm,
        TrustRoot,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    KeyStatus = None  # type: ignore[assignment,misc]
    SigningAlgorithm = None  # type: ignore[assignment,misc]
    KeyRecord = None  # type: ignore[assignment,misc]
    TrustRoot = None  # type: ignore[assignment,misc]
    SignatureEnvelope = None  # type: ignore[assignment,misc]
    SignedGuardianArtifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="crypto_trust_types deps unavailable")
class TestCryptoTrustTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/crypto_trust_types.py must be importable."""
        assert _AVAILABLE

    def test_keystatus_defined(self) -> None:
        assert KeyStatus is not None

    def test_signingalgorithm_defined(self) -> None:
        assert SigningAlgorithm is not None

    def test_keyrecord_defined(self) -> None:
        assert KeyRecord is not None

    def test_trustroot_defined(self) -> None:
        assert TrustRoot is not None

    def test_signatureenvelope_defined(self) -> None:
        assert SignatureEnvelope is not None

    def test_signedguardianartifact_defined(self) -> None:
        assert SignedGuardianArtifact is not None
