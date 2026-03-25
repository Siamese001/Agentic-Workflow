"""ADG importability contract for agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.runtime_mutation_guardrail  # noqa: F401


def test_module_importable():
    """Module runtime_mutation_guardrail must be importable."""
    assert agentic_core.L5_safety.enforcement.runtime_mutation_guardrail is not None
