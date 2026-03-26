"""ADG importability contract for agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.StructuralValidatorAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.StructuralValidatorAgent  # noqa: F401
        """Module StructuralValidatorAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.StructuralValidatorAgent is not None

    assert agentic_core.L5_safety.reasoning.StructuralValidatorAgent is not None
