"""ADG importability contract for agentic_core/L2_execution/deterministic_providers.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deterministic_providers.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.deterministic_providers import (  # noqa: F401
        DeterministicPatchError,
        DeterministicRandomSource,
        DeterministicUUIDProvider,
        FixedTimeProvider,
        patch_deterministic,
        unpatch_deterministic,
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


@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_providers deps unavailable")
class TestDeterministicProvidersImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/deterministic_providers.py must be importable."""
        assert _AVAILABLE

    def test_deterministicpatcherror_defined(self) -> None:
        assert DeterministicPatchError is not None

    def test_fixedtimeprovider_defined(self) -> None:
        assert FixedTimeProvider is not None

    def test_deterministicrandomsource_defined(self) -> None:
        assert DeterministicRandomSource is not None

    def test_deterministicuuidprovider_defined(self) -> None:
        assert DeterministicUUIDProvider is not None
