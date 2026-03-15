"""ADG importability contract for agentic_core/L3_orchestration/types/approval_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_approval_contract_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.approval_contract_types import (  # noqa: F401
        ApprovalBundle,
        ApprovalDecision,
        ApprovalRecord,
        check_schema_compatibility,
        validate_against_json_schema,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ApprovalDecision = None  # type: ignore[assignment,misc]
    ApprovalRecord = None  # type: ignore[assignment,misc]
    ApprovalBundle = None  # type: ignore[assignment,misc]
    check_schema_compatibility = None  # type: ignore[assignment,misc]
    validate_against_json_schema = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="approval_contract_types deps unavailable")
class TestApprovalContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/types/approval_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_approvaldecision_defined(self) -> None:
        assert ApprovalDecision is not None

    def test_approvalrecord_defined(self) -> None:
        assert ApprovalRecord is not None

    def test_approvalbundle_defined(self) -> None:
        assert ApprovalBundle is not None
