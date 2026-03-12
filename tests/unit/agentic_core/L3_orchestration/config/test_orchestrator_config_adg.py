"""ADG-driven tests for L3 orchestrator_config — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.config.orchestrator_config import OrchestratorConfig


class TestOrchestratorConfigDefaults:
    def test_creates_with_defaults(self):
        cfg = OrchestratorConfig()
        assert cfg is not None

    def test_mission_id_default(self):
        cfg = OrchestratorConfig()
        assert cfg.mission_id == "default-mission"

    def test_max_iterations_default_10(self):
        cfg = OrchestratorConfig()
        assert cfg.max_iterations == 10

    def test_max_phases_default_none(self):
        cfg = OrchestratorConfig()
        assert cfg.max_phases is None

    def test_enable_tri_brain_default_false(self):
        cfg = OrchestratorConfig()
        assert cfg.enable_tri_brain is False

    def test_enable_reflection_default_true(self):
        cfg = OrchestratorConfig()
        assert cfg.enable_reflection is True

    def test_retry_on_failure_default_true(self):
        cfg = OrchestratorConfig()
        assert cfg.retry_on_failure is True

    def test_max_retries_default_3(self):
        cfg = OrchestratorConfig()
        assert cfg.max_retries == 3

    def test_parallel_actions_default_false(self):
        cfg = OrchestratorConfig()
        assert cfg.parallel_actions is False

    def test_metadata_default_empty(self):
        cfg = OrchestratorConfig()
        assert cfg.metadata == {}


class TestOrchestratorConfigToDict:
    def test_to_dict_returns_dict(self):
        cfg = OrchestratorConfig()
        d = cfg.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_mission_id(self):
        cfg = OrchestratorConfig(mission_id="test-mission")
        d = cfg.to_dict()
        assert d["mission_id"] == "test-mission"

    def test_to_dict_has_max_iterations(self):
        cfg = OrchestratorConfig(max_iterations=5)
        d = cfg.to_dict()
        assert d["max_iterations"] == 5

    def test_custom_values_preserved(self):
        cfg = OrchestratorConfig(
            mission_id="custom",
            enable_tri_brain=True,
            parallel_actions=True,
        )
        assert cfg.enable_tri_brain is True
        assert cfg.parallel_actions is True
