"""ADG importability contract for agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent  # noqa: F401
    """Module ArchitectureGovernorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent is not None
