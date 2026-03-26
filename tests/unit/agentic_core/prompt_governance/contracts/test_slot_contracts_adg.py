"""ADG importability contract for agentic_core/prompt_governance/contracts/slot_contracts.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.contracts.slot_contracts  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.contracts.slot_contracts  # noqa: F401
        """Module slot_contracts must be importable."""
        assert agentic_core.prompt_governance.contracts.slot_contracts is not None

    assert agentic_core.prompt_governance.contracts.slot_contracts is not None
