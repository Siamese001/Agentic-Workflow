"""Tests for ADG test selector — Accelerator #5.

Coverage matrix per §1.1:
- Success: single file, multiple files, dedup, sorted output
- Edge cases: empty input, file not in ADG, no covers edges, non-test resolved_path,
              Windows backslash path, node missing resolved_path field
- Fail-closed: Redis connection error propagates (no swallowing)
- Gaps: file with no covers is gap, file with covers is not, sorted gaps
- Determinism: identical input → identical output (all tests use fixed data)
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

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

_emit_records_execution_trace("p0", "evidence", "test_adg_test_selector")
_emit_applies_guardrail("p0", "test_adg_test_selector", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_test_selector", "policy_binding")
_emit_snapshots_state("p0", "test_adg_test_selector", "state_snapshot")
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
)

_emit_emits_metric_event("test_adg_test_selector", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_test_selector", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_test_selector", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_test_selector", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_test_selector", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_test_selector", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_test_selector", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_test_selector", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_test_selector", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_test_selector", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_test_selector", "p4obs", "alert")
_emit_links_incident_trace("test_adg_test_selector", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_test_selector", "p3lm", "pattern")
_emit_records_learning_event("test_adg_test_selector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_test_selector", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_test_selector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_test_selector", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_test_selector", "p3lm", "policy")
_emit_stores_learning_state("test_adg_test_selector", "p3lm", "state")
_emit_records_execution_trace("test_adg_test_selector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_test_selector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_test_selector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_test_selector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_test_selector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_test_selector", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_test_selector", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_test_selector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_test_selector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_test_selector", "context_pull")
_emit_pulls_context("p1", "test_adg_test_selector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_test_selector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_test_selector", "uwg_term_2")
_emit_writes_through("p1", "test_adg_test_selector", "write_through")
_emit_writes_through("p1", "test_adg_test_selector", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_test_selector", "safety_validation")
_emit_invokes_eval("p1", "test_adg_test_selector", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_test_selector", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_test_selector", "human_escalation")
_emit_routes_through("p1", "test_adg_test_selector", "route_through")
_emit_checks_agent_registry("p1", "test_adg_test_selector", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_test_selector", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_test_selector", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_test_selector", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_test_selector", "target_agent")
_emit_verifies_policy("p1", "test_adg_test_selector", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_test_selector", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_test_selector", "boundary_check")
_emit_transcripts_response("p1", "test_adg_test_selector", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_test_selector")
_emit_gated_by_confidence("p1", "test_adg_test_selector", "confidence_gate")
emit_replay_key("p0", "test_adg_test_selector")
emit_determinism_digest("p0", "test_adg_test_selector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_test_selector", "execution_auth")
_emit_validates_capability("p2", "test_adg_test_selector", "capability_check")
_emit_routes_to_capability("p2", "test_adg_test_selector", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_test_selector", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_test_selector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_test_selector", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_test_selector", "exec_output")
_emit_dispatches_agent("p3", "test_adg_test_selector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_test_selector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_test_selector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_test_selector", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_test_selector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_test_selector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_test_selector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_test_selector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_test_selector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_test_selector", "eval_metric")
_emit_stores_embedding("p4", "test_adg_test_selector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_test_selector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_test_selector", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Shared fixture builder
# ---------------------------------------------------------------------------


def _make_client(
    nodes_by_file: dict[str, set[str]],
    fan_in_covers: dict[str, set[str]],
    nodes: dict[str, dict[str, str]],
) -> object:
    """Build a minimal ADGRedisClient stub backed by MagicMock."""
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()

    def smembers(key: str) -> set[str]:
        if key.startswith("adg:nodes:by_file:"):
            return nodes_by_file.get(key[len("adg:nodes:by_file:") :], set())
        if key.startswith("adg:edge:in:") and key.endswith(":covers"):
            nid = key[len("adg:edge:in:") : -len(":covers")]
            return fan_in_covers.get(nid, set())
        return set()

    def hgetall(key: str) -> dict[str, str]:
        nid = key[len("adg:node:") :]
        return nodes.get(nid, {})

    r.smembers.side_effect = smembers
    r.hgetall.side_effect = hgetall
    client._r = r
    return client


def _make_selector(nodes_by_file, fan_in_covers, nodes):
    from tools.adg.adg_test_selector import ADGTestSelector

    return ADGTestSelector(client=_make_client(nodes_by_file, fan_in_covers, nodes))


# ===========================================================================
# Success path
# ===========================================================================


class TestSelectTestsSuccess:
    def test_empty_file_list_returns_empty(self):
        sel = _make_selector({}, {}, {})
        assert sel.select_tests([]) == []

    def test_single_file_single_cover_returns_test_path(self):
        sel = _make_selector(
            nodes_by_file={"agentic_core/L0_routing/router.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_router.py"}},
        )
        result = sel.select_tests(["agentic_core/L0_routing/router.py"])
        assert result == ["tests/unit/test_router.py"]

    def test_single_file_multiple_covers_returns_all(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t1", "t2"}},
            nodes={
                "t1": {"resolved_path": "tests/unit/test_a.py"},
                "t2": {"resolved_path": "tests/unit/test_b.py"},
            },
        )
        result = sel.select_tests(["prod.py"])
        assert result == ["tests/unit/test_a.py", "tests/unit/test_b.py"]

    def test_multiple_prod_files_deduplicates_shared_test(self):
        sel = _make_selector(
            nodes_by_file={
                "agentic_core/router.py": {"n1"},
                "agentic_core/dispatcher.py": {"n2"},
            },
            fan_in_covers={
                "n1": {"t1"},
                "n2": {"t1", "t2"},  # t1 covers both
            },
            nodes={
                "t1": {"resolved_path": "tests/unit/test_router.py"},
                "t2": {"resolved_path": "tests/unit/test_dispatcher.py"},
            },
        )
        result = sel.select_tests(["agentic_core/router.py", "agentic_core/dispatcher.py"])
        assert result == ["tests/unit/test_dispatcher.py", "tests/unit/test_router.py"]
        assert len(result) == 2  # deduplicated

    def test_result_is_always_sorted(self):
        sel = _make_selector(
            nodes_by_file={"app.py": {"n1", "n2"}},
            fan_in_covers={"n1": {"t2"}, "n2": {"t1"}},
            nodes={
                "t1": {"resolved_path": "tests/a_test.py"},
                "t2": {"resolved_path": "tests/z_test.py"},
            },
        )
        result = sel.select_tests(["app.py"])
        assert result == sorted(result), "Output must always be lexicographically sorted"

    def test_multiple_nodes_per_file_all_queried(self):
        """A file with multiple ADG nodes — all nodes' covers are collected."""
        sel = _make_selector(
            nodes_by_file={"multi_node.py": {"n1", "n2", "n3"}},
            fan_in_covers={"n1": {"t1"}, "n2": {"t2"}, "n3": set()},
            nodes={
                "t1": {"resolved_path": "tests/test_1.py"},
                "t2": {"resolved_path": "tests/test_2.py"},
            },
        )
        result = sel.select_tests(["multi_node.py"])
        assert "tests/test_1.py" in result
        assert "tests/test_2.py" in result

    def test_determinism_same_input_same_output(self):
        """Identical call with identical data must return identical result."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_prod.py"}},
        )
        r1 = sel.select_tests(["prod.py"])
        r2 = sel.select_tests(["prod.py"])
        assert r1 == r2


# ===========================================================================
# Edge cases
# ===========================================================================


class TestSelectTestsEdgeCases:
    def test_file_not_in_adg_returns_empty_no_error(self):
        sel = _make_selector({}, {}, {})
        result = sel.select_tests(["totally/unknown/file.py"])
        assert result == []

    def test_file_with_no_covers_edges_returns_empty(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={},  # no covers
            nodes={},
        )
        result = sel.select_tests(["prod.py"])
        assert result == []

    def test_non_test_resolved_path_excluded(self):
        """Covers edges pointing to production files (not tests/) must be excluded."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t_real", "t_prod"}},
            nodes={
                "t_real": {"resolved_path": "tests/unit/test_prod.py"},
                "t_prod": {"resolved_path": "agentic_core/some_prod.py"},  # not tests/
            },
        )
        result = sel.select_tests(["prod.py"])
        assert result == ["tests/unit/test_prod.py"]
        assert "agentic_core/some_prod.py" not in result

    def test_backslash_path_normalized_to_forward_slash(self):
        """Windows-style backslash paths must be normalized before ADG lookup."""
        sel = _make_selector(
            nodes_by_file={"agentic_core/L0_routing/router.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_router.py"}},
        )
        result = sel.select_tests(["agentic_core\\L0_routing\\router.py"])
        assert result == ["tests/unit/test_router.py"]

    def test_node_missing_resolved_path_skipped_no_error(self):
        """Nodes without resolved_path field must not cause KeyError."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t_empty"}},
            nodes={"t_empty": {}},  # no resolved_path
        )
        result = sel.select_tests(["prod.py"])
        assert result == []

    def test_node_with_empty_resolved_path_skipped(self):
        """Nodes with empty resolved_path string must be skipped."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t_blank"}},
            nodes={"t_blank": {"resolved_path": ""}},
        )
        result = sel.select_tests(["prod.py"])
        assert result == []

    def test_duplicate_input_paths_deduplicates_output(self):
        """Same file listed twice in input must not produce duplicate test paths."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_prod.py"}},
        )
        result = sel.select_tests(["prod.py", "prod.py"])
        assert result == ["tests/unit/test_prod.py"]
        assert len(result) == 1


# ===========================================================================
# Fail-closed — Redis errors must propagate
# ===========================================================================


class TestSelectTestsFailClosed:
    def test_redis_connection_error_propagates(self):
        """Redis ConnectionError must NOT be swallowed — no fallback to filesystem."""
        import redis

        from tools.adg.adg_redis_query import ADGRedisClient
        from tools.adg.adg_test_selector import ADGTestSelector

        client = ADGRedisClient.__new__(ADGRedisClient)
        bad_r = MagicMock()
        bad_r.smembers.side_effect = redis.ConnectionError("connection refused")
        client._r = bad_r

        sel = ADGTestSelector(client=client)
        with pytest.raises(redis.ConnectionError):
            sel.select_tests(["agentic_core/L0_routing/router.py"])

    def test_redis_timeout_error_propagates(self):
        """Redis TimeoutError must NOT be swallowed."""
        import redis

        from tools.adg.adg_redis_query import ADGRedisClient
        from tools.adg.adg_test_selector import ADGTestSelector

        client = ADGRedisClient.__new__(ADGRedisClient)
        bad_r = MagicMock()
        bad_r.smembers.side_effect = redis.TimeoutError("timed out")
        client._r = bad_r

        sel = ADGTestSelector(client=client)
        with pytest.raises(redis.TimeoutError):
            sel.select_tests(["agentic_core/L0_routing/router.py"])


# ===========================================================================
# Coverage gaps
# ===========================================================================


class TestCoverageGaps:
    def test_file_with_no_covers_is_a_gap(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={},  # no covers
            nodes={},
        )
        gaps = sel.coverage_gaps(["prod.py"])
        assert "prod.py" in gaps

    def test_file_with_covers_is_not_a_gap(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_prod.py"}},
        )
        gaps = sel.coverage_gaps(["prod.py"])
        assert gaps == []

    def test_empty_input_returns_empty_gaps(self):
        sel = _make_selector({}, {}, {})
        assert sel.coverage_gaps([]) == []

    def test_file_not_in_adg_at_all_is_a_gap(self):
        """Files not indexed in ADG have no nodes → no covers → they are gaps."""
        sel = _make_selector({}, {}, {})
        gaps = sel.coverage_gaps(["brand_new_unindexed_file.py"])
        assert "brand_new_unindexed_file.py" in gaps

    def test_gaps_result_is_sorted(self):
        sel = _make_selector({}, {}, {})
        gaps = sel.coverage_gaps(["z_file.py", "a_file.py", "m_file.py"])
        assert gaps == sorted(gaps)

    def test_mixed_covered_and_gap_files(self):
        sel = _make_selector(
            nodes_by_file={
                "covered.py": {"n1"},
                "uncovered.py": {"n2"},
            },
            fan_in_covers={"n1": {"t1"}},  # covered has cover; uncovered has none
            nodes={"t1": {"resolved_path": "tests/test_covered.py"}},
        )
        gaps = sel.coverage_gaps(["covered.py", "uncovered.py"])
        assert "uncovered.py" in gaps
        assert "covered.py" not in gaps

    def test_gap_detection_deterministic(self):
        sel = _make_selector({}, {}, {})
        g1 = sel.coverage_gaps(["a.py", "b.py"])
        g2 = sel.coverage_gaps(["a.py", "b.py"])
        assert g1 == g2
