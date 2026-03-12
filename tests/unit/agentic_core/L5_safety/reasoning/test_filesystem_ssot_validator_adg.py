"""ADG-driven tests for L5_safety/reasoning/filesystem_ssot_validator.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.filesystem_ssot_validator import (
    CHECK_ID,
    FilesystemSSOTValidatorAgent,
)


class TestFilesystemSSOTValidatorAgent:
    def test_check_id_value(self):
        assert CHECK_ID == "filesystem_ssot_drift"

    def test_creates(self, tmp_path):
        agent = FilesystemSSOTValidatorAgent(project_root=tmp_path)
        assert agent is not None

    def test_project_root_resolved(self, tmp_path):
        agent = FilesystemSSOTValidatorAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()

    def test_has_scan(self):
        assert hasattr(FilesystemSSOTValidatorAgent, "scan")

    def test_has_to_check_dict(self):
        assert hasattr(FilesystemSSOTValidatorAgent, "to_check_dict")

    def test_has_run(self):
        assert hasattr(FilesystemSSOTValidatorAgent, "run")

    def test_to_check_dict_returns_dict(self, tmp_path):
        agent = FilesystemSSOTValidatorAgent(project_root=tmp_path)
        result = agent.to_check_dict()
        assert isinstance(result, dict)
        assert result.get("check_id") == CHECK_ID
