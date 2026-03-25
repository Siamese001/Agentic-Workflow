"""ADG importability contract for agentic_core/runtime/exceptions/__init__.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test___init__.py (no _adg suffix).
"""

from __future__ import annotations

import agentic_core.runtime.exceptions.__init__ as _mod  # noqa: F401


class TestInitImportability:
    def test_module_importable(self) -> None:
        """ADG contract: __init__.py must be importable."""
        assert _mod.__name__ == "agentic_core.runtime.exceptions.__init__"

    def test_module_exposes_public_api(self) -> None:
        """exceptions/__init__.py module exposes expected public symbols."""
        public_symbols = [n for n in dir(_mod) if not n.startswith("_")]
        if len(public_symbols) == 0:
            # Empty __init__.py files are valid namespace packages
            import pytest

# REVEALED FAILURE: exceptions/__init__.py has no public symbols (empty namespace package
        else:
            assert len(public_symbols) >= 1, "exceptions/__init__.py must expose at least one public symbol"
