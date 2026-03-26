"""ADG importability contract for agentic_core/L5_safety/reasoning/ReportLocationAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.ReportLocationAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.ReportLocationAgent  # noqa: F401
        """Module ReportLocationAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.ReportLocationAgent is not None

    assert agentic_core.L5_safety.reasoning.ReportLocationAgent is not None
