"""ADG importability contract for apps_shared/types/hardened_gemini_executor_types.py."""
from __future__ import annotations

import apps_shared.types.hardened_gemini_executor_types  # noqa: F401


def test_module_importable():
    """Module hardened_gemini_executor_types must be importable."""
    assert apps_shared.types.hardened_gemini_executor_types is not None
