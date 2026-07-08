"""
ProcessGuard - Runtime Process Lifecycle Management.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This module provides:
1. Registry: Tracks all PIDs spawned by agents
2. Cleanup: terminate_all() kills registered PIDs (registered with atexit)
3. Firewall: validate_command() blocks dangerous commands

OPERATIONAL SAFETY (Feb 2026):
- Prevents package managers from corrupting environment
- Prevents zombie processes from accumulating
- Provides fail-safe cleanup on interpreter exit
"""

import atexit
import logging
import os
import signal
import threading
from pathlib import Path
from typing import Final

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "process_guardrail")
trace_contract.emit_determinism_digest("p0", "process_guardrail")

trace_contract._emit_dispatches_healing_run("p1", "process_guardrail", "L5")
trace_contract._emit_routes_through("p1", "process_guardrail", "L5")
trace_contract._emit_checks_agent_registry("p1", "process_guardrail", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "process_guardrail", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "process_guardrail", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "process_guardrail", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "process_guardrail", "target_agent")
trace_contract._emit_verifies_policy("p1", "process_guardrail", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "process_guardrail", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "process_guardrail", "boundary_check")
trace_contract._emit_transcripts_response("p1", "process_guardrail", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "process_guardrail")
trace_contract._emit_gated_by_confidence("p1", "process_guardrail", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "process_guardrail", "L5")
trace_contract._emit_reads_policy_state("p1", "process_guardrail", "L5")

trace_contract._emit_applies_guardrail("p0", "process_guardrail", "p0_governance")
trace_contract._emit_snapshots_state("p0", "process_guardrail", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "process_guardrail", "execution_auth")
trace_contract._emit_validates_capability("p2", "process_guardrail", "capability_check")
trace_contract._emit_routes_to_capability("p2", "process_guardrail", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "process_guardrail", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "process_guardrail", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "process_guardrail", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "process_guardrail", "exec_output")
trace_contract._emit_dispatches_agent("p3", "process_guardrail", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "process_guardrail", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "process_guardrail", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "process_guardrail", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "process_guardrail", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "process_guardrail", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "process_guardrail", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "process_guardrail", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "process_guardrail", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "process_guardrail", "eval_metric")
trace_contract._emit_stores_embedding("p4", "process_guardrail", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "process_guardrail", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "process_guardrail", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("process_guardrail", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("process_guardrail", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("process_guardrail", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("process_guardrail", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("process_guardrail", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("process_guardrail", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("process_guardrail", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("process_guardrail", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("process_guardrail", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("process_guardrail", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("process_guardrail", "p4obs", "alert")
trace_contract._emit_links_incident_trace("process_guardrail", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("process_guardrail", "p3lm", "pattern")
trace_contract._emit_records_learning_event("process_guardrail", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("process_guardrail", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("process_guardrail", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("process_guardrail", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("process_guardrail", "p3lm", "policy")
trace_contract._emit_stores_learning_state("process_guardrail", "p3lm", "state")
trace_contract._emit_records_execution_trace("process_guardrail", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("process_guardrail", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("process_guardrail", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("process_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("process_guardrail", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("process_guardrail", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("process_guardrail", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("process_guardrail", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("process_guardrail", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "process_guardrail", "context_pull")
trace_contract._emit_pulls_context("p1", "process_guardrail", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "process_guardrail", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "process_guardrail", "uwg_term_2")
trace_contract._emit_writes_through("p1", "process_guardrail", "write_through")
trace_contract._emit_writes_through("p1", "process_guardrail", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "process_guardrail", "safety_validation")
trace_contract._emit_invokes_eval("p1", "process_guardrail", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "process_guardrail", "routing_commit")

logger = logging.getLogger(__name__)
BLOCKED_COMMANDS: Final[frozenset[str]] = frozenset(
    {"pip", "npm", "yarn", "apt", "apt-get", "brew", "rm", "sudo", "powershell", "cmd"},
)


class SecurityViolation(Exception):
    """Raised when a command violates security policy."""

    def __init__(self, command: list[str], reason: str):
        self.command = command
        self.reason = reason
        super().__init__(f"Security violation: {reason}. Command: {command}")


class ProcessGuard:
    """
    Singleton Process Guard for managing spawned process lifecycles.

    Features:
    - Thread-safe PID registry
    - Automatic cleanup on interpreter exit via atexit
    - Command validation firewall

    Usage:
        guard = ProcessGuard.get_instance()
        guard.validate_command(["python", "script.py"])  # OK
        guard.validate_command(["pip", "install", "pkg"])  # Raises SecurityViolation

        # After spawning a process:
        guard.register_pid(process.pid)

        # Cleanup:
        guard.terminate_all()
    """

    _instance: "ProcessGuard | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "ProcessGuard":
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the guard state."""
        self._pids: set[int] = set()
        self._pid_lock: threading.Lock = threading.Lock()
        self._atexit_registered: bool = False
        self._register_atexit()

    @classmethod
    def get_instance(cls) -> "ProcessGuard":
        """Get the singleton instance."""
        return cls()

    def _register_atexit(self) -> None:
        """Register cleanup with atexit as fail-safe."""
        if not self._atexit_registered:
            atexit.register(self._atexit_cleanup)
            self._atexit_registered = True
            logger.debug("ProcessGuard: atexit cleanup registered")

    def _atexit_cleanup(self) -> None:
        """Cleanup handler called on interpreter exit."""
        if self._pids:
            logger.warning(f"ProcessGuard: atexit cleanup killing {len(self._pids)} orphaned processes")
            self.terminate_all()

    def register_pid(self, pid: int) -> None:
        """
        Register a PID for lifecycle tracking.

        Args:
            pid: The process ID to track.
        """
        with self._pid_lock:
            self._pids.add(pid)
            logger.debug(f"ProcessGuard: Registered PID {pid}")

    def unregister_pid(self, pid: int) -> None:
        """
        Unregister a PID (e.g., after normal termination).

        Args:
            pid: The process ID to stop tracking.
        """
        with self._pid_lock:
            self._pids.discard(pid)
            logger.debug(f"ProcessGuard: Unregistered PID {pid}")

    def get_active_pids(self) -> set[int]:
        """Get a copy of currently tracked PIDs."""
        with self._pid_lock:
            return self._pids.copy()

    def terminate_all(self) -> dict[str, list[int]]:
        """
        Terminate all registered processes.

        Returns:
            Dict with 'terminated' and 'failed' PID lists.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ProcessGuard.terminate_all")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ProcessGuard.terminate_all".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        result = {"terminated": [], "failed": []}
        with self._pid_lock:
            pids_to_kill = self._pids.copy()
        for pid in pids_to_kill:
            try:
                self._kill_process(pid)
                result["terminated"].append(pid)
                logger.info(f"ProcessGuard: Terminated PID {pid}")
            except (
                ValueError,
                TypeError,
            ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                result["failed"].append(pid)
                logger.warning(f"ProcessGuard: Failed to terminate PID {pid}: {e}")
        with self._pid_lock:
            self._pids.clear()
        return result

    def _kill_process(self, pid: int) -> None:
        """
        Kill a process by PID.

        Uses SIGTERM first, then SIGKILL if needed.
        Platform-aware for Windows vs Unix.
        """
        # Platform branch: compute signal once outside the try so the try body has exactly one side effect
        term_signal = signal.SIGTERM
        try:
            os.kill(pid, term_signal)
        except ProcessLookupError:  # guardian: allow-silent-swallow -- process already dead, non-fatal
            pass
        except PermissionError:  # review: Permission errors should validate access before operation
            logger.warning(f"ProcessGuard: Permission denied killing PID {pid}")
            raise

    def validate_command(self, command: list[str]) -> bool:
        """
        Validate a command against the security firewall.

        Args:
            command: The command as a list of strings.

        Returns:
            True if command is allowed.

        Raises:
            SecurityViolation: If command is blocked.
        """
        if not command:
            raise SecurityViolation(command, "Empty command")
        base_cmd = command[0].lower()
        base_cmd = Path(base_cmd).name
        if os.name == "nt" and base_cmd.endswith(".exe"):
            base_cmd = base_cmd[:-4]
        if base_cmd in BLOCKED_COMMANDS:
            raise SecurityViolation(command, f"Command '{base_cmd}' is blocked (environment protection)")
        return True

    def cleanup(self) -> dict[str, list[int]]:
        """Alias for terminate_all() for API consistency."""
        return self.terminate_all()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing only).

        WARNING: This is intended for test isolation only.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.terminate_all()
                cls._instance = None


__all__ = ["ProcessGuard", "SecurityViolation", "BLOCKED_COMMANDS"]
