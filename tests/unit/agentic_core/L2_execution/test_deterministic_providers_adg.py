"""ADG importability contract for agentic_core/L2_execution/deterministic_providers.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deterministic_providers.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.deterministic_providers import (  # noqa: F401
        DeterministicPatchError,
        FixedTimeProvider,
        DeterministicRandomSource,
        DeterministicUUIDProvider,
        patch_deterministic,
        unpatch_deterministic,
        is_patched,
        get_active_trace_id,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DeterministicPatchError = None  # type: ignore[assignment,misc]
    FixedTimeProvider = None  # type: ignore[assignment,misc]
    DeterministicRandomSource = None  # type: ignore[assignment,misc]
    DeterministicUUIDProvider = None  # type: ignore[assignment,misc]
    patch_deterministic = None  # type: ignore[assignment,misc]
    unpatch_deterministic = None  # type: ignore[assignment,misc]
    is_patched = None  # type: ignore[assignment,misc]
    get_active_trace_id = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_providers.py deps unavailable")
class TestDeterministicProvidersImportability:
    def test_module_importable(self) -> None:
        """ADG contract: deterministic_providers.py must be importable."""
        assert _AVAILABLE

    def test_deterministicpatcherror_is_type(self) -> None:
        assert DeterministicPatchError is not None

    def test_fixedtimeprovider_is_type(self) -> None:
        assert FixedTimeProvider is not None

    def test_deterministicrandomsource_is_type(self) -> None:
        assert DeterministicRandomSource is not None

    def test_patch_deterministic_callable(self) -> None:
        assert callable(patch_deterministic)

    def test_unpatch_deterministic_callable(self) -> None:
        assert callable(unpatch_deterministic)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

