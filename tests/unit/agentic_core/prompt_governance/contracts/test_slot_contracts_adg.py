"""ADG importability contract for agentic_core/prompt_governance/contracts/slot_contracts.py."""
from __future__ import annotations

import agentic_core.prompt_governance.contracts.slot_contracts  # noqa: F401


def test_module_importable():
    """Module slot_contracts must be importable."""
    assert agentic_core.prompt_governance.contracts.slot_contracts is not None
