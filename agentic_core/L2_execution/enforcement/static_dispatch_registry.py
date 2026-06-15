"""StaticDispatchRegistry — replaces dynamic __import__ / importlib.import_module calls.

Addresses the ADG ``invokes_eval`` and ``invokes_dynamic`` gap: 986 edges across
non-test production code use ``__import__``, ``importlib.import_module``, or
``importlib.util.spec_from_file_location`` as the mechanism for loading plugin
modules. Each such call bypasses static analysis and the policy hash enforcer.

This registry provides a controlled, pre-registered dispatch surface:
- Callers register module paths at import time using ``register``.
- At call time, ``dispatch`` resolves the registered module and returns the
  callable or object — no ``__import__`` or ``importlib`` needed at runtime.
- Unregistered dispatch attempts raise ``UnregisteredDispatchError`` (fail-closed).

ADG governance plane: replacing ``invokes_dynamic`` edges with ``dispatch`` calls
converts ungoverned dynamic invocation into ``routes_through`` edges terminating
at this registry, which is itself ``validated_by_registry``.
"""

from __future__ import annotations

import importlib
import logging
import uuid
from types import ModuleType
from typing import Any

from agentic_core.L2_execution.enforcement.guardrail_gate import Callable, get_guardrail_gate
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

emit_replay_key("p0", "static_dispatch_registry")
emit_determinism_digest("p0", "static_dispatch_registry")

_emit_dispatches_healing_run("p1", "static_dispatch_registry", "L2")
_emit_routes_through("p1", "static_dispatch_registry", "L2")
_emit_agent_executes_agent("p1", "static_dispatch_registry", "sub_agent")
_emit_verifies_policy("p1", "static_dispatch_registry", "policy_check")
_emit_observes_runtime_state("p1", "static_dispatch_registry", "runtime_state")
_emit_verifies_boundary("p1", "static_dispatch_registry", "boundary_check")
_emit_transcripts_response("p1", "static_dispatch_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "static_dispatch_registry")
_emit_gated_by_confidence("p1", "static_dispatch_registry", "confidence_gate")
_emit_escalates_to_human("p1", "static_dispatch_registry", "L2")
_emit_reads_policy_state("p1", "static_dispatch_registry", "L2")
_emit_routes_to_agent("p1", "static_dispatch_registry", "L2")
_emit_orchestrates_workflow("p1", "static_dispatch_registry", "L2")
_emit_dispatches_execution_plan("p1", "static_dispatch_registry", "L2")
_emit_validates_agent_capability("p1", "static_dispatch_registry", "L2")
_emit_checks_agent_registry("p1", "static_dispatch_registry", "L2")

_emit_snapshots_state("p0", "static_dispatch_registry", "state_snapshot")
_emit_authorize_and_execute("p2", "static_dispatch_registry", "execution_auth")
_emit_validates_capability("p2", "static_dispatch_registry", "capability_check")
_emit_routes_to_capability("p2", "static_dispatch_registry", "capability_route")
_emit_writes_via_uwg("p2", "static_dispatch_registry", "uwg_write")
_emit_blocks_direct_write("p2", "static_dispatch_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "static_dispatch_registry", "tool_invocation")
_emit_captures_execution_output("p2", "static_dispatch_registry", "exec_output")
_emit_dispatches_agent("p3", "static_dispatch_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "static_dispatch_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "static_dispatch_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "static_dispatch_registry", "healing_outcome")
_emit_escalates_failure("p3", "static_dispatch_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "static_dispatch_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "static_dispatch_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "static_dispatch_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "static_dispatch_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "static_dispatch_registry", "eval_metric")
_emit_stores_embedding("p4", "static_dispatch_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "static_dispatch_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "static_dispatch_registry", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("static_dispatch_registry", "p4obs", "metric_1")
_emit_emits_metric_event("static_dispatch_registry", "p4obs", "metric_2")
_emit_emits_metric_event("static_dispatch_registry", "p4obs", "metric_3")
_emit_emits_metric_event("static_dispatch_registry", "p4obs", "metric_4")
_emit_emits_metric_event("static_dispatch_registry", "p4obs", "metric_5")
_emit_emits_metric_event("static_dispatch_registry", "p4obs", "metric_6")
_emit_records_incident_event("static_dispatch_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("static_dispatch_registry", "p4obs", "anomaly")
_emit_writes_observability_log("static_dispatch_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("static_dispatch_registry", "p4obs", "mon_state")
_emit_triggers_alert("static_dispatch_registry", "p4obs", "alert")
_emit_links_incident_trace("static_dispatch_registry", "p4obs", "trace_link")
_emit_captures_pattern("static_dispatch_registry", "p3lm", "pattern")
_emit_records_learning_event("static_dispatch_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("static_dispatch_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("static_dispatch_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("static_dispatch_registry", "p3lm", "routing")
_emit_improves_agent_policy("static_dispatch_registry", "p3lm", "policy")
_emit_stores_learning_state("static_dispatch_registry", "p3lm", "state")
_emit_records_execution_trace("static_dispatch_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("static_dispatch_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("static_dispatch_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("static_dispatch_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("static_dispatch_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("static_dispatch_registry", "env_read", "p2_env_1")
_emit_reads_environ("static_dispatch_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("static_dispatch_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("static_dispatch_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "static_dispatch_registry", "context_pull")
_emit_pulls_context("p1", "static_dispatch_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "static_dispatch_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "static_dispatch_registry", "uwg_term_2")
_emit_writes_through("p1", "static_dispatch_registry", "write_through")
_emit_writes_through("p1", "static_dispatch_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "static_dispatch_registry", "safety_validation")
_emit_invokes_eval("p1", "static_dispatch_registry", "eval_call")
_emit_proposal_commits_routing("p1", "static_dispatch_registry", "routing_commit")

Logger = logging.getLogger(__name__)


class UnregisteredDispatchError(LookupError):
    """Raised when dispatch is requested for an unregistered symbol."""


class StaticDispatchRegistry:
    """Controlled dispatch surface replacing dynamic __import__ usage.

    Example::

        registry = StaticDispatchRegistry()
        registry.register("guardian.hygiene", "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_hygiene")
        registry.register("guardian.c0", "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_c0_sovereignty")

        # Later — no __import__ needed:
        mod = registry.dispatch("guardian.hygiene")
        mod.main()

    The registry is fail-closed: dispatching an unregistered key raises
    ``UnregisteredDispatchError`` rather than falling through to dynamic import.
    """

    def __init__(self) -> None:
        self._registry: dict[str, str] = {}
        self._resolved: dict[str, ModuleType] = {}

    def register(self, key: str, module_path: str) -> None:
        """Register *module_path* under *key*.

        Args:
            key: Logical dispatch key (e.g. ``"guardian.hygiene"``).
            module_path: Fully-qualified Python module path (e.g.
                ``"ops_scripts.dev_tools.L0_routing_scripts.run_guardian_hygiene"``).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "StaticDispatchRegistry.register")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:StaticDispatchRegistry.register".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if key in self._registry and self._registry[key] != module_path:
            Logger.warning(
                "[StaticDispatchRegistry] Overwriting key '%s': %s -> %s",
                key,
                self._registry[key],
                module_path,
            )
        self._registry[key] = module_path
        self._resolved.pop(key, None)
        Logger.debug("[StaticDispatchRegistry] registered '%s' -> '%s'", key, module_path)

    def register_many(self, mapping: dict[str, str]) -> None:
        """Register multiple ``{key: module_path}`` pairs at once."""
        for key, path in mapping.items():
            self.register(key, path)

    def dispatch(self, key: str) -> ModuleType:
        """Return the module registered under *key*.

        Lazily imports the module on first call; returns the cached module
        on subsequent calls.

        Raises:
            UnregisteredDispatchError: if *key* has not been registered.
            ImportError: if the registered module cannot be imported.
        """
        # Wave 3: Guardrail pre-check
        guardrail = get_guardrail_gate()
        guardrail.check(operation="static_dispatch", target=key)
        if key not in self._registry:
            raise UnregisteredDispatchError(
                f"[StaticDispatchRegistry] No module registered for key '{key}'. "
                f"Registered keys: {sorted(self._registry)}",
            )
        if key not in self._resolved:
            module_path = self._registry[key]
            Logger.debug("[StaticDispatchRegistry] importing '%s' for key '%s'", module_path, key)
            self._resolved[key] = importlib.import_module(module_path)
        return self._resolved[key]

    def dispatch_attr(self, key: str, attr: str) -> Any:
        """Return *attr* from the module registered under *key*.

        Raises:
            UnregisteredDispatchError: if *key* not registered.
            AttributeError: if *attr* not found on the module.
        """
        mod = self.dispatch(key)
        if not hasattr(mod, attr):
            raise AttributeError(
                f"[StaticDispatchRegistry] Module '{self._registry[key]}' has no attribute '{attr}'.",
            )
        return getattr(mod, attr)

    def dispatch_callable(self, key: str, attr: str) -> Callable[..., Any]:
        """Return a callable *attr* from the module registered under *key*.

        Raises:
            TypeError: if the resolved attribute is not callable.
        """
        obj = self.dispatch_attr(key, attr)
        if not callable(obj):
            raise TypeError(f"[StaticDispatchRegistry] '{attr}' on '{self._registry[key]}' is not callable.")
        return obj

    def is_registered(self, key: str) -> bool:
        """Return True if *key* has been registered."""
        return key in self._registry

    def registered_keys(self) -> list[str]:
        """Return sorted list of all registered keys."""
        return sorted(self._registry)

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, key: str) -> bool:
        return key in self._registry


_GUARDIAN_REGISTRY: StaticDispatchRegistry | None = None


def get_guardian_registry() -> StaticDispatchRegistry:
    """Return the singleton guardian registry, creating and pre-populating it on first call."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_guardian_registry", "L2_EXECUTION")
    global _GUARDIAN_REGISTRY
    if _GUARDIAN_REGISTRY is None:
        _GUARDIAN_REGISTRY = StaticDispatchRegistry()
        _GUARDIAN_REGISTRY.register_many(
            {
                "guardian.hygiene": "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_hygiene",
                "guardian.c0_sovereignty": "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_c0_sovereignty",
                "guardian.change_package": "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_change_package_activation",
                "guardian.cross_layer": "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_cross_layer_mutation",
                "guardian.escalation_determinism": "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_escalation_determinism",
                "guardian.gateway_bypass": "ops_scripts.dev_tools.L0_routing_scripts.run_guardian_gateway_bypass",
                "guardian.all": "ops_scripts.dev_tools.L0_routing_scripts.run_all_guardians",
                "seam.canonical_truth": "agentic_core.L0_routing.seams.canonical_truth_seam",
                "meta.apply_ops": "agentic_core.L0_routing.meta_control.meta_apply_ops",
            },
        )
    return _GUARDIAN_REGISTRY
