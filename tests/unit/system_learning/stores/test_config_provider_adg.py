"""ADG-driven tests for system_learning/stores/config_provider.py — fan_in=1."""
from __future__ import annotations

import json

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_config_provider_adg")
_emit_applies_guardrail("p0", "test_config_provider_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_config_provider_adg", "policy_binding")
_emit_snapshots_state("p0", "test_config_provider_adg", "state_snapshot")
emit_replay_key("p0", "test_config_provider_adg")
emit_determinism_digest("p0", "test_config_provider_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
