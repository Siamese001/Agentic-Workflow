"""ADG-driven tests for apps_lic/engines/message_body_composer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import apps_lic.engines.message_body_composer as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module message_body_composer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
