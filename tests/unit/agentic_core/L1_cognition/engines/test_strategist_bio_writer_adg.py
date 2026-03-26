"""ADG-driven tests for agentic_core/L1_cognition/engines/strategist_bio_writer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.strategist_bio_writer  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.engines.strategist_bio_writer  # noqa: F401
    """Module strategist_bio_writer must be importable."""
    assert agentic_core.L1_cognition.engines.strategist_bio_writer is not None
