"""ADG importability contract for agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.HygieneGuardianAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.HygieneGuardianAgent  # noqa: F401
        """Module HygieneGuardianAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.HygieneGuardianAgent is not None

    assert agentic_core.L5_safety.reasoning.HygieneGuardianAgent is not None
