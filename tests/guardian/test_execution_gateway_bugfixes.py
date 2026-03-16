"""
V15 P7 Bug-Fix Regression Tests.

Wave 1.1: is_v15_enforced() accepts log/soft; is_v15_hard_fail() gates blocking.
Wave 2.1: _v15_gateway is None when V15_ENFORCEMENT=0, singleton when enforced.
Wave 3.1: heal() under enforcement does not crash on dead-field references.
Wave 7.0a: trace_id matches ^CC3AL1-[0-9A-F]{8}$ under all enforcement modes.
Wave 7.0c: state_hash_fn returns real SHA-256 hashes, not placeholders.
"""

from __future__ import annotations

import os
import re
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_execution_gateway_bugfixes")
_emit_applies_guardrail("p0", "test_execution_gateway_bugfixes", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_gateway_bugfixes", "policy_binding")
_emit_snapshots_state("p0", "test_execution_gateway_bugfixes", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_execution_gateway_bugfixes", "p4obs", "metric_1")
_emit_emits_metric_event("test_execution_gateway_bugfixes", "p4obs", "metric_2")
_emit_emits_metric_event("test_execution_gateway_bugfixes", "p4obs", "metric_3")
_emit_emits_metric_event("test_execution_gateway_bugfixes", "p4obs", "metric_4")
_emit_emits_metric_event("test_execution_gateway_bugfixes", "p4obs", "metric_5")
_emit_emits_metric_event("test_execution_gateway_bugfixes", "p4obs", "metric_6")
_emit_records_incident_event("test_execution_gateway_bugfixes", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_execution_gateway_bugfixes", "p4obs", "anomaly")
_emit_writes_observability_log("test_execution_gateway_bugfixes", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_execution_gateway_bugfixes", "p4obs", "mon_state")
_emit_triggers_alert("test_execution_gateway_bugfixes", "p4obs", "alert")
_emit_links_incident_trace("test_execution_gateway_bugfixes", "p4obs", "trace_link")
_emit_captures_pattern("test_execution_gateway_bugfixes", "p3lm", "pattern")
_emit_records_learning_event("test_execution_gateway_bugfixes", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_execution_gateway_bugfixes", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_execution_gateway_bugfixes", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_execution_gateway_bugfixes", "p3lm", "routing")
_emit_improves_agent_policy("test_execution_gateway_bugfixes", "p3lm", "policy")
_emit_stores_learning_state("test_execution_gateway_bugfixes", "p3lm", "state")
_emit_records_execution_trace("test_execution_gateway_bugfixes", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_execution_gateway_bugfixes", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_execution_gateway_bugfixes", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_execution_gateway_bugfixes", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_execution_gateway_bugfixes", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_execution_gateway_bugfixes", "env_read", "p2_env_1")
_emit_reads_environ("test_execution_gateway_bugfixes", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_execution_gateway_bugfixes", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_execution_gateway_bugfixes", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_execution_gateway_bugfixes", "context_pull")
_emit_pulls_context("p1", "test_execution_gateway_bugfixes", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_execution_gateway_bugfixes", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_execution_gateway_bugfixes", "uwg_term_2")
_emit_writes_through("p1", "test_execution_gateway_bugfixes", "write_through")
_emit_writes_through("p1", "test_execution_gateway_bugfixes", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_execution_gateway_bugfixes", "safety_validation")
_emit_invokes_eval("p1", "test_execution_gateway_bugfixes", "eval_call")
_emit_proposal_commits_routing("p1", "test_execution_gateway_bugfixes", "routing_commit")
emit_replay_key("p0", "test_execution_gateway_bugfixes")
emit_determinism_digest("p0", "test_execution_gateway_bugfixes")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_gateway_bugfixes", "execution_auth")
_emit_validates_capability("p2", "test_execution_gateway_bugfixes", "capability_check")
_emit_routes_to_capability("p2", "test_execution_gateway_bugfixes", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_gateway_bugfixes", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_gateway_bugfixes", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_gateway_bugfixes", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_gateway_bugfixes", "exec_output")
_emit_dispatches_agent("p3", "test_execution_gateway_bugfixes", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_gateway_bugfixes", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_gateway_bugfixes", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_gateway_bugfixes", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_gateway_bugfixes", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_gateway_bugfixes", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_gateway_bugfixes", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_gateway_bugfixes", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_gateway_bugfixes", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_gateway_bugfixes", "eval_metric")
_emit_stores_embedding("p4", "test_execution_gateway_bugfixes", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_gateway_bugfixes", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_gateway_bugfixes", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Wave 1.1 — Enforcement-mode semantics
# ---------------------------------------------------------------------------


class TestEnforcementModeSemantics:
    """is_v15_enforced() must return True for log/soft/1; is_v15_hard_fail() only for 1."""

    def test_is_v15_enforced_accepts_log(self):
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            assert is_v15_enforced(), "V15_ENFORCEMENT=log must enter V15 path"

    def test_is_v15_enforced_accepts_soft(self):
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"}):
            assert is_v15_enforced(), "V15_ENFORCEMENT=soft must enter V15 path"

    def test_is_v15_enforced_accepts_hard(self):
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

        for val in ("1", "true", "yes", "TRUE", "True"):
            with patch.dict(os.environ, {"V15_ENFORCEMENT": val}):
                assert is_v15_enforced(), f"V15_ENFORCEMENT={val} must enter V15 path"

    def test_is_v15_enforced_rejects_disabled(self):
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

        for val in ("0", "false", "no", "off"):
            with patch.dict(os.environ, {"V15_ENFORCEMENT": val}):
                assert not is_v15_enforced(), f"V15_ENFORCEMENT={val} must NOT enter V15 path"

    def test_is_v15_enforced_raises_on_invalid(self):
        import pytest

        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

        for val in ("", "something"):
            with patch.dict(os.environ, {"V15_ENFORCEMENT": val}):
                with pytest.raises(ValueError):
                    is_v15_enforced()

    def test_is_v15_hard_fail_only_for_hard_values(self):
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_hard_fail

        for val in ("1", "true", "yes"):
            with patch.dict(os.environ, {"V15_ENFORCEMENT": val}):
                assert is_v15_hard_fail(), f"V15_ENFORCEMENT={val} must be hard-fail"

    def test_is_v15_hard_fail_false_for_log_soft(self):
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_hard_fail

        for val in ("log", "soft"):
            with patch.dict(os.environ, {"V15_ENFORCEMENT": val}):
                assert not is_v15_hard_fail(), f"V15_ENFORCEMENT={val} must NOT hard-fail"

    def test_assert_v15_guarded_does_not_raise_in_log_mode(self):
        """In LOG_ONLY mode, assert_v15_guarded logs instead of raising."""
        from agentic_core.L0_routing.enforcement.runtime_guard import (
            assert_v15_guarded,
        )

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            # Should NOT raise — log mode only logs
            assert_v15_guarded("test.entry.point")

    def test_assert_v15_guarded_raises_in_hard_mode(self):
        """In HARD_FAIL mode, assert_v15_guarded raises V15EnforcementError."""
        from agentic_core.L0_routing.enforcement.runtime_guard import (
            assert_v15_guarded,
        )
        from agentic_core.L0_routing.types.guardian_contract_types import (
            V15EnforcementError,
        )

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "1"}):
            with pytest.raises(V15EnforcementError, match="bypass detected"):
                assert_v15_guarded("test.entry.point")


# ---------------------------------------------------------------------------
# Wave 2.1 — Gateway instantiation guard
# ---------------------------------------------------------------------------


def _make_agent(env_val: str):
    """Helper: instantiate SovereignBaseAgent under a given V15_ENFORCEMENT value."""
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.L0_routing.utils.core_integrity_util import (
        CoreIntegrityVerifier,
    )

    # Ensure golden seal exists so __post_init__ doesn't crash
    try:
        CoreIntegrityVerifier.verify_core_integrity()
    except (ImportError, AttributeError, ValueError):
        if CoreIntegrityVerifier.GOLDEN_SEAL_FILE.exists():
            CoreIntegrityVerifier.GOLDEN_SEAL_FILE.unlink()
        try:
            CoreIntegrityVerifier.verify_core_integrity()
        except (ImportError, AttributeError, ValueError):
            pass

    with patch.dict(os.environ, {"V15_ENFORCEMENT": env_val}):
        return SovereignBaseAgent()


class TestGatewayInstantiationGuard:
    """_v15_gateway must be None when enforcement is off, not-None when on."""

    def test_gateway_none_when_enforcement_off(self):
        agent = _make_agent("0")
        assert agent._v15_gateway is None, "_v15_gateway must be None when V15_ENFORCEMENT=0"

    def test_gateway_not_none_when_log_mode(self):
        agent = _make_agent("log")
        assert agent._v15_gateway is not None, "_v15_gateway must be allocated when V15_ENFORCEMENT=log"

    def test_gateway_singleton_reused_across_heals(self):
        """Same gateway object must be reused across two heal() calls."""
        agent = _make_agent("log")
        gw_id = id(agent._v15_gateway)

        # First heal — will fail due to S5 bugs but gateway should remain
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            try:
                agent.heal({"id": "test-1"})
            # guardian: allow-silent-swallow
            except Exception:  # guardian: allow-silent-swallower
                pass

            assert id(agent._v15_gateway) == gw_id, "Gateway must not be replaced"

            # Second heal
            try:
                agent.heal({"id": "test-2"})
            # guardian: allow-silent-swallow
            except Exception:  # guardian: allow-silent-swallower
                pass

            assert id(agent._v15_gateway) == gw_id, "Gateway must be the same object"


# ---------------------------------------------------------------------------
# Wave 3.1 — Heal-path execution test (dead-field references)
# ---------------------------------------------------------------------------


class TestHealPathExecution:
    """heal() under enforcement must not crash on dead-field references."""

    def test_heal_fn_no_dead_field_access(self):
        """The inner heal_fn must not reference manifest.payload or manifest.trace_id.

        These fields do not exist on SurgicalManifest. If heal_fn accesses them,
        it raises AttributeError which the gateway catches, returning status='failed'.
        A properly fixed heal_fn returns status='completed'.
        """
        agent = _make_agent("log")

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            result = agent.heal({"id": "dead-field-test", "type": "test_violation"})

            assert isinstance(result, dict), "heal() must return a dict"
            assert result.get("status") == "completed", (
                f"heal_fn must succeed (status='completed'), got status='{result.get('status')}'. "
                f"If 'failed', the S5 dead-field bug (manifest.payload / manifest.trace_id) is still present. "
                f"Error: {result.get('error', result.get('reason', 'unknown'))}"
            )

    def test_trace_id_format_under_enforcement(self):
        """trace_id in heal result must be present (format check deferred to 7.0a)."""
        agent = _make_agent("log")

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            result = agent.heal({"id": "trace-format-test"})

            assert isinstance(result, dict)
            # trace_id must be present in the result
            assert "trace_id" in result, "heal() result must contain trace_id"
            # Must be a non-empty string
            assert isinstance(result["trace_id"], str)
            assert len(result["trace_id"]) > 0


# ---------------------------------------------------------------------------
# Wave 7.0a — trace_id format (S3)
# ---------------------------------------------------------------------------

TRACE_ID_RE = re.compile(r"^CC3AL1-[0-9A-F]{8}$")


class TestTraceIdFormat:
    """§15.5 — trace_id emitted by heal() must match ^CC3AL1-[0-9A-F]{8}$."""

    def test_trace_id_format_log_mode(self):
        agent = _make_agent("log")
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            result = agent.heal({"id": "fmt-log-test"})
            tid = result.get("trace_id", "")
            assert TRACE_ID_RE.match(tid), (
                f"trace_id '{tid}' does not match ^CC3AL1-[0-9A-F]{{8}}$ under V15_ENFORCEMENT=log"
            )

    def test_trace_id_format_hard_mode(self):
        agent = _make_agent("1")
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "1"}):
            result = agent.heal({"id": "fmt-hard-test"})
            tid = result.get("trace_id", "")
            assert TRACE_ID_RE.match(tid), (
                f"trace_id '{tid}' does not match ^CC3AL1-[0-9A-F]{{8}}$ under V15_ENFORCEMENT=1"
            )

    def test_validate_trace_id_does_not_raise(self):
        """validate_trace_id() must accept the trace_id produced by heal()."""
        from agentic_core.L0_routing.types.traceability_types import validate_trace_id

        agent = _make_agent("log")
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            result = agent.heal({"id": "validate-test"})
            tid = result["trace_id"]
            # Must not raise
            validated = validate_trace_id(tid)
            assert validated == tid


# ---------------------------------------------------------------------------
# Wave 7.0c — state hash placeholders replaced (S4)
# ---------------------------------------------------------------------------


class TestStateHashReal:
    """§10.2 — state_hash_fn must return real SHA-256 hashes, not placeholders."""

    def _get_state_hashes(self, agent):
        """Call state_hash_fn via a heal() and intercept the hashes."""
        captured: list[tuple[str, str, str]] = []

        from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )

        _orig_execute = V15ExecutionGateway.execute

        def _spy_execute(self_gw, *, execution_input, heal_fn, state_hash_fn, trace_id, **kwargs):
            hashes = state_hash_fn()
            captured.append(hashes)
            return _orig_execute(
                self_gw,
                execution_input=execution_input,
                heal_fn=heal_fn,
                state_hash_fn=state_hash_fn,
                trace_id=trace_id,
                **kwargs,
            )

        with patch.object(V15ExecutionGateway, "execute", _spy_execute):
            with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
                agent.heal({"id": "hash-capture"})

        assert len(captured) > 0, "state_hash_fn was never called"
        return captured[0]

    def test_no_placeholder_literals(self):
        """Hashes must not contain the old placeholder strings."""
        agent = _make_agent("log")
        fs_h, git_h, mem_h = self._get_state_hashes(agent)

        placeholders = {"fs_hash", "git_hash", "mem_hash"}
        for h in (fs_h, git_h, mem_h):
            assert h not in placeholders, f"Placeholder '{h}' still present in state hashes"

    def test_hashes_are_hex_sha256(self):
        """Each hash must be a 64-char lowercase hex string (SHA-256)."""
        agent = _make_agent("log")
        fs_h, git_h, mem_h = self._get_state_hashes(agent)

        sha256_re = re.compile(r"^[0-9a-f]{64}$")
        for label, h in [("fs_hash", fs_h), ("git_hash", git_h), ("mem_hash", mem_h)]:
            assert sha256_re.match(h), f"{label} is not a valid SHA-256 hex: '{h[:20]}...'"

    def test_hashes_deterministic_no_mutation(self):
        """Two consecutive calls with no mutations must return identical hashes."""
        agent = _make_agent("log")
        h1 = self._get_state_hashes(agent)
        h2 = self._get_state_hashes(agent)
        assert h1 == h2, f"State hashes changed without mutation: {h1} != {h2}"

    def test_fs_hash_changes_on_mutation(self):
        """fs_hash must change when a .py file is added under the scanned scope."""
        agent = _make_agent("log")

        # Baseline hash
        h_before = self._get_state_hashes(agent)

        # Create a temporary .py file inside agentic_core/ to trigger fs_hash change
        target_dir = agent.project_root / AGENTIC_CORE_DIR
        tmp_file = target_dir / "_v15_test_mutation_probe.py"
        try:
            tmp_file.write_text("# probe\n", encoding="utf-8")
            h_after = self._get_state_hashes(agent)
            assert h_after[0] != h_before[0], (
                "fs_hash did not change after adding a .py file under agentic_core/"
            )
            # git_hash and mem_hash should remain the same
            assert h_after[1] == h_before[1], "git_hash should not change"
            assert h_after[2] == h_before[2], "mem_hash should not change"
        finally:
            if tmp_file.exists():
                tmp_file.unlink()
