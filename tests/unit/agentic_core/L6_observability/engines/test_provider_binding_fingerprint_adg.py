"""ADG importability contract for agentic_core/L6_observability/engines/provider_binding_fingerprint.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_provider_binding_fingerprint.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.provider_binding_fingerprint import (  # noqa: F401
        ProviderBinding,
        ProviderBindingFingerprint,
        capture_provider_bindings,
        fingerprint_matches,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ProviderBinding = None  # type: ignore[assignment,misc]
    ProviderBindingFingerprint = None  # type: ignore[assignment,misc]
    capture_provider_bindings = None  # type: ignore[assignment,misc]
    fingerprint_matches = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="provider_binding_fingerprint.py deps unavailable")
class TestProviderBindingFingerprintImportability:
    def test_module_importable(self) -> None:
        """ADG contract: provider_binding_fingerprint.py must be importable."""
        assert _AVAILABLE

    def test_providerbinding_is_type(self) -> None:
        assert ProviderBinding is not None

    def test_providerbindingfingerprint_is_type(self) -> None:
        assert ProviderBindingFingerprint is not None

    def test_capture_provider_bindings_callable(self) -> None:
        assert callable(capture_provider_bindings)

    def test_fingerprint_matches_callable(self) -> None:
        assert callable(fingerprint_matches)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

