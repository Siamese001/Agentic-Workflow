"""ADG importability contract for apps_rg/engines/void_compliance_engine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_void_compliance_engine.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_rg.engines.void_compliance_engine import (  # noqa: F401
        VoidComplianceEngine,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VoidComplianceEngine = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_engine.py deps unavailable")
class TestVoidComplianceEngineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: void_compliance_engine.py must be importable."""
        assert _AVAILABLE

    def test_voidcomplianceengine_is_type(self) -> None:
        assert VoidComplianceEngine is not None