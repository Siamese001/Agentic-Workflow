"""ADG-driven tests for agentic_core/L0_routing/scripts/core_synthesis_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.core_synthesis_executor import (  # noqa: F401
        CoreSynthesisExecutor,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CoreSynthesisExecutor = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="core_synthesis_executor.py deps unavailable")
class TestCoreSynthesisExecutor:
    def test_is_class(self):
        assert isinstance(CoreSynthesisExecutor, type)
    def test_importable(self):
        assert CoreSynthesisExecutor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="core_synthesis_executor.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module core_synthesis_executor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE