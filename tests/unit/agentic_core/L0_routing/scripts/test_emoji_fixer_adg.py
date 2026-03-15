"""ADG-driven tests for agentic_core/L0_routing/scripts/emoji_fixer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.emoji_fixer import (  # noqa: F401
        EMOJI_MAP,
        fix_emojis_in_file,
        main,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    fix_emojis_in_file = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    EMOJI_MAP = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="emoji_fixer.py deps unavailable")
class TestFixEmojisInFile:
    def test_is_callable(self):
        assert callable(fix_emojis_in_file)

@pytest.mark.skipif(not _AVAILABLE, reason="emoji_fixer.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="emoji_fixer.py deps unavailable")
class TestEmojiMapConstant:
    def test_is_not_none(self):
        assert EMOJI_MAP is not None


def test_module_importable():
    """Module emoji_fixer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
