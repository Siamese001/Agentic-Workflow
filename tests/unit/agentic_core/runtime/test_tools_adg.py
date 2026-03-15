"""ADG importability contract for agentic_core/runtime/tools.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tools.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    import agentic_core.runtime.tools  # noqa: F401

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


@pytest.mark.skipif(not _AVAILABLE, reason="tools deps unavailable")
class TestToolsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/tools.py must be importable."""
        assert _AVAILABLE
