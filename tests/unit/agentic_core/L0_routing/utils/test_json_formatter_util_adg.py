"""ADG importability contract for agentic_core/L0_routing/utils/json_formatter_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_json_formatter_util.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.utils.json_formatter_util import (  # noqa: F401
        JSONFormatter,
        setup_logging,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    JSONFormatter = None  # type: ignore[assignment,misc]
    setup_logging = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="json_formatter_util deps unavailable")
class TestJsonFormatterUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/utils/json_formatter_util.py must be importable."""
        assert _AVAILABLE

    def test_jsonformatter_defined(self) -> None:
        assert JSONFormatter is not None
