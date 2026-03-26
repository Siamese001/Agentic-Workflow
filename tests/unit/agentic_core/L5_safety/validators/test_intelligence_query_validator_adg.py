"""ADG importability contract for agentic_core/L5_safety/validators/intelligence_query_validator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.validators.intelligence_query_validator  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.validators.intelligence_query_validator  # noqa: F401
        """Module intelligence_query_validator must be importable."""
        assert agentic_core.L5_safety.validators.intelligence_query_validator is not None

    assert agentic_core.L5_safety.validators.intelligence_query_validator is not None
