"""ADG importability contract for agentic_core/mixins/autonomy_mixin.py."""

from __future__ import annotations

import agentic_core.mixins.autonomy_mixin as _autonomy_mixin_mod  # noqa: F401


def test_module_importable():
    """Module must be importable."""
    assert _autonomy_mixin_mod.__name__ == "agentic_core.mixins.autonomy_mixin"


def test_module_exposes_public_api():
    """autonomy_mixin module exposes expected public symbols."""
    public_symbols = [n for n in dir(_autonomy_mixin_mod) if not n.startswith("_")]
    assert len(public_symbols) >= 1, "autonomy_mixin must expose at least one public symbol"
