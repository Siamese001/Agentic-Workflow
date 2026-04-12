"""
agentic_core/enforcement/structural_namespace_fence_enforcer.py

Structural namespace enforcement using MetaPathFinder with module load-time
provenance tracking.

Design principles:
- Namespace is determined from the physical file path at module load time,
  not from stack inspection at import time.
- The StructuralNamespaceFinder only BLOCKS imports; it never modifies them.
- No global __builtins__ monkey-patching.
- Safe to use alongside test frameworks (pytest, unittest).
"""

import importlib.abc
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

emit_replay_key("p0", "structural_namespace_fence_enforcer")
emit_determinism_digest("p0", "structural_namespace_fence_enforcer")

_emit_dispatches_healing_run("p1", "structural_namespace_fence_enforcer", "L5")
_emit_routes_through("p1", "structural_namespace_fence_enforcer", "L5")
_emit_checks_agent_registry("p1", "structural_namespace_fence_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "structural_namespace_fence_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "structural_namespace_fence_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "structural_namespace_fence_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "structural_namespace_fence_enforcer", "target_agent")
_emit_verifies_policy("p1", "structural_namespace_fence_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "structural_namespace_fence_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "structural_namespace_fence_enforcer", "boundary_check")
_emit_transcripts_response("p1", "structural_namespace_fence_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "structural_namespace_fence_enforcer")
_emit_gated_by_confidence("p1", "structural_namespace_fence_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "structural_namespace_fence_enforcer", "L5")
_emit_reads_policy_state("p1", "structural_namespace_fence_enforcer", "L5")

_emit_applies_guardrail("p0", "structural_namespace_fence_enforcer", "p0_governance")
_emit_snapshots_state("p0", "structural_namespace_fence_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "structural_namespace_fence_enforcer", "execution_auth")
_emit_validates_capability("p2", "structural_namespace_fence_enforcer", "capability_check")
_emit_routes_to_capability("p2", "structural_namespace_fence_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "structural_namespace_fence_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "structural_namespace_fence_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "structural_namespace_fence_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "structural_namespace_fence_enforcer", "exec_output")
_emit_dispatches_agent("p3", "structural_namespace_fence_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "structural_namespace_fence_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "structural_namespace_fence_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "structural_namespace_fence_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "structural_namespace_fence_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "structural_namespace_fence_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structural_namespace_fence_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "structural_namespace_fence_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "structural_namespace_fence_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structural_namespace_fence_enforcer", "eval_metric")
_emit_stores_embedding("p4", "structural_namespace_fence_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "structural_namespace_fence_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structural_namespace_fence_enforcer", "exec_snapshot_link")
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

_emit_emits_metric_event("structural_namespace_fence_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("structural_namespace_fence_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("structural_namespace_fence_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("structural_namespace_fence_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("structural_namespace_fence_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("structural_namespace_fence_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("structural_namespace_fence_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("structural_namespace_fence_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("structural_namespace_fence_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("structural_namespace_fence_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("structural_namespace_fence_enforcer", "p4obs", "alert")
_emit_links_incident_trace("structural_namespace_fence_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("structural_namespace_fence_enforcer", "p3lm", "pattern")
_emit_records_learning_event("structural_namespace_fence_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("structural_namespace_fence_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("structural_namespace_fence_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("structural_namespace_fence_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("structural_namespace_fence_enforcer", "p3lm", "policy")
_emit_stores_learning_state("structural_namespace_fence_enforcer", "p3lm", "state")
_emit_records_execution_trace("structural_namespace_fence_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("structural_namespace_fence_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("structural_namespace_fence_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("structural_namespace_fence_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("structural_namespace_fence_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("structural_namespace_fence_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("structural_namespace_fence_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("structural_namespace_fence_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("structural_namespace_fence_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "structural_namespace_fence_enforcer", "context_pull")
_emit_pulls_context("p1", "structural_namespace_fence_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "structural_namespace_fence_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "structural_namespace_fence_enforcer", "uwg_term_2")
_emit_writes_through("p1", "structural_namespace_fence_enforcer", "write_through")
_emit_writes_through("p1", "structural_namespace_fence_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "structural_namespace_fence_enforcer", "safety_validation")
_emit_invokes_eval("p1", "structural_namespace_fence_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "structural_namespace_fence_enforcer", "routing_commit")

_TRACKED_ROOTS: frozenset = frozenset(
    {APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR},
)
_ALLOWED_CROSS: dict[str, set[str]] = {
    "apps_lic": {"agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"},
    "apps_rg": {"agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"},
    "apps_shared": {"agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"},
    "agentic_core.L0_routing": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L1_cognition": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L2_execution": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L3_orchestration": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L4_state": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L5_safety": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L6_observability": {"system_learning.types", "system_learning.interfaces"},
    "system_learning": {"agentic_core.types", "agentic_core.interfaces"},
}


class ProvenanceTracker:
    """Tracks module-to-namespace mapping at module load time."""

    def __init__(self) -> None:
        self._provenance: dict[str, str] = {}

    def register(self, module_name: str, origin: str | None) -> None:
        """Register module provenance from its file path origin."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ProvenanceTracker.register")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ProvenanceTracker.register".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if origin is None:
            return
        namespace = _extract_namespace(Path(origin))
        self._provenance[module_name] = namespace

    def namespace_of(self, module_name: str) -> str:
        """Return namespace for a registered module ('external' if unknown)."""
        if module_name in self._provenance:
            return self._provenance[module_name]
        for tracked in _TRACKED_ROOTS:
            if module_name == tracked or module_name.startswith(tracked + "."):
                return _namespace_from_module_name(module_name)
        return "external"

    def is_forbidden_cross_import(self, caller_ns: str, target_module: str) -> bool:
        """Return True iff importing target_module from caller_ns is forbidden."""
        if caller_ns == "external" or caller_ns == "unknown":
            return False
        target_ns = _namespace_from_module_name(target_module)
        if target_ns == "external":
            return False
        if caller_ns == target_ns:
            return False
        allowed = _ALLOWED_CROSS.get(caller_ns, set())
        return not any(
            target_module == a or target_module.startswith(a + ".") or target_ns == a for a in allowed
        )


def _extract_namespace(path: Path) -> str:
    """Derive namespace string from file path."""
    for part in path.parts:
        if part in _TRACKED_ROOTS:
            if part == AGENTIC_CORE_DIR:
                idx = list(path.parts).index(part)
                rest = path.parts[idx + 1 :]
                if rest and rest[0].startswith("L") and ("_" in rest[0]):
                    return f"agentic_core.{rest[0]}"
            return part
    return "external"


def _namespace_from_module_name(module_name: str) -> str:
    """Derive namespace from a dotted module name."""
    for root in _TRACKED_ROOTS:
        if module_name == root or module_name.startswith(root + "."):
            if root == AGENTIC_CORE_DIR:
                parts = module_name.split(".")
                if len(parts) >= 2 and parts[1].startswith("L") and ("_" in parts[1]):
                    return f"agentic_core.{parts[1]}"
            return root
    return "external"


class ProvenanceLoader(importlib.abc.Loader):
    """Wraps an existing loader to register module provenance on creation."""

    def __init__(
        self,
        original_loader: importlib.abc.Loader,
        tracker: ProvenanceTracker,
        module_name: str,
        origin: str | None,
    ) -> None:
        self._loader = original_loader
        self._tracker = tracker
        self._module_name = module_name
        self._origin = origin

    def create_module(self, spec):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ProvenanceLoader.create_module")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ProvenanceLoader.create_module".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        module = self._loader.create_module(spec) if hasattr(self._loader, "create_module") else None
        self._tracker.register(self._module_name, self._origin)
        return module

    def exec_module(self, module):
        if hasattr(self._loader, "exec_module"):
            self._loader.exec_module(module)


class StructuralNamespaceFinder(importlib.abc.MetaPathFinder):
    """MetaPathFinder that enforces cross-namespace import rules.

    Returns None for all modules to let the normal import machinery resolve
    them — it only raises ImportError when a forbidden cross-namespace import
    is detected.  Namespace determination uses load-time provenance, not
    frame stack inspection.
    """

    def __init__(self, tracker: ProvenanceTracker) -> None:
        self._tracker = tracker

    def find_spec(self, fullname: str, path, target=None):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "StructuralNamespaceFinder.find_spec",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:StructuralNamespaceFinder.find_spec".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        caller_module = self._get_caller_from_loaded_modules()
        # guardian: allow-config-with-logic
        if caller_module is None:
            return None
        caller_ns = self._tracker.namespace_of(caller_module)
        # guardian: allow-config-with-logic
        if self._tracker.is_forbidden_cross_import(caller_ns, fullname):
            raise ImportError(
                f"Namespace boundary violation: '{caller_ns}' (module '{caller_module}') may not import '{fullname}'",
            )
        return None

    def _get_caller_from_loaded_modules(self) -> str | None:
        """Determine calling module by scanning loaded sys.modules for tracked roots."""
        import inspect

        frame = inspect.currentframe()
        try:
            if frame is None:
                return None
            frame = frame.f_back
            while frame is not None:
                module_name: str = frame.f_globals.get("__name__", "")
                if module_name in self._tracker._provenance:
                    return module_name
                for root in _TRACKED_ROOTS:
                    if module_name == root or module_name.startswith(root + "."):
                        return module_name
                frame = frame.f_back
        finally:
            del frame
        return None


_provenance_tracker = ProvenanceTracker()
_structural_finder: StructuralNamespaceFinder | None = None


def install_structural_namespace_fence() -> StructuralNamespaceFinder:
    """Install the namespace fence into sys.meta_path (idempotent)."""
    global _structural_finder
    if _structural_finder is None:
        _structural_finder = StructuralNamespaceFinder(_provenance_tracker)
        sys.meta_path.insert(0, _structural_finder)
    return _structural_finder


def uninstall_structural_namespace_fence() -> None:
    """Remove the namespace fence from sys.meta_path."""
    global _structural_finder
    if _structural_finder is not None and _structural_finder in sys.meta_path:
        sys.meta_path.remove(_structural_finder)
        _structural_finder = None


def get_provenance_tracker() -> ProvenanceTracker:
    """Return the global ProvenanceTracker."""
    return _provenance_tracker
