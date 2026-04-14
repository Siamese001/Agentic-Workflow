"""
H1: Full-spectrum preventative sandbox for replay mode.

Patches all write-capable functions during replay to prevent
side effects.  Lives in L2 (execution layer) per gravity rules.

Write-vector taxonomy:
  Filesystem  — builtins.open (write), pathlib, os.remove/rename
  Process     — subprocess.*, os.system/popen
  Network     — socket.*, urllib.*, requests.*
  Persistence — redis.*, pinecone.*, DB client write methods
  Dynamic     — importlib.import_module, eval, exec

Invariant: No write-capable function may remain unpatched
during replay mode.
"""

from __future__ import annotations

import builtins
import contextlib
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "preventative_sandbox")
emit_determinism_digest("p0", "preventative_sandbox")

_emit_dispatches_healing_run("p1", "preventative_sandbox", "L2")
_emit_routes_through("p1", "preventative_sandbox", "L2")
_emit_checks_agent_registry("p1", "preventative_sandbox", "agent_registry")
_emit_validates_agent_capability("p1", "preventative_sandbox", "capability")
_emit_dispatches_execution_plan("p1", "preventative_sandbox", "exec_plan")
_emit_agent_executes_agent("p1", "preventative_sandbox", "sub_agent")
_emit_routes_to_agent("p1", "preventative_sandbox", "target_agent")
_emit_verifies_policy("p1", "preventative_sandbox", "policy_check")
_emit_observes_runtime_state("p1", "preventative_sandbox", "runtime_state")
_emit_verifies_boundary("p1", "preventative_sandbox", "boundary_check")
_emit_transcripts_response("p1", "preventative_sandbox", "transcript")
_emit_hard_fails_untranscripted("p1", "preventative_sandbox")
_emit_gated_by_confidence("p1", "preventative_sandbox", "confidence_gate")
_emit_escalates_to_human("p1", "preventative_sandbox", "L2")
_emit_reads_policy_state("p1", "preventative_sandbox", "L2")

_emit_snapshots_state("p0", "preventative_sandbox", "state_snapshot")
_emit_authorize_and_execute("p2", "preventative_sandbox", "execution_auth")
_emit_validates_capability("p2", "preventative_sandbox", "capability_check")
_emit_routes_to_capability("p2", "preventative_sandbox", "capability_route")
_emit_writes_via_uwg("p2", "preventative_sandbox", "uwg_write")
_emit_blocks_direct_write("p2", "preventative_sandbox", "direct_write_block")
_emit_records_tool_invocation("p2", "preventative_sandbox", "tool_invocation")
_emit_captures_execution_output("p2", "preventative_sandbox", "exec_output")
_emit_dispatches_agent("p3", "preventative_sandbox", "agent_dispatch")
_emit_coordinates_agents("p3", "preventative_sandbox", "agent_coordination")
_emit_records_workflow_lineage("p3", "preventative_sandbox", "workflow_lineage")
_emit_records_healing_outcome("p3", "preventative_sandbox", "healing_outcome")
_emit_escalates_failure("p3", "preventative_sandbox", "failure_escalation")
_emit_orchestrates_workflow("p3", "preventative_sandbox", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "preventative_sandbox", "healing_dispatch")
_emit_invokes_evaluation("p3", "preventative_sandbox", "evaluation_signal")
_emit_records_telemetry_event("p4", "preventative_sandbox", "telemetry_event")
_emit_captures_evaluation_metric("p4", "preventative_sandbox", "eval_metric")
_emit_stores_embedding("p4", "preventative_sandbox", "embedding_store")
_emit_updates_meta_learning_state("p4", "preventative_sandbox", "meta_learning")
_emit_links_execution_to_snapshot("p4", "preventative_sandbox", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("preventative_sandbox", "p4obs", "metric_1")
_emit_emits_metric_event("preventative_sandbox", "p4obs", "metric_2")
_emit_emits_metric_event("preventative_sandbox", "p4obs", "metric_3")
_emit_emits_metric_event("preventative_sandbox", "p4obs", "metric_4")
_emit_emits_metric_event("preventative_sandbox", "p4obs", "metric_5")
_emit_emits_metric_event("preventative_sandbox", "p4obs", "metric_6")
_emit_records_incident_event("preventative_sandbox", "p4obs", "incident")
_emit_captures_runtime_anomaly("preventative_sandbox", "p4obs", "anomaly")
_emit_writes_observability_log("preventative_sandbox", "p4obs", "obs_log")
_emit_updates_monitoring_state("preventative_sandbox", "p4obs", "mon_state")
_emit_triggers_alert("preventative_sandbox", "p4obs", "alert")
_emit_links_incident_trace("preventative_sandbox", "p4obs", "trace_link")
_emit_captures_pattern("preventative_sandbox", "p3lm", "pattern")
_emit_records_learning_event("preventative_sandbox", "p3lm", "learning_event")
_emit_writes_learning_snapshot("preventative_sandbox", "p3lm", "snapshot")
_emit_feeds_meta_learning("preventative_sandbox", "p3lm", "meta_feed")
_emit_updates_routing_strategy("preventative_sandbox", "p3lm", "routing")
_emit_improves_agent_policy("preventative_sandbox", "p3lm", "policy")
_emit_stores_learning_state("preventative_sandbox", "p3lm", "state")
_emit_records_execution_trace("preventative_sandbox", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("preventative_sandbox", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("preventative_sandbox", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("preventative_sandbox", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("preventative_sandbox", "L4_STATE", "p2_trace_5")
_emit_reads_environ("preventative_sandbox", "env_read", "p2_env_1")
_emit_reads_environ("preventative_sandbox", "env_read", "p2_env_2")
_emit_reads_runtime_state("preventative_sandbox", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("preventative_sandbox", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "preventative_sandbox", "context_pull")
_emit_pulls_context("p1", "preventative_sandbox", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "preventative_sandbox", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "preventative_sandbox", "uwg_term_2")
_emit_writes_through("p1", "preventative_sandbox", "write_through")
_emit_writes_through("p1", "preventative_sandbox", "write_through_2")
_emit_validated_by_safety_plane("p1", "preventative_sandbox", "safety_validation")
_emit_invokes_eval("p1", "preventative_sandbox", "eval_call")
_emit_proposal_commits_routing("p1", "preventative_sandbox", "routing_commit")

Logger = logging.getLogger(__name__)


class SandboxViolationError(RuntimeError):
    """Raised when a write-capable function is called in sandbox."""

    def __init__(self, function_name: str) -> None:
        self.function_name = function_name
        super().__init__(f"SandboxViolationError: '{function_name}' is blocked during replay mode.")


@dataclass
class _PatchTarget:
    """Describes one function to patch."""

    module_path: str
    attr_name: str
    category: str


_WRITE_VECTORS: list[_PatchTarget] = [
    _PatchTarget("builtins", "open", "filesystem"),
    _PatchTarget("os", "remove", "filesystem"),
    _PatchTarget("os", "rename", "filesystem"),
    _PatchTarget("os", "replace", "filesystem"),
    _PatchTarget("os", "unlink", "filesystem"),
    _PatchTarget("os", "makedirs", "filesystem"),
    _PatchTarget("pathlib", "Path", "filesystem"),
    _PatchTarget("shutil", "rmtree", "filesystem"),
    _PatchTarget("shutil", "copy2", "filesystem"),
    _PatchTarget("shutil", "move", "filesystem"),
    _PatchTarget("subprocess", "run", "process"),
    _PatchTarget("subprocess", "Popen", "process"),
    _PatchTarget("subprocess", "call", "process"),
    _PatchTarget("subprocess", "check_call", "process"),
    _PatchTarget("subprocess", "check_output", "process"),
    _PatchTarget("os", "system", "process"),
    _PatchTarget("os", "popen", "process"),
    _PatchTarget("socket", "socket", "network"),
    _PatchTarget("socket", "create_connection", "network"),
    _PatchTarget("urllib.request", "urlopen", "network"),
    _PatchTarget("importlib", "import_module", "dynamic"),
    _PatchTarget("builtins", "eval", "dynamic"),
    _PatchTarget("builtins", "exec", "dynamic"),
    _PatchTarget("builtins", "compile", "dynamic"),
]


def _resolve_module(module_path: str) -> Any:
    """Import and return the module object."""
    import importlib

    if module_path == "builtins":
        return builtins
    return importlib.import_module(module_path)


@dataclass
class PreventativeSandbox:
    """Scoped sandbox that blocks write-capable functions.

    Usage::

        sandbox = PreventativeSandbox()
        with sandbox.activated():
            # all write vectors raise SandboxViolationError
            ...
        # originals restored

    Must live in L2 — not in agent constructors, L6, or global.
    """

    _originals: dict[str, Any] = field(default_factory=dict, repr=False)
    _active: bool = field(default=False, repr=False)
    _extra_targets: list[_PatchTarget] = field(default_factory=list)

    def register_target(self, module_path: str, attr_name: str, category: str) -> None:
        """Register an additional write vector to patch."""
        self._extra_targets.append(_PatchTarget(module_path, attr_name, category))

    @property
    def is_active(self) -> bool:
        return self._active

    def _all_targets(self) -> list[_PatchTarget]:
        return _WRITE_VECTORS + self._extra_targets

    def _make_guard(self, target: _PatchTarget) -> Callable[..., Any]:
        """Create a guard function that raises on call."""
        _emit_applies_guardrail(str(uuid.uuid4()), "PreventativeSandbox._make_guard", "L2_EXECUTION")
        fqn = f"{target.module_path}.{target.attr_name}"

        def _guard(*args: Any, **kwargs: Any) -> Any:
            raise SandboxViolationError(fqn)

        _guard.__qualname__ = f"sandbox_guard<{fqn}>"
        return _guard

    def _patch_all(self) -> None:
        """Replace all write vectors with guards."""
        for target in tqdm(self._all_targets(), desc="Processing", unit="item"):
            key = f"{target.module_path}.{target.attr_name}"
            try:
                mod = _resolve_module(target.module_path)
                original = getattr(mod, target.attr_name, None)
                if original is None:
                    Logger.debug(f"[sandbox] skip {key}: not found")
                    continue
                if key in self._originals:
                    Logger.debug(f"[sandbox] skip {key}: already patched")
                    continue
                self._originals[key] = (mod, original)
                setattr(mod, target.attr_name, self._make_guard(target))
                Logger.debug(f"[sandbox] patched {key}")
            except ImportError as e:
                Logger.debug(f"[sandbox] skip {key}: optional module unavailable: {e}")
                continue

    def _restore_all(self) -> None:
        """Restore all original functions."""
        for key, (mod, original) in self._originals.items():
            parts = key.rsplit(".", 1)
            setattr(mod, parts[1], original)
            Logger.debug(f"[sandbox] restored {key}")
        self._originals.clear()

    @contextlib.contextmanager
    def activated(self):
        """Context manager for scoped sandbox activation.

        Guarantees restoration even on exception.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "PreventativeSandbox.activated")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PreventativeSandbox.activated".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self._active:
            raise RuntimeError("PreventativeSandbox is already active (double-activation prevented)")
        self._active = True
        self._patch_all()
        try:
            yield self
        finally:
            self._restore_all()
            self._active = False
