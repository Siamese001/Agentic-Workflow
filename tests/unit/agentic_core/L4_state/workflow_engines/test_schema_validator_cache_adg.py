"""ADG-driven tests for agentic_core/L4_state/workflow_engines/schema_validator_cache.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.workflow_engines.schema_validator_cache  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.workflow_engines.schema_validator_cache  # noqa: F401
    """Module schema_validator_cache must be importable."""
    assert agentic_core.L4_state.workflow_engines.schema_validator_cache is not None
