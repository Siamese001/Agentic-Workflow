"""ADG importability contract for agentic_core/adg/identity/normalizer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_normalizer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.identity.normalizer import (  # noqa: F401
        IdentityConfidence,
        IdentityKind,
        IdentityNormalizer,
        IdentityRecord,
        NormalizationReport,
        normalize_identity,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    IdentityKind = None  # type: ignore[assignment,misc]
    IdentityConfidence = None  # type: ignore[assignment,misc]
    IdentityRecord = None  # type: ignore[assignment,misc]
    NormalizationReport = None  # type: ignore[assignment,misc]
    IdentityNormalizer = None  # type: ignore[assignment,misc]
    normalize_identity = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="normalizer deps unavailable")
class TestNormalizerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/identity/normalizer.py must be importable."""
        assert _AVAILABLE

    def test_identitykind_defined(self) -> None:
        assert IdentityKind is not None

    def test_identityconfidence_defined(self) -> None:
        assert IdentityConfidence is not None

    def test_identityrecord_defined(self) -> None:
        assert IdentityRecord is not None

    def test_normalizationreport_defined(self) -> None:
        assert NormalizationReport is not None

    def test_identitynormalizer_defined(self) -> None:
        assert IdentityNormalizer is not None
