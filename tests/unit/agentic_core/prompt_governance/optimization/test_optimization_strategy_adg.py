"""ADG importability contract for agentic_core/prompt_governance/optimization/optimization_strategy.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.optimization.optimization_strategy  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.optimization.optimization_strategy  # noqa: F401
    """Module optimization_strategy must be importable."""
    assert agentic_core.prompt_governance.optimization.optimization_strategy is not None
