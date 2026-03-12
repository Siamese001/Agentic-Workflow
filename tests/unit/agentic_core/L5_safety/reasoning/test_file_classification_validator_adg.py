"""ADG-driven tests for L5_safety/reasoning/file_classification_validator.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.file_classification_validator import (
    CHECK_ID,
    FileClassificationValidatorAgent,
)


class TestFileClassificationValidatorAgent:
    def test_check_id_string(self):
        assert isinstance(CHECK_ID, str)
        assert CHECK_ID == "file_classification"

    def test_creates(self, tmp_path):
        agent = FileClassificationValidatorAgent(project_root=tmp_path)
        assert agent is not None

    def test_project_root_stored(self, tmp_path):
        agent = FileClassificationValidatorAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()

    def test_has_scan(self):
        assert hasattr(FileClassificationValidatorAgent, "scan")

    def test_has_to_check_dict(self):
        assert hasattr(FileClassificationValidatorAgent, "to_check_dict")

    def test_scan_returns_dict(self, tmp_path):
        agent = FileClassificationValidatorAgent(project_root=tmp_path)
        result = agent.scan()
        assert isinstance(result, dict)
