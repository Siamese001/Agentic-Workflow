"""ADG-driven tests for agentic_core/L4_state/config/ledger_retention_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.config.ledger_retention_config  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.config.ledger_retention_config  # noqa: F401
    """Module ledger_retention_config must be importable."""
    assert agentic_core.L4_state.config.ledger_retention_config is not None
