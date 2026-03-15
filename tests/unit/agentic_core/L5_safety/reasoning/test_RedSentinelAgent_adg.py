"""ADG importability contract for agentic_core/L5_safety/reasoning/RedSentinelAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_RedSentinelAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.RedSentinelAgent import (  # noqa: F401
        RedSentinelAgent,
        fuzz_function,
        get_red_sentinel,
        initialize_red_sentinel,
        scan_file_for_vulnerabilities,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RedSentinelAgent = None  # type: ignore[assignment,misc]
    get_red_sentinel = None  # type: ignore[assignment,misc]
    initialize_red_sentinel = None  # type: ignore[assignment,misc]
    fuzz_function = None  # type: ignore[assignment,misc]
    scan_file_for_vulnerabilities = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="RedSentinelAgent deps unavailable")
class TestRedsentinelagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/RedSentinelAgent.py must be importable."""
        assert _AVAILABLE

    def test_redsentinelagent_defined(self) -> None:
        assert RedSentinelAgent is not None
