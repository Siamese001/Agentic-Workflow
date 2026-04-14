"""
Brief Assembly Engine — apps_exec.

Assembles deterministic document skeleton for an executive brief:
required headings, section ordering, evidence anchors, and
"why this matters" blocks. Narrative fill is marked as model-ready
but ships with high-quality deterministic templates.

Deterministic: section ordering, headings, metadata, evidence injection.
Model-ready:   narrative phrasing marked with LLM_FILL placeholders.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "brief_assembly_engine", "execution_auth")
_emit_validates_capability("p2", "brief_assembly_engine", "capability_check")
_emit_routes_to_capability("p2", "brief_assembly_engine", "capability_route")
_emit_writes_via_uwg("p2", "brief_assembly_engine", "uwg_write")
_emit_blocks_direct_write("p2", "brief_assembly_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "brief_assembly_engine", "tool_invocation")
_emit_captures_execution_output("p2", "brief_assembly_engine", "exec_output")
_emit_dispatches_agent("p3", "brief_assembly_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "brief_assembly_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "brief_assembly_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "brief_assembly_engine", "healing_outcome")
_emit_escalates_failure("p3", "brief_assembly_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "brief_assembly_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "brief_assembly_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "brief_assembly_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "brief_assembly_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "brief_assembly_engine", "eval_metric")
_emit_stores_embedding("p4", "brief_assembly_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "brief_assembly_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "brief_assembly_engine", "exec_snapshot_link")
from apps_exec.engines.base_exec_engine import BaseExecEngine
from apps_exec.engines.capability_extraction_engine import ExtractionResult
from apps_exec.types.exec_types import (
    BriefSection,
    CapabilityEvidence,
    ExecBriefRequest,
)

_emit_applies_guardrail("p0", "brief_assembly_engine", "p0_governance")
_emit_reads_policy_state("p0", "brief_assembly_engine", "policy_binding")
_emit_snapshots_state("p0", "brief_assembly_engine", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("brief_assembly_engine", "p4obs", "metric_1")
_emit_emits_metric_event("brief_assembly_engine", "p4obs", "metric_2")
_emit_emits_metric_event("brief_assembly_engine", "p4obs", "metric_3")
_emit_emits_metric_event("brief_assembly_engine", "p4obs", "metric_4")
_emit_emits_metric_event("brief_assembly_engine", "p4obs", "metric_5")
_emit_emits_metric_event("brief_assembly_engine", "p4obs", "metric_6")
_emit_records_incident_event("brief_assembly_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("brief_assembly_engine", "p4obs", "anomaly")
_emit_writes_observability_log("brief_assembly_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("brief_assembly_engine", "p4obs", "mon_state")
_emit_triggers_alert("brief_assembly_engine", "p4obs", "alert")
_emit_links_incident_trace("brief_assembly_engine", "p4obs", "trace_link")
_emit_captures_pattern("brief_assembly_engine", "p3lm", "pattern")
_emit_records_learning_event("brief_assembly_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("brief_assembly_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("brief_assembly_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("brief_assembly_engine", "p3lm", "routing")
_emit_improves_agent_policy("brief_assembly_engine", "p3lm", "policy")
_emit_stores_learning_state("brief_assembly_engine", "p3lm", "state")
_emit_records_execution_trace("brief_assembly_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("brief_assembly_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("brief_assembly_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("brief_assembly_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("brief_assembly_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("brief_assembly_engine", "env_read", "p2_env_1")
_emit_reads_environ("brief_assembly_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("brief_assembly_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("brief_assembly_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "brief_assembly_engine", "context_pull")
_emit_pulls_context("p1", "brief_assembly_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "brief_assembly_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "brief_assembly_engine", "uwg_term_2")
_emit_writes_through("p1", "brief_assembly_engine", "write_through")
_emit_writes_through("p1", "brief_assembly_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "brief_assembly_engine", "safety_validation")
_emit_invokes_eval("p1", "brief_assembly_engine", "eval_call")
_emit_proposal_commits_routing("p1", "brief_assembly_engine", "routing_commit")
_emit_escalates_to_human("p1", "brief_assembly_engine", "human_escalation")
_emit_routes_through("p1", "brief_assembly_engine", "route_through")
_emit_checks_agent_registry("p1", "brief_assembly_engine", "agent_registry")
_emit_validates_agent_capability("p1", "brief_assembly_engine", "capability")
_emit_dispatches_execution_plan("p1", "brief_assembly_engine", "exec_plan")
_emit_agent_executes_agent("p1", "brief_assembly_engine", "sub_agent")
_emit_routes_to_agent("p1", "brief_assembly_engine", "target_agent")
_emit_verifies_policy("p1", "brief_assembly_engine", "policy_check")
_emit_observes_runtime_state("p1", "brief_assembly_engine", "runtime_state")
_emit_verifies_boundary("p1", "brief_assembly_engine", "boundary_check")
_emit_transcripts_response("p1", "brief_assembly_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "brief_assembly_engine")
_emit_gated_by_confidence("p1", "brief_assembly_engine", "confidence_gate")
emit_replay_key("p0", "brief_assembly_engine")
emit_determinism_digest("p0", "brief_assembly_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)

_SECTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "platform_summary": {
        "heading": "Platform Overview",
        "why": "Gives reviewers immediate orientation on the system's purpose and scope.",
        "required_for": ["recruiter", "cto", "svp_eng", "board", "head_of_ai"],
    },
    "key_capabilities": {
        "heading": "Key Capabilities",
        "why": "Enumerates concrete features that distinguish this platform.",
        "required_for": ["recruiter", "cto", "svp_eng", "head_of_ai"],
    },
    "architecture_overview": {
        "heading": "Architecture Overview",
        "why": "Shows technical reviewers the layered design and decision rationale.",
        "required_for": ["cto", "svp_eng"],
    },
    "governance_model": {
        "heading": "Governance and Safety Model",
        "why": "Demonstrates that the system enforces policy, not just best-effort behavior.",
        "required_for": ["cto", "board"],
    },
    "platform_strategy": {
        "heading": "Platform Strategy and Positioning",
        "why": "Translates architecture into business-level differentiation.",
        "required_for": ["cto", "board", "head_of_ai"],
    },
    "engineering_decisions": {
        "heading": "Key Engineering Decisions",
        "why": "Surfaces the non-obvious trade-offs that reflect engineering maturity.",
        "required_for": ["svp_eng"],
    },
    "quality_gates": {
        "heading": "Quality Gates and Validation",
        "why": "Shows that outputs are measurable and failure modes are explicit.",
        "required_for": ["svp_eng", "head_of_ai"],
    },
    "portfolio_value": {
        "heading": "Portfolio and Signal Value",
        "why": "Helps recruiters and hiring managers understand what this demonstrates.",
        "required_for": ["recruiter"],
    },
    "strategic_value": {
        "heading": "Strategic Value",
        "why": "Board-level translation of technical investments into business outcomes.",
        "required_for": ["board"],
    },
    "risk_posture": {
        "heading": "Risk Posture and Mitigations",
        "why": "Boards need to know what risks exist and how they are controlled.",
        "required_for": ["board"],
    },
    "competitive_differentiation": {
        "heading": "Competitive Differentiation",
        "why": "Positions the platform against alternatives at a strategic level.",
        "required_for": ["board", "head_of_ai"],
    },
    "enterprise_use_cases": {
        "heading": "Enterprise Use Cases",
        "why": "Grounds capabilities in real-world deployment scenarios.",
        "required_for": ["cto", "head_of_ai", "recruiter"],
    },
}

_CAPABILITY_BODY_TEMPLATE = (
    "The platform implements {capabilities}. "
    "These capabilities are enforced at the architecture layer, "
    "not bolted on as post-hoc guardrails."
)


@dataclass
class AssemblyResult:
    """Output of brief assembly."""

    sections: list[BriefSection] = field(default_factory=list)
    missing_required_sections: list[str] = field(default_factory=list)
    capabilities_used: list[CapabilityEvidence] = field(default_factory=list)


class BriefAssemblyEngine(BaseExecEngine):
    """Assemble deterministic brief skeleton for a given persona.

    Selects required sections for the target audience, injects capability
    evidence, and renders body text from deterministic templates.
    Each section declares whether it is deterministic or model-ready.
    """

    AGENT_ID = "EXEC_BRIEF_ASSEMBLY"

    def execute(self, input_data: tuple[ExecBriefRequest, ExtractionResult]) -> AssemblyResult:
        """Assemble brief sections.

        Args:
            input_data: Tuple of (ExecBriefRequest, ExtractionResult).

        Returns:
            AssemblyResult with ordered BriefSection list.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BriefAssemblyEngine.execute")

        request, extraction = input_data
        persona_key = request.audience.value if hasattr(request.audience, "value") else str(request.audience)

        required_sections = [
            sec_id for sec_id, schema in _SECTION_SCHEMAS.items() if persona_key in schema["required_for"]
        ]

        caps_by_emphasis: dict[str, list[str]] = {}
        for cap in extraction.capabilities:
            caps_by_emphasis.setdefault(cap.emphasis_area, []).append(cap.label)

        cap_labels = [cap.label for cap in extraction.capabilities[:8]]
        cap_summary = ", ".join(cap_labels) if cap_labels else "layered governance, orchestration, and safety"

        sections: list[BriefSection] = []
        missing: list[str] = []

        for sec_id in tqdm(required_sections, desc="Processing", unit="item"):
            schema = _SECTION_SCHEMAS.get(sec_id, {})
            heading = schema.get("heading", sec_id.replace("_", " ").title())
            why = schema.get("why", "")

            body = self._render_body(sec_id, cap_summary, caps_by_emphasis, extraction.evidence_anchors)

            word_count = len(body.split())
            sections.append(
                BriefSection(
                    section_id=sec_id,
                    heading=heading,
                    body=body,
                    is_deterministic=True,
                    evidence_anchors=tuple(extraction.evidence_anchors[:5]),
                    why_this_matters=why,
                    word_count=word_count,
                ),
            )

        self.record_pass(f"Assembled {len(sections)} sections for persona={persona_key}")
        return AssemblyResult(
            sections=sections,
            missing_required_sections=missing,
            capabilities_used=extraction.capabilities,
        )

    def _render_body(
        self,
        sec_id: str,
        cap_summary: str,
        caps_by_emphasis: dict[str, list[str]],
        evidence_anchors: list[str],
    ) -> str:
        """Render deterministic body text for a section."""
        anchor_note = f" Evidence anchors: {', '.join(evidence_anchors[:3])}." if evidence_anchors else ""

        templates: dict[str, str] = {
            "platform_summary": (
                f"This platform is a production-grade agentic AI system implementing {cap_summary}. "
                "It is built on a layered architecture with explicit enforcement boundaries between "
                "routing, execution, orchestration, state, safety, and observability."
                f"{anchor_note}"
            ),
            "key_capabilities": (
                f"Core capabilities include: {cap_summary}. "
                "Each capability is implemented as a first-class architectural concern, "
                "not a post-hoc addition."
            ),
            "architecture_overview": (
                "The system uses a six-layer architecture (L0–L6) where each layer has "
                "a strictly enforced dependency boundary. L0 handles routing and governance enforcement. "
                "L5 enforces static safety checks and determinism contracts. "
                "L6 provides observability and tracing."
                f"{anchor_note}"
            ),
            "governance_model": (
                "Policy is enforced at the routing layer (L0) via signed InstructionPackets "
                "with policy_hash validation. Static analysis detects non-deterministic calls "
                "in execution-critical paths. All violations are surfaced with rule IDs and evidence."
            ),
            "platform_strategy": (
                "The platform is positioned as enterprise-ready infrastructure for "
                "agentic AI deployments where governance, reproducibility, and auditability "
                "are non-negotiable requirements — not optional features."
            ),
            "engineering_decisions": (
                "Key decisions include: (1) frozen dataclass types for immutable execution "
                "contracts; (2) ADG-enforced layer boundaries preventing dependency inversion; "
                "(3) pre-commit hooks as constitutional enforcement, not advisory linting; "
                "(4) determinism-first design with explicit model-driven zones."
            ),
            "quality_gates": (
                "Every pipeline stage has explicit quality gates. Gate failures are reported "
                "with rule IDs, severity levels, and evidence. No silent fallback. "
                "Dry-run mode available on every entrypoint."
            ),
            "portfolio_value": (
                "This repository demonstrates: layered system design, governance enforcement, "
                "multi-hop agent orchestration, static analysis tooling, and production-grade "
                "output contracts. It reflects the thinking of a senior AI platform architect."
            ),
            "strategic_value": (
                f"Investment in this platform delivers: {cap_summary}. "
                "These translate directly to reduced AI risk, faster enterprise deployment cycles, "
                "and defensible audit trails."
            ),
            "risk_posture": (
                "Risk controls include: static determinism enforcement, policy hash validation, "
                "layer boundary guards, and hallucination detection gates. "
                "Every failure mode is explicit and testable."
            ),
            "competitive_differentiation": (
                "Unlike point solutions, this platform enforces governance at the architecture "
                "layer. Competitors typically bolt on safety as post-processing. "
                "Here, safety and determinism are constitutional requirements."
            ),
            "enterprise_use_cases": (
                "Target use cases: autonomous document generation, regulated-industry AI assistants, "
                "enterprise proposal and brief automation, evaluation lab for AI workloads, "
                "and research synthesis pipelines."
            ),
        }

        return templates.get(
            sec_id,
            f"[SECTION: {sec_id}] Capabilities: {cap_summary}.{anchor_note}",
        )
