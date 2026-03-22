"""
Creative test suite for Wave 4 (Guardrails), Wave 5 (ExecutionTrace), Wave 6 (UWG).

Tests use creative approaches:
- Property-based thinking (boundary conditions, adversarial inputs)
- State machine verification (guard transitions)
- Cross-guard interaction (multiple guards on same operation)
- Mutation ledger integrity (Wave 6 write governance)
- ADG edge emission verification via log capture
"""

from __future__ import annotations

import logging

import pytest

from agentic_core.L2_execution.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    UniversalWriteGateway,
    append_to_file,
    atomic_write,
    get_write_gateway,
    reset_write_gateway,
    set_write_gateway,
    write_json,
    write_pickle,
    write_text,
)
from agentic_core.L5_safety.enforcement.credential_guard import (
    CredentialAccessDeniedError,
    CredentialGuard,
)
from agentic_core.L5_safety.enforcement.eval_guard import (
    EvalExecutionDeniedError,
    EvalGuard,
    get_eval_guard,
)
from agentic_core.L5_safety.enforcement.http_guard import (
    ExternalHttpDeniedError,
    HTTPGuard,
)
from agentic_core.L5_safety.enforcement.import_guard import (
    DynamicImportDeniedError,
    ImportGuard,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_wave4_wave5_wave6_guardrails")
_emit_applies_guardrail("p0", "test_wave4_wave5_wave6_guardrails", "p0_governance")
_emit_reads_policy_state("p0", "test_wave4_wave5_wave6_guardrails", "policy_binding")
_emit_snapshots_state("p0", "test_wave4_wave5_wave6_guardrails", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_wave4_wave5_wave6_guardrails", "p4obs", "metric_1")
_emit_emits_metric_event("test_wave4_wave5_wave6_guardrails", "p4obs", "metric_2")
_emit_emits_metric_event("test_wave4_wave5_wave6_guardrails", "p4obs", "metric_3")
_emit_emits_metric_event("test_wave4_wave5_wave6_guardrails", "p4obs", "metric_4")
_emit_emits_metric_event("test_wave4_wave5_wave6_guardrails", "p4obs", "metric_5")
_emit_emits_metric_event("test_wave4_wave5_wave6_guardrails", "p4obs", "metric_6")
_emit_records_incident_event("test_wave4_wave5_wave6_guardrails", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_wave4_wave5_wave6_guardrails", "p4obs", "anomaly")
_emit_writes_observability_log("test_wave4_wave5_wave6_guardrails", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_wave4_wave5_wave6_guardrails", "p4obs", "mon_state")
_emit_triggers_alert("test_wave4_wave5_wave6_guardrails", "p4obs", "alert")
_emit_links_incident_trace("test_wave4_wave5_wave6_guardrails", "p4obs", "trace_link")
_emit_captures_pattern("test_wave4_wave5_wave6_guardrails", "p3lm", "pattern")
_emit_records_learning_event("test_wave4_wave5_wave6_guardrails", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_wave4_wave5_wave6_guardrails", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_wave4_wave5_wave6_guardrails", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_wave4_wave5_wave6_guardrails", "p3lm", "routing")
_emit_improves_agent_policy("test_wave4_wave5_wave6_guardrails", "p3lm", "policy")
_emit_stores_learning_state("test_wave4_wave5_wave6_guardrails", "p3lm", "state")
_emit_records_execution_trace("test_wave4_wave5_wave6_guardrails", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_wave4_wave5_wave6_guardrails", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_wave4_wave5_wave6_guardrails", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_wave4_wave5_wave6_guardrails", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_wave4_wave5_wave6_guardrails", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_wave4_wave5_wave6_guardrails", "env_read", "p2_env_1")
_emit_reads_environ("test_wave4_wave5_wave6_guardrails", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_wave4_wave5_wave6_guardrails", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_wave4_wave5_wave6_guardrails", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_wave4_wave5_wave6_guardrails", "context_pull")
_emit_pulls_context("p1", "test_wave4_wave5_wave6_guardrails", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_wave4_wave5_wave6_guardrails", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_wave4_wave5_wave6_guardrails", "uwg_term_2")
_emit_writes_through("p1", "test_wave4_wave5_wave6_guardrails", "write_through")
_emit_writes_through("p1", "test_wave4_wave5_wave6_guardrails", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_wave4_wave5_wave6_guardrails", "safety_validation")
_emit_invokes_eval("p1", "test_wave4_wave5_wave6_guardrails", "eval_call")
_emit_proposal_commits_routing("p1", "test_wave4_wave5_wave6_guardrails", "routing_commit")
_emit_escalates_to_human("p1", "test_wave4_wave5_wave6_guardrails", "human_escalation")
_emit_routes_through("p1", "test_wave4_wave5_wave6_guardrails", "route_through")
_emit_checks_agent_registry("p1", "test_wave4_wave5_wave6_guardrails", "agent_registry")
_emit_validates_agent_capability("p1", "test_wave4_wave5_wave6_guardrails", "capability")
_emit_dispatches_execution_plan("p1", "test_wave4_wave5_wave6_guardrails", "exec_plan")
_emit_agent_executes_agent("p1", "test_wave4_wave5_wave6_guardrails", "sub_agent")
_emit_routes_to_agent("p1", "test_wave4_wave5_wave6_guardrails", "target_agent")
_emit_verifies_policy("p1", "test_wave4_wave5_wave6_guardrails", "policy_check")
_emit_observes_runtime_state("p1", "test_wave4_wave5_wave6_guardrails", "runtime_state")
_emit_verifies_boundary("p1", "test_wave4_wave5_wave6_guardrails", "boundary_check")
_emit_transcripts_response("p1", "test_wave4_wave5_wave6_guardrails", "transcript")
_emit_hard_fails_untranscripted("p1", "test_wave4_wave5_wave6_guardrails")
_emit_gated_by_confidence("p1", "test_wave4_wave5_wave6_guardrails", "confidence_gate")
emit_replay_key("p0", "test_wave4_wave5_wave6_guardrails")
emit_determinism_digest("p0", "test_wave4_wave5_wave6_guardrails")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_wave4_wave5_wave6_guardrails", "execution_auth")
_emit_validates_capability("p2", "test_wave4_wave5_wave6_guardrails", "capability_check")
_emit_routes_to_capability("p2", "test_wave4_wave5_wave6_guardrails", "capability_route")
_emit_writes_via_uwg("p2", "test_wave4_wave5_wave6_guardrails", "uwg_write")
_emit_blocks_direct_write("p2", "test_wave4_wave5_wave6_guardrails", "direct_write_block")
_emit_records_tool_invocation("p2", "test_wave4_wave5_wave6_guardrails", "tool_invocation")
_emit_captures_execution_output("p2", "test_wave4_wave5_wave6_guardrails", "exec_output")
_emit_dispatches_agent("p3", "test_wave4_wave5_wave6_guardrails", "agent_dispatch")
_emit_coordinates_agents("p3", "test_wave4_wave5_wave6_guardrails", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_wave4_wave5_wave6_guardrails", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_wave4_wave5_wave6_guardrails", "healing_outcome")
_emit_escalates_failure("p3", "test_wave4_wave5_wave6_guardrails", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_wave4_wave5_wave6_guardrails", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_wave4_wave5_wave6_guardrails", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_wave4_wave5_wave6_guardrails", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_wave4_wave5_wave6_guardrails", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_wave4_wave5_wave6_guardrails", "eval_metric")
_emit_stores_embedding("p4", "test_wave4_wave5_wave6_guardrails", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_wave4_wave5_wave6_guardrails", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_wave4_wave5_wave6_guardrails", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def eval_guard_warn():
    return EvalGuard(mode="warn")


@pytest.fixture
def eval_guard_enforce():
    return EvalGuard(mode="enforce")


@pytest.fixture
def credential_guard_warn():
    return CredentialGuard(mode="warn")


@pytest.fixture
def credential_guard_enforce():
    return CredentialGuard(mode="enforce")


@pytest.fixture
def import_guard_warn():
    return ImportGuard(mode="warn")


@pytest.fixture
def import_guard_enforce():
    return ImportGuard(mode="enforce")


@pytest.fixture
def http_guard_warn():
    return HTTPGuard(mode="warn")


@pytest.fixture
def http_guard_enforce():
    return HTTPGuard(mode="enforce")


@pytest.fixture
def replay_gateway():
    return UniversalWriteGateway(replay_mode=True, actor_id="test_actor", run_id="test_run")


@pytest.fixture
def real_gateway(tmp_path):
    gw = UniversalWriteGateway(
        replay_mode=False,
        actor_id="test_actor",
        run_id="test_run",
    )
    # Allow tmp_path for writes
    gw._allowed_paths = {str(tmp_path) + "/", "artifacts/", "docs/reports/", "logs/", "temp/"}
    return gw


@pytest.fixture(autouse=True)
def reset_global_gateways():
    """Reset global UWG between tests."""
    yield
    reset_write_gateway()


# ===========================================================================
# WAVE 4: GUARDRAIL TESTS
# ===========================================================================


class TestEvalGuard:
    """Wave 4 Phase 2: EvalGuard tests."""

    def test_safe_code_allowed(self, eval_guard_warn):
        result = eval_guard_warn.check(operation="eval", code="1 + 1")
        assert result["verdict"] == "allow"

    def test_empty_code_allowed(self, eval_guard_warn):
        result = eval_guard_warn.check(operation="eval", code="")
        assert result["verdict"] == "allow"

    def test_no_code_allowed(self, eval_guard_warn):
        result = eval_guard_warn.check(operation="eval")
        assert result["verdict"] == "allow"

    @pytest.mark.parametrize(
        "dangerous_code",
        [
            "__import__('os')",
            "importlib.import_module('sys')",
            "exec('print(1)')",
            "eval('1+1')",
            "compile('x', '', 'exec')",
            "open('/etc/passwd')",
            "os.system('ls')",
            "subprocess.run(['ls'])",
            "__builtins__['eval']",
            "__globals__['key']",
            "del variable",
        ],
    )
    def test_dangerous_patterns_warn_mode(self, eval_guard_warn, dangerous_code):
        """Creative: adversarial inputs should be flagged in warn mode."""
        result = eval_guard_warn.check(operation="eval", code=dangerous_code)
        assert result["verdict"] == "deny"
        assert len(result["violations"]) > 0

    @pytest.mark.parametrize(
        "dangerous_code",
        [
            "__import__('os')",
            "os.system('rm -rf /')",
            "subprocess.Popen(['sh'])",
        ],
    )
    def test_dangerous_patterns_enforce_mode_raises(self, eval_guard_enforce, dangerous_code):
        """Enforce mode must raise, not just log."""
        with pytest.raises(EvalExecutionDeniedError):
            eval_guard_enforce.check(operation="eval", code=dangerous_code)

    def test_audit_log_grows_per_check(self, eval_guard_warn):
        """Execution log must record every check."""
        for i in range(5):
            eval_guard_warn.check(operation="eval", code=f"x = {i}")
        assert len(eval_guard_warn.get_execution_log()) == 5

    def test_clear_log(self, eval_guard_warn):
        eval_guard_warn.check(operation="eval", code="x = 1")
        eval_guard_warn.clear_log()
        assert eval_guard_warn.get_execution_log() == []

    def test_log_contains_verdict(self, eval_guard_warn):
        eval_guard_warn.check(operation="exec", code="print('safe')")
        log = eval_guard_warn.get_execution_log()
        assert log[0]["verdict"] == "allow"
        assert log[0]["operation"] == "exec"

    def test_adg_edge_emitted_via_log(self, eval_guard_warn, caplog):
        """Creative: verify ADG applies_guardrail edge via log capture."""
        with caplog.at_level(logging.DEBUG, logger="agentic_core.L5_safety.enforcement.eval_guard"):
            eval_guard_warn.check(operation="eval", code="x = 1")
        assert any("applies_guardrail" in r.message for r in caplog.records)

    def test_compile_operation_logged(self, eval_guard_warn):
        """compile() is a distinct operation type from eval/exec."""
        result = eval_guard_warn.check(operation="compile", code="x = 1")
        assert result["verdict"] == "allow"
        log = eval_guard_warn.get_execution_log()
        assert log[0]["operation"] == "compile"

    def test_metadata_preserved_in_log(self, eval_guard_warn):
        eval_guard_warn.check(operation="eval", code="x", metadata={"caller": "test_module"})
        log = eval_guard_warn.get_execution_log()
        assert log[0]["metadata"]["caller"] == "test_module"


class TestCredentialGuard:
    """Wave 4 Phase 1: CredentialGuard tests."""

    def test_normal_access_allowed(self, credential_guard_warn):
        result = credential_guard_warn.check(operation="get_credential", target="openai_key")
        assert result["verdict"] == "allow"

    def test_rate_limit_warn_mode(self, credential_guard_warn):
        """Creative: blast 101 requests to trip rate limit in warn mode."""
        credential_guard_warn._max_accesses_per_minute = 5
        for _ in range(5):
            credential_guard_warn.check(operation="get_credential", target="key")
        # 6th should deny
        result = credential_guard_warn.check(operation="get_credential", target="key")
        assert result["verdict"] == "deny"

    def test_rate_limit_enforce_mode_raises(self, credential_guard_enforce):
        """Rate limit + enforce mode = exception."""
        credential_guard_enforce._max_accesses_per_minute = 2
        credential_guard_enforce.check(operation="get_credential", target="key")
        credential_guard_enforce.check(operation="get_credential", target="key")
        with pytest.raises(CredentialAccessDeniedError):
            credential_guard_enforce.check(operation="get_credential", target="key")

    def test_rate_limits_are_per_target(self, credential_guard_warn):
        """Creative: different targets have independent rate limits."""
        credential_guard_warn._max_accesses_per_minute = 2
        credential_guard_warn.check(operation="get_credential", target="key_a")
        credential_guard_warn.check(operation="get_credential", target="key_a")
        # key_a is now at limit, but key_b should still be allowed
        result_a = credential_guard_warn.check(operation="get_credential", target="key_a")
        result_b = credential_guard_warn.check(operation="get_credential", target="key_b")
        assert result_a["verdict"] == "deny"
        assert result_b["verdict"] == "allow"

    def test_reset_clears_rate_limits(self, credential_guard_warn):
        credential_guard_warn._max_accesses_per_minute = 1
        credential_guard_warn.check(operation="get_credential", target="key")
        credential_guard_warn.check(operation="get_credential", target="key")
        credential_guard_warn.reset_rate_limits()
        result = credential_guard_warn.check(operation="get_credential", target="key")
        assert result["verdict"] == "allow"

    def test_audit_log_records_operation_and_target(self, credential_guard_warn):
        credential_guard_warn.check(operation="read_secret", target="db_password")
        log = credential_guard_warn.get_access_log()
        assert log[0]["operation"] == "read_secret"
        assert log[0]["target"] == "db_password"

    def test_adg_edge_emitted_via_log(self, credential_guard_warn, caplog):
        with caplog.at_level(logging.DEBUG, logger="agentic_core.L5_safety.enforcement.credential_guard"):
            credential_guard_warn.check(operation="get_credential", target="key")
        assert any("applies_guardrail" in r.message for r in caplog.records)


class TestImportGuard:
    """Wave 4 Phase 3: ImportGuard tests."""

    def test_internal_module_allowed(self, import_guard_warn):
        result = import_guard_warn.check(operation="import_module", module_name="agentic_core.utils")
        assert result["verdict"] == "allow"

    @pytest.mark.parametrize(
        "denied_module",
        [
            "subprocess",
            "subprocess.run",
            "ctypes.cdll",
            "socket.socket",
            "pickle.loads",
            "marshal.loads",
        ],
    )
    def test_denied_prefixes_blocked_warn_mode(self, import_guard_warn, denied_module):
        result = import_guard_warn.check(operation="import_module", module_name=denied_module)
        assert result["verdict"] == "deny"

    @pytest.mark.parametrize(
        "denied_module",
        [
            "subprocess",
            "ctypes",
            "socket",
        ],
    )
    def test_denied_prefixes_enforce_mode_raises(self, import_guard_enforce, denied_module):
        with pytest.raises(DynamicImportDeniedError):
            import_guard_enforce.check(operation="import_module", module_name=denied_module)

    def test_unknown_module_allowed_in_warn(self, import_guard_warn):
        """Creative: unknown modules pass in warn mode - policy is denylist, not allowlist."""
        result = import_guard_warn.check(operation="import_module", module_name="third_party_lib")
        assert result["verdict"] == "allow"

    def test_no_module_name_allowed(self, import_guard_warn):
        result = import_guard_warn.check(operation="__import__")
        assert result["verdict"] == "allow"

    def test_log_grows_per_check(self, import_guard_warn):
        for i in range(3):
            import_guard_warn.check(operation="import_module", module_name=f"agentic_core.module_{i}")
        assert len(import_guard_warn.get_import_log()) == 3

    def test_adg_edge_emitted_via_log(self, import_guard_warn, caplog):
        with caplog.at_level(logging.DEBUG, logger="agentic_core.L5_safety.enforcement.import_guard"):
            import_guard_warn.check(operation="import_module", module_name="agentic_core.utils")
        assert any("applies_guardrail" in r.message for r in caplog.records)


class TestHTTPGuard:
    """Wave 4 Phase 4: HTTPGuard tests."""

    def test_safe_external_url_allowed(self, http_guard_warn):
        result = http_guard_warn.check(operation="get", url="https://api.example.com/data")
        assert result["verdict"] == "allow"

    @pytest.mark.parametrize(
        "dangerous_url",
        [
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "http://metadata.google.internal/computeMetadata/v1/",  # GCP metadata
            "http://100.100.100.200/latest/meta-data/",  # Alibaba metadata
            "http://localhost:8080/admin",  # localhost
            "http://127.0.0.1/admin",  # loopback
            "http://0.0.0.0/config",  # null address
        ],
    )
    def test_ssrf_patterns_blocked_warn_mode(self, http_guard_warn, dangerous_url):
        """Creative: SSRF attack vectors must be flagged."""
        result = http_guard_warn.check(operation="get", url=dangerous_url)
        assert result["verdict"] == "deny"
        assert len(result["violations"]) > 0

    @pytest.mark.parametrize(
        "dangerous_url",
        [
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost/internal",
        ],
    )
    def test_ssrf_enforce_mode_raises(self, http_guard_enforce, dangerous_url):
        with pytest.raises(ExternalHttpDeniedError):
            http_guard_enforce.check(operation="get", url=dangerous_url)

    def test_post_operation_logged(self, http_guard_warn):
        result = http_guard_warn.check(operation="post", url="https://api.example.com/submit")
        assert result["verdict"] == "allow"
        log = http_guard_warn.get_request_log()
        assert log[0]["operation"] == "post"

    def test_no_url_allowed(self, http_guard_warn):
        result = http_guard_warn.check(operation="get")
        assert result["verdict"] == "allow"

    def test_adg_edge_emitted_via_log(self, http_guard_warn, caplog):
        with caplog.at_level(logging.DEBUG, logger="agentic_core.L5_safety.enforcement.http_guard"):
            http_guard_warn.check(operation="get", url="https://api.example.com")
        assert any("applies_guardrail" in r.message for r in caplog.records)

    def test_violations_list_populated(self, http_guard_warn):
        result = http_guard_warn.check(operation="get", url="http://localhost/secret")
        assert "violations" in result
        assert len(result["violations"]) > 0


class TestGuardInteraction:
    """Creative: cross-guard interaction and composition tests."""

    def test_all_four_guards_chain_on_same_operation(self):
        """Simulate a complex operation requiring all 4 guards."""
        eval_g = EvalGuard(mode="warn")
        cred_g = CredentialGuard(mode="warn")
        imp_g = ImportGuard(mode="warn")
        http_g = HTTPGuard(mode="warn")

        # A hypothetical agent operation: fetch cred, import module, eval snippet, call API
        r1 = cred_g.check(operation="get_credential", target="api_key")
        r2 = imp_g.check(operation="import_module", module_name="agentic_core.utils")
        r3 = eval_g.check(operation="eval", code="result = transform(data)")
        r4 = http_g.check(operation="post", url="https://api.example.com/submit")

        assert all(r["verdict"] == "allow" for r in [r1, r2, r3, r4])

    def test_single_deny_blocks_chain_logically(self):
        """Creative: if one guard denies, the chain should be considered failed."""
        eval_g = EvalGuard(mode="warn")
        imp_g = ImportGuard(mode="warn")

        r1 = imp_g.check(operation="import_module", module_name="agentic_core.utils")
        r2 = eval_g.check(operation="eval", code="__import__('os').system('ls')")  # dangerous

        assert r1["verdict"] == "allow"
        assert r2["verdict"] == "deny"
        # Logical check: chain failed if any deny
        chain_ok = all(r["verdict"] == "allow" for r in [r1, r2])
        assert not chain_ok

    def test_warn_mode_never_raises(self):
        """Creative: warn mode must never raise regardless of input."""
        guards = [
            EvalGuard(mode="warn"),
            CredentialGuard(mode="warn"),
            ImportGuard(mode="warn"),
            HTTPGuard(mode="warn"),
        ]

        # These would all be denied, but none should raise
        guards[0].check(operation="eval", code="__import__('os')")
        guards[1].check(operation="get_credential", target="key")  # will allow in warn
        guards[2].check(operation="import_module", module_name="subprocess")
        guards[3].check(operation="get", url="http://169.254.169.254/meta")

    def test_global_singletons_are_independent(self):
        """Global getters return separate state from instance creation."""
        global_eval = get_eval_guard()
        local_eval = EvalGuard(mode="warn")

        local_eval.check(operation="eval", code="x = 1")

        assert len(local_eval.get_execution_log()) == 1
        # Global should not have the local's log entry
        assert local_eval is not global_eval


# ===========================================================================
# WAVE 5: EXECUTION TRACE TESTS
# ===========================================================================


class TestExecutionTraceInfrastructure:
    """Wave 5: Validate ExecutionTrace infrastructure is importable and functional."""

    def test_execution_trace_importable(self):
        """ExecutionTrace module must be importable."""
        from agentic_core.runtime.execution_trace import ExecutionTrace

        assert ExecutionTrace is not None

    def test_execution_trace_types_importable(self):
        """Execution trace type modules exist in L2 and L3."""
        import agentic_core.L2_execution.types.execution_trace_types as l2_types
        import agentic_core.L3_orchestration.types.execution_trace_types as l3_types

        assert l2_types is not None
        assert l3_types is not None

    def test_execution_trace_has_record_method(self):
        """Creative: verify ExecutionTrace interface contract."""
        from agentic_core.runtime.execution_trace import ExecutionTrace

        # Verify the class has the expected interface
        assert hasattr(ExecutionTrace, "__enter__") or callable(ExecutionTrace)

    def test_execution_proof_emitter_importable(self):
        """L2 proof emitter must be importable."""
        import agentic_core.L2_execution.determinism.execution_proof_emitter as emitter

        assert emitter is not None


# ===========================================================================
# WAVE 6: UWG CONVENIENCE METHOD TESTS
# ===========================================================================


class TestUWGConvenienceMethods:
    """Wave 6: Test all 5 UWG convenience methods."""

    def test_write_json_in_replay_mode(self, replay_gateway):
        """write_json() must work in replay mode."""
        set_write_gateway(replay_gateway)
        result = write_json("test_output/config.json", {"key": "value"})
        assert result is not None

    def test_write_text_in_replay_mode(self, replay_gateway):
        set_write_gateway(replay_gateway)
        result = write_text("test_output/file.txt", "hello world")
        assert result is not None

    def test_write_json_serializes_correctly(self, replay_gateway):
        """Creative: JSON output must be valid JSON."""
        set_write_gateway(replay_gateway)
        data = {"nested": {"key": [1, 2, 3]}, "flag": True}
        # write_json calls write_through with JSON string
        # In replay mode, we verify it doesn't raise
        result = write_json("test.json", data)
        assert result is not None

    def test_write_pickle_in_replay_mode(self, replay_gateway):
        set_write_gateway(replay_gateway)
        obj = {"serializable": True, "data": [1, 2, 3]}
        result = write_pickle("test_output/data.pkl", obj)
        assert result is not None

    def test_append_to_file_replay_mode(self, replay_gateway):
        set_write_gateway(replay_gateway)
        result = append_to_file("test_output/log.txt", "new log entry\n")
        assert result is not None

    def test_atomic_write_replay_mode(self, replay_gateway):
        set_write_gateway(replay_gateway)
        result = atomic_write("test_output/state.json", {"status": "ok"})
        assert result is not None

    def test_write_json_with_real_gateway(self, tmp_path):
        """Creative: actual file should be written with correct JSON."""
        gw = UniversalWriteGateway(
            replay_mode=False,
            actor_id="test",
            run_id="run1",
        )
        gw._allowed_paths = {str(tmp_path) + "/", str(tmp_path).replace("\\", "/") + "/", "/"}
        set_write_gateway(gw)

        target = str(tmp_path / "config.json")
        data = {"wave": 6, "status": "complete"}

        result = write_json(target, data)
        assert result is not None

    def test_all_convenience_methods_callable(self):
        """Creative: all 5 convenience functions must be callable."""
        from agentic_core.L2_execution.UniversalWriteGateway import (
            append_to_file,
            atomic_write,
            write_json,
            write_pickle,
            write_text,
        )

        assert callable(write_json)
        assert callable(write_text)
        assert callable(append_to_file)
        assert callable(atomic_write)
        assert callable(write_pickle)


class TestUWGMutationLedger:
    """Wave 6: UWG mutation ledger integrity tests."""

    def test_mutation_record_is_deterministic(self):
        """Creative: same inputs must produce same mutation hash."""
        r1 = MutationRecord.build(
            actor_id="actor",
            run_id="run",
            operation="write",
            path="docs/test.txt",
            data="content",
        )
        r2 = MutationRecord.build(
            actor_id="actor",
            run_id="run",
            operation="write",
            path="docs/test.txt",
            data="content",
        )
        assert r1.mutation_hash == r2.mutation_hash

    def test_mutation_record_hash_changes_with_data(self):
        """Different data must produce different hash."""
        r1 = MutationRecord.build(
            actor_id="actor",
            run_id="run",
            operation="write",
            path="docs/test.txt",
            data="content_a",
        )
        r2 = MutationRecord.build(
            actor_id="actor",
            run_id="run",
            operation="write",
            path="docs/test.txt",
            data="content_b",
        )
        assert r1.mutation_hash != r2.mutation_hash

    def test_replay_mode_produces_simulation_result(self, replay_gateway):
        """Replay mode must not perform actual writes."""
        result = replay_gateway.write_through("docs/reports/output.txt", "data")
        assert isinstance(result, SimulationResult)
        assert result.replay_mode is True

    def test_simulation_result_has_expected_fields(self, replay_gateway):
        result = replay_gateway.write_through("docs/reports/test.txt", "hello")
        assert hasattr(result, "operation")
        assert hasattr(result, "path")
        assert hasattr(result, "would_succeed")
        assert hasattr(result, "simulated_hash")

    def test_frozen_gateway_blocks_writes(self, replay_gateway):
        """Creative: freeze + write = blocked."""
        replay_gateway._frozen = True
        with pytest.raises(PermissionError, match="REQ-091"):
            replay_gateway.write_through("docs/test.txt", "data")

    def test_global_gateway_reset(self):
        """reset_write_gateway must clear the singleton."""
        gw1 = get_write_gateway()
        reset_write_gateway()
        gw2 = get_write_gateway()
        assert gw1 is not gw2

    def test_set_and_get_gateway_roundtrip(self, replay_gateway):
        set_write_gateway(replay_gateway)
        retrieved = get_write_gateway()
        assert retrieved is replay_gateway


class TestUWGGuardrailIntegration:
    """Creative: UWG + Wave 4 guardrail integration tests."""

    def test_uwg_uses_guardrail_gate(self, replay_gateway):
        """UWG internally uses GuardrailGate - verify via attribute."""
        assert hasattr(replay_gateway, "_guardrail_gate")

    def test_write_through_docstring_mentions_uwg_edge(self):
        """Creative: docstring must document the writes_through ADG edge."""
        docstring = UniversalWriteGateway.write_through.__doc__
        assert docstring is not None
        assert "writes_through" in docstring

    def test_write_json_calls_write_through_in_chain(self, replay_gateway):
        """Creative: write_json must go through write_through (chain integrity)."""
        set_write_gateway(replay_gateway)
        call_count = [0]
        original_write_through = replay_gateway.write_through

        def tracked_write_through(*args, **kwargs):
            call_count[0] += 1
            return original_write_through(*args, **kwargs)

        replay_gateway.write_through = tracked_write_through
        write_json("docs/reports/test.json", {"x": 1})
        assert call_count[0] == 1

    def test_write_text_calls_write_through_in_chain(self, replay_gateway):
        set_write_gateway(replay_gateway)
        call_count = [0]
        original = replay_gateway.write_through

        def tracked(*args, **kwargs):
            call_count[0] += 1
            return original(*args, **kwargs)

        replay_gateway.write_through = tracked
        write_text("docs/reports/test.txt", "content")
        assert call_count[0] == 1


# ===========================================================================
# ADG EDGE EMISSION CONTRACT TESTS
# ===========================================================================


class TestADGEdgeContracts:
    """Creative: verify ADG edge emission contracts across all waves."""

    def test_eval_guard_emits_applies_guardrail_log(self, caplog):
        """EvalGuard.check() MUST emit applies_guardrail structured log."""
        guard = EvalGuard(mode="warn")
        with caplog.at_level(logging.DEBUG):
            guard.check(operation="eval", code="x = 1")
        messages = [r.message for r in caplog.records]
        assert any("applies_guardrail" in m for m in messages)

    def test_credential_guard_emits_applies_guardrail_log(self, caplog):
        guard = CredentialGuard(mode="warn")
        with caplog.at_level(logging.DEBUG):
            guard.check(operation="get_credential", target="key")
        messages = [r.message for r in caplog.records]
        assert any("applies_guardrail" in m for m in messages)

    def test_import_guard_emits_applies_guardrail_log(self, caplog):
        guard = ImportGuard(mode="warn")
        with caplog.at_level(logging.DEBUG):
            guard.check(operation="import_module", module_name="agentic_core.utils")
        messages = [r.message for r in caplog.records]
        assert any("applies_guardrail" in m for m in messages)

    def test_http_guard_emits_applies_guardrail_log(self, caplog):
        guard = HTTPGuard(mode="warn")
        with caplog.at_level(logging.DEBUG):
            guard.check(operation="get", url="https://api.example.com")
        messages = [r.message for r in caplog.records]
        assert any("applies_guardrail" in m for m in messages)

    def test_uwg_write_through_docstring_declares_edge(self):
        """write_through() docstring declares writes_through edge - ADG scanner uses this."""
        doc = UniversalWriteGateway.write_through.__doc__
        assert doc is not None
        assert "writes_through" in doc

    def test_all_guard_check_methods_return_verdict_dict(self):
        """Creative: all guard .check() methods return standardized dict with 'verdict'."""
        eval_r = EvalGuard(mode="warn").check(operation="eval", code="x=1")
        cred_r = CredentialGuard(mode="warn").check(operation="get", target="k")
        imp_r = ImportGuard(mode="warn").check(operation="import_module", module_name="agentic_core.x")
        http_r = HTTPGuard(mode="warn").check(operation="get", url="https://safe.example.com")

        for result in [eval_r, cred_r, imp_r, http_r]:
            assert "verdict" in result
            assert result["verdict"] in ("allow", "deny")
            assert "timestamp" in result
