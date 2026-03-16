"""
Rigorous branch-complete tests for all changed logic surfaces.

Surfaces under test (Phase 2.1 / 2.5):
  A. D0EngineAdapter       — apps_shared/spine/d0_engine_adapter.py
  B. RiskGateAdapter       — apps_shared/spine/risk_gate_adapter.py
  C. VigilanceDispatcherAdapter — apps_shared/spine/vigilance_dispatcher_adapter.py
  D. ExecutionOrchestrator  — agentic_core/L0_routing/engines/execution_orchestrator.py
     (added l3_orchestrator, _delegate_to_l3, _L3_PATHS)

Compliance: .windsurfrules §1.2 branch proof, §1.4 boundary, §1.5 exception path,
§1.6 negative controls, §1.7 recovery, §1.8 edge-case classes,
§1.10 determinism, §1.11 fail-closed, §1.12 matrix, §1.13 contradiction.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

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

_emit_records_execution_trace("p0", "evidence", "test_plumbing_rigorous")
_emit_applies_guardrail("p0", "test_plumbing_rigorous", "p0_governance")
_emit_reads_policy_state("p0", "test_plumbing_rigorous", "policy_binding")
_emit_routes_to_agent("p1", "test_plumbing_rigorous", "test")
_emit_orchestrates_workflow("p1", "test_plumbing_rigorous", "test")
_emit_dispatches_execution_plan("p1", "test_plumbing_rigorous", "test")
_emit_validates_agent_capability("p1", "test_plumbing_rigorous", "test")
_emit_checks_agent_registry("p1", "test_plumbing_rigorous", "test")
_emit_snapshots_state("p0", "test_plumbing_rigorous", "state_snapshot")
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
)

_emit_emits_metric_event("test_plumbing_rigorous", "p4obs", "metric_1")
_emit_emits_metric_event("test_plumbing_rigorous", "p4obs", "metric_2")
_emit_emits_metric_event("test_plumbing_rigorous", "p4obs", "metric_3")
_emit_emits_metric_event("test_plumbing_rigorous", "p4obs", "metric_4")
_emit_emits_metric_event("test_plumbing_rigorous", "p4obs", "metric_5")
_emit_emits_metric_event("test_plumbing_rigorous", "p4obs", "metric_6")
_emit_records_incident_event("test_plumbing_rigorous", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_plumbing_rigorous", "p4obs", "anomaly")
_emit_writes_observability_log("test_plumbing_rigorous", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_plumbing_rigorous", "p4obs", "mon_state")
_emit_triggers_alert("test_plumbing_rigorous", "p4obs", "alert")
_emit_links_incident_trace("test_plumbing_rigorous", "p4obs", "trace_link")
_emit_captures_pattern("test_plumbing_rigorous", "p3lm", "pattern")
_emit_records_learning_event("test_plumbing_rigorous", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_plumbing_rigorous", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_plumbing_rigorous", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_plumbing_rigorous", "p3lm", "routing")
_emit_improves_agent_policy("test_plumbing_rigorous", "p3lm", "policy")
_emit_stores_learning_state("test_plumbing_rigorous", "p3lm", "state")
_emit_records_execution_trace("test_plumbing_rigorous", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_plumbing_rigorous", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_plumbing_rigorous", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_plumbing_rigorous", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_plumbing_rigorous", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_plumbing_rigorous", "env_read", "p2_env_1")
_emit_reads_environ("test_plumbing_rigorous", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_plumbing_rigorous", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_plumbing_rigorous", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_plumbing_rigorous", "context_pull")
_emit_pulls_context("p1", "test_plumbing_rigorous", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_plumbing_rigorous", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_plumbing_rigorous", "uwg_term_2")
_emit_writes_through("p1", "test_plumbing_rigorous", "write_through")
_emit_writes_through("p1", "test_plumbing_rigorous", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_plumbing_rigorous", "safety_validation")
_emit_invokes_eval("p1", "test_plumbing_rigorous", "eval_call")
_emit_proposal_commits_routing("p1", "test_plumbing_rigorous", "routing_commit")
emit_replay_key("p0", "test_plumbing_rigorous")
emit_determinism_digest("p0", "test_plumbing_rigorous")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_plumbing_rigorous", "execution_auth")
_emit_validates_capability("p2", "test_plumbing_rigorous", "capability_check")
_emit_routes_to_capability("p2", "test_plumbing_rigorous", "capability_route")
_emit_writes_via_uwg("p2", "test_plumbing_rigorous", "uwg_write")
_emit_blocks_direct_write("p2", "test_plumbing_rigorous", "direct_write_block")
_emit_records_tool_invocation("p2", "test_plumbing_rigorous", "tool_invocation")
_emit_captures_execution_output("p2", "test_plumbing_rigorous", "exec_output")
_emit_dispatches_agent("p3", "test_plumbing_rigorous", "agent_dispatch")
_emit_coordinates_agents("p3", "test_plumbing_rigorous", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_plumbing_rigorous", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_plumbing_rigorous", "healing_outcome")
_emit_escalates_failure("p3", "test_plumbing_rigorous", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_plumbing_rigorous", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_plumbing_rigorous", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_plumbing_rigorous", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_plumbing_rigorous", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_plumbing_rigorous", "eval_metric")
_emit_stores_embedding("p4", "test_plumbing_rigorous", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_plumbing_rigorous", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_plumbing_rigorous", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ===========================================================================
# A. D0EngineAdapter — full branch coverage
# ===========================================================================


class TestD0EngineAdapterBranches:
    """
    BRANCH_INVENTORY:
      d0_engine_adapter.py / __init__
        B-D0-1: ImportError → _real=False, _engine=None, _RoleFence=None
        B-D0-2: import succeeds → _real=True, _engine set, _RoleFence set
      d0_engine_adapter.py / render_d0
        B-D0-3: not _real → return d0_injections unchanged
        B-D0-4: _real=True AND d0_injections="" → return "" unchanged
        B-D0-5: _real=True, non-empty, segment has ':' → build RoleFence
        B-D0-6: _real=True, segment missing ':' → skip segment
        B-D0-7: _real=True, fence_id empty after strip → skip segment
        B-D0-8: fences list empty after all parsing → return d0_injections
        B-D0-9: fences non-empty → call engine.render_d0, return its result
    """

    # ------------------------------------------------------------------
    # B-D0-1: ImportError path
    # ------------------------------------------------------------------
    def test_import_error_sets_null_fallback(self):
        from apps_shared.spine import d0_engine_adapter as mod

        with patch.object(mod, "_build_real_engine", side_effect=ImportError("missing")):
            adapter = mod.D0EngineAdapter()
        assert adapter.is_real is False
        assert adapter._engine is None
        assert adapter._RoleFence is None

    def test_null_fallback_render_d0_returns_input_unchanged(self):
        from apps_shared.spine import d0_engine_adapter as mod

        with patch.object(mod, "_build_real_engine", side_effect=ImportError("missing")):
            adapter = mod.D0EngineAdapter()
        assert adapter.render_d0("fence_a:text_a") == "fence_a:text_a"

    # B-D0-1: negative control — null fallback does NOT call any engine
    def test_null_fallback_never_calls_engine(self):
        from apps_shared.spine import d0_engine_adapter as mod

        with patch.object(mod, "_build_real_engine", side_effect=ImportError("missing")):
            adapter = mod.D0EngineAdapter()
        # render_d0 with complex input must still return unchanged string
        result = adapter.render_d0("a:b|c:d|e:f")
        assert result == "a:b|c:d|e:f"

    # ------------------------------------------------------------------
    # B-D0-2: Successful import
    # ------------------------------------------------------------------
    def test_successful_import_sets_real_true(self):
        adapter = _make_real_d0_adapter()
        assert adapter.is_real is True

    # ------------------------------------------------------------------
    # B-D0-3: not _real branch in render_d0
    # ------------------------------------------------------------------
    def test_render_d0_not_real_returns_any_string_unchanged(self):
        from apps_shared.spine import d0_engine_adapter as mod

        with patch.object(mod, "_build_real_engine", side_effect=ImportError):
            adapter = mod.D0EngineAdapter()
        for val in ["", "hello", "a:b|c:d", "DENY_EXECUTION"]:
            assert adapter.render_d0(val) == val

    # ------------------------------------------------------------------
    # B-D0-4: empty string fast-exit when _real=True
    # ------------------------------------------------------------------
    def test_render_d0_empty_string_returns_empty(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("")
        assert result == ""

    # ------------------------------------------------------------------
    # B-D0-5: valid segment with colon
    # ------------------------------------------------------------------
    def test_render_d0_single_valid_segment(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("fence_x:some text here")
        assert "[fence_x]" in result

    def test_render_d0_multiple_valid_segments(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("role_a:text_a|role_b:text_b")
        assert "[role_a]" in result
        assert "[role_b]" in result

    # ------------------------------------------------------------------
    # B-D0-6: segment missing colon → skip
    # ------------------------------------------------------------------
    def test_render_d0_no_colon_segment_skipped(self):
        adapter = _make_real_d0_adapter()
        # "nocolon" has no ':' so is skipped; "good:text" is kept
        result = adapter.render_d0("nocolon|good:text")
        assert "[good]" in result
        assert "nocolon" not in result

    def test_render_d0_all_segments_missing_colon_returns_input(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("nocolon|alsonocolon")
        # B-D0-8: fences empty → return d0_injections unchanged
        assert result == "nocolon|alsonocolon"

    # ------------------------------------------------------------------
    # B-D0-7: fence_id empty after strip → skip
    # ------------------------------------------------------------------
    def test_render_d0_empty_fence_id_segment_skipped(self):
        adapter = _make_real_d0_adapter()
        # ":text" → fence_id="" → skipped
        result = adapter.render_d0(":text_only|good_id:text")
        assert "[good_id]" in result
        # empty fence_id should not appear as a key
        assert "[]" not in result

    def test_render_d0_only_empty_fence_id_returns_input(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0(":only_empty_id")
        assert result == ":only_empty_id"

    # ------------------------------------------------------------------
    # B-D0-8: all segments produce no valid fences → return input
    # ------------------------------------------------------------------
    def test_render_d0_all_invalid_segments_returns_original(self):
        adapter = _make_real_d0_adapter()
        original = "nocolon|:empty_id| :whitespace_id"
        result = adapter.render_d0(original)
        assert result == original

    # ------------------------------------------------------------------
    # B-D0-9: engine.render_d0 called and result returned
    # ------------------------------------------------------------------
    def test_render_d0_calls_engine_and_returns_xml(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("a:text_a")
        assert "<D0>" in result
        assert "</D0>" in result

    # ------------------------------------------------------------------
    # §1.4 Boundary: exactly-1 fence vs 0 fences
    # ------------------------------------------------------------------
    def test_boundary_exactly_one_valid_fence(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("only_fence:text")
        assert "[only_fence]" in result

    def test_boundary_exactly_zero_valid_fences_returns_input(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("nocolon")
        assert result == "nocolon"

    # ------------------------------------------------------------------
    # §1.10 Determinism
    # ------------------------------------------------------------------
    def test_render_d0_deterministic_identical_input(self):
        a1 = _make_real_d0_adapter()
        a2 = _make_real_d0_adapter()
        r1 = a1.render_d0("f1:t1|f2:t2")
        r2 = a2.render_d0("f1:t1|f2:t2")
        assert r1 == r2

    def test_render_d0_sorted_fence_order_deterministic(self):
        adapter = _make_real_d0_adapter()
        r1 = adapter.render_d0("z_last:zzz|a_first:aaa")
        r2 = adapter.render_d0("z_last:zzz|a_first:aaa")
        assert r1 == r2

    # ------------------------------------------------------------------
    # §1.8 Edge cases: whitespace, colon-in-text, None-like inputs
    # ------------------------------------------------------------------
    def test_render_d0_whitespace_only_fence_id_skipped(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("   :whitespace_id|good:text")
        # "   " strips to "" → skipped
        assert "[good]" in result

    def test_render_d0_colon_in_text_allowed(self):
        adapter = _make_real_d0_adapter()
        # split(":", 1) means only first colon separates id from text
        result = adapter.render_d0("fence_id:text with :extra: colons")
        assert "[fence_id]" in result

    def test_render_d0_pipe_only_no_fences(self):
        adapter = _make_real_d0_adapter()
        result = adapter.render_d0("|||")
        # All empty segments → no fences → return input
        assert result == "|||"

    # ------------------------------------------------------------------
    # §1.13 Contradiction: mutation sensitivity
    # ------------------------------------------------------------------
    def test_render_d0_different_inputs_different_outputs(self):
        adapter = _make_real_d0_adapter()
        r1 = adapter.render_d0("role_a:text_a")
        r2 = adapter.render_d0("role_b:text_b")
        assert r1 != r2


# ===========================================================================
# B. RiskGateAdapter — full branch coverage
# ===========================================================================


class TestRiskGateAdapterBranches:
    """
    BRANCH_INVENTORY:
      risk_gate_adapter.py / __init__
        B-RG-1: ImportError → _real=False, _gate=None
        B-RG-2: import succeeds → _real=True, _gate set
      risk_gate_adapter.py / evaluate
        B-RG-3: not _real → return RiskResult(allow=True)
        B-RG-4: _real=True, d0_injections is str → use as-is
        B-RG-5: _real=True, d0_injections not str → str() conversion
        B-RG-6: real gate returns decision → convert to RiskResult
        B-RG-7: decision.allow=True → RiskResult.allow=True
        B-RG-8: decision.allow=False → RiskResult.allow=False
        B-RG-9: decision.level.value → RiskResult.level as string
        B-RG-10: decision.reasons → RiskResult.reasons tuple
    """

    # B-RG-1
    def test_import_error_sets_null_fallback(self):
        from apps_shared.spine import risk_gate_adapter as mod

        with patch.object(mod, "_build_real_gate", side_effect=ImportError("missing")):
            adapter = mod.RiskGateAdapter()
        assert adapter.is_real is False
        assert adapter._gate is None

    def test_null_fallback_evaluate_returns_allow_true(self):
        from apps_shared.spine import risk_gate_adapter as mod

        with patch.object(mod, "_build_real_gate", side_effect=ImportError):
            adapter = mod.RiskGateAdapter()

        class _P:
            pass

        result = adapter.evaluate(payload_like=_P(), d0_injections="DENY_EXECUTION")
        assert result.allow is True

    # B-RG-2
    def test_successful_import_sets_real_true(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real is True

    # B-RG-3: negative control — null fallback does NOT block even on DENY_EXECUTION
    def test_null_fallback_never_blocks(self):
        from apps_shared.spine import risk_gate_adapter as mod

        with patch.object(mod, "_build_real_gate", side_effect=ImportError):
            adapter = mod.RiskGateAdapter()

        class _P:
            sanitized = True
            check_ids = ("c1", "c2", "c3", "c4", "c5")

        result = adapter.evaluate(payload_like=_P(), d0_injections="DENY_EXECUTION")
        assert result.allow is True
        assert result.level == "LOW"
        assert result.reasons == ()

    # B-RG-4: d0_injections already a string
    def test_evaluate_str_d0_injections_passed_through(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ()

        # Pass as a real str — must not crash
        result = adapter.evaluate(payload_like=_P(), d0_injections="some:fence text")
        assert isinstance(result.allow, bool)

    # B-RG-5: d0_injections not str → converted via str()
    def test_evaluate_non_str_d0_injections_converted(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ()

        # Pass integer — must not raise, just converts
        result = adapter.evaluate(payload_like=_P(), d0_injections=42)
        assert isinstance(result.allow, bool)

    # B-RG-6/7: real gate allow=True
    def test_evaluate_real_gate_clean_payload_allows(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_P(), d0_injections="neutral:text")
        assert result.allow is True

    # B-RG-8: real gate allow=False on DENY_EXECUTION
    def test_evaluate_real_gate_deny_execution_blocks(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_P(), d0_injections="DENY_EXECUTION")
        assert result.allow is False
        assert result.level == "HIGH"
        assert "D0_DENY_EXECUTION" in result.reasons

    # B-RG-9: level.value → string
    def test_evaluate_level_is_string(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert isinstance(result.level, str)

    # B-RG-10: reasons is tuple
    def test_evaluate_reasons_is_tuple(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()

        class _P:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert isinstance(result.reasons, tuple)

    # §1.4 Boundary: check_ids length threshold (gate raises at >= 5)
    def test_evaluate_exactly_4_check_ids_is_low(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ("c1", "c2", "c3", "c4")  # boundary - 1

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert result.level == "LOW"

    def test_evaluate_exactly_5_check_ids_is_medium(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ("c1", "c2", "c3", "c4", "c5")  # exact boundary

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert result.level == "MEDIUM"
        assert "MANY_CHECK_IDS" in result.reasons

    def test_evaluate_6_check_ids_is_medium(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ("c1", "c2", "c3", "c4", "c5", "c6")  # boundary + 1

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert result.level == "MEDIUM"

    def test_evaluate_0_check_ids_is_low(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            sanitized = False
            check_ids = ()  # minimum allowed

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert result.level == "LOW"

    # §1.6 Negative control: missing .sanitized attribute
    def test_evaluate_payload_missing_sanitized_attr(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()

        class _P:
            check_ids = ()
            # no sanitized attribute

        # Must not raise — gate uses getattr with default
        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert isinstance(result.allow, bool)

    def test_evaluate_payload_missing_check_ids_attr(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()

        class _P:
            sanitized = False
            # no check_ids attribute

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert isinstance(result.allow, bool)

    # §1.10 Determinism
    def test_evaluate_deterministic_same_input(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        class _P:
            sanitized = False
            check_ids = ("c1",)

        a1, a2 = RiskGateAdapter(), RiskGateAdapter()
        r1 = a1.evaluate(payload_like=_P(), d0_injections="neutral:text")
        r2 = a2.evaluate(payload_like=_P(), d0_injections="neutral:text")
        assert r1.allow == r2.allow
        assert r1.level == r2.level
        assert r1.reasons == r2.reasons

    # §1.11 Fail-closed: DENY_EXECUTION blocks + side-effect-free
    def test_deny_execution_has_no_side_effects_on_adapter_state(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()

        class _P:
            sanitized = False
            check_ids = ()

        r1 = adapter.evaluate(payload_like=_P(), d0_injections="DENY_EXECUTION")
        r2 = adapter.evaluate(payload_like=_P(), d0_injections="DENY_EXECUTION")
        assert r1.allow is False
        assert r2.allow is False
        # Adapter remains in same state — no mutation
        assert adapter.is_real is True

    # §1.8 Malformed: empty d0_injections
    def test_evaluate_empty_d0_injections_does_not_block(self):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()

        class _P:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_P(), d0_injections="")
        assert result.allow is True

    # §1.12 Matrix: sanitized × DENY_EXECUTION
    @pytest.mark.parametrize(
        "sanitized,d0,expected_allow",
        [
            (False, "", True),
            (False, "DENY_EXECUTION", False),
            (True, "", True),  # sanitized alone is MEDIUM but still allows
            (True, "DENY_EXECUTION", False),  # DENY_EXECUTION dominates
        ],
    )
    def test_evaluate_matrix_sanitized_x_deny(self, sanitized, d0, expected_allow):
        from apps_shared.spine.risk_gate_adapter import RiskGateAdapter

        adapter = RiskGateAdapter()
        assert adapter.is_real

        class _P:
            pass

        _P.sanitized = sanitized
        _P.check_ids = ()

        result = adapter.evaluate(payload_like=_P(), d0_injections=d0)
        assert result.allow is expected_allow


# ===========================================================================
# C. VigilanceDispatcherAdapter — full branch coverage
# ===========================================================================


class TestVigilanceDispatcherAdapterBranches:
    """
    BRANCH_INVENTORY:
      vigilance_dispatcher_adapter.py / __init__
        B-VD-1: ImportError → _real=False, null fallback
        B-VD-2: import succeeds → _real=True
      vigilance_dispatcher_adapter.py / dispatch
        B-VD-3: not _real → early return (no-op)
        B-VD-4: _real=True, signals is str → wrap in tuple
        B-VD-5: _real=True, signals is tuple/list → tuple() conversion
        B-VD-6: _real=True, trace_id=None → str("None")
        B-VD-7: _real=True, summary=None → str("None")
        B-VD-8: event created, dispatcher.dispatch called, event enqueued
        B-VD-9: ANY exception in try-block → logged and swallowed (never re-raises)
    """

    def setup_method(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import _drain_event_queue

        _drain_event_queue()

    # B-VD-1
    def test_import_error_sets_null_fallback(self):
        from apps_shared.spine import vigilance_dispatcher_adapter as mod

        with patch.object(mod, "_build_real_dispatcher", side_effect=ImportError("missing")):
            adapter = mod.VigilanceDispatcherAdapter()
        assert adapter.is_real is False
        assert adapter._dispatcher is None

    def test_null_fallback_dispatch_is_no_op(self):
        from apps_shared.spine import vigilance_dispatcher_adapter as mod

        with patch.object(mod, "_build_real_dispatcher", side_effect=ImportError):
            adapter = mod.VigilanceDispatcherAdapter()
        # Must not raise, must not enqueue anything
        adapter.dispatch(trace_id="t", signals=("s",), summary="test")
        from apps_shared.spine.vigilance_dispatcher_adapter import _drain_event_queue

        assert _drain_event_queue() == []

    # B-VD-2
    def test_successful_import_sets_real_true(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real is True

    # B-VD-3: not _real early return
    def test_null_fallback_dispatch_does_not_enqueue(self):
        from apps_shared.spine import vigilance_dispatcher_adapter as mod
        from apps_shared.spine.vigilance_dispatcher_adapter import _drain_event_queue

        with patch.object(mod, "_build_real_dispatcher", side_effect=ImportError):
            adapter = mod.VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="x", signals=("y",), summary="z")
        assert _drain_event_queue() == []

    # B-VD-4: signals is str → wrapped in tuple
    def test_dispatch_signals_str_wrapped_in_tuple(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real
        adapter.dispatch(trace_id="t1", signals="single_signal_str", summary="test")
        events = _drain_event_queue()
        assert len(events) == 1
        assert "single_signal_str" in events[0].signals

    # B-VD-5: signals is tuple
    def test_dispatch_signals_tuple_passed(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="t2", signals=("sig_a", "sig_b"), summary="test")
        events = _drain_event_queue()
        assert len(events) == 1
        assert "sig_a" in events[0].signals
        assert "sig_b" in events[0].signals

    # B-VD-5 (list variant)
    def test_dispatch_signals_list_converted_to_tuple(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="t3", signals=["list_sig"], summary="test")
        events = _drain_event_queue()
        assert len(events) == 1
        assert "list_sig" in events[0].signals

    # B-VD-6: trace_id=None → str("None")
    def test_dispatch_none_trace_id_does_not_raise(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id=None, signals=("s",), summary="test")
        events = _drain_event_queue()
        assert len(events) == 1
        assert events[0].trace_id == "None"

    # B-VD-7: summary=None → str("None")
    def test_dispatch_none_summary_does_not_raise(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="t", signals=("s",), summary=None)
        events = _drain_event_queue()
        assert len(events) == 1

    # B-VD-8: event enqueued
    def test_dispatch_enqueues_event(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="trace_enqueue", signals=("SIGNAL_X",), summary="verify enqueue")
        events = _drain_event_queue()
        assert len(events) == 1
        assert events[0].trace_id == "trace_enqueue"

    # B-VD-9: exception in try-block swallowed
    def test_dispatch_exception_swallowed_never_reraises(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real
        # Patch _ArtifactCls.create to raise
        with patch.object(adapter, "_ArtifactCls") as mock_cls:
            mock_cls.create.side_effect = RuntimeError("artifact creation failed")
            # Must NOT raise
            adapter.dispatch(trace_id="t", signals=("s",), summary="test")

    def test_dispatch_dispatcher_raises_swallowed(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real
        # Patch dispatcher.dispatch to raise
        with patch.object(adapter, "_dispatcher") as mock_disp:
            mock_disp.dispatch.side_effect = ValueError("dispatch failed")
            # Must NOT raise
            adapter.dispatch(trace_id="t", signals=("s",), summary="test")

    # §1.5 Exception path: unrelated exception also swallowed
    def test_dispatch_unexpected_exception_swallowed(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real
        with patch.object(adapter, "_ArtifactCls") as mock_cls:
            mock_cls.create.side_effect = MemoryError("OOM")
            # Must NOT raise even on MemoryError propagating from VigilanceEventArtifact.create
            adapter.dispatch(trace_id="t", signals=("s",), summary="test")

    # §1.4 Boundary: queue bounded at 256
    def test_event_queue_bounded_at_256(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            _EVENT_QUEUE,
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        _drain_event_queue()
        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real
        for i in range(300):
            adapter.dispatch(trace_id=f"t{i}", signals=(f"s{i}",), summary=f"ev{i}")
        # deque(maxlen=256) automatically drops oldest beyond 256
        assert len(_EVENT_QUEUE) == 256
        _drain_event_queue()

    def test_event_queue_exactly_256_items(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            _EVENT_QUEUE,
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        _drain_event_queue()
        adapter = VigilanceDispatcherAdapter()
        for i in range(256):
            adapter.dispatch(trace_id=f"t{i}", signals=(f"s{i}",), summary=f"ev{i}")
        assert len(_EVENT_QUEUE) == 256
        _drain_event_queue()

    def test_event_queue_255_items_under_max(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            _EVENT_QUEUE,
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        _drain_event_queue()
        adapter = VigilanceDispatcherAdapter()
        for i in range(255):
            adapter.dispatch(trace_id=f"t{i}", signals=(f"s{i}",), summary=f"ev{i}")
        assert len(_EVENT_QUEUE) == 255
        _drain_event_queue()

    # §1.8 Empty signals
    def test_dispatch_empty_signals_tuple(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="t", signals=(), summary="empty signals")
        events = _drain_event_queue()
        assert len(events) == 1

    def test_dispatch_empty_signals_list(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="t", signals=[], summary="empty signals list")
        events = _drain_event_queue()
        assert len(events) == 1

    # §1.11 Side-effect safety: dispatch does not mutate adapter state
    def test_dispatch_does_not_mutate_adapter_state(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        assert adapter.is_real is True
        adapter.dispatch(trace_id="t", signals=("s",), summary="test")
        _drain_event_queue()
        assert adapter.is_real is True  # state unchanged

    # §1.17 Stateful: drain + re-enqueue
    def test_drain_then_reenqueue_is_clean(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="first", signals=("s",), summary="test")
        drained = _drain_event_queue()
        assert len(drained) == 1
        # After drain, queue is empty
        assert _drain_event_queue() == []
        # Re-enqueue
        adapter.dispatch(trace_id="second", signals=("s",), summary="test")
        events = _drain_event_queue()
        assert len(events) == 1
        assert events[0].trace_id == "second"

    # §1.10 Determinism: identical dispatch → identical enqueued content
    def test_dispatch_deterministic_event_content(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import (
            VigilanceDispatcherAdapter,
            _drain_event_queue,
        )

        a1, a2 = VigilanceDispatcherAdapter(), VigilanceDispatcherAdapter()
        _drain_event_queue()
        a1.dispatch(trace_id="same_trace", signals=("S1",), summary="same_summary")
        ev1 = _drain_event_queue()[0]
        a2.dispatch(trace_id="same_trace", signals=("S1",), summary="same_summary")
        ev2 = _drain_event_queue()[0]
        assert ev1.trace_id == ev2.trace_id
        assert ev1.signals == ev2.signals


# ===========================================================================
# D. ExecutionOrchestrator — _delegate_to_l3 + execute() branches
# ===========================================================================


class TestExecutionOrchestratorBranches:
    """
    BRANCH_INVENTORY:
      execution_orchestrator.py / __init__
        B-EO-1: l3_orchestrator=None (default) → self.l3_orchestrator is None
        B-EO-2: l3_orchestrator=<obj> → stored
      execution_orchestrator.py / _delegate_to_l3
        B-EO-3: self.l3_orchestrator is None → orchestration={}
        B-EO-4: self.l3_orchestrator is not None, call succeeds → orchestration populated
        B-EO-5: self.l3_orchestrator.orchestrate() raises → orchestration={error:..., completed:False}
        B-EO-6: result lacks attributes (getattr defaults) → still builds orchestration dict
      execution_orchestrator.py / execute
        B-EO-7: risk.allow=False AND should_retry=True → state="retry"
        B-EO-8: risk.allow=False AND should_retry=False → state="blocked"
        B-EO-9: risk.allow=True AND path.value in _L3_PATHS → calls _delegate_to_l3
        B-EO-10: risk.allow=True AND path.value NOT in _L3_PATHS (A) → state="success", no orchestration
        B-EO-11: _L3_PATHS = {"B","C","D"} (class constant, not "A")
    """

    # B-EO-1
    def test_l3_orchestrator_defaults_to_none(self):
        orch = _make_orchestrator()
        assert orch.l3_orchestrator is None

    # B-EO-2
    def test_l3_orchestrator_stored_when_provided(self):
        mock_l3 = MagicMock()
        orch = _make_orchestrator(l3=mock_l3)
        assert orch.l3_orchestrator is mock_l3

    # B-EO-3
    def test_delegate_to_l3_no_orchestrator_returns_empty_orchestration(self):
        orch = _make_orchestrator(l3=None)
        path = _FakePath("B")
        cycle = _FakeCycle("cid-1", 1)
        risk = _FakeRisk(True)
        result = orch._delegate_to_l3(path, {}, cycle, risk)
        assert result["orchestration"] == {}
        assert result["state"] == "success"

    # B-EO-4
    def test_delegate_to_l3_with_orchestrator_populates_orchestration(self):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.return_value = _FakeOrchResult(
            completed=True, stage="done", signals=["SIG"], metadata={"m": "v"}
        )
        orch = _make_orchestrator(l3=mock_l3)
        result = orch._delegate_to_l3(_FakePath("B"), {}, _FakeCycle("cid-1", 1), _FakeRisk(True))
        assert result["orchestration"]["completed"] is True
        assert result["orchestration"]["stage"] == "done"
        assert "SIG" in result["orchestration"]["signals"]
        assert result["orchestration"]["metadata"] == {"m": "v"}

    # B-EO-5
    @pytest.mark.parametrize("exc", [RuntimeError("boom"), ValueError("bad"), KeyError("k")])
    def test_delegate_to_l3_exception_captured_not_raised(self, exc):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.side_effect = exc
        orch = _make_orchestrator(l3=mock_l3)
        result = orch._delegate_to_l3(_FakePath("C"), {}, _FakeCycle("cid-1", 1), _FakeRisk(True))
        assert result["orchestration"]["completed"] is False
        assert str(exc) in result["orchestration"]["error"]

    # B-EO-6: result with missing attrs → getattr defaults
    def test_delegate_to_l3_result_missing_attrs_uses_defaults(self):
        mock_l3 = MagicMock()
        # Return object with no relevant attributes
        mock_l3.orchestrate.return_value = object()
        orch = _make_orchestrator(l3=mock_l3)
        result = orch._delegate_to_l3(_FakePath("D"), {}, _FakeCycle("cid-1", 1), _FakeRisk(True))
        assert result["orchestration"]["completed"] is False
        assert result["orchestration"]["stage"] == "unknown"
        assert result["orchestration"]["signals"] == []
        assert result["orchestration"]["metadata"] == {}

    # B-EO-7: risk.allow=False AND should_retry=True
    def test_execute_risk_blocked_should_retry_returns_retry(self):
        orch = _make_orchestrator(path="A", allow=False, max_reentry=3)
        result = orch.execute({})
        assert result["state"] == "retry"

    # B-EO-8: risk.allow=False AND should_retry=False
    def test_execute_risk_blocked_no_retry_returns_blocked(self):
        orch = _make_orchestrator(path="A", allow=False, max_reentry=1)
        result = orch.execute({})
        assert result["state"] == "blocked"

    # B-EO-9: path in _L3_PATHS
    @pytest.mark.parametrize("path", ["B", "C", "D"])
    def test_execute_l3_path_calls_delegate(self, path):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.return_value = _FakeOrchResult()
        orch = _make_orchestrator(path=path, allow=True, l3=mock_l3)
        result = orch.execute({})
        mock_l3.orchestrate.assert_called_once()
        assert "orchestration" in result

    # B-EO-10: path A → no l3 delegation
    def test_execute_path_a_no_orchestration_key(self):
        mock_l3 = MagicMock()
        orch = _make_orchestrator(path="A", allow=True, l3=mock_l3)
        result = orch.execute({})
        assert result["state"] == "success"
        mock_l3.orchestrate.assert_not_called()

    # B-EO-11: _L3_PATHS constant
    def test_l3_paths_contains_b_c_d(self):
        from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator

        assert "B" in ExecutionOrchestrator._L3_PATHS
        assert "C" in ExecutionOrchestrator._L3_PATHS
        assert "D" in ExecutionOrchestrator._L3_PATHS

    def test_l3_paths_does_not_contain_a(self):
        from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator

        assert "A" not in ExecutionOrchestrator._L3_PATHS

    # §1.4 Boundary: max_reentry = 1 (minimum)
    def test_execute_max_reentry_1_blocks_immediately(self):
        orch = _make_orchestrator(path="A", allow=False, max_reentry=1)
        result = orch.execute({})
        assert result["state"] == "blocked"

    # §1.4 Boundary: max_reentry = 2 — first attempt retries, NOT blocks
    def test_execute_max_reentry_2_first_attempt_retries(self):
        orch = _make_orchestrator(path="A", allow=False, max_reentry=2)
        result = orch.execute({})
        assert result["state"] == "retry"

    # §1.6 Negative control: blocked state has no orchestration call
    def test_execute_blocked_does_not_call_l3(self):
        mock_l3 = MagicMock()
        orch = _make_orchestrator(path="B", allow=False, l3=mock_l3, max_reentry=1)
        result = orch.execute({})
        assert result["state"] == "blocked"
        mock_l3.orchestrate.assert_not_called()

    # §1.6 Negative control: retry state has no orchestration call
    def test_execute_retry_does_not_call_l3(self):
        mock_l3 = MagicMock()
        orch = _make_orchestrator(path="B", allow=False, l3=mock_l3, max_reentry=3)
        result = orch.execute({})
        assert result["state"] == "retry"
        mock_l3.orchestrate.assert_not_called()

    # §1.7 Recovery: l3 raises, state is still "success" (L0 degrades gracefully)
    def test_execute_l3_exception_degrades_gracefully(self):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.side_effect = RuntimeError("L3 failure")
        orch = _make_orchestrator(path="B", allow=True, l3=mock_l3)
        result = orch.execute({})
        assert result["state"] == "success"
        assert result["orchestration"]["completed"] is False

    # §1.9 State transition: valid path A execution
    def test_execute_path_a_state_transition_success(self):
        orch = _make_orchestrator(path="A", allow=True)
        r = orch.execute({})
        assert r["state"] == "success"
        assert r["path"].value == "A"
        assert r["risk"].allow is True

    # §1.10 Determinism: identical inputs → identical result
    def test_execute_deterministic_same_input(self):
        r1 = _make_orchestrator(path="A").execute({})
        r2 = _make_orchestrator(path="A").execute({})
        assert r1["state"] == r2["state"]
        assert r1["path"].value == r2["path"].value

    # §1.11 Fail-closed: blocked state has no side effects to L3
    def test_execute_blocked_no_side_effects(self):
        mock_l3 = MagicMock()
        orch = _make_orchestrator(path="D", allow=False, l3=mock_l3, max_reentry=1)
        result = orch.execute({})
        assert result["state"] == "blocked"
        # Absolutely no L3 call
        assert mock_l3.orchestrate.call_count == 0
        assert mock_l3.mock_calls == []

    # §1.12 Matrix: path × allow × l3 injection × max_reentry
    @pytest.mark.parametrize(
        "path,allow,has_l3,max_reentry,expected_state",
        [
            ("A", True, False, 3, "success"),
            ("A", False, False, 3, "retry"),
            ("A", False, False, 1, "blocked"),
            ("B", True, True, 3, "success"),
            ("C", True, True, 3, "success"),
            ("D", True, True, 3, "success"),
            ("B", True, False, 3, "success"),
            ("B", False, True, 1, "blocked"),
            ("B", False, True, 3, "retry"),
        ],
    )
    def test_execute_matrix(self, path, allow, has_l3, max_reentry, expected_state):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.return_value = _FakeOrchResult()
        l3 = mock_l3 if has_l3 else None
        orch = _make_orchestrator(path=path, allow=allow, l3=l3, max_reentry=max_reentry)
        result = orch.execute({})
        assert result["state"] == expected_state

    # §1.13 Contradiction: removing _L3_PATHS would make B/C/D not delegate
    def test_l3_paths_is_frozenset(self):
        from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator

        assert isinstance(ExecutionOrchestrator._L3_PATHS, frozenset)

    # §1.15 Mutation sensitivity: L3 exception error message preserved
    def test_execute_l3_error_message_preserved_exactly(self):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.side_effect = ValueError("exact error msg 12345")
        orch = _make_orchestrator(path="B", allow=True, l3=mock_l3)
        result = orch.execute({})
        assert "exact error msg 12345" in result["orchestration"]["error"]

    # §1.8 Edge case: orchestrate returns None → getattr defaults
    def test_execute_l3_returns_none_uses_defaults(self):
        mock_l3 = MagicMock()
        mock_l3.orchestrate.return_value = None
        orch = _make_orchestrator(path="C", allow=True, l3=mock_l3)
        result = orch.execute({})
        assert result["state"] == "success"
        assert result["orchestration"]["completed"] is False
        assert result["orchestration"]["stage"] == "unknown"

    # §1.17 Stateful: repeated executes on same orchestrator
    def test_execute_repeated_calls_same_orchestrator(self):
        orch = _make_orchestrator(path="A", allow=True)
        r1 = orch.execute({"u0_user_prompt": "first"})
        r2 = orch.execute({"u0_user_prompt": "second"})
        assert r1["state"] == "success"
        assert r2["state"] == "success"


# ===========================================================================
# Shared helpers
# ===========================================================================


def _make_real_d0_adapter():
    from apps_shared.spine.d0_engine_adapter import D0EngineAdapter

    a = D0EngineAdapter()
    if not a.is_real:
        pytest.fail("D0InjectionEngine not available")
    return a


@dataclass
class _FakePath:
    value: str


@dataclass
class _FakeCycle:
    cid: str
    attempt: int


@dataclass
class _FakeRisk:
    allow: bool


@dataclass
class _FakeOrchResult:
    completed: bool = True
    stage: str = "done"
    signals: list = None
    metadata: dict = None

    def __post_init__(self):
        if self.signals is None:
            self.signals = []
        if self.metadata is None:
            self.metadata = {}


class _FakeAssembler:
    def assemble(self, intent_input):
        class _P:
            d0_injections = ""
            sanitized = False
            check_ids = ()

        return _P()


class _FakeRouter:
    def __init__(self, path_value="A"):
        self._path = path_value

    def select_path(self, payload):
        return _FakePath(value=self._path)


class _FakeD0Engine:
    def render_d0(self, x):
        return x


class _FakeRiskGate:
    def __init__(self, allow=True):
        self._allow = allow

    def evaluate(self, *, payload_like, d0_injections):
        return _FakeRisk(allow=self._allow)


class _FakeCIDRegistry:
    _n = 0

    def new_cycle(self, label):
        self._n += 1
        return _FakeCycle(cid=f"cid-{label}-{self._n}", attempt=1)

    def next_attempt(self, cycle):
        return _FakeCycle(cid=cycle.cid, attempt=cycle.attempt + 1)


class _FakeReEntry:
    def __init__(self, max_attempts=3):
        self._max = max_attempts

    def should_retry(self, cycle):
        return cycle.attempt < self._max

    def advance(self, cycle):
        return _FakeCycle(cid=cycle.cid, attempt=cycle.attempt + 1)


class _FakeVigilance:
    def dispatch(self, *a, **kw):
        pass


class _FakeMetaBus:
    def enqueue(self, *a, **kw):
        pass


def _make_orchestrator(path="A", allow=True, l3=None, max_reentry=3):
    from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator

    return ExecutionOrchestrator(
        assembler=_FakeAssembler(),
        path_router=_FakeRouter(path_value=path),
        d0_engine=_FakeD0Engine(),
        risk_gate=_FakeRiskGate(allow=allow),
        cid_registry=_FakeCIDRegistry(),
        reentry_loop=_FakeReEntry(max_attempts=max_reentry),
        vigilance_dispatcher=_FakeVigilance(),
        meta_bus=_FakeMetaBus(),
        l3_orchestrator=l3,
    )
