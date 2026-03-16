"""ADG-driven tests for L5_safety/reasoning/file_classification_validator.py — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_file_classification_validator_adg")
_emit_applies_guardrail("p0", "test_file_classification_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_file_classification_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_file_classification_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_file_classification_validator_adg")
emit_determinism_digest("p0", "test_file_classification_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
