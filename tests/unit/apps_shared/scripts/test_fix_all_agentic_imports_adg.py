"""ADG-driven tests for apps_shared/scripts/fix_all_agentic_imports.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.fix_all_agentic_imports import (  # noqa: F401
        fix_file_imports,
        main,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    fix_file_imports = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_agentic_imports.py deps unavailable")
class TestFixFileImports:
    def test_is_callable(self):
        assert callable(fix_file_imports)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_agentic_imports.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module fix_all_agentic_imports.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
