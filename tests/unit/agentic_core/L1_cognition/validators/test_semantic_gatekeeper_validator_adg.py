"""ADG-driven tests for L1_cognition/validators/semantic_gatekeeper_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.semantic_gatekeeper_validator import semantic_gatekeeper


class TestSemanticGatekeeper:
    def test_creates(self):
        gk = semantic_gatekeeper(config={"mission_scope": "software_development"})
        assert gk.mission_scope == "software_development"

    def test_creates_with_default_scope(self):
        gk = semantic_gatekeeper(config={})
        assert gk.mission_scope == "software_development"

    def test_has_check_drift(self):
        assert hasattr(semantic_gatekeeper, "check_drift")
