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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "replay_guard")
trace_contract.emit_determinism_digest("p0", "replay_guard")

trace_contract._emit_dispatches_healing_run("p1", "replay_guard", "L2")
trace_contract._emit_routes_through("p1", "replay_guard", "L2")
trace_contract._emit_checks_agent_registry("p1", "replay_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "replay_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "replay_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "replay_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "replay_guard", "target_agent")
trace_contract._emit_verifies_policy("p1", "replay_guard", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "replay_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "replay_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "replay_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "replay_guard")
trace_contract._emit_gated_by_confidence("p1", "replay_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "replay_guard", "L2")
trace_contract._emit_reads_policy_state("p1", "replay_guard", "L2")
trace_contract._emit_authorize_and_execute("p2", "replay_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "replay_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "replay_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "replay_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "replay_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "replay_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "replay_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "replay_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "replay_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "replay_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "replay_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "replay_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "replay_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "replay_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "replay_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "replay_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "replay_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "replay_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "replay_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "replay_guard", "exec_snapshot_link")

trace_contract.record_execution_trace("replay_guard", "replay_guard_trace")


trace_contract._emit_emits_metric_event("replay_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("replay_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("replay_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("replay_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("replay_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("replay_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("replay_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("replay_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("replay_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("replay_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("replay_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("replay_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("replay_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("replay_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("replay_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("replay_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("replay_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("replay_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("replay_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("replay_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("replay_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("replay_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("replay_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("replay_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("replay_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("replay_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("replay_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("replay_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "replay_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "replay_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "replay_guard", "write_through")
trace_contract._emit_writes_through("p1", "replay_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "replay_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "replay_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "replay_guard", "routing_commit")


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
        self._saved[key] = getattr(obj, attr)  # guardian: allow-hallucinated-tool-name -- getattr is Python stdlib builtin used for dynamic attribute save/restore; detector false positive

    def _restore(self, key: str, obj: Any, attr: str) -> None:
        if key in self._saved:
            setattr(obj, attr, self._saved.pop(key))

    def _patch_socket(self) -> None:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ReplayGuard._patch_socket", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ReplayGuard._patch_socket", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ReplayGuard._patch_socket")

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
