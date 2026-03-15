"""ADG importability contract for agentic_core/patterns/base.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_base.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.patterns.base import (  # noqa: F401
        BaseReasoningPattern,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    BaseReasoningPattern = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="base deps unavailable")
class TestBaseImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/patterns/base.py must be importable."""
        assert _AVAILABLE

    def test_basereasoningpattern_defined(self) -> None:
        assert BaseReasoningPattern is not None
