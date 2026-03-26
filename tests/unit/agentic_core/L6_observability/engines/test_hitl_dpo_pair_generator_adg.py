"""ADG importability contract for agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L6_observability.engines.hitl_dpo_pair_generator  # noqa: F401


def test_module_importable():
    import agentic_core.L6_observability.engines.hitl_dpo_pair_generator  # noqa: F401
    """Module hitl_dpo_pair_generator must be importable."""
    assert agentic_core.L6_observability.engines.hitl_dpo_pair_generator is not None
