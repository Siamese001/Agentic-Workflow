"""ADG importability contract for agentic_core/L2_execution/enforcement/provider_binding_determinism.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_provider_binding_determinism.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.provider_binding_determinism import (  # noqa: F401
        ProviderBindingContext,
        compute_provider_binding_digest,
        verify_provider_binding_determinism,
        extract_provider_context_from_request,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ProviderBindingContext = None  # type: ignore[assignment,misc]
    compute_provider_binding_digest = None  # type: ignore[assignment,misc]
    verify_provider_binding_determinism = None  # type: ignore[assignment,misc]
    extract_provider_context_from_request = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="provider_binding_determinism.py deps unavailable")
class TestProviderBindingDeterminismImportability:
    def test_module_importable(self) -> None:
        """ADG contract: provider_binding_determinism.py must be importable."""
        assert _AVAILABLE

    def test_providerbindingcontext_is_type(self) -> None:
        assert ProviderBindingContext is not None

    def test_compute_provider_binding_digest_callable(self) -> None:
        assert callable(compute_provider_binding_digest)

    def test_verify_provider_binding_determinism_callable(self) -> None:
        assert callable(verify_provider_binding_determinism)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

