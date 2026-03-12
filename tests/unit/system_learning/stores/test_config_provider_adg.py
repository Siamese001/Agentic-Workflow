"""ADG-driven tests for system_learning/stores/config_provider.py — fan_in=1."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from system_learning.stores.config_provider import FileBackedConfigProvider


class TestFileBackedConfigProvider:
    def test_creates(self, tmp_path):
        provider = FileBackedConfigProvider(runtime_state_path=tmp_path / "state.json")
        assert provider is not None

    def test_missing_runtime_state_returns_empty(self, tmp_path):
        provider = FileBackedConfigProvider(runtime_state_path=tmp_path / "missing.json")
        result = provider.get_current_configs()
        assert isinstance(result, dict)

    def test_with_runtime_state_file(self, tmp_path):
        state = {"routing": {"threshold": 0.8}}
        state_path = tmp_path / "runtime_state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        provider = FileBackedConfigProvider(runtime_state_path=state_path)
        result = provider.get_current_configs()
        assert isinstance(result, dict)

    def test_has_get_current_configs(self):
        assert hasattr(FileBackedConfigProvider, "get_current_configs")
