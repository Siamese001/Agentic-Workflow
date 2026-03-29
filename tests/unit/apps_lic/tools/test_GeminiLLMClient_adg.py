"""ADG-driven tests for apps_lic/tools/GeminiLLMClient.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module GeminiLLMClient must be importable."""
    import apps_lic.tools.GeminiLLMClient  # noqa: F401

    assert apps_lic.tools.GeminiLLMClient is not None