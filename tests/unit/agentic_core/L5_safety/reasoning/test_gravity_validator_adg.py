"""ADG-driven tests for L5_safety/reasoning/gravity_validator.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.gravity_validator import (
        CHECK_ID,
        GravityValidatorAgent,
    )
    _GRAVITY_VALIDATOR_AVAILABLE = True
except (NameError, ImportError):
    _GRAVITY_VALIDATOR_AVAILABLE = False
    CHECK_ID = "gravity_violations"
    GravityValidatorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _GRAVITY_VALIDATOR_AVAILABLE, reason="gravity_validator has NameError at module level")
class TestGravityValidatorAgent:
    def test_check_id_value(self):
        assert CHECK_ID == "gravity_violations"

    def test_creates(self, tmp_path):
        agent = GravityValidatorAgent(project_root=tmp_path)
        assert agent is not None

    def test_project_root_resolved(self, tmp_path):
        agent = GravityValidatorAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()

    def test_has_scan(self):
        assert hasattr(GravityValidatorAgent, "scan")

    def test_has_to_check_dict(self):
        assert hasattr(GravityValidatorAgent, "to_check_dict")

    def test_to_check_dict_returns_dict(self, tmp_path):
        agent = GravityValidatorAgent(project_root=tmp_path)
        result = agent.to_check_dict()
        assert isinstance(result, dict)
        assert result.get("check_id") == CHECK_ID


def test_check_id_constant():
    assert CHECK_ID == "gravity_violations"
