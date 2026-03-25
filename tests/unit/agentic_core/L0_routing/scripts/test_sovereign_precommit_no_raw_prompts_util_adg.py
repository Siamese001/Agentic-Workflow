"""ADG-driven tests for agentic_core/L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.sovereign_precommit_no_raw_prompts_util  # noqa: F401


def test_module_importable():
    """Module sovereign_precommit_no_raw_prompts_util must be importable."""
    assert agentic_core.L0_routing.scripts.sovereign_precommit_no_raw_prompts_util is not None
