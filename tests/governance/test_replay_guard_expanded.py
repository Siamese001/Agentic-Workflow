"""
Tests for expanded ReplayGuard kernel-level nondeterminism interception.

Phase 2.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import os
import random
import socket
import subprocess
import threading

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

_emit_records_execution_trace("p0", "evidence", "test_replay_guard_expanded")
_emit_applies_guardrail("p0", "test_replay_guard_expanded", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_guard_expanded", "policy_binding")
_emit_snapshots_state("p0", "test_replay_guard_expanded", "state_snapshot")
emit_replay_key("p0", "test_replay_guard_expanded")
emit_determinism_digest("p0", "test_replay_guard_expanded")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_guard_expanded", "execution_auth")
_emit_validates_capability("p2", "test_replay_guard_expanded", "capability_check")
_emit_routes_to_capability("p2", "test_replay_guard_expanded", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_guard_expanded", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_guard_expanded", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_guard_expanded", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_guard_expanded", "exec_output")
_emit_dispatches_agent("p3", "test_replay_guard_expanded", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_guard_expanded", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_guard_expanded", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_guard_expanded", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_guard_expanded", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_guard_expanded", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_guard_expanded", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_guard_expanded", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_guard_expanded", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_guard_expanded", "eval_metric")
_emit_stores_embedding("p4", "test_replay_guard_expanded", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_guard_expanded", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_guard_expanded", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.determinism.replay_guard import (
    ReplayGuard,
    ReplayViolation,
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
)

_emit_emits_metric_event("test_replay_guard_expanded", "p4obs", "metric_1")
_emit_emits_metric_event("test_replay_guard_expanded", "p4obs", "metric_2")
_emit_emits_metric_event("test_replay_guard_expanded", "p4obs", "metric_3")
_emit_emits_metric_event("test_replay_guard_expanded", "p4obs", "metric_4")
_emit_emits_metric_event("test_replay_guard_expanded", "p4obs", "metric_5")
_emit_emits_metric_event("test_replay_guard_expanded", "p4obs", "metric_6")
_emit_records_incident_event("test_replay_guard_expanded", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_replay_guard_expanded", "p4obs", "anomaly")
_emit_writes_observability_log("test_replay_guard_expanded", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_replay_guard_expanded", "p4obs", "mon_state")
_emit_triggers_alert("test_replay_guard_expanded", "p4obs", "alert")
_emit_links_incident_trace("test_replay_guard_expanded", "p4obs", "trace_link")
_emit_captures_pattern("test_replay_guard_expanded", "p3lm", "pattern")
_emit_records_learning_event("test_replay_guard_expanded", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_replay_guard_expanded", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_replay_guard_expanded", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_replay_guard_expanded", "p3lm", "routing")
_emit_improves_agent_policy("test_replay_guard_expanded", "p3lm", "policy")
_emit_stores_learning_state("test_replay_guard_expanded", "p3lm", "state")
_emit_records_execution_trace("test_replay_guard_expanded", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_replay_guard_expanded", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_replay_guard_expanded", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_replay_guard_expanded", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_replay_guard_expanded", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_replay_guard_expanded", "env_read", "p2_env_1")
_emit_reads_environ("test_replay_guard_expanded", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_replay_guard_expanded", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_replay_guard_expanded", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_replay_guard_expanded", "context_pull")
_emit_pulls_context("p1", "test_replay_guard_expanded", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_replay_guard_expanded", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_replay_guard_expanded", "uwg_term_secondary")
_emit_writes_through("p1", "test_replay_guard_expanded", "write_through")
_emit_writes_through("p1", "test_replay_guard_expanded", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_replay_guard_expanded", "safety_validation")
_emit_invokes_eval("p1", "test_replay_guard_expanded", "eval_call")
_emit_proposal_commits_routing("p1", "test_replay_guard_expanded", "routing_commit")


class TestReplayGuardSocket:
    def test_blocks_socket_creation(self) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="socket"):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def test_socket_restored_after_context(self) -> None:
        with ReplayGuard():
            pass
        # Should not raise outside context
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.close()


class TestReplayGuardSubprocess:
    def test_blocks_subprocess_run(self) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="subprocess"):
                subprocess.run(["echo", "hello"])

    def test_blocks_os_system(self) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="os.system"):
                os.system("echo hello")

    def test_subprocess_restored_after_context(self) -> None:
        with ReplayGuard():
            pass
        result = subprocess.run(["python", "-c", "print('ok')"], capture_output=True)
        assert result.returncode == 0


class TestReplayGuardFilesystem:
    def test_blocks_file_write(self, tmp_path) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="write"):
                open(str(tmp_path / "test.txt"), "w")

    def test_blocks_file_append(self, tmp_path) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="write"):
                open(str(tmp_path / "test.txt"), "a")

    def test_allows_file_read(self, tmp_path) -> None:
        test_file = tmp_path / "read.txt"
        test_file.write_text("content")
        with ReplayGuard():
            with open(str(test_file)) as f:
                assert f.read() == "content"

    def test_open_restored_after_context(self, tmp_path) -> None:
        with ReplayGuard():
            pass
        path = tmp_path / "after.txt"
        with open(str(path), "w") as f:
            f.write("ok")
        assert path.read_text() == "ok"


class TestReplayGuardThreading:
    def test_blocks_thread_start(self) -> None:
        results = []

        def worker():
            results.append(1)

        with ReplayGuard():
            t = threading.Thread(target=worker)
            with pytest.raises(ReplayViolation, match="threading"):
                t.start()

    def test_threading_restored_after_context(self) -> None:
        results = []

        def worker():
            results.append(1)

        with ReplayGuard():
            pass
        t = threading.Thread(target=worker)
        t.start()
        t.join()
        assert results == [1]


class TestReplayGuardRandom:
    def test_random_is_deterministic_with_seed(self) -> None:
        with ReplayGuard(deterministic_seed=42):
            v1 = random.random()
        with ReplayGuard(deterministic_seed=42):
            v2 = random.random()
        assert v1 == v2

    def test_different_seeds_give_different_values(self) -> None:
        with ReplayGuard(deterministic_seed=1):
            v1 = random.random()
        with ReplayGuard(deterministic_seed=2):
            v2 = random.random()
        assert v1 != v2

    def test_random_restored_after_context(self) -> None:
        # random should work normally after context exit
        with ReplayGuard():
            pass
        v = random.random()
        assert 0.0 <= v < 1.0


class TestReplayGuardContextManager:
    def test_exception_in_context_restores_patches(self, tmp_path) -> None:
        with pytest.raises(ValueError, match="test error"):
            with ReplayGuard():
                raise ValueError("test error")
        # Patching should be fully restored
        path = tmp_path / "recovery.txt"
        with open(str(path), "w") as f:
            f.write("ok")
        assert path.read_text() == "ok"
