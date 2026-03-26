"""ADG importability contract for agentic_core/L5_safety/config/contract_stage_config.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.config.contract_stage_config  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.config.contract_stage_config  # noqa: F401
    """Module contract_stage_config must be importable."""
    assert agentic_core.L5_safety.config.contract_stage_config is not None
