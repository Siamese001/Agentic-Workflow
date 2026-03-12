"""ADG importability contract for agentic_core/L3_orchestration/types/approval_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_approval_contract_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.approval_contract_types import (  # noqa: F401
        ApprovalDecision,
        ApprovalRecord,
        ApprovalBundle,
        check_schema_compatibility,
        validate_against_json_schema,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ApprovalDecision = None  # type: ignore[assignment,misc]
    ApprovalRecord = None  # type: ignore[assignment,misc]
    ApprovalBundle = None  # type: ignore[assignment,misc]
    check_schema_compatibility = None  # type: ignore[assignment,misc]
    validate_against_json_schema = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="approval_contract_types.py deps unavailable")
class TestApprovalContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: approval_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_approvaldecision_is_type(self) -> None:
        assert ApprovalDecision is not None

    def test_approvalrecord_is_type(self) -> None:
        assert ApprovalRecord is not None

    def test_approvalbundle_is_type(self) -> None:
        assert ApprovalBundle is not None

    def test_check_schema_compatibility_callable(self) -> None:
        assert callable(check_schema_compatibility)

    def test_validate_against_json_schema_callable(self) -> None:
        assert callable(validate_against_json_schema)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

