"""Tests for CredentialAccessGuard — safety-plane credential enforcement."""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_credential_access_guard")
_emit_applies_guardrail("p0", "test_credential_access_guard", "p0_governance")
_emit_reads_policy_state("p0", "test_credential_access_guard", "policy_binding")
_emit_snapshots_state("p0", "test_credential_access_guard", "state_snapshot")
emit_replay_key("p0", "test_credential_access_guard")
emit_determinism_digest("p0", "test_credential_access_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_credential_access_guard", "execution_auth")
_emit_validates_capability("p2", "test_credential_access_guard", "capability_check")
_emit_routes_to_capability("p2", "test_credential_access_guard", "capability_route")
_emit_writes_via_uwg("p2", "test_credential_access_guard", "uwg_write")
_emit_blocks_direct_write("p2", "test_credential_access_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "test_credential_access_guard", "tool_invocation")
_emit_captures_execution_output("p2", "test_credential_access_guard", "exec_output")
_emit_dispatches_agent("p3", "test_credential_access_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "test_credential_access_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_credential_access_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_credential_access_guard", "healing_outcome")
_emit_escalates_failure("p3", "test_credential_access_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_credential_access_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_credential_access_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_credential_access_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_credential_access_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_credential_access_guard", "eval_metric")
_emit_stores_embedding("p4", "test_credential_access_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_credential_access_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_credential_access_guard", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.adg.runtime.secret_access import SecretAccessOutcome, SecretKind
from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
    CredentialAccessDenied,
    CredentialAccessGuard,
)


class TestCredentialAccessGuardGetSecret:
    def test_returns_env_var_value(self, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "sk-test-123")
        guard = CredentialAccessGuard(agent_id="TestAgent", run_id="run-1")
        value = guard.guarded_get_secret("TEST_API_KEY")
        assert value == "sk-test-123"

    def test_records_success_event(self, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "sk-test-123")
        guard = CredentialAccessGuard(agent_id="TestAgent", run_id="run-1")
        guard.guarded_get_secret("TEST_API_KEY")
        report = guard.access_report
        assert report.total_accesses == 1
        assert report.events[0].outcome == SecretAccessOutcome.SUCCESS

    def test_missing_secret_no_default_raises(self, monkeypatch):
        monkeypatch.delenv("MISSING_SECRET", raising=False)
        guard = CredentialAccessGuard(agent_id="TestAgent", run_id="run-1")
        with pytest.raises(KeyError, match="MISSING_SECRET"):
            guard.guarded_get_secret("MISSING_SECRET")

    def test_missing_secret_with_default_returns_default(self, monkeypatch):
        monkeypatch.delenv("MISSING_SECRET", raising=False)
        guard = CredentialAccessGuard(agent_id="TestAgent", run_id="run-1")
        value = guard.guarded_get_secret("MISSING_SECRET", default="fallback")
        assert value == "fallback"

    def test_missing_secret_with_default_records_not_found(self, monkeypatch):
        monkeypatch.delenv("MISSING_SECRET", raising=False)
        guard = CredentialAccessGuard(agent_id="TestAgent", run_id="run-1")
        guard.guarded_get_secret("MISSING_SECRET", default="fallback")
        report = guard.access_report
        assert report.events[0].outcome == SecretAccessOutcome.NOT_FOUND

    def test_kind_is_recorded(self, monkeypatch):
        monkeypatch.setenv("DB_TOKEN", "tok-xyz")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        guard.guarded_get_secret("DB_TOKEN", kind=SecretKind.TOKEN)
        assert guard.access_report.events[0].secret_kind == SecretKind.TOKEN


class TestCredentialAccessGuardPolicy:
    def test_denied_prefix_raises(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r", policy_enforced=True)
        with pytest.raises(CredentialAccessDenied, match="denied by safety policy"):
            guard.guarded_get_secret("AWS_SECRET_ACCESS_KEY")

    def test_denied_prefix_records_denied_event(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r", policy_enforced=True)
        try:
            guard.guarded_get_secret("PRIVATE_KEY_PEM")
        except CredentialAccessDenied:
            pass
        assert guard.access_report.denied_count == 1

    def test_policy_disabled_allows_denied_prefix(self, monkeypatch):
        monkeypatch.setenv("AWS_SECRET_BYPASS", "value")
        guard = CredentialAccessGuard(agent_id="A", run_id="r", policy_enforced=False)
        value = guard.guarded_get_secret("AWS_SECRET_BYPASS")
        assert value == "value"

    def test_custom_denied_prefixes(self, monkeypatch):
        guard = CredentialAccessGuard(agent_id="A", run_id="r", denied_prefixes=("MY_BLOCKED_",))
        with pytest.raises(CredentialAccessDenied):
            guard.guarded_get_secret("MY_BLOCKED_KEY")

    def test_non_blocked_key_not_denied(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-ok")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        value = guard.guarded_get_secret("OPENAI_API_KEY")
        assert value == "sk-ok"


class TestCredentialAccessGuardGetEnv:
    def test_returns_env_value(self, monkeypatch):
        monkeypatch.setenv("MY_ENV_VAR", "hello")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        assert guard.guarded_get_env("MY_ENV_VAR") == "hello"

    def test_missing_env_var_returns_none(self, monkeypatch):
        monkeypatch.delenv("ABSENT_VAR", raising=False)
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        assert guard.guarded_get_env("ABSENT_VAR") is None

    def test_missing_env_var_with_default(self, monkeypatch):
        monkeypatch.delenv("ABSENT_VAR", raising=False)
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        assert guard.guarded_get_env("ABSENT_VAR", default="def") == "def"

    def test_records_env_var_event(self, monkeypatch):
        monkeypatch.setenv("MY_ENV_VAR", "val")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        guard.guarded_get_env("MY_ENV_VAR")
        assert guard.access_report.total_accesses == 1
        assert guard.access_report.events[0].secret_kind == SecretKind.ENV_VAR


class TestCredentialAccessGuardAccessCredential:
    def test_resolver_called(self):
        def resolver(name):
            return "resolved-value"

        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        value = guard.guarded_access_credential("MY_CRED", resolver=resolver)
        assert value == "resolved-value"

    def test_no_resolver_falls_back_to_env(self, monkeypatch):
        monkeypatch.setenv("MY_CRED_TOKEN", "env-val")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        value = guard.guarded_access_credential("MY_CRED_TOKEN")
        assert value == "env-val"

    def test_records_access_event(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        guard.guarded_access_credential("MY_CRED", resolver=lambda n: "x")
        assert guard.access_report.total_accesses == 1

    def test_policy_blocks_denied_prefix(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r", policy_enforced=True)
        with pytest.raises(CredentialAccessDenied):
            guard.guarded_access_credential("PRIVATE_KEY_CERT", resolver=lambda n: "x")


class TestCredentialAccessGuardHashCredential:
    def test_hash_is_16_hex_chars(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        h = guard.hash_credential("sk-secret-value")
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_same_value_same_hash(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        assert guard.hash_credential("abc") == guard.hash_credential("abc")

    def test_different_values_different_hashes(self):
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        assert guard.hash_credential("abc") != guard.hash_credential("xyz")


class TestCredentialAccessGuardReport:
    def test_report_tracks_multiple_accesses(self, monkeypatch):
        monkeypatch.setenv("KEY_A", "a")
        monkeypatch.setenv("KEY_B", "b")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        guard.guarded_get_secret("KEY_A")
        guard.guarded_get_secret("KEY_B")
        assert guard.access_report.total_accesses == 2

    def test_report_unique_secrets(self, monkeypatch):
        monkeypatch.setenv("KEY_A", "a")
        guard = CredentialAccessGuard(agent_id="A", run_id="r")
        guard.guarded_get_secret("KEY_A")
        guard.guarded_get_secret("KEY_A")
        assert "KEY_A" in guard.access_report.unique_secrets
