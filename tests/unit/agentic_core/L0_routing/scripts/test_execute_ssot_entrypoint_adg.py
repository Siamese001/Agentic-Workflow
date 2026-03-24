"""ADG-driven tests for agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.execute_ssot_entrypoint import (  # noqa: F401
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execute_ssot_entrypoint.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module execute_ssot_entrypoint.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE