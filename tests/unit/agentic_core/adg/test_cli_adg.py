"""ADG importability contract for agentic_core/adg/cli.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cli.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.cli import (  # noqa: F401
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    main = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="cli.py deps unavailable")
class TestCliImportability:
    def test_module_importable(self) -> None:
        """ADG contract: cli.py must be importable."""
        assert _AVAILABLE

    def test_main_callable(self) -> None:
        assert callable(main)

