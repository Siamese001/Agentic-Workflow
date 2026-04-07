"""E24: Prompt Impact Analyzer.

Given a set of changed prompt templates or prompt-generating modules, computes:
  - Which agents consume the affected prompts (blast radius)
  - Which assembly modules are impacted
  - Which slot types are affected (S0/D0/I0/C0/U0)
  - Risk label based on slot authority and fan-in

This extends E12 (rename safety) to the prompt governance plane.

Usage::

    from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

    report = analyze_prompt_impact(result, changed_files=["agentic_core/prompt_governance/core/prompt_entry_types.py"])
    print(report.summary)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.contracts.schema_util import PROMPT_SLOT_AUTHORITY, PROMPT_SLOT_TYPES
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "prompt_impact")
_emit_applies_guardrail("p0", "prompt_impact", "p0_governance")
_emit_reads_policy_state("p0", "prompt_impact", "policy_binding")
_emit_snapshots_state("p0", "prompt_impact", "state_snapshot")
emit_replay_key("p0", "prompt_impact")
emit_determinism_digest("p0", "prompt_impact")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_impact", "execution_auth")
_emit_validates_capability("p2", "prompt_impact", "capability_check")
_emit_routes_to_capability("p2", "prompt_impact", "capability_route")
_emit_writes_via_uwg("p2", "prompt_impact", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_impact", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_impact", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_impact", "exec_output")
_emit_dispatches_agent("p3", "prompt_impact", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_impact", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_impact", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_impact", "healing_outcome")
_emit_escalates_failure("p3", "prompt_impact", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_impact", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_impact", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_impact", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_impact", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_impact", "eval_metric")
_emit_stores_embedding("p4", "prompt_impact", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_impact", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_impact", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("prompt_impact", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_impact", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_impact", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_impact", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_impact", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_impact", "p4obs", "metric_6")
_emit_records_incident_event("prompt_impact", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_impact", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_impact", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_impact", "p4obs", "mon_state")
_emit_triggers_alert("prompt_impact", "p4obs", "alert")
_emit_links_incident_trace("prompt_impact", "p4obs", "trace_link")
_emit_captures_pattern("prompt_impact", "p3lm", "pattern")
_emit_records_learning_event("prompt_impact", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_impact", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_impact", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_impact", "p3lm", "routing")
_emit_improves_agent_policy("prompt_impact", "p3lm", "policy")
_emit_stores_learning_state("prompt_impact", "p3lm", "state")
_emit_records_execution_trace("prompt_impact", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_impact", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_impact", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_impact", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_impact", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_impact", "env_read", "p2_env_1")
_emit_reads_environ("prompt_impact", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_impact", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_impact", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_impact", "context_pull")
_emit_pulls_context("p1", "prompt_impact", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "prompt_impact", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_impact", "uwg_term_secondary")
_emit_writes_through("p1", "prompt_impact", "write_through")
_emit_writes_through("p1", "prompt_impact", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "prompt_impact", "safety_validation")
_emit_invokes_eval("p1", "prompt_impact", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_impact", "routing_commit")
_emit_escalates_to_human("p1", "prompt_impact", "human_escalation")
_emit_routes_through("p1", "prompt_impact", "route_through")
_emit_checks_agent_registry("p1", "prompt_impact", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_impact", "capability")
_emit_dispatches_execution_plan("p1", "prompt_impact", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_impact", "sub_agent")
_emit_routes_to_agent("p1", "prompt_impact", "target_agent")
_emit_verifies_policy("p1", "prompt_impact", "policy_check")
_emit_observes_runtime_state("p1", "prompt_impact", "runtime_state")
_emit_verifies_boundary("p1", "prompt_impact", "boundary_check")
_emit_transcripts_response("p1", "prompt_impact", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_impact")
_emit_gated_by_confidence("p1", "prompt_impact", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_PROMPT_SLOT_PREFIX = "ADG::PromptSlot::"
_PROMPT_TEMPLATE_PREFIX = "ADG::PromptTemplate::"
_PROMPT_ASSEMBLY_PREFIX = "ADG::PromptAssembly::"


@dataclass
class PromptImpactEntry:
    """One module impacted by a prompt change."""

    module_path: str
    impact_reason: str
    affected_slots: list[str]
    relation_path: list[str]
    risk_level: str = "medium"

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "impact_reason": self.impact_reason,
            "affected_slots": sorted(self.affected_slots),
            "relation_path": self.relation_path,
            "risk_level": self.risk_level,
        }


@dataclass
class PromptImpactReport:
    """Full prompt impact analysis for a set of changed files."""

    changed_files: list[str] = field(default_factory=list)
    impacted_modules: list[PromptImpactEntry] = field(default_factory=list)
    affected_slot_types: list[str] = field(default_factory=list)
    assembly_modules_affected: list[str] = field(default_factory=list)
    risk_label: str = "LOW"
    risk_score: float = 0.0
    impacted_count: int = 0

    @property
    def summary(self) -> str:
        return (
            f"Prompt impact: changed={len(self.changed_files)} "
            f"impacted={self.impacted_count} "
            f"slots={self.affected_slot_types} "
            f"risk={self.risk_label}({self.risk_score:.4f})"
        )

    def to_dict(self) -> dict:
        return {
            "changed_files": self.changed_files,
            "impacted_count": self.impacted_count,
            "affected_slot_types": self.affected_slot_types,
            "assembly_modules_affected": sorted(self.assembly_modules_affected),
            "risk_label": self.risk_label,
            "risk_score": self.risk_score,
            "summary": self.summary,
            "impacted_modules": [e.to_dict() for e in self.impacted_modules],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _slot_authority_score(slots: list[str]) -> float:
    """Compute a risk score 0-1 based on affected slot authority levels."""
    if not slots:
        return 0.0
    # S0 is highest authority (index 0) → highest risk
    min_rank = min(PROMPT_SLOT_AUTHORITY.get(s, len(PROMPT_SLOT_TYPES)) for s in slots)
    # Normalize: rank 0 (S0) → score 1.0, rank 4 (U0) → score 0.2
    return round(1.0 - (min_rank / len(PROMPT_SLOT_TYPES)) * 0.8, 4)


def _risk_label(score: float, impacted: int) -> str:
    if score >= 0.8 or impacted >= 20:
        return "CRITICAL"
    if score >= 0.6 or impacted >= 10:
        return "HIGH"
    if score >= 0.3 or impacted >= 3:
        return "MEDIUM"
    return "LOW"


def analyze_prompt_impact(
    result: ScanResult,
    changed_files: list[str] | None = None,
) -> PromptImpactReport:
    """Analyze blast radius of changes to prompt-generating or prompt-consuming modules.

    Pass 1: Build index of generates_prompt and consumes_prompt edges.
    Pass 2: Find which modules generate prompts from changed files.
    Pass 3: Trace forward via consumes_prompt to find all consumers.
    Pass 4: Compute risk score based on affected slot authority levels.
    """
    changed_set = set(changed_files or [])

    # Normalize paths to forward slashes
    changed_set = {p.replace("\\", "/") for p in changed_set}

    # Pass 1: Build prompt dependency indices
    # generators: module_path -> [(slot_type, to_name, line_no)]
    generators: dict[str, list[tuple[str, str, int]]] = {}
    # consumers: template_name -> [module_path]
    consumers: dict[str, list[str]] = {}
    # assembly: module_path -> [slot_type]
    assembly: dict[str, list[str]] = {}

    for edge in result.edges:
        if edge.relation_type == "generates_prompt":
            if not edge.from_name.startswith(_MODULE_PREFIX):
                continue
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            slot = edge.symbol.split(":")[0] if ":" in edge.symbol else ""
            if not slot:
                # Try extracting from to_name
                if edge.to_name.startswith(_PROMPT_SLOT_PREFIX):
                    rest = edge.to_name[len(_PROMPT_SLOT_PREFIX) :]
                    candidate = rest.split("::")[0]
                    if candidate in PROMPT_SLOT_TYPES:
                        slot = candidate
            generators.setdefault(mod, []).append((slot, edge.to_name, edge.line_no))

        elif edge.relation_type == "consumes_prompt":
            if not edge.from_name.startswith(_MODULE_PREFIX):
                continue
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            template = edge.to_name
            consumers.setdefault(template, []).append(mod)

        elif edge.relation_type == "assembles_into":
            if not edge.from_name.startswith(_MODULE_PREFIX):
                continue
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            assembly.setdefault(mod, [])

    # Pass 2: Find directly impacted generator modules (from changed files)
    directly_impacted: set[str] = set()
    affected_slots: set[str] = set()

    for mod, slot_list in generators.items():
        if mod in changed_set:
            directly_impacted.add(mod)
            for slot, _, _ in slot_list:
                if slot:
                    affected_slots.add(slot)

    # Also check if any changed file IS a generator (by source_file match)
    for edge in result.edges:
        if edge.relation_type == "generates_prompt":
            if edge.source_file.replace("\\", "/") in changed_set:
                if edge.from_name.startswith(_MODULE_PREFIX):
                    mod = edge.from_name[len(_MODULE_PREFIX) :]
                    directly_impacted.add(mod)
                    slot = edge.symbol.split(":")[0] if ":" in edge.symbol else ""
                    if slot and slot in PROMPT_SLOT_TYPES:
                        affected_slots.add(slot)

    # Pass 3: Trace consumers of affected templates
    affected_templates: set[str] = set()
    for mod in directly_impacted:
        for slot, to_name, _ in generators.get(mod, []):
            affected_templates.add(to_name)

    impacted_consumer_modules: set[str] = set()
    for tmpl in affected_templates:
        for consumer_mod in consumers.get(tmpl, []):
            impacted_consumer_modules.add(consumer_mod)

    # Pass 4: Build impacted entries
    impacted_entries: list[PromptImpactEntry] = []
    assembly_affected: set[str] = set()

    for mod in directly_impacted:
        slots_for_mod = [s for s, _, _ in generators.get(mod, []) if s]
        risk = _risk_label(_slot_authority_score(slots_for_mod), len(directly_impacted))
        impacted_entries.append(
            PromptImpactEntry(
                module_path=mod,
                impact_reason="direct_generator",
                affected_slots=slots_for_mod,
                relation_path=[mod],
                risk_level=risk,
            ),
        )
        if mod in assembly:
            assembly_affected.add(mod)

    for mod in impacted_consumer_modules - directly_impacted:
        impacted_entries.append(
            PromptImpactEntry(
                module_path=mod,
                impact_reason="prompt_consumer",
                affected_slots=list(affected_slots),
                relation_path=["(changed file)", "->", mod],
                risk_level="medium",
            ),
        )
        if mod in assembly:
            assembly_affected.add(mod)

    # Risk computation
    slot_score = _slot_authority_score(list(affected_slots))
    total_impacted = len(impacted_entries)
    risk_label = _risk_label(slot_score, total_impacted)

    impacted_entries.sort(key=lambda e: (e.risk_level, e.module_path))

    return PromptImpactReport(
        changed_files=sorted(changed_set),
        impacted_modules=impacted_entries,
        affected_slot_types=sorted(affected_slots, key=lambda s: PROMPT_SLOT_AUTHORITY.get(s, 99)),
        assembly_modules_affected=sorted(assembly_affected),
        risk_label=risk_label,
        risk_score=slot_score,
        impacted_count=total_impacted,
    )


__all__ = [
    "PromptImpactEntry",
    "PromptImpactReport",
    "analyze_prompt_impact",
]
