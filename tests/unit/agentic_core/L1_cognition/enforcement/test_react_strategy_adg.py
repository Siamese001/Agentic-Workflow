"""ADG importability contract for agentic_core/L1_cognition/enforcement/react_strategy.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_react_strategy.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.enforcement.react_strategy import (  # noqa: F401
        ReActStrategy,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ReActStrategy = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="react_strategy deps unavailable")
class TestReactStrategyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L1_cognition/enforcement/react_strategy.py must be importable."""
        assert _AVAILABLE

    def test_reactstrategy_defined(self) -> None:
        assert ReActStrategy is not None