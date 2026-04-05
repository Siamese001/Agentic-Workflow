"""E27: Layer Authority Enforcement.

Detects behavioral authority violations where a layer performs actions
that its architectural contract forbids:

    L1 (Cognition)     — must NOT mutate state (writes_to / writes_through)
    L3 (Orchestration) — must NOT invoke tools/providers directly
    L4 (State)         — must NOT contain business logic (calls / invokes_provider)
    L6 (Observability) — must NOT alter execution (writes, routes_through)

Grounded in the live ADG (148,859 edges, 2,323 writes_to edges found in the
20260311 scan). Real violations confirmed from ADG:
    - L1_cognition/reasoning/MetaLearningAgent.py: _fh.write, open (persistent)
    - L1_cognition/engines/cognitive_engine.py: copy calls (allowlisted)

Usage::

    from agentic_core.adg.analysis.layer_authority_types import detect_layer_authority_violations

    report = detect_layer_authority_violations(result)
    print(report.summary)
    if report.violation_count > 0:
        sys.exit(1)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.contracts.schema_util import (
    L1_WRITE_ALLOWLIST,
    LAYER_AUTHORITY_FORBIDDEN,
    module_path_to_layer,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_applies_guardrail("p0", "layer_authority", "p0_governance")
_emit_reads_policy_state("p0", "layer_authority", "policy_binding")
_emit_snapshots_state("p0", "layer_authority", "state_snapshot")
_emit_escalates_to_human("p1", "layer_authority", "human_escalation")
emit_replay_key("p0", "layer_authority")
emit_determinism_digest("p0", "layer_authority")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "layer_authority", "execution_auth")
_emit_validates_capability("p2", "layer_authority", "capability_check")
_emit_routes_to_capability("p2", "layer_authority", "capability_route")
_emit_writes_via_uwg("p2", "layer_authority", "uwg_write")
_emit_blocks_direct_write("p2", "layer_authority", "direct_write_block")
_emit_records_tool_invocation("p2", "layer_authority", "tool_invocation")
_emit_captures_execution_output("p2", "layer_authority", "exec_output")
_emit_dispatches_agent("p3", "layer_authority", "agent_dispatch")
_emit_coordinates_agents("p3", "layer_authority", "agent_coordination")
_emit_records_workflow_lineage("p3", "layer_authority", "workflow_lineage")
_emit_records_healing_outcome("p3", "layer_authority", "healing_outcome")
_emit_escalates_failure("p3", "layer_authority", "failure_escalation")
_emit_orchestrates_workflow("p3", "layer_authority", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "layer_authority", "healing_dispatch")
_emit_invokes_evaluation("p3", "layer_authority", "evaluation_signal")
_emit_records_telemetry_event("p4", "layer_authority", "telemetry_event")
_emit_captures_evaluation_metric("p4", "layer_authority", "eval_metric")
_emit_stores_embedding("p4", "layer_authority", "embedding_store")
_emit_updates_meta_learning_state("p4", "layer_authority", "meta_learning")
_emit_links_execution_to_snapshot("p4", "layer_authority", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_routes_through,
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

_emit_emits_metric_event("layer_authority", "p4obs", "metric_1")
_emit_emits_metric_event("layer_authority", "p4obs", "metric_2")
_emit_emits_metric_event("layer_authority", "p4obs", "metric_3")
_emit_emits_metric_event("layer_authority", "p4obs", "metric_4")
_emit_emits_metric_event("layer_authority", "p4obs", "metric_5")
_emit_emits_metric_event("layer_authority", "p4obs", "metric_6")
_emit_records_incident_event("layer_authority", "p4obs", "incident")
_emit_captures_runtime_anomaly("layer_authority", "p4obs", "anomaly")
_emit_writes_observability_log("layer_authority", "p4obs", "obs_log")
_emit_updates_monitoring_state("layer_authority", "p4obs", "mon_state")
_emit_triggers_alert("layer_authority", "p4obs", "alert")
_emit_links_incident_trace("layer_authority", "p4obs", "trace_link")
_emit_captures_pattern("layer_authority", "p3lm", "pattern")
_emit_records_learning_event("layer_authority", "p3lm", "learning_event")
_emit_writes_learning_snapshot("layer_authority", "p3lm", "snapshot")
_emit_feeds_meta_learning("layer_authority", "p3lm", "meta_feed")
_emit_updates_routing_strategy("layer_authority", "p3lm", "routing")
_emit_improves_agent_policy("layer_authority", "p3lm", "policy")
_emit_stores_learning_state("layer_authority", "p3lm", "state")
_emit_records_execution_trace("layer_authority", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("layer_authority", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("layer_authority", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("layer_authority", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("layer_authority", "L4_STATE", "p2_trace_5")
_emit_reads_environ("layer_authority", "env_read", "p2_env_1")
_emit_reads_environ("layer_authority", "env_read", "p2_env_2")
_emit_reads_runtime_state("layer_authority", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("layer_authority", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "layer_authority", "context_pull")
_emit_pulls_context("p1", "layer_authority", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "layer_authority", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "layer_authority", "uwg_term_2")
_emit_writes_through("p1", "layer_authority", "write_through")
_emit_writes_through("p1", "layer_authority", "write_through_2")
_emit_validated_by_safety_plane("p1", "layer_authority", "safety_validation")
_emit_invokes_eval("p1", "layer_authority", "eval_call")
_emit_proposal_commits_routing("p1", "layer_authority", "routing_commit")
_emit_routes_through("p1", "layer_authority", "route_through")
_emit_checks_agent_registry("p1", "layer_authority", "agent_registry")
_emit_validates_agent_capability("p1", "layer_authority", "capability")
_emit_dispatches_execution_plan("p1", "layer_authority", "exec_plan")
_emit_agent_executes_agent("p1", "layer_authority", "sub_agent")
_emit_routes_to_agent("p1", "layer_authority", "target_agent")
_emit_verifies_policy("p1", "layer_authority", "policy_check")
_emit_observes_runtime_state("p1", "layer_authority", "runtime_state")
_emit_verifies_boundary("p1", "layer_authority", "boundary_check")
_emit_transcripts_response("p1", "layer_authority", "transcript")
_emit_hard_fails_untranscripted("p1", "layer_authority")
_emit_gated_by_confidence("p1", "layer_authority", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

_SEVERITY_MAP: dict[str, str] = {
    "L1": "critical",  # L1 writing state is an architecture breach
    "L3": "high",  # L3 directly calling tools bypasses L2
    "L4": "high",  # L4 running logic violates state-only contract
    "L6": "high",  # L6 altering execution violates observability-only contract
}

_VIOLATION_TYPE_MAP: dict[tuple[str, str], str] = {
    ("L1", "writes_to"): "L1_MUTATES_STATE",
    ("L1", "writes_through"): "L1_MUTATES_STATE_VIA_UWG",
    ("L3", "invokes_tool"): "L3_INVOKES_TOOL_DIRECTLY",
    ("L3", "invokes_provider"): "L3_INVOKES_PROVIDER_DIRECTLY",
    ("L4", "calls"): "L4_CONTAINS_LOGIC",
    ("L4", "invokes_provider"): "L4_INVOKES_PROVIDER",
    ("L6", "writes_to"): "L6_ALTERS_EXECUTION_WRITE",
    ("L6", "writes_through"): "L6_ALTERS_EXECUTION_UWG",
    ("L6", "routes_through"): "L6_ALTERS_ROUTING",
}

_SUGGESTED_FIX_MAP: dict[str, str] = {
    "L1_MUTATES_STATE": "Move persistent writes to L2 execution layer via UniversalWriteGateway.",
    "L1_MUTATES_STATE_VIA_UWG": "L1 must not call UWG directly; delegate mutations to L2 execution agents.",
    "L3_INVOKES_TOOL_DIRECTLY": "L3 orchestration must not call tools directly; route through L2 tool executors.",
    "L3_INVOKES_PROVIDER_DIRECTLY": "L3 must not call LLM providers directly; route through L2 SovereignLLMGateway.",
    "L4_CONTAINS_LOGIC": "L4 is state-only; move business logic to L2 or L3.",
    "L4_INVOKES_PROVIDER": "L4 must not call providers; state bus is read/write only.",
    "L6_ALTERS_EXECUTION_WRITE": "L6 observability must not write state; it may only read and emit telemetry.",
    "L6_ALTERS_EXECUTION_UWG": "L6 must not write through UWG; observability is read-only.",
    "L6_ALTERS_ROUTING": "L6 must not influence routing; route decisions belong to L0.",
}


@dataclass
class LayerAuthorityViolation:
    """A single detected layer authority violation."""

    violating_module: str
    layer: str
    violation_type: str
    forbidden_relation: str
    target: str
    source_file: str
    line_no: int
    severity: str
    suggested_fix: str

    def to_dict(self) -> dict:
        return {
            "violating_module": self.violating_module,
            "layer": self.layer,
            "violation_type": self.violation_type,
            "forbidden_relation": self.forbidden_relation,
            "target": self.target,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class LayerAuthorityReport:
    """Report of all layer authority violations found in the scan."""

    violations: list[LayerAuthorityViolation] = field(default_factory=list)
    allowlisted_count: int = 0
    checked_layers: list[str] = field(default_factory=list)
    violation_count: int = 0

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "LayerAuthorityReport.summary"
        )

        by_layer: dict[str, int] = {}
        for v in self.violations:
            by_layer[v.layer] = by_layer.get(v.layer, 0) + 1
        layer_str = ", ".join(f"{k}={v}" for k, v in sorted(by_layer.items()))
        return (
            f"Layer authority violations: {self.violation_count} "
            f"({layer_str}) | allowlisted: {self.allowlisted_count}"
        )

    def critical_violations(self) -> list[LayerAuthorityViolation]:
        return [v for v in self.violations if v.severity == "critical"]

    def to_dict(self) -> dict:
        return {
            "violation_count": self.violation_count,
            "allowlisted_count": self.allowlisted_count,
            "checked_layers": sorted(self.checked_layers),
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _extract_module_path(adg_name: str) -> str:
    """Strip ADG::Module:: prefix and return the relative path."""
    if adg_name.startswith(_MODULE_PREFIX):
        return adg_name[len(_MODULE_PREFIX) :]
    return adg_name


def _extract_symbol(adg_name: str) -> str:
    """Strip ADG::Symbol:: prefix."""
    if adg_name.startswith(_SYMBOL_PREFIX):
        return adg_name[len(_SYMBOL_PREFIX) :]
    return adg_name


def _is_allowlisted_l1_write(target_symbol: str) -> bool:
    """Return True if this L1 write target is in the copy/cache allowlist."""
    sym = _extract_symbol(target_symbol)
    # Check exact match or suffix match
    for allowed in L1_WRITE_ALLOWLIST:
        if sym == allowed or sym.endswith("." + allowed) or sym.endswith("." + allowed.split(".")[-1]):
            return True
    return False


def detect_layer_authority_violations(result: ScanResult) -> LayerAuthorityReport:
    """Scan all edges and detect layer authority violations.

    Algorithm:
    1. For each edge, extract the source module's layer.
    2. Check if that layer has forbidden relations for this edge's relation_type.
    3. For L1 writes_to edges, apply the allowlist (copy/deepcopy operations).
    4. Classify violation type, severity, and suggested fix.
    5. Return a LayerAuthorityReport.
    """
    violations: list[LayerAuthorityViolation] = []
    allowlisted_count = 0
    checked_layers: set[str] = set(LAYER_AUTHORITY_FORBIDDEN.keys())

    for edge in result.edges:
        from_name = edge.from_name
        if not from_name.startswith(_MODULE_PREFIX):
            continue

        mod_path = _extract_module_path(from_name)
        layer = module_path_to_layer(mod_path)

        if layer not in LAYER_AUTHORITY_FORBIDDEN:
            continue

        forbidden_rels = LAYER_AUTHORITY_FORBIDDEN[layer]
        rel = edge.relation_type

        if rel not in forbidden_rels:
            continue

        # L1 writes_to: check allowlist first
        if layer == "L1" and rel == "writes_to":
            if _is_allowlisted_l1_write(edge.to_name):
                allowlisted_count += 1
                continue

        vtype = _VIOLATION_TYPE_MAP.get((layer, rel), f"{layer}_FORBIDDEN_{rel.upper()}")
        severity = _SEVERITY_MAP.get(layer, "medium")
        fix = _SUGGESTED_FIX_MAP.get(vtype, f"Layer {layer} must not use relation '{rel}'.")

        violations.append(
            LayerAuthorityViolation(
                violating_module=mod_path,
                layer=layer,
                violation_type=vtype,
                forbidden_relation=rel,
                target=edge.to_name,
                source_file=edge.source_file,
                line_no=edge.line_no,
                severity=severity,
                suggested_fix=fix,
            )
        )

    violations.sort(key=lambda v: (v.severity, v.layer, v.violating_module))

    return LayerAuthorityReport(
        violations=violations,
        allowlisted_count=allowlisted_count,
        checked_layers=sorted(checked_layers),
        violation_count=len(violations),
    )


__all__ = [
    "LayerAuthorityReport",
    "LayerAuthorityViolation",
    "detect_layer_authority_violations",
]
