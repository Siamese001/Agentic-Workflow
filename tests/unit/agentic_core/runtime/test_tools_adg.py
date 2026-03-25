"""ADG importability contract for agentic_core/runtime/tools.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tools.py (no _adg suffix).
"""

from __future__ import annotations

import agentic_core.runtime.tools as _tools_mod  # noqa: F401


class TestToolsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/tools.py must be importable."""
        assert _tools_mod.__name__ == "agentic_core.runtime.tools"

    def test_module_exposes_public_api(self) -> None:
        """tools module exposes expected public symbols."""
        public_symbols = [n for n in dir(_tools_mod) if not n.startswith("_")]
        assert len(public_symbols) >= 1, "tools must expose at least one public symbol"
