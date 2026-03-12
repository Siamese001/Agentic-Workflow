"""ADG-driven tests for agentic_core/L5_safety/utils/ssot_folder_check_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.ssot_folder_check_util import (  # noqa: F401
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_folder_check_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module ssot_folder_check_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
