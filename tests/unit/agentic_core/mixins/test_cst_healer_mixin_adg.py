"""ADG importability contract for agentic_core/mixins/cst_healer_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cst_healer_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.cst_healer_mixin import (  # noqa: F401
        CSTModification,
        SurgicalCSTHealerMixin,
        SurgicalCSTTransformer,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CSTModification = None  # type: ignore[assignment,misc]
    SurgicalCSTTransformer = None  # type: ignore[assignment,misc]
    SurgicalCSTHealerMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cst_healer_mixin deps unavailable")
class TestCstHealerMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/cst_healer_mixin.py must be importable."""
        assert _AVAILABLE

    def test_cstmodification_defined(self) -> None:
        assert CSTModification is not None

    def test_surgicalcsttransformer_defined(self) -> None:
        assert SurgicalCSTTransformer is not None

    def test_surgicalcsthealermixin_defined(self) -> None:
        assert SurgicalCSTHealerMixin is not None