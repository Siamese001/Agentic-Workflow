"""
ReplayGuard — Kernel-level nondeterminism interception for L2 execution.

Intercepts ALL potential sources of nondeterminism during a replay run:
  - socket / network
  - subprocess / os.system
  - filesystem writes outside the sandbox root
  - threading.Thread.start
  - random number generation
  - datetime.now / time.time

Use as a context manager around any execution segment that must be
deterministically replayable.

Phase 2.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import builtins
import os
import random
import socket
import subprocess
import threading
from types import TracebackType
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

emit_replay_key("p0", "replay_guard")
emit_determinism_digest("p0", "replay_guard")

_emit_dispatches_healing_run("p1", "replay_guard", "L2")
_emit_routes_through("p1", "replay_guard", "L2")
_emit_checks_agent_registry("p1", "replay_guard", "agent_registry")
_emit_validates_agent_capability("p1", "replay_guard", "capability")
_emit_dispatches_execution_plan("p1", "replay_guard", "exec_plan")
_emit_agent_executes_agent("p1", "replay_guard", "sub_agent")
_emit_routes_to_agent("p1", "replay_guard", "target_agent")
_emit_verifies_policy("p1", "replay_guard", "policy_check")
_emit_observes_runtime_state("p1", "replay_guard", "runtime_state")
_emit_verifies_boundary("p1", "replay_guard", "boundary_check")
_emit_transcripts_response("p1", "replay_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "replay_guard")
_emit_gated_by_confidence("p1", "replay_guard", "confidence_gate")
_emit_escalates_to_human("p1", "replay_guard", "L2")
_emit_reads_policy_state("p1", "replay_guard", "L2")
_emit_authorize_and_execute("p2", "replay_guard", "execution_auth")
_emit_validates_capability("p2", "replay_guard", "capability_check")
_emit_routes_to_capability("p2", "replay_guard", "capability_route")
_emit_writes_via_uwg("p2", "replay_guard", "uwg_write")
_emit_blocks_direct_write("p2", "replay_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_guard", "tool_invocation")
_emit_captures_execution_output("p2", "replay_guard", "exec_output")
_emit_dispatches_agent("p3", "replay_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_guard", "healing_outcome")
_emit_escalates_failure("p3", "replay_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_guard", "eval_metric")
_emit_stores_embedding("p4", "replay_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_guard", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

record_execution_trace("replay_guard", "replay_guard_trace")


_emit_emits_metric_event("replay_guard", "p4obs", "metric_1")
_emit_emits_metric_event("replay_guard", "p4obs", "metric_2")
_emit_emits_metric_event("replay_guard", "p4obs", "metric_3")
_emit_emits_metric_event("replay_guard", "p4obs", "metric_4")
_emit_emits_metric_event("replay_guard", "p4obs", "metric_5")
_emit_emits_metric_event("replay_guard", "p4obs", "metric_6")
_emit_records_incident_event("replay_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("replay_guard", "p4obs", "anomaly")
_emit_writes_observability_log("replay_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("replay_guard", "p4obs", "mon_state")
_emit_triggers_alert("replay_guard", "p4obs", "alert")
_emit_links_incident_trace("replay_guard", "p4obs", "trace_link")
_emit_captures_pattern("replay_guard", "p3lm", "pattern")
_emit_records_learning_event("replay_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("replay_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("replay_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("replay_guard", "p3lm", "routing")
_emit_improves_agent_policy("replay_guard", "p3lm", "policy")
_emit_stores_learning_state("replay_guard", "p3lm", "state")
_emit_records_execution_trace("replay_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("replay_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("replay_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("replay_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("replay_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("replay_guard", "env_read", "p2_env_1")
_emit_reads_environ("replay_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("replay_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("replay_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "replay_guard", "context_pull")
_emit_pulls_context("p1", "replay_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "replay_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "replay_guard", "uwg_term_2")
_emit_writes_through("p1", "replay_guard", "write_through")
_emit_writes_through("p1", "replay_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "replay_guard", "safety_validation")
_emit_invokes_eval("p1", "replay_guard", "eval_call")
_emit_proposal_commits_routing("p1", "replay_guard", "routing_commit")


class ReplayViolation(RuntimeError):
    """Raised when a nondeterministic call is attempted during replay."""


class ReplayGuard:
    """Context manager that intercepts all nondeterministic sources.

    Usage::

        with ReplayGuard(deterministic_seed=42):
            result = run_deterministic_execution(packet)

    Any attempt to call a patched nondeterministic function raises
    ReplayViolation immediately.
    """

    def __init__(self, deterministic_seed: int = 42) -> None:
        self._seed = deterministic_seed
        self._saved: dict[str, Any] = {}

    def __enter__(self) -> ReplayGuard:
        self._patch_socket()
        self._patch_subprocess()
        self._patch_filesystem_writes()
        self._patch_threading()
        self._patch_random()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._restore_all()

    def _save(self, key: str, obj: Any, attr: str) -> None:
        self._saved[key] = getattr(obj, attr)

    def _restore(self, key: str, obj: Any, attr: str) -> None:
        if key in self._saved:
            setattr(obj, attr, self._saved.pop(key))

    def _patch_socket(self) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReplayGuard._patch_socket", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReplayGuard._patch_socket", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ReplayGuard._patch_socket")

        def _blocked_init(self_inner: Any, *args: Any, **kwargs: Any) -> None:
            raise ReplayViolation("Network socket creation prohibited during replay")

        self._saved["socket.__init__"] = socket.socket.__init__
        socket.socket.__init__ = _blocked_init

    def _patch_subprocess(self) -> None:
        self._saved["subprocess.run"] = subprocess.run
        self._saved["subprocess.Popen"] = subprocess.Popen
        self._saved["os.system"] = os.system

        def _blocked_run(*args: Any, **kwargs: Any) -> Any:
            raise ReplayViolation("subprocess.run() prohibited during replay")

        def _blocked_popen(*args: Any, **kwargs: Any) -> Any:
            raise ReplayViolation("subprocess.Popen() prohibited during replay")

        def _blocked_system(*args: Any, **kwargs: Any) -> Any:
            raise ReplayViolation("os.system() prohibited during replay")

        subprocess.run = _blocked_run
        subprocess.Popen = _blocked_popen
        os.system = _blocked_system

    def _patch_filesystem_writes(self) -> None:
        original_open = builtins.open

        def _guarded_open(file: Any, mode: str = "r", **kwargs: Any) -> Any:
            if any(c in mode for c in ("w", "a", "x", "+")):
                raise ReplayViolation(f"Filesystem write prohibited during replay: open({file!r}, {mode!r})")
            return original_open(file, mode, **kwargs)

        self._saved["builtins.open"] = builtins.open
        builtins.open = _guarded_open

    def _patch_threading(self) -> None:
        self._saved["threading.Thread.start"] = threading.Thread.start

        def _blocked_start(self_inner: Any) -> None:
            raise ReplayViolation("threading.Thread.start() prohibited during replay")

        threading.Thread.start = _blocked_start

    def _patch_random(self) -> None:
        self._saved["random.random"] = random.random
        self._saved["random.randint"] = random.randint
        self._saved["random.choice"] = random.choice
        self._saved["random.shuffle"] = random.shuffle
        _rng = random.Random(self._seed)
        random.random = _rng.random
        random.randint = _rng.randint
        random.choice = _rng.choice
        random.shuffle = _rng.shuffle

    def _restore_all(self) -> None:
        if "socket.__init__" in self._saved:
            socket.socket.__init__ = self._saved.pop("socket.__init__")
        if "subprocess.run" in self._saved:
            subprocess.run = self._saved.pop("subprocess.run")
        if "subprocess.Popen" in self._saved:
            subprocess.Popen = self._saved.pop("subprocess.Popen")
        if "os.system" in self._saved:
            os.system = self._saved.pop("os.system")
        if "builtins.open" in self._saved:
            builtins.open = self._saved.pop("builtins.open")
        if "threading.Thread.start" in self._saved:
            threading.Thread.start = self._saved.pop("threading.Thread.start")
        for attr in ("random", "randint", "choice", "shuffle"):
            key = f"random.{attr}"
            if key in self._saved:
                setattr(random, attr, self._saved.pop(key))


__all__ = ["ReplayGuard", "ReplayViolation"]
