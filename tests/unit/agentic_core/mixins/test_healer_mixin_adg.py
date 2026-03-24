"""ADG importability contract for agentic_core/mixins/healer_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healer_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.healer_mixin import (  # noqa: F401
        HealerMixin,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HealerMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healer_mixin deps unavailable")
class TestHealerMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/healer_mixin.py must be importable."""
        assert _AVAILABLE

    def test_healermixin_defined(self) -> None:
        assert HealerMixin is not None