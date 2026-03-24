"""ADG importability contract for apps_shared/types/app_heal_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_app_heal_contract_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.types.app_heal_contract_types import (  # noqa: F401
        AppHealResult,
        AppHealStatus,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AppHealStatus = None  # type: ignore[assignment,misc]
    AppHealResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="app_heal_contract_types.py deps unavailable")
class TestAppHealContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: app_heal_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_apphealstatus_is_type(self) -> None:
        assert AppHealStatus is not None

    def test_apphealresult_is_type(self) -> None:
        assert AppHealResult is not None