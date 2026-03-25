"""ADG importability contract for apps_rg/engines/hardened_gemini_executor.py."""
from __future__ import annotations

import apps_rg.engines.hardened_gemini_executor  # noqa: F401


def test_module_importable():
    """Module hardened_gemini_executor must be importable."""
    assert apps_rg.engines.hardened_gemini_executor is not None
