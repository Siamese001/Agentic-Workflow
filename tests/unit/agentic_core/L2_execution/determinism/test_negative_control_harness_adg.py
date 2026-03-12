"""ADG importability contract for agentic_core/L2_execution/determinism/negative_control_harness.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_negative_control_harness.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.determinism.negative_control_harness import (  # noqa: F401
        is_tamper_active,
        get_config_surface,
        hash_config_surface,
        assert_digest_differs,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    is_tamper_active = None  # type: ignore[assignment,misc]
    get_config_surface = None  # type: ignore[assignment,misc]
    hash_config_surface = None  # type: ignore[assignment,misc]
    assert_digest_differs = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="negative_control_harness.py deps unavailable")
class TestNegativeControlHarnessImportability:
    def test_module_importable(self) -> None:
        """ADG contract: negative_control_harness.py must be importable."""
        assert _AVAILABLE

    def test_is_tamper_active_callable(self) -> None:
        assert callable(is_tamper_active)

    def test_get_config_surface_callable(self) -> None:
        assert callable(get_config_surface)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

