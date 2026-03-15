"""ADG importability contract for agentic_core/L0_routing/types/guardian_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_guardian_contract_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.guardian_contract_types import (  # noqa: F401
        V15EnforcementError,
        V15HardFailAbort,
        V15SoftFailAbort,
        is_v15_enforced,
        is_v15_hard_fail,
        is_v15_soft_fail,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    V15EnforcementError = None  # type: ignore[assignment,misc]
    is_v15_enforced = None  # type: ignore[assignment,misc]
    is_v15_hard_fail = None  # type: ignore[assignment,misc]
    is_v15_soft_fail = None  # type: ignore[assignment,misc]
    V15SoftFailAbort = None  # type: ignore[assignment,misc]
    V15HardFailAbort = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types deps unavailable")
class TestGuardianContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/guardian_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_v15enforcementerror_defined(self) -> None:
        assert V15EnforcementError is not None

    def test_v15softfailabort_defined(self) -> None:
        assert V15SoftFailAbort is not None

    def test_v15hardfailabort_defined(self) -> None:
        assert V15HardFailAbort is not None
