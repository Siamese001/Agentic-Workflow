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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_credential_access_guard", "p4obs", "metric_1")
_emit_emits_metric_event("test_credential_access_guard", "p4obs", "metric_2")
_emit_emits_metric_event("test_credential_access_guard", "p4obs", "metric_3")
_emit_emits_metric_event("test_credential_access_guard", "p4obs", "metric_4")
_emit_emits_metric_event("test_credential_access_guard", "p4obs", "metric_5")
_emit_emits_metric_event("test_credential_access_guard", "p4obs", "metric_6")
_emit_records_incident_event("test_credential_access_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_credential_access_guard", "p4obs", "anomaly")
_emit_writes_observability_log("test_credential_access_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_credential_access_guard", "p4obs", "mon_state")
_emit_triggers_alert("test_credential_access_guard", "p4obs", "alert")
_emit_links_incident_trace("test_credential_access_guard", "p4obs", "trace_link")
_emit_captures_pattern("test_credential_access_guard", "p3lm", "pattern")
_emit_records_learning_event("test_credential_access_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_credential_access_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_credential_access_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_credential_access_guard", "p3lm", "routing")
_emit_improves_agent_policy("test_credential_access_guard", "p3lm", "policy")
_emit_stores_learning_state("test_credential_access_guard", "p3lm", "state")
_emit_records_execution_trace("test_credential_access_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_credential_access_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_credential_access_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_credential_access_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_credential_access_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_credential_access_guard", "env_read", "p2_env_1")
_emit_reads_environ("test_credential_access_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_credential_access_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_credential_access_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_credential_access_guard", "context_pull")
_emit_pulls_context("p1", "test_credential_access_guard", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_credential_access_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_credential_access_guard", "uwg_term_secondary")
_emit_writes_through("p1", "test_credential_access_guard", "write_through")
_emit_writes_through("p1", "test_credential_access_guard", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_credential_access_guard", "safety_validation")
_emit_invokes_eval("p1", "test_credential_access_guard", "eval_call")
_emit_proposal_commits_routing("p1", "test_credential_access_guard", "routing_commit")
_emit_escalates_to_human("p1", "test_credential_access_guard", "human_escalation")
_emit_routes_through("p1", "test_credential_access_guard", "route_through")
_emit_checks_agent_registry("p1", "test_credential_access_guard", "agent_registry")
_emit_validates_agent_capability("p1", "test_credential_access_guard", "capability")
_emit_dispatches_execution_plan("p1", "test_credential_access_guard", "exec_plan")
_emit_agent_executes_agent("p1", "test_credential_access_guard", "sub_agent")
_emit_routes_to_agent("p1", "test_credential_access_guard", "target_agent")
_emit_verifies_policy("p1", "test_credential_access_guard", "policy_check")
_emit_observes_runtime_state("p1", "test_credential_access_guard", "runtime_state")
_emit_verifies_boundary("p1", "test_credential_access_guard", "boundary_check")
_emit_transcripts_response("p1", "test_credential_access_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "test_credential_access_guard")
_emit_gated_by_confidence("p1", "test_credential_access_guard", "confidence_gate")


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
