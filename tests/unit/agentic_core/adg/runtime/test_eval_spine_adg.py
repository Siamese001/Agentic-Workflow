"""ADG importability contract for agentic_core/adg/runtime/eval_spine.py."""
from __future__ import annotations

import agentic_core.adg.runtime.eval_spine  # noqa: F401


def test_module_importable():
    """Module eval_spine must be importable."""
    assert agentic_core.adg.runtime.eval_spine is not None
