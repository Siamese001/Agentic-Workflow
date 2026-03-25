"""ADG importability contract for agentic_core/adg/extraction/static_scanner.py."""
from __future__ import annotations

import agentic_core.adg.extraction.static_scanner  # noqa: F401


def test_module_importable():
    """Module static_scanner must be importable."""
    assert agentic_core.adg.extraction.static_scanner is not None
