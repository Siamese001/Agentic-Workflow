"""ADG importability contract for agentic_core/L3_orchestration/types/approval_contract_types.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.types.approval_contract_types  # noqa: F401


def test_module_importable():
    """Module approval_contract_types must be importable."""
    assert agentic_core.L3_orchestration.types.approval_contract_types is not None
