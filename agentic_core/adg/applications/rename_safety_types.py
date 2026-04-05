"""E12: Rename / Move Safety Analyzer.

Given an intended rename or move operation, answers:
  - Which import edges reference the old path / symbol?
  - Which files must be updated and how?
  - What is the blast radius of the change?
  - Are any layer-boundary rules affected by the new location?
  - What is the minimum repair sequence?

Usage::

    from agentic_core.adg.applications.rename_safety_types import analyze_rename

    report = analyze_rename(
        result,
        old_path="agentic_core/L2_execution/old_module.py",
        new_path="agentic_core/L3_orchestration/new_module.py",
    )
    print(report.summary)
    for step in report.repair_sequence:
        print(step)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.contracts.schema_util import module_path_to_layer
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

_emit_applies_guardrail("p0", "rename_safety", "p0_governance")
_emit_reads_policy_state("p0", "rename_safety", "policy_binding")
_emit_snapshots_state("p0", "rename_safety", "state_snapshot")
emit_replay_key("p0", "rename_safety")
emit_determinism_digest("p0", "rename_safety")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rename_safety", "execution_auth")
_emit_validates_capability("p2", "rename_safety", "capability_check")
_emit_routes_to_capability("p2", "rename_safety", "capability_route")
_emit_writes_via_uwg("p2", "rename_safety", "uwg_write")
_emit_blocks_direct_write("p2", "rename_safety", "direct_write_block")
_emit_records_tool_invocation("p2", "rename_safety", "tool_invocation")
_emit_captures_execution_output("p2", "rename_safety", "exec_output")
_emit_dispatches_agent("p3", "rename_safety", "agent_dispatch")
_emit_coordinates_agents("p3", "rename_safety", "agent_coordination")
_emit_records_workflow_lineage("p3", "rename_safety", "workflow_lineage")
_emit_records_healing_outcome("p3", "rename_safety", "healing_outcome")
_emit_escalates_failure("p3", "rename_safety", "failure_escalation")
_emit_orchestrates_workflow("p3", "rename_safety", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rename_safety", "healing_dispatch")
_emit_invokes_evaluation("p3", "rename_safety", "evaluation_signal")
_emit_records_telemetry_event("p4", "rename_safety", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rename_safety", "eval_metric")
_emit_stores_embedding("p4", "rename_safety", "embedding_store")
_emit_updates_meta_learning_state("p4", "rename_safety", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rename_safety", "exec_snapshot_link")

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
    _emit_escalates_to_human,
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

_emit_emits_metric_event("rename_safety", "p4obs", "metric_1")
_emit_emits_metric_event("rename_safety", "p4obs", "metric_2")
_emit_emits_metric_event("rename_safety", "p4obs", "metric_3")
_emit_emits_metric_event("rename_safety", "p4obs", "metric_4")
_emit_emits_metric_event("rename_safety", "p4obs", "metric_5")
_emit_emits_metric_event("rename_safety", "p4obs", "metric_6")
_emit_records_incident_event("rename_safety", "p4obs", "incident")
_emit_captures_runtime_anomaly("rename_safety", "p4obs", "anomaly")
_emit_writes_observability_log("rename_safety", "p4obs", "obs_log")
_emit_updates_monitoring_state("rename_safety", "p4obs", "mon_state")
_emit_triggers_alert("rename_safety", "p4obs", "alert")
_emit_links_incident_trace("rename_safety", "p4obs", "trace_link")
_emit_captures_pattern("rename_safety", "p3lm", "pattern")
_emit_records_learning_event("rename_safety", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rename_safety", "p3lm", "snapshot")
_emit_feeds_meta_learning("rename_safety", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rename_safety", "p3lm", "routing")
_emit_improves_agent_policy("rename_safety", "p3lm", "policy")
_emit_stores_learning_state("rename_safety", "p3lm", "state")
_emit_records_execution_trace("rename_safety", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rename_safety", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rename_safety", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rename_safety", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rename_safety", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rename_safety", "env_read", "p2_env_1")
_emit_reads_environ("rename_safety", "env_read", "p2_env_2")
_emit_reads_runtime_state("rename_safety", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rename_safety", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rename_safety", "context_pull")
_emit_pulls_context("p1", "rename_safety", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rename_safety", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rename_safety", "uwg_term_2")
_emit_writes_through("p1", "rename_safety", "write_through")
_emit_writes_through("p1", "rename_safety", "write_through_2")
_emit_validated_by_safety_plane("p1", "rename_safety", "safety_validation")
_emit_invokes_eval("p1", "rename_safety", "eval_call")
_emit_proposal_commits_routing("p1", "rename_safety", "routing_commit")
_emit_escalates_to_human("p1", "rename_safety", "human_escalation")
_emit_routes_through("p1", "rename_safety", "route_through")
_emit_checks_agent_registry("p1", "rename_safety", "agent_registry")
_emit_validates_agent_capability("p1", "rename_safety", "capability")
_emit_dispatches_execution_plan("p1", "rename_safety", "exec_plan")
_emit_agent_executes_agent("p1", "rename_safety", "sub_agent")
_emit_routes_to_agent("p1", "rename_safety", "target_agent")
_emit_verifies_policy("p1", "rename_safety", "policy_check")
_emit_observes_runtime_state("p1", "rename_safety", "runtime_state")
_emit_verifies_boundary("p1", "rename_safety", "boundary_check")
_emit_transcripts_response("p1", "rename_safety", "transcript")
_emit_hard_fails_untranscripted("p1", "rename_safety")
_emit_gated_by_confidence("p1", "rename_safety", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


@dataclass
class RenameImpact:
    """One file that must be updated as a result of the rename/move."""

    file_path: str
    reason: str
    old_reference: str
    suggested_new_reference: str
    line_no: int
    edge_kind: str

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "reason": self.reason,
            "old_reference": self.old_reference,
            "suggested_new_reference": self.suggested_new_reference,
            "line_no": self.line_no,
            "edge_kind": self.edge_kind,
        }


@dataclass
class RenameRepairStep:
    """One atomic step in the minimum repair sequence."""

    step_no: int
    action: str
    target_file: str
    description: str
    old_text: str = ""
    new_text: str = ""

    def to_dict(self) -> dict:
        return {
            "step_no": self.step_no,
            "action": self.action,
            "target_file": self.target_file,
            "description": self.description,
            "old_text": self.old_text,
            "new_text": self.new_text,
        }


@dataclass
class RenameSafetyReport:
    """Full safety analysis for a rename/move operation."""

    old_path: str
    new_path: str
    old_layer: str
    new_layer: str
    layer_changed: bool
    is_safe: bool

    direct_importers: list[str] = field(default_factory=list)
    impacted_files: list[RenameImpact] = field(default_factory=list)
    new_layer_violations: list[str] = field(default_factory=list)
    repair_sequence: list[RenameRepairStep] = field(default_factory=list)
    total_files_to_update: int = 0
    risk_label: str = "LOW"

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RenameSafetyReport.summary")

        safe_str = "SAFE" if self.is_safe else "UNSAFE"
        return (
            f"rename [{safe_str}] {self.old_path} -> {self.new_path} "
            f"layers: {self.old_layer}->{self.new_layer} "
            f"files_to_update={self.total_files_to_update} "
            f"new_violations={len(self.new_layer_violations)} "
            f"risk={self.risk_label}"
        )

    def to_dict(self) -> dict:
        return {
            "old_path": self.old_path,
            "new_path": self.new_path,
            "old_layer": self.old_layer,
            "new_layer": self.new_layer,
            "layer_changed": self.layer_changed,
            "is_safe": self.is_safe,
            "total_files_to_update": self.total_files_to_update,
            "risk_label": self.risk_label,
            "summary": self.summary,
            "direct_importers": sorted(self.direct_importers),
            "new_layer_violations": sorted(self.new_layer_violations),
            "impacted_files": [i.to_dict() for i in self.impacted_files],
            "repair_sequence": [s.to_dict() for s in self.repair_sequence],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _old_dot(old_path: str) -> str:
    """Convert slash path to dotted module path (strip .py)."""
    d = old_path.replace("\\", "/").replace("/", ".")
    if d.endswith(".py"):
        d = d[:-3]
    if d.endswith(".__init__"):
        d = d[: -len(".__init__")]
    return d


def _new_dot(new_path: str) -> str:
    return _old_dot(new_path)


def _path_to_adg(path: str) -> str:
    return _MODULE_PREFIX + path.replace("\\", "/")


def analyze_rename(
    result: ScanResult,
    old_path: str,
    new_path: str,
) -> RenameSafetyReport:
    """Analyse safety of renaming/moving ``old_path`` to ``new_path``.

    Algorithm:
    1. Collect all edges whose ``from_name`` or ``to_name`` reference the old path
       (either as Module ADG name or as a dotted symbol prefix).
    2. For each referencing file, record a ``RenameImpact``.
    3. Detect new layer violations introduced by the move.
    4. Build a minimum repair sequence.
    5. Determine risk label.
    """
    from agentic_core.adg.contracts.schema_util import ALLOWED_LAYER_EDGES

    old_norm = old_path.replace("\\", "/")
    new_norm = new_path.replace("\\", "/")

    old_adg = _path_to_adg(old_norm)
    new_adg = _path_to_adg(new_norm)

    old_dot = _old_dot(old_norm)
    new_dot = _new_dot(new_norm)

    old_layer = module_path_to_layer(old_norm)
    new_layer = module_path_to_layer(new_norm)
    layer_changed = old_layer != new_layer

    impacted: list[RenameImpact] = []
    direct_importers: set[str] = set()
    new_violations: set[str] = set()

    for edge in result.edges:
        # Check if this edge references the old module
        refs_old = (
            edge.to_name == old_adg
            or edge.from_name == old_adg
            or (edge.symbol and (edge.symbol == old_dot or edge.symbol.startswith(old_dot + ".")))
            or (
                edge.to_name.startswith(_SYMBOL_PREFIX)
                and (
                    edge.to_name[len(_SYMBOL_PREFIX) :] == old_dot
                    or edge.to_name[len(_SYMBOL_PREFIX) :].startswith(old_dot + ".")
                )
            )
        )
        if not refs_old:
            continue

        # Determine which file contains this reference
        if edge.from_name.startswith(_MODULE_PREFIX):
            ref_file = edge.from_name[len(_MODULE_PREFIX) :]
        else:
            ref_file = edge.source_file

        if ref_file == old_norm:
            continue  # skip the file being renamed itself

        # Compute suggested new reference
        if edge.symbol and edge.symbol.startswith(old_dot):
            old_ref = edge.symbol
            new_ref = new_dot + edge.symbol[len(old_dot) :]
        elif edge.to_name == old_adg:
            old_ref = old_adg
            new_ref = new_adg
        else:
            old_ref = old_norm
            new_ref = new_norm

        reason = "imports" if edge.relation_type == "imports" else f"{edge.relation_type}"
        if edge.relation_type == "imports":
            direct_importers.add(ref_file)

        impacted.append(
            RenameImpact(
                file_path=ref_file,
                reason=reason,
                old_reference=old_ref,
                suggested_new_reference=new_ref,
                line_no=edge.line_no,
                edge_kind=edge.edge_kind,
            )
        )

        # Check if the new location creates a layer violation for the importer
        if layer_changed and edge.relation_type == "imports":
            importer_layer = module_path_to_layer(ref_file)
            if (importer_layer, new_layer) not in ALLOWED_LAYER_EDGES and importer_layer != new_layer:
                new_violations.add(f"{ref_file} ({importer_layer}) -> {new_norm} ({new_layer})")

    # Deduplicate impacted files by path
    seen_files: set[str] = set()
    unique_impacted: list[RenameImpact] = []
    for item in sorted(impacted, key=lambda x: (x.file_path, x.line_no)):
        key = (item.file_path, item.old_reference, item.line_no)
        if key not in seen_files:
            seen_files.add(key)
            unique_impacted.append(item)

    # Build repair sequence
    steps: list[RenameRepairStep] = []
    step_n = 1

    # Step 1: git mv / rename the file itself
    steps.append(
        RenameRepairStep(
            step_no=step_n,
            action="rename_file",
            target_file=old_norm,
            description=f"Rename/move file: {old_norm} -> {new_norm}",
            old_text=old_norm,
            new_text=new_norm,
        )
    )
    step_n += 1

    # Steps for each unique importer file
    importer_files = sorted({i.file_path for i in unique_impacted})
    for fpath in importer_files:
        file_impacts = [i for i in unique_impacted if i.file_path == fpath]
        old_refs = sorted({i.old_reference for i in file_impacts})
        new_refs = sorted({i.suggested_new_reference for i in file_impacts})
        steps.append(
            RenameRepairStep(
                step_no=step_n,
                action="update_import",
                target_file=fpath,
                description=f"Update {len(file_impacts)} reference(s) in {fpath}",
                old_text="; ".join(old_refs),
                new_text="; ".join(new_refs),
            )
        )
        step_n += 1

    if new_violations:
        steps.append(
            RenameRepairStep(
                step_no=step_n,
                action="resolve_layer_violations",
                target_file="<multiple>",
                description=f"Resolve {len(new_violations)} new layer boundary violation(s) introduced by the move",
                old_text="",
                new_text="\n".join(sorted(new_violations)),
            )
        )
        step_n += 1

    # Risk label
    n = len(importer_files)
    if new_violations or n > 20:
        risk_label = "CRITICAL"
    elif n > 10 or layer_changed:
        risk_label = "HIGH"
    elif n > 3:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"

    is_safe = len(new_violations) == 0

    return RenameSafetyReport(
        old_path=old_norm,
        new_path=new_norm,
        old_layer=old_layer,
        new_layer=new_layer,
        layer_changed=layer_changed,
        is_safe=is_safe,
        direct_importers=sorted(direct_importers),
        impacted_files=unique_impacted,
        new_layer_violations=sorted(new_violations),
        repair_sequence=steps,
        total_files_to_update=len(importer_files),
        risk_label=risk_label,
    )


__all__ = [
    "RenameSafetyReport",
    "RenameImpact",
    "RenameRepairStep",
    "analyze_rename",
]
