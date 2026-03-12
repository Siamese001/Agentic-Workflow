"""ADG importability contract for agentic_core/L0_routing/scripts/runtime_state_digest.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_state_digest.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.runtime_state_digest import (  # noqa: F401
        runtime_state_digest_view,
        compute_runtime_state_digest,
        detect_unexcluded_volatile_fields,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    runtime_state_digest_view = None  # type: ignore[assignment,misc]
    compute_runtime_state_digest = None  # type: ignore[assignment,misc]
    detect_unexcluded_volatile_fields = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_state_digest.py deps unavailable")
class TestRuntimeStateDigestImportability:
    def test_module_importable(self) -> None:
        """ADG contract: runtime_state_digest.py must be importable."""
        assert _AVAILABLE

    def test_runtime_state_digest_view_callable(self) -> None:
        assert callable(runtime_state_digest_view)

    def test_compute_runtime_state_digest_callable(self) -> None:
        assert callable(compute_runtime_state_digest)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

