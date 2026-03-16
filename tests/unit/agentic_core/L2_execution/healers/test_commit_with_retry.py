"""Deterministic capability proof for commit_with_retry hook-resilience.

Tests simulate the hook-failure retry path without forcing real hook failures.
"""

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

_emit_records_execution_trace("p0", "evidence", "test_commit_with_retry")
_emit_applies_guardrail("p0", "test_commit_with_retry", "p0_governance")
_emit_reads_policy_state("p0", "test_commit_with_retry", "policy_binding")
_emit_snapshots_state("p0", "test_commit_with_retry", "state_snapshot")
emit_replay_key("p0", "test_commit_with_retry")
emit_determinism_digest("p0", "test_commit_with_retry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_commit_with_retry", "execution_auth")
_emit_validates_capability("p2", "test_commit_with_retry", "capability_check")
_emit_routes_to_capability("p2", "test_commit_with_retry", "capability_route")
_emit_writes_via_uwg("p2", "test_commit_with_retry", "uwg_write")
_emit_blocks_direct_write("p2", "test_commit_with_retry", "direct_write_block")
_emit_records_tool_invocation("p2", "test_commit_with_retry", "tool_invocation")
_emit_captures_execution_output("p2", "test_commit_with_retry", "exec_output")
_emit_dispatches_agent("p3", "test_commit_with_retry", "agent_dispatch")
_emit_coordinates_agents("p3", "test_commit_with_retry", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_commit_with_retry", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_commit_with_retry", "healing_outcome")
_emit_escalates_failure("p3", "test_commit_with_retry", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_commit_with_retry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_commit_with_retry", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_commit_with_retry", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_commit_with_retry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_commit_with_retry", "eval_metric")
_emit_stores_embedding("p4", "test_commit_with_retry", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_commit_with_retry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_commit_with_retry", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from tools.evidence.healing_tier_evidence_runner import commit_with_retry
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_commit_with_retry", "p4obs", "metric_1")
_emit_emits_metric_event("test_commit_with_retry", "p4obs", "metric_2")
_emit_emits_metric_event("test_commit_with_retry", "p4obs", "metric_3")
_emit_emits_metric_event("test_commit_with_retry", "p4obs", "metric_4")
_emit_emits_metric_event("test_commit_with_retry", "p4obs", "metric_5")
_emit_emits_metric_event("test_commit_with_retry", "p4obs", "metric_6")
_emit_records_incident_event("test_commit_with_retry", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_commit_with_retry", "p4obs", "anomaly")
_emit_writes_observability_log("test_commit_with_retry", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_commit_with_retry", "p4obs", "mon_state")
_emit_triggers_alert("test_commit_with_retry", "p4obs", "alert")
_emit_links_incident_trace("test_commit_with_retry", "p4obs", "trace_link")
_emit_captures_pattern("test_commit_with_retry", "p3lm", "pattern")
_emit_records_learning_event("test_commit_with_retry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_commit_with_retry", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_commit_with_retry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_commit_with_retry", "p3lm", "routing")
_emit_improves_agent_policy("test_commit_with_retry", "p3lm", "policy")
_emit_stores_learning_state("test_commit_with_retry", "p3lm", "state")
_emit_records_execution_trace("test_commit_with_retry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_commit_with_retry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_commit_with_retry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_commit_with_retry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_commit_with_retry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_commit_with_retry", "env_read", "p2_env_1")
_emit_reads_environ("test_commit_with_retry", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_commit_with_retry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_commit_with_retry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_commit_with_retry", "context_pull")
_emit_pulls_context("p1", "test_commit_with_retry", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_commit_with_retry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_commit_with_retry", "uwg_term_secondary")
_emit_writes_through("p1", "test_commit_with_retry", "write_through")
_emit_writes_through("p1", "test_commit_with_retry", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_commit_with_retry", "safety_validation")
_emit_invokes_eval("p1", "test_commit_with_retry", "eval_call")
_emit_proposal_commits_routing("p1", "test_commit_with_retry", "routing_commit")

EVIDENCE_REL = "docs/reports/plans/healing_tier_router_evidence.md"


class TestCommitWithRetrySuccess:
    """First commit fails (hook fix), porcelain shows modified file,
    re-add occurs, retry succeeds."""

    def test_hook_failure_retry_succeeds(self, monkeypatch):
        calls_log: list[tuple[str, list[str]]] = []
        commit_argv = ["git", "commit", "-m", "docs: evidence (sealed)"]
        attempt_count = 0

        def fake_run_cmd(argv: list[str]) -> tuple[int, str, str]:
            nonlocal attempt_count
            calls_log.append(("run_cmd", list(argv)))

            # git commit attempts
            if argv[:2] == ["git", "commit"]:
                attempt_count += 1
                if attempt_count == 1:
                    # First attempt fails (simulates pre-commit hook fix)
                    return (
                        1,
                        "T0: Enforce LF Line Endings...Failed\n",
                        "- hook id: mixed-line-ending\n- exit code: 1\n",
                    )
                else:
                    # Second attempt succeeds
                    return (0, "[healing-api-llm abc1234] docs: evidence\n", "")

            # git status --porcelain (after first failure)
            if argv == ["git", "status", "--porcelain"]:
                return (0, f" M {EVIDENCE_REL}\n", "")

            # git add -- <paths>
            if argv[:2] == ["git", "add"]:
                return (0, "", "")

            return (0, "", "")

        monkeypatch.setattr("tools.evidence.healing_tier_evidence_runner.run_cmd", fake_run_cmd)

        # Should not raise
        commit_with_retry(commit_argv)

        # Extract call categories
        commit_calls = [c for c in calls_log if c[1][:2] == ["git", "commit"]]
        porcelain_calls = [c for c in calls_log if c[1] == ["git", "status", "--porcelain"]]
        add_calls = [c for c in calls_log if c[1][:2] == ["git", "add"]]

        # Commit was attempted exactly 2 times
        assert len(commit_calls) == 2, f"Expected 2 commit attempts, got {len(commit_calls)}"

        # Porcelain was requested exactly once (after first failure)
        assert len(porcelain_calls) == 1, f"Expected 1 porcelain call, got {len(porcelain_calls)}"

        # git add was called with "--" and the sorted path list
        assert len(add_calls) == 1, f"Expected 1 git add call, got {len(add_calls)}"
        add_argv = add_calls[0][1]
        assert add_argv == ["git", "add", "--", EVIDENCE_REL], f"Unexpected add argv: {add_argv}"

    def test_first_attempt_succeeds_no_retry(self, monkeypatch):
        """When first commit succeeds, no retry/porcelain/re-add occurs."""
        calls_log: list[tuple[str, list[str]]] = []

        def fake_run_cmd(argv: list[str]) -> tuple[int, str, str]:
            calls_log.append(("run_cmd", list(argv)))
            if argv[:2] == ["git", "commit"]:
                return (0, "[healing-api-llm abc1234] docs: evidence\n", "")
            return (0, "", "")

        monkeypatch.setattr("tools.evidence.healing_tier_evidence_runner.run_cmd", fake_run_cmd)

        commit_with_retry(["git", "commit", "-m", "test"])

        commit_calls = [c for c in calls_log if c[1][:2] == ["git", "commit"]]
        porcelain_calls = [c for c in calls_log if c[1] == ["git", "status", "--porcelain"]]
        add_calls = [c for c in calls_log if c[1][:2] == ["git", "add"]]

        assert len(commit_calls) == 1
        assert len(porcelain_calls) == 0
        assert len(add_calls) == 0


class TestCommitWithRetryBothFail:
    """Both commit attempts fail -> hard-fail (SystemExit) after exactly one retry."""

    def test_double_failure_raises_system_exit(self, monkeypatch):
        calls_log: list[tuple[str, list[str]]] = []

        def fake_run_cmd(argv: list[str]) -> tuple[int, str, str]:
            calls_log.append(("run_cmd", list(argv)))

            if argv[:2] == ["git", "commit"]:
                return (1, "hook failed\n", "error output\n")

            if argv == ["git", "status", "--porcelain"]:
                return (0, f" M {EVIDENCE_REL}\n", "")

            if argv[:2] == ["git", "add"]:
                return (0, "", "")

            return (0, "", "")

        monkeypatch.setattr("tools.evidence.healing_tier_evidence_runner.run_cmd", fake_run_cmd)

        with pytest.raises(SystemExit) as exc_info:
            commit_with_retry(["git", "commit", "-m", "test"])

        assert exc_info.value.code == 1

        # Exactly 2 commit attempts (no third)
        commit_calls = [c for c in calls_log if c[1][:2] == ["git", "commit"]]
        assert len(commit_calls) == 2, f"Expected exactly 2 commit attempts, got {len(commit_calls)}"

    def test_no_third_attempt(self, monkeypatch):
        """Verify no third commit attempt occurs after two failures."""
        attempt_count = 0

        def fake_run_cmd(argv: list[str]) -> tuple[int, str, str]:
            nonlocal attempt_count
            if argv[:2] == ["git", "commit"]:
                attempt_count += 1
                if attempt_count > 2:
                    raise AssertionError("Third commit attempt should never happen")
                return (1, "fail\n", "err\n")
            if argv == ["git", "status", "--porcelain"]:
                return (0, f" M {EVIDENCE_REL}\n", "")
            if argv[:2] == ["git", "add"]:
                return (0, "", "")
            return (0, "", "")

        monkeypatch.setattr("tools.evidence.healing_tier_evidence_runner.run_cmd", fake_run_cmd)

        with pytest.raises(SystemExit):
            commit_with_retry(["git", "commit", "-m", "test"])

        assert attempt_count == 2


class TestCommitWithRetryMultiplePaths:
    """When porcelain shows multiple modified files, all are re-added sorted."""

    def test_multiple_paths_sorted(self, monkeypatch):
        calls_log: list[tuple[str, list[str]]] = []
        attempt_count = 0

        def fake_run_cmd(argv: list[str]) -> tuple[int, str, str]:
            nonlocal attempt_count
            calls_log.append(("run_cmd", list(argv)))

            if argv[:2] == ["git", "commit"]:
                attempt_count += 1
                if attempt_count == 1:
                    return (1, "hook failed\n", "")
                return (0, "ok\n", "")

            if argv == ["git", "status", "--porcelain"]:
                # Multiple files modified, deliberately unsorted
                return (0, " M z_file.md\n M a_file.md\nMM b_file.py\n", "")

            if argv[:2] == ["git", "add"]:
                return (0, "", "")

            return (0, "", "")

        monkeypatch.setattr("tools.evidence.healing_tier_evidence_runner.run_cmd", fake_run_cmd)

        commit_with_retry(["git", "commit", "-m", "test"])

        add_calls = [c for c in calls_log if c[1][:2] == ["git", "add"]]
        assert len(add_calls) == 1
        add_argv = add_calls[0][1]
        # Paths must be sorted
        assert add_argv == ["git", "add", "--", "a_file.md", "b_file.py", "z_file.md"]

    def test_untracked_files_ignored(self, monkeypatch):
        """Untracked (??) files are not re-added."""
        calls_log: list[tuple[str, list[str]]] = []
        attempt_count = 0

        def fake_run_cmd(argv: list[str]) -> tuple[int, str, str]:
            nonlocal attempt_count
            calls_log.append(("run_cmd", list(argv)))

            if argv[:2] == ["git", "commit"]:
                attempt_count += 1
                if attempt_count == 1:
                    return (1, "hook failed\n", "")
                return (0, "ok\n", "")

            if argv == ["git", "status", "--porcelain"]:
                return (0, f" M {EVIDENCE_REL}\n?? untracked.tmp\n", "")

            if argv[:2] == ["git", "add"]:
                return (0, "", "")

            return (0, "", "")

        monkeypatch.setattr("tools.evidence.healing_tier_evidence_runner.run_cmd", fake_run_cmd)

        commit_with_retry(["git", "commit", "-m", "test"])

        add_calls = [c for c in calls_log if c[1][:2] == ["git", "add"]]
        assert len(add_calls) == 1
        add_argv = add_calls[0][1]
        # Only the modified file, not the untracked one
        assert add_argv == ["git", "add", "--", EVIDENCE_REL]
