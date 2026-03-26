"""ADG importability contract for agentic_core/L4_state/engines/fresh_data_validator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.engines.fresh_data_validator  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.engines.fresh_data_validator  # noqa: F401
        """Module fresh_data_validator must be importable."""
        assert agentic_core.L4_state.engines.fresh_data_validator is not None

    assert agentic_core.L4_state.engines.fresh_data_validator is not None
