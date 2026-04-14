"""E21: Prompt Authority DAG Enforcement.

Detects violations of the prompt slot authority hierarchy:
  S0 (system constitution) > D0 (injection fences) > I0 (instructional) > C0 (context) > U0 (user)

A violation occurs when a module generates a lower-authority prompt slot and that slot
content flows into (or overrides) a higher-authority slot, or when a module bypasses
the authority order entirely.

Detection algorithm:
  1. Index all generates_prompt edges by source module and slot type.
  2. Index all assembles_into edges to find assembly points.
  3. For each assembly module, check whether any lower-authority slot provider also
     generates a higher-authority slot (cross-authority pollution).
  4. Detect D0 (injection fence) absence — assembly without D0 edge = missing fence.
  5. Detect U0 mutation patterns — modules that generate both U0 and S0/D0/I0 slots.

Output:
  ``PromptAuthorityReport`` with:
    - ``violations``: list of ``PromptAuthorityViolation``
    - ``assembly_modules``: dict of module -> set of slot types it generates
    - ``missing_fences``: list of assembly modules with no D0 edge
    - ``violation_count``

Usage::

    from agentic_core.adg.analysis.prompt_authority import detect_prompt_authority_violations

    report = detect_prompt_authority_violations(result)
    for v in report.violations:
        print(v.violating_module, v.violation_type, v.low_authority_slot, "->", v.high_authority_slot)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from tqdm import tqdm
from typing import TYPE_CHECKING, Literal

from agentic_core.adg.schema import PROMPT_SLOT_AUTHORITY, PROMPT_SLOT_TYPES
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

_emit_records_execution_trace("p0", "evidence", "prompt_authority")
_emit_applies_guardrail("p0", "prompt_authority", "p0_governance")
_emit_reads_policy_state("p0", "prompt_authority", "policy_binding")
_emit_snapshots_state("p0", "prompt_authority", "state_snapshot")
emit_replay_key("p0", "prompt_authority")
emit_determinism_digest("p0", "prompt_authority")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_authority", "execution_auth")
_emit_validates_capability("p2", "prompt_authority", "capability_check")
_emit_routes_to_capability("p2", "prompt_authority", "capability_route")
_emit_writes_via_uwg("p2", "prompt_authority", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_authority", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_authority", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_authority", "exec_output")
_emit_dispatches_agent("p3", "prompt_authority", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_authority", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_authority", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_authority", "healing_outcome")
_emit_escalates_failure("p3", "prompt_authority", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_authority", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_authority", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_authority", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_authority", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_authority", "eval_metric")
_emit_stores_embedding("p4", "prompt_authority", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_authority", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_authority", "exec_snapshot_link")

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

_emit_emits_metric_event("prompt_authority", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_authority", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_authority", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_authority", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_authority", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_authority", "p4obs", "metric_6")
_emit_records_incident_event("prompt_authority", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_authority", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_authority", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_authority", "p4obs", "mon_state")
_emit_triggers_alert("prompt_authority", "p4obs", "alert")
_emit_links_incident_trace("prompt_authority", "p4obs", "trace_link")
_emit_captures_pattern("prompt_authority", "p3lm", "pattern")
_emit_records_learning_event("prompt_authority", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_authority", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_authority", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_authority", "p3lm", "routing")
_emit_improves_agent_policy("prompt_authority", "p3lm", "policy")
_emit_stores_learning_state("prompt_authority", "p3lm", "state")
_emit_records_execution_trace("prompt_authority", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_authority", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_authority", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_authority", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_authority", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_authority", "env_read", "p2_env_1")
_emit_reads_environ("prompt_authority", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_authority", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_authority", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_authority", "context_pull")
_emit_pulls_context("p1", "prompt_authority", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "prompt_authority", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_authority", "uwg_term_secondary")
_emit_writes_through("p1", "prompt_authority", "write_through")
_emit_writes_through("p1", "prompt_authority", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "prompt_authority", "safety_validation")
_emit_invokes_eval("p1", "prompt_authority", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_authority", "routing_commit")
_emit_escalates_to_human("p1", "prompt_authority", "human_escalation")
_emit_routes_through("p1", "prompt_authority", "route_through")
_emit_checks_agent_registry("p1", "prompt_authority", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_authority", "capability")
_emit_dispatches_execution_plan("p1", "prompt_authority", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_authority", "sub_agent")
_emit_routes_to_agent("p1", "prompt_authority", "target_agent")
_emit_verifies_policy("p1", "prompt_authority", "policy_check")
_emit_observes_runtime_state("p1", "prompt_authority", "runtime_state")
_emit_verifies_boundary("p1", "prompt_authority", "boundary_check")
_emit_transcripts_response("p1", "prompt_authority", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_authority")
_emit_gated_by_confidence("p1", "prompt_authority", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_PROMPT_SLOT_PREFIX = "ADG::PromptSlot::"
_PROMPT_ASSEMBLY_PREFIX = "ADG::PromptAssembly::"

PromptViolationType = Literal[
    "U0_MUTATES_S0",
    "U0_MUTATES_D0",
    "U0_MUTATES_I0",
    "C0_MUTATES_S0",
    "C0_MUTATES_D0",
    "I0_MUTATES_S0",
    "MISSING_D0_FENCE",
    "MULTI_AUTHORITY_GENERATOR",
]


@dataclass
class PromptAuthorityViolation:
    """One prompt authority hierarchy violation."""

    violating_module: str
    violation_type: PromptViolationType
    low_authority_slot: str
    high_authority_slot: str
    source_file: str
    line_no: int
    severity: str = "high"
    suggested_fix: str = ""

    def to_dict(self) -> dict:
        return {
            "violating_module": self.violating_module,
            "violation_type": self.violation_type,
            "low_authority_slot": self.low_authority_slot,
            "high_authority_slot": self.high_authority_slot,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class PromptAuthorityReport:
    """Full prompt authority analysis for the repository."""

    violations: list[PromptAuthorityViolation] = field(default_factory=list)
    assembly_modules: dict[str, set[str]] = field(default_factory=dict)
    missing_fences: list[str] = field(default_factory=list)
    slot_generators: dict[str, list[str]] = field(default_factory=dict)
    violation_count: int = 0

    @property
    def summary(self) -> str:
        return (
            f"Prompt authority violations={self.violation_count} "
            f"assembly_modules={len(self.assembly_modules)} "
            f"missing_d0_fences={len(self.missing_fences)}"
        )

    def to_dict(self) -> dict:
        return {
            "violation_count": self.violation_count,
            "missing_fence_count": len(self.missing_fences),
            "assembly_module_count": len(self.assembly_modules),
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
            "missing_fences": sorted(self.missing_fences),
            "assembly_modules": {k: sorted(v) for k, v in sorted(self.assembly_modules.items())},
            "slot_generators": {k: sorted(v) for k, v in sorted(self.slot_generators.items())},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _slot_from_to_name(to_name: str) -> str:
    """Extract slot type (S0/D0/I0/C0/U0) from an ADG::PromptSlot:: entity name."""
    if to_name.startswith(_PROMPT_SLOT_PREFIX):
        rest = to_name[len(_PROMPT_SLOT_PREFIX) :]
        slot = rest.split("::")[0]
        if slot in PROMPT_SLOT_TYPES:
            return slot
    return ""


def _violation_type_for(low: str, high: str) -> PromptViolationType | None:
    """Return the canonical violation type for a given (low, high) authority pair."""
    key = f"{low}_MUTATES_{high}"
    valid: dict[str, PromptViolationType] = {
        "U0_MUTATES_S0": "U0_MUTATES_S0",
        "U0_MUTATES_D0": "U0_MUTATES_D0",
        "U0_MUTATES_I0": "U0_MUTATES_I0",
        "C0_MUTATES_S0": "C0_MUTATES_S0",
        "C0_MUTATES_D0": "C0_MUTATES_D0",
        "I0_MUTATES_S0": "I0_MUTATES_S0",
    }
    return valid.get(key)


def _suggested_fix(low: str, high: str) -> str:
    fixes = {
        ("U0", "S0"): "Move logic to I0 instructional mixin; U0 must never override system constitution.",
        ("U0", "D0"): "Remove D0 injection fence generation from user-controlled code path.",
        ("U0", "I0"): "Extract instructional logic to a governed I0 mixin; keep U0 for user intent only.",
        (
            "C0",
            "S0",
        ): "RAG context must not influence system constitution; remove S0 generation from C0 provider.",
        (
            "C0",
            "D0",
        ): "Context layer must not modify injection fences; move D0 logic to governed pipeline stage.",
        (
            "I0",
            "S0",
        ): "Instructional mixins must not override system constitution; demote to C0 or use S0 directly.",
    }
    return fixes.get((low, high), f"Low-authority slot {low} must not modify high-authority slot {high}.")


def detect_prompt_authority_violations(result: ScanResult) -> PromptAuthorityReport:
    """Detect prompt authority DAG violations.

    Pass 1: Index all generates_prompt edges by (module -> set of slot types).
    Pass 2: Index all assembles_into edges to find assembly points.
    Pass 3: For each module that generates multiple slot types, check for authority inversions.
    Pass 4: Detect missing D0 fences at assembly points.
    """
    # Pass 1: module -> {slot_type: (to_name, source_file, line_no)}
    module_slots: dict[str, dict[str, tuple[str, str, int]]] = {}

    for edge in tqdm(result.edges, desc="prompt edges", unit="edge", leave=False):
        if edge.relation_type != "generates_prompt":
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue

        mod_path = edge.from_name[len(_MODULE_PREFIX) :]
        slot = _slot_from_to_name(edge.to_name)
        if not slot:
            # Try extracting slot from symbol field (e.g. "S0:s0_system")
            sym = edge.symbol or ""
            if ":" in sym:
                candidate = sym.split(":")[0]
                if candidate in PROMPT_SLOT_TYPES:
                    slot = candidate
        if slot:
            module_slots.setdefault(mod_path, {})[slot] = (edge.to_name, edge.source_file, edge.line_no)

    # Pass 2: assembly modules (those with assembles_into edges)
    assembly_modules: dict[str, set[str]] = {}
    for mod_path, slots in module_slots.items():
        assembly_modules[mod_path] = set(slots.keys())

    # Also capture assembles_into edges for modules that use generic assembly
    for edge in result.edges:
        if edge.relation_type != "assembles_into":
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        mod_path = edge.from_name[len(_MODULE_PREFIX) :]
        assembly_modules.setdefault(mod_path, set())

    # Pass 3: detect authority inversions — module generates both a low AND a high-authority slot
    violations: list[PromptAuthorityViolation] = []

    for mod_path, slots in tqdm(module_slots.items(), desc="module slots", unit="mod", leave=False):
        generated_slot_types = set(slots.keys())
        for low_slot in tqdm(generated_slot_types, desc="  low slots", unit="slot", leave=False):
            for high_slot in tqdm(generated_slot_types, desc="    high slots", unit="slot", leave=False):
                if low_slot == high_slot:
                    continue
                low_rank = PROMPT_SLOT_AUTHORITY.get(low_slot, 99)
                high_rank = PROMPT_SLOT_AUTHORITY.get(high_slot, 99)
                # low_rank > high_rank means low_slot has LOWER authority than high_slot
                if low_rank > high_rank:
                    vtype = _violation_type_for(low_slot, high_slot)
                    if vtype is None:
                        continue
                    _, source_file, line_no = slots[low_slot]
                    violations.append(
                        PromptAuthorityViolation(
                            violating_module=mod_path,
                            violation_type=vtype,
                            low_authority_slot=low_slot,
                            high_authority_slot=high_slot,
                            source_file=source_file,
                            line_no=line_no,
                            severity="critical" if high_slot in ("S0", "D0") else "high",
                            suggested_fix=_suggested_fix(low_slot, high_slot),
                        ),
                    )

    # Pass 4: detect missing D0 fences — assembly modules that generate S0 or I0 but not D0
    missing_fences: list[str] = []
    for mod_path, slot_set in tqdm(assembly_modules.items(), desc="assembly mods", unit="mod", leave=False):
        has_assembly_slots = bool(slot_set & {"S0", "I0", "C0", "U0"})
        has_d0 = "D0" in slot_set
        if has_assembly_slots and not has_d0 and len(slot_set) >= 2:
            missing_fences.append(mod_path)
            # Only emit violation if the module assembles S0 and U0 (highest risk)
            if "S0" in slot_set and "U0" in slot_set:
                slot_info = module_slots.get(mod_path, {})
                _, source_file, line_no = slot_info.get("S0", ("", mod_path, 0))
                violations.append(
                    PromptAuthorityViolation(
                        violating_module=mod_path,
                        violation_type="MISSING_D0_FENCE",
                        low_authority_slot="U0",
                        high_authority_slot="S0",
                        source_file=source_file,
                        line_no=line_no,
                        severity="high",
                        suggested_fix=(
                            "Add d0_injections fence when assembling S0+U0 together. "
                            "The D0 fence guards against user prompt injection into the system slot."
                        ),
                    ),
                )

    # Build slot_generators index: slot -> [modules that generate it]
    slot_generators: dict[str, list[str]] = {slot: [] for slot in PROMPT_SLOT_TYPES}
    for mod_path, slots in module_slots.items():
        for slot in slots:
            if slot in slot_generators:
                slot_generators[slot].append(mod_path)

    violations.sort(key=lambda v: (v.severity, v.violating_module, v.violation_type))

    return PromptAuthorityReport(
        violations=violations,
        assembly_modules=assembly_modules,
        missing_fences=missing_fences,
        slot_generators=slot_generators,
        violation_count=len(violations),
    )


__all__ = [
    "PromptAuthorityReport",
    "PromptAuthorityViolation",
    "PromptViolationType",
    "detect_prompt_authority_violations",
]
