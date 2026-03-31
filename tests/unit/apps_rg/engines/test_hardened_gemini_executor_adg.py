"""ADG importability contract for apps_rg/engines/hardened_gemini_executor.py."""
from __future__ import annotations


def test_module_importable():
    """Module hardened_gemini_executor must be importable."""
    import apps_rg.engines.hardened_gemini_executor  # noqa: F401

    assert apps_rg.engines.hardened_gemini_executor is not None
