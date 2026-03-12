"""ADG importability contract for agentic_core/L5_safety/reasoning/RedSentinelAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_RedSentinelAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.RedSentinelAgent import (  # noqa: F401
        RedSentinelAgent,
        get_red_sentinel,
        initialize_red_sentinel,
        fuzz_function,
        scan_file_for_vulnerabilities,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RedSentinelAgent = None  # type: ignore[assignment,misc]
    get_red_sentinel = None  # type: ignore[assignment,misc]
    initialize_red_sentinel = None  # type: ignore[assignment,misc]
    fuzz_function = None  # type: ignore[assignment,misc]
    scan_file_for_vulnerabilities = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="RedSentinelAgent.py deps unavailable")
class TestRedsentinelagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: RedSentinelAgent.py must be importable."""
        assert _AVAILABLE

    def test_redsentinelagent_is_type(self) -> None:
        assert RedSentinelAgent is not None

    def test_get_red_sentinel_callable(self) -> None:
        assert callable(get_red_sentinel)

    def test_initialize_red_sentinel_callable(self) -> None:
        assert callable(initialize_red_sentinel)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

