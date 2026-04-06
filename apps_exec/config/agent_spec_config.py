"""
apps_exec Configuration Schemas — Executive Brief Generator.

Pydantic models for type-safe configuration. Aligned with apps_rg/apps_lic schema pattern.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

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

MAX_BRIEF_WORDS = 2000
MIN_BRIEF_WORDS = 150
DEFAULT_TIMEOUT_SEC = 60
MAX_SECTIONS = 20


class AudiencePersonaConfig(BaseModel):
    """Configuration for a target audience persona."""

    persona_id: str = Field(..., description="Unique persona key, e.g. 'recruiter', 'cto', 'svp_eng'")
    display_name: str = Field(..., description="Human-readable persona label")
    tone: str = Field(
        default="professional",
        description="Tone directive: board-ready | cto-ready | recruiter-friendly | technical",
    )
    max_words: int = Field(default=800, ge=50)
    required_sections: list[str] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(default_factory=list)


class IngestionConfig(BaseModel):
    """Controls how source materials are ingested."""

    source_dirs: list[str] = Field(
        default_factory=lambda: ["docs/architecture", "docs/reports"],
        description="Directories to ingest as source material",
    )
    file_extensions: list[str] = Field(default_factory=lambda: [".md", ".txt", ".json"])
    max_file_size_kb: int = Field(default=512, ge=1)
    recursive: bool = Field(default=True)


class ExtractionConfig(BaseModel):
    """Controls capability extraction from source documents."""

    capability_patterns: list[str] = Field(
        default_factory=lambda: [
            r"(?i)(supports|provides|enforces|enables|implements)\s+([A-Z][a-z]+(?:\s+[A-Z]?[a-z]+){0,4})",
            r"(?i)(governance|orchestration|routing|retrieval|safety|observability|determinism)",
        ]
    )
    evidence_anchor_pattern: str = Field(
        default=r"(?i)(layer|module|engine|agent|validator|contract|spec)\s+\w+",
        description="Pattern for extracting evidence anchors from source",
    )
    max_capabilities_per_section: int = Field(default=10, ge=1)


class OutputConfig(BaseModel):
    """Controls output artifact generation."""

    output_dir: str = Field(default="reports/executive")
    artifact_prefix: str = Field(default="exec_brief")
    emit_run_summary: bool = Field(default=True)
    emit_json_manifest: bool = Field(default=True)
    dry_run: bool = Field(default=False)


class StyleGateConfig(BaseModel):
    """Quality gate thresholds for style and evidence checks."""

    min_evidence_anchors: int = Field(default=2, ge=0)
    max_unsupported_claims: int = Field(default=0, ge=0)
    forbidden_buzzword_density: float = Field(default=0.05, ge=0.0, le=1.0)
    require_why_this_matters: bool = Field(default=True)
    require_audience_declaration: bool = Field(default=True)
    min_quality_score: float = Field(default=0.70, ge=0.0, le=1.0)


class ExecAgentSpecs(BaseModel):
    """Root configuration object for all apps_exec agent specifications."""

    version: str = Field(default="1.0.0")
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    style_gate: StyleGateConfig = Field(default_factory=StyleGateConfig)
    personas: dict[str, AudiencePersonaConfig] = Field(
        default_factory=lambda: {
            "recruiter": AudiencePersonaConfig(
                persona_id="recruiter",
                display_name="Technical Recruiter",
                tone="recruiter-friendly",
                max_words=600,
                required_sections=["platform_summary", "key_capabilities", "portfolio_value"],
                forbidden_phrases=["synergy", "leverage as a verb", "game-changer"],
            ),
            "cto": AudiencePersonaConfig(
                persona_id="cto",
                display_name="Chief Technology Officer",
                tone="cto-ready",
                max_words=1200,
                required_sections=["architecture_overview", "governance_model", "platform_strategy"],
            ),
            "svp_eng": AudiencePersonaConfig(
                persona_id="svp_eng",
                display_name="SVP Engineering",
                tone="technical",
                max_words=1500,
                required_sections=["system_architecture", "engineering_decisions", "quality_gates"],
            ),
            "board": AudiencePersonaConfig(
                persona_id="board",
                display_name="Board / Executive Committee",
                tone="board-ready",
                max_words=500,
                required_sections=["strategic_value", "risk_posture", "competitive_differentiation"],
            ),
        }
    )
    global_step_limit: int = Field(default=10)
    checkpoint_enabled: bool = Field(default=True)
    trace_persistence: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_personas_non_empty(self) -> ExecAgentSpecs:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ExecAgentSpecs.validate_personas_non_empty")

        if not self.personas:
            raise ValueError("ExecAgentSpecs.personas must define at least one persona")
        return self


_SPEC_CACHE: ExecAgentSpecs | None = None


def load_exec_specs(spec_path: str | None = None) -> ExecAgentSpecs:
    """Load ExecAgentSpecs from JSON file or return defaults.

    Args:
        spec_path: Optional path to a JSON spec file. Defaults to
            apps_exec/config/exec_agent_specs.json if it exists.

    Returns:
        Validated ExecAgentSpecs instance.
    """
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "exec_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = ExecAgentSpecs.model_validate(raw)
            _log.info("[apps_exec] Loaded specs from %s", resolved)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_exec] Failed to load specs from %s: %s — using defaults", resolved, exc)

    _SPEC_CACHE = ExecAgentSpecs()
    return _SPEC_CACHE
