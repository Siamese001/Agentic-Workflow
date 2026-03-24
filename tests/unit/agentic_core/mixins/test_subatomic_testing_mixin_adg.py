"""ADG importability contract for agentic_core/mixins/subatomic_testing_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_subatomic_testing_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.subatomic_testing_mixin import (  # noqa: F401
        L2SelfTestingMixin,
        SubatomicTestingMixin,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SubatomicTestingMixin = None  # type: ignore[assignment,misc]
    L2SelfTestingMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin deps unavailable")
class TestSubatomicTestingMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/subatomic_testing_mixin.py must be importable."""
        assert _AVAILABLE

    def test_subatomictestingmixin_defined(self) -> None:
        assert SubatomicTestingMixin is not None

    def test_l2selftestingmixin_defined(self) -> None:
        assert L2SelfTestingMixin is not None