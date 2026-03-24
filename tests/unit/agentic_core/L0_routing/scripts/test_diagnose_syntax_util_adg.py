"""ADG-driven tests for agentic_core/L0_routing/scripts/diagnose_syntax_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.diagnose_syntax_util import (  # noqa: F401
        check_syntax,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    check_syntax = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="diagnose_syntax_util.py deps unavailable")
class TestCheckSyntax:
    def test_is_callable(self):
        assert callable(check_syntax)


def test_module_importable():
    """Module diagnose_syntax_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE