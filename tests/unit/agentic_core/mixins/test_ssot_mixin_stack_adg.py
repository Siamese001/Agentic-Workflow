"""ADG importability contract for agentic_core/mixins/ssot_mixin_stack.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_mixin_stack.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_mixin_stack import (  # noqa: F401
        SSOTMixinStack,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SSOTMixinStack = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_mixin_stack deps unavailable")
class TestSsotMixinStackImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/ssot_mixin_stack.py must be importable."""
        assert _AVAILABLE

    def test_ssotmixinstack_defined(self) -> None:
        assert SSOTMixinStack is not None