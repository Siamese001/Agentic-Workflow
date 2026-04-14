"""Smoke tests for the cognitive endurance surface."""

from __future__ import annotations

import pytest

from L1_cognition.test_support import assert_module_surface


@pytest.mark.unit
def test_cognitive_endurance_surface():
    assert_module_surface(
        "agentic_core.cognitive_endurance",
        "CognitiveEndurance",
        "validate_cognitive_endurance",
    )
