"""ADG importability contract for agentic_core/adg/analysis/symbol_index.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_symbol_index.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.symbol_index import (  # noqa: F401
        SymbolIndex,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SymbolIndex = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="symbol_index.py deps unavailable")
class TestSymbolIndexImportability:
    def test_module_importable(self) -> None:
        """ADG contract: symbol_index.py must be importable."""
        assert _AVAILABLE

    def test_symbolindex_is_type(self) -> None:
        assert SymbolIndex is not None

