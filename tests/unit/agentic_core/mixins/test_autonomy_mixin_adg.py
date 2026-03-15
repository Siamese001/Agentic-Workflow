"""ADG importability contract for agentic_core/mixins/autonomy_mixin.py."""

from __future__ import annotations

import pytest

try:
    import agentic_core.mixins.autonomy_mixin as _autonomy_mixin_mod  # noqa: F401

    _AVAILABLE = True
except ImportError:
    _autonomy_mixin_mod = None  # type: ignore[assignment]
    _AVAILABLE = False


@pytest.mark.skipif(not _AVAILABLE, reason="autonomy_mixin deps unavailable")
def test_autonomy_mixin_importable() -> None:
    """ADG contract: agentic_core/mixins/autonomy_mixin.py must be importable."""
    assert _AVAILABLE
