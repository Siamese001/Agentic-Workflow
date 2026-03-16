"""ADG-driven tests for agentic_core/L0_routing/types/integration_contract_types.py — fan_in=2.

Contract tests: Finding, ResultEnvelope, SCHEMA_VERSION.
"""
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

_emit_records_execution_trace("p0", "evidence", "test_integration_contract_types_adg")
_emit_applies_guardrail("p0", "test_integration_contract_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_integration_contract_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_integration_contract_types_adg", "state_snapshot")
emit_replay_key("p0", "test_integration_contract_types_adg")
emit_determinism_digest("p0", "test_integration_contract_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.types.integration_contract_types import (
    SCHEMA_VERSION,
    Finding,
    ResultEnvelope,
)


class TestSchemaVersion:
    def test_is_string(self):
        assert isinstance(SCHEMA_VERSION, str)

    def test_semver_format(self):
        parts = SCHEMA_VERSION.split(".")
        assert len(parts) == 3
        for p in parts:
            int(p)  # each part must be numeric


class TestFinding:
    def test_valid_creation(self):
        f = Finding(code="E001", severity="ERROR", message="something wrong")
        assert f.code == "E001"
        assert f.severity == "ERROR"

    def test_frozen(self):
        f = Finding(code="E001", severity="INFO", message="ok")
        with pytest.raises(Exception):
            f.code = "X"  # type: ignore[misc]

    def test_to_ordered_dict_has_keys(self):
        f = Finding(code="W001", severity="WARN", message="warning", context={"k": "v"})
        d = f.to_ordered_dict()
        assert set(d.keys()) == {"code", "context", "message", "severity"}

    def test_context_defaults_to_empty_dict(self):
        f = Finding(code="I001", severity="INFO", message="info", context=None)
        d = f.to_ordered_dict()
        assert d["context"] == {}

    def test_to_ordered_dict_sorted_keys(self):
        f = Finding(code="E002", severity="ERROR", message="msg")
        d = f.to_ordered_dict()
        assert list(d.keys()) == sorted(d.keys())


class TestResultEnvelope:
    def _make(self, exit_code: int = 0, findings=None) -> ResultEnvelope:
        return ResultEnvelope(
            tool="test_tool",
            exit_code=exit_code,
            findings=findings or [],
        )

    def test_status_pass_on_zero_exit(self):
        env = self._make(exit_code=0)
        assert env.status == "PASS"

    def test_status_fail_on_nonzero_exit(self):
        env = self._make(exit_code=1)
        assert env.status == "FAIL"

    def test_status_fail_on_error_finding(self):
        f = Finding(code="E001", severity="ERROR", message="err")
        env = self._make(exit_code=0, findings=[f])
        assert env.status == "FAIL"

    def test_status_warn_on_warn_finding(self):
        f = Finding(code="W001", severity="WARN", message="warn")
        env = self._make(exit_code=0, findings=[f])
        assert env.status == "WARN"

    def test_to_ordered_dict_has_required_keys(self):
        env = self._make()
        d = env.to_ordered_dict()
        for key in ("exit_code", "findings", "inputs", "outputs", "schema_version", "status", "tool"):
            assert key in d

    def test_to_json_valid_json(self):
        env = self._make()
        parsed = json.loads(env.to_json())
        assert parsed["tool"] == "test_tool"

    def test_to_json_deterministic(self):
        env = self._make()
        assert env.to_json() == env.to_json()

    def test_findings_serialized(self):
        f = Finding(code="I001", severity="INFO", message="info")
        env = self._make(findings=[f])
        d = env.to_ordered_dict()
        assert len(d["findings"]) == 1
        assert d["findings"][0]["code"] == "I001"
