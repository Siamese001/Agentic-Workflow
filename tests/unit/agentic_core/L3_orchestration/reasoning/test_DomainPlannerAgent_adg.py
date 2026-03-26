"""ADG importability contract for agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.reasoning.DomainPlannerAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.reasoning.DomainPlannerAgent  # noqa: F401
    """Module DomainPlannerAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.DomainPlannerAgent is not None
