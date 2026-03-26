"""ADG importability contract for agentic_core/L3_orchestration/engines/parallelization_engine.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.engines.parallelization_engine  # noqa: F401


def test_module_importable():
        import agentic_core.L3_orchestration.engines.parallelization_engine  # noqa: F401
        """Module parallelization_engine must be importable."""
        assert agentic_core.L3_orchestration.engines.parallelization_engine is not None

    assert agentic_core.L3_orchestration.engines.parallelization_engine is not None
