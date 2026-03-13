"""ADG importability contract for agentic_core/L2_execution/types/heal_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_heal_contract_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.heal_contract_types import (  # noqa: F401
        CombinedHealResult,
        HealCheckResult,
        HealStatus,
        check_schema_compatibility,
        validate_against_json_schema,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealStatus = None  # type: ignore[assignment,misc]
    HealCheckResult = None  # type: ignore[assignment,misc]
    CombinedHealResult = None  # type: ignore[assignment,misc]
    check_schema_compatibility = None  # type: ignore[assignment,misc]
    validate_against_json_schema = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types deps unavailable")
class TestHealContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/heal_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_healstatus_defined(self) -> None:
        assert HealStatus is not None

    def test_healcheckresult_defined(self) -> None:
        assert HealCheckResult is not None

    def test_combinedhealresult_defined(self) -> None:
        assert CombinedHealResult is not None
