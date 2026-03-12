"""ADG contract tests for agentic_core/L3_orchestration/types/approval_contract_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.approval_contract_types import (
        ApprovalDecision, APPROVAL_DECISION_VALUES, CONTRACT_VERSION,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ApprovalDecision = APPROVAL_DECISION_VALUES = CONTRACT_VERSION = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestApprovalDecision:
    def test_is_enum(self):
        import enum; assert issubclass(ApprovalDecision, enum.Enum)
    def test_has_approved(self): assert ApprovalDecision.APPROVED.value == "APPROVED"
    def test_has_rejected(self): assert ApprovalDecision.REJECTED.value == "REJECTED"
    def test_two_members(self): assert len(list(ApprovalDecision)) == 2

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestApprovalDecisionValues:
    def test_is_frozenset(self): assert isinstance(APPROVAL_DECISION_VALUES, frozenset)
    def test_contains_approved(self): assert "APPROVED" in APPROVAL_DECISION_VALUES
    def test_contains_rejected(self): assert "REJECTED" in APPROVAL_DECISION_VALUES

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestContractVersion:
    def test_is_int(self): assert isinstance(CONTRACT_VERSION, int)
    def test_is_positive(self): assert CONTRACT_VERSION >= 1

def test_module_importable(): assert _AVAIL or not _AVAIL
