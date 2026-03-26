"""ADG importability contract for agentic_core/L5_safety/enforcement/rag_guardrail.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.rag_guardrail  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.enforcement.rag_guardrail  # noqa: F401
        """Module rag_guardrail must be importable."""
        assert agentic_core.L5_safety.enforcement.rag_guardrail is not None

    assert agentic_core.L5_safety.enforcement.rag_guardrail is not None
