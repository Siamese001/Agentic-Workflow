"""
apps_rfp Configuration Schemas — AI Proposal / RFP Generator.

Pydantic models for type-safe configuration. Aligned with apps_rg pattern.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec

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

_emit_applies_guardrail("p0", "agent_spec_config", "p0_governance")
_emit_reads_policy_state("p0", "agent_spec_config", "policy_binding")
_emit_snapshots_state("p0", "agent_spec_config", "state_snapshot")
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

_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_1")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_2")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_3")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_4")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_5")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_6")
_emit_records_incident_event("agent_spec_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_spec_config", "p4obs", "anomaly")
_emit_writes_observability_log("agent_spec_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_spec_config", "p4obs", "mon_state")
_emit_triggers_alert("agent_spec_config", "p4obs", "alert")
_emit_links_incident_trace("agent_spec_config", "p4obs", "trace_link")
_emit_captures_pattern("agent_spec_config", "p3lm", "pattern")
_emit_records_learning_event("agent_spec_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_spec_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_spec_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_spec_config", "p3lm", "routing")
_emit_improves_agent_policy("agent_spec_config", "p3lm", "policy")
_emit_stores_learning_state("agent_spec_config", "p3lm", "state")
_emit_records_execution_trace("agent_spec_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_spec_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_spec_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_spec_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_spec_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_spec_config", "env_read", "p2_env_1")
_emit_reads_environ("agent_spec_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_spec_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_spec_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_spec_config", "context_pull")
_emit_pulls_context("p1", "agent_spec_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_spec_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_spec_config", "uwg_term_2")
_emit_writes_through("p1", "agent_spec_config", "write_through")
_emit_writes_through("p1", "agent_spec_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_spec_config", "safety_validation")
_emit_invokes_eval("p1", "agent_spec_config", "eval_call")
_emit_proposal_commits_routing("p1", "agent_spec_config", "routing_commit")
_emit_escalates_to_human("p1", "agent_spec_config", "human_escalation")
_emit_routes_through("p1", "agent_spec_config", "route_through")
_emit_checks_agent_registry("p1", "agent_spec_config", "agent_registry")
_emit_validates_agent_capability("p1", "agent_spec_config", "capability")
_emit_dispatches_execution_plan("p1", "agent_spec_config", "exec_plan")
_emit_agent_executes_agent("p1", "agent_spec_config", "sub_agent")
_emit_routes_to_agent("p1", "agent_spec_config", "target_agent")
_emit_verifies_policy("p1", "agent_spec_config", "policy_check")
_emit_observes_runtime_state("p1", "agent_spec_config", "runtime_state")
_emit_verifies_boundary("p1", "agent_spec_config", "boundary_check")
_emit_transcripts_response("p1", "agent_spec_config", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_spec_config")
_emit_gated_by_confidence("p1", "agent_spec_config", "confidence_gate")
emit_replay_key("p0", "agent_spec_config")
emit_determinism_digest("p0", "agent_spec_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_spec_config", "execution_auth")
_emit_validates_capability("p2", "agent_spec_config", "capability_check")
_emit_routes_to_capability("p2", "agent_spec_config", "capability_route")
_emit_writes_via_uwg("p2", "agent_spec_config", "uwg_write")
_emit_blocks_direct_write("p2", "agent_spec_config", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_spec_config", "tool_invocation")
_emit_captures_execution_output("p2", "agent_spec_config", "exec_output")
_emit_dispatches_agent("p3", "agent_spec_config", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_spec_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_spec_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_spec_config", "healing_outcome")
_emit_escalates_failure("p3", "agent_spec_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_spec_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_spec_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_spec_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_spec_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_spec_config", "eval_metric")
_emit_stores_embedding("p4", "agent_spec_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_spec_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_spec_config", "exec_snapshot_link")

_log = logging.getLogger(__name__)


class ProposalSectionConfig(BaseModel):
    """Schema for a single proposal section template."""

    section_id: str
    heading: str
    required: bool = True
    requires_assumptions: bool = False
    requires_evidence: bool = True
    max_words: int = Field(default=500, ge=50)


class IndustryProfileConfig(BaseModel):
    """Industry-specific configuration for proposal generation."""

    industry_id: str
    display_name: str
    regulatory_flags: list[str] = Field(default_factory=list)
    typical_pain_points: list[str] = Field(default_factory=list)
    preferred_architecture: str = "cloud-first"


class RoadmapConfig(BaseModel):
    """Phased roadmap template configuration."""

    phases: list[str] = Field(default_factory=lambda: ["Discovery", "Foundation", "Pilot", "Scale", "Govern"])
    min_phases: int = Field(default=3, ge=1)
    require_governance_phase: bool = True
    require_measurement_phase: bool = True


class RiskMatrixConfig(BaseModel):
    """Risk matrix template configuration."""

    risk_categories: list[str] = Field(
        default_factory=lambda: [
            "technical_complexity",
            "data_quality",
            "regulatory_compliance",
            "change_management",
            "model_drift",
            "integration_risk",
        ],
    )
    severity_levels: list[str] = Field(default_factory=lambda: ["LOW", "MEDIUM", "HIGH", "CRITICAL"])


class ProposalOutputConfig(BaseModel):
    """Output configuration for RFP proposals."""

    output_dir: str = Field(default="artifacts/rfp")
    artifact_prefix: str = Field(default="proposal")
    emit_run_summary: bool = True
    emit_json_manifest: bool = True
    dry_run: bool = False


class ProposalGateConfig(BaseModel):
    """Quality gates for proposal validation."""

    require_assumptions_labeled: bool = True
    require_governance_section: bool = True
    require_value_rationale: bool = True
    max_empty_sections: int = Field(default=0, ge=0)
    min_quality_score: float = Field(default=0.75, ge=0.0, le=1.0)


class RfpAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root configuration for all apps_rfp agent specifications."""

    version: str = "1.0.0"
    sections: list[ProposalSectionConfig] = Field(
        default_factory=lambda: [
            ProposalSectionConfig(section_id="executive_summary", heading="Executive Summary", required=True),
            ProposalSectionConfig(
                section_id="current_state",
                heading="Current State and Pain Points",
                required=True,
                requires_assumptions=True,
            ),
            ProposalSectionConfig(
                section_id="future_state",
                heading="Future State Architecture",
                required=True,
                requires_evidence=True,
            ),
            ProposalSectionConfig(
                section_id="implementation_roadmap",
                heading="Implementation Roadmap",
                required=True,
                requires_assumptions=True,
            ),
            ProposalSectionConfig(
                section_id="risk_and_governance",
                heading="Risk and Governance",
                required=True,
            ),
            ProposalSectionConfig(
                section_id="value_case",
                heading="Value Case",
                required=True,
                requires_evidence=True,
            ),
            ProposalSectionConfig(
                section_id="solution_appendix",
                heading="Solution Appendix",
                required=False,
            ),
        ],
    )
    roadmap: RoadmapConfig = Field(default_factory=RoadmapConfig)
    risk_matrix: RiskMatrixConfig = Field(default_factory=RiskMatrixConfig)
    output: ProposalOutputConfig = Field(default_factory=ProposalOutputConfig)
    gate: ProposalGateConfig = Field(default_factory=ProposalGateConfig)
    industries: dict[str, IndustryProfileConfig] = Field(
        default_factory=lambda: {
            "financial_services": IndustryProfileConfig(
                industry_id="financial_services",
                display_name="Financial Services",
                regulatory_flags=["SOX", "GDPR", "MiFID II"],
                typical_pain_points=[
                    "manual compliance workflows",
                    "model explainability gaps",
                    "data silos",
                ],
                preferred_architecture="sovereign",
            ),
            "healthcare": IndustryProfileConfig(
                industry_id="healthcare",
                display_name="Healthcare",
                regulatory_flags=["HIPAA", "FDA 21 CFR Part 11"],
                typical_pain_points=[
                    "unstructured clinical notes",
                    "care coordination latency",
                    "audit trail gaps",
                ],
                preferred_architecture="hybrid",
            ),
            "technology": IndustryProfileConfig(
                industry_id="technology",
                display_name="Technology",
                regulatory_flags=[],
                typical_pain_points=["engineering velocity", "context switching", "knowledge fragmentation"],
                preferred_architecture="cloud-first",
            ),
            "government": IndustryProfileConfig(
                industry_id="government",
                display_name="Government / Public Sector",
                regulatory_flags=["FedRAMP", "FISMA", "ITAR"],
                typical_pain_points=["legacy system modernization", "data sovereignty", "approval latency"],
                preferred_architecture="sovereign",
            ),
        },
    )
    global_step_limit: int = Field(default=12)
    checkpoint_enabled: bool = True
    trace_persistence: bool = True

    @model_validator(mode="after")
    def validate_required_sections_present(self) -> RfpAgentSpecs:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RfpAgentSpecs.validate_required_sections_present"
        )

        required_ids = {s.section_id for s in self.sections if s.required}
        must_have = {"executive_summary", "implementation_roadmap", "risk_and_governance", "value_case"}
        missing = must_have - required_ids
        if missing:
            raise ValueError(f"Required proposal sections missing: {missing}")
        return self


_SPEC_CACHE: RfpAgentSpecs | None = None


def load_rfp_specs(spec_path: str | None = None) -> RfpAgentSpecs:
    """Load RfpAgentSpecs from JSON file or return defaults."""
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "rfp_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = RfpAgentSpecs.model_validate(raw)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_rfp] Failed to load specs from %s: %s — using defaults", resolved, exc)

    _SPEC_CACHE = RfpAgentSpecs()
    return _SPEC_CACHE
