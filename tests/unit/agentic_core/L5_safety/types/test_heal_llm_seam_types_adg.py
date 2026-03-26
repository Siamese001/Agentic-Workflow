"""ADG importability contract for agentic_core/L5_safety/types/heal_llm_seam_types.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.types.heal_llm_seam_types  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.types.heal_llm_seam_types  # noqa: F401
    """Module heal_llm_seam_types must be importable."""
    assert agentic_core.L5_safety.types.heal_llm_seam_types is not None
