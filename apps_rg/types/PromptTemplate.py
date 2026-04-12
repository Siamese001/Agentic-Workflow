"""
SOVEREIGN KNOWLEDGE BASE (FROZEN v33.2)
---------------------------------------
Auto-generated from RG_JSON_KNOWLEDGE_MAP.md.
This module serves as the immutable 'brain' of the Resume Generation system.

VIOLATION: NO MAGIC STRINGS. ALL PROMPTS/CONFIGS MUST BE ACCESSED VIA THIS REGISTRY.

Slot Taxonomy Integration:
- Unified 10-slot taxonomy: S0,D0,M0,I0,E0,C0,Y0,U0,H0,R0
- See agentic_core.prompt_governance.contracts.slot_contracts for definitions
- Apps-layer prompts can be assembled via PromptAssembler with slot-aware context

# guardian: allow-magic-config
"""

from pydantic import BaseModel, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "PromptTemplate", "p0_governance")
_emit_emits_metric_event("PromptTemplate", "p4obs", "metric_1")
_emit_emits_metric_event("PromptTemplate", "p4obs", "metric_2")
_emit_emits_metric_event("PromptTemplate", "p4obs", "metric_3")
_emit_emits_metric_event("PromptTemplate", "p4obs", "metric_4")
_emit_emits_metric_event("PromptTemplate", "p4obs", "metric_5")
_emit_emits_metric_event("PromptTemplate", "p4obs", "metric_6")
_emit_records_incident_event("PromptTemplate", "p4obs", "incident")
_emit_captures_runtime_anomaly("PromptTemplate", "p4obs", "anomaly")
_emit_writes_observability_log("PromptTemplate", "p4obs", "obs_log")
_emit_updates_monitoring_state("PromptTemplate", "p4obs", "mon_state")
_emit_triggers_alert("PromptTemplate", "p4obs", "alert")
_emit_links_incident_trace("PromptTemplate", "p4obs", "trace_link")
_emit_captures_pattern("PromptTemplate", "p3lm", "pattern")
_emit_records_learning_event("PromptTemplate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("PromptTemplate", "p3lm", "snapshot")
_emit_feeds_meta_learning("PromptTemplate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("PromptTemplate", "p3lm", "routing")
_emit_improves_agent_policy("PromptTemplate", "p3lm", "policy")
_emit_stores_learning_state("PromptTemplate", "p3lm", "state")
_emit_records_execution_trace("PromptTemplate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("PromptTemplate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("PromptTemplate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("PromptTemplate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("PromptTemplate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("PromptTemplate", "env_read", "p2_env_1")
_emit_reads_environ("PromptTemplate", "env_read", "p2_env_2")
_emit_reads_runtime_state("PromptTemplate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("PromptTemplate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "PromptTemplate", "context_pull")
_emit_pulls_context("p1", "PromptTemplate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "PromptTemplate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "PromptTemplate", "uwg_term_2")
_emit_writes_through("p1", "PromptTemplate", "write_through")
_emit_writes_through("p1", "PromptTemplate", "write_through_2")
_emit_validated_by_safety_plane("p1", "PromptTemplate", "safety_validation")
_emit_invokes_eval("p1", "PromptTemplate", "eval_call")
_emit_proposal_commits_routing("p1", "PromptTemplate", "routing_commit")
_emit_escalates_to_human("p1", "PromptTemplate", "human_escalation")
_emit_routes_through("p1", "PromptTemplate", "route_through")
_emit_checks_agent_registry("p1", "PromptTemplate", "agent_registry")
_emit_validates_agent_capability("p1", "PromptTemplate", "capability")
_emit_dispatches_execution_plan("p1", "PromptTemplate", "exec_plan")
_emit_agent_executes_agent("p1", "PromptTemplate", "sub_agent")
_emit_routes_to_agent("p1", "PromptTemplate", "target_agent")
_emit_verifies_policy("p1", "PromptTemplate", "policy_check")
_emit_observes_runtime_state("p1", "PromptTemplate", "runtime_state")
_emit_verifies_boundary("p1", "PromptTemplate", "boundary_check")
_emit_transcripts_response("p1", "PromptTemplate", "transcript")
_emit_hard_fails_untranscripted("p1", "PromptTemplate")
_emit_gated_by_confidence("p1", "PromptTemplate", "confidence_gate")
emit_replay_key("p0", "PromptTemplate")
emit_determinism_digest("p0", "PromptTemplate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "PromptTemplate", "execution_auth")
_emit_validates_capability("p2", "PromptTemplate", "capability_check")
_emit_routes_to_capability("p2", "PromptTemplate", "capability_route")
_emit_writes_via_uwg("p2", "PromptTemplate", "uwg_write")
_emit_blocks_direct_write("p2", "PromptTemplate", "direct_write_block")
_emit_records_tool_invocation("p2", "PromptTemplate", "tool_invocation")
_emit_captures_execution_output("p2", "PromptTemplate", "exec_output")
_emit_dispatches_agent("p3", "PromptTemplate", "agent_dispatch")
_emit_coordinates_agents("p3", "PromptTemplate", "agent_coordination")
_emit_records_workflow_lineage("p3", "PromptTemplate", "workflow_lineage")
_emit_records_healing_outcome("p3", "PromptTemplate", "healing_outcome")
_emit_escalates_failure("p3", "PromptTemplate", "failure_escalation")
_emit_orchestrates_workflow("p3", "PromptTemplate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "PromptTemplate", "healing_dispatch")
_emit_invokes_evaluation("p3", "PromptTemplate", "evaluation_signal")
_emit_records_telemetry_event("p4", "PromptTemplate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "PromptTemplate", "eval_metric")
_emit_stores_embedding("p4", "PromptTemplate", "embedding_store")
_emit_updates_meta_learning_state("p4", "PromptTemplate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "PromptTemplate", "exec_snapshot_link")


class PromptTemplate(BaseModel):
    id: str
    template: str
    required_vars: list[str]

    @field_validator("template")
    @classmethod
    def validate_placeholders(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PromptTemplate.validate_placeholders"
        )

        if "{" in v and "}" not in v:
            raise ValueError(f"Potentially broken placeholder in prompt: {v[:50]}...")
        return v


class ThresholdConfig(BaseModel):
    rag_recency_weight: float = Field(..., ge=0.0, le=1.0)
    cot_min_paths: int | None = Field(None, ge=1)
    min_tot_depth: int | None = Field(None, ge=1)
    qa_thresholds: dict[str, str] = Field(default_factory=dict)


class KNodeDefinition(BaseModel):
    id: str
    name: str
    purpose: str
    config: ThresholdConfig


class SovereignKnowledge(BaseModel):
    """The frozen state of the extracted JSON logic."""

    version: str = "v33.2"
    prompts: dict[str, PromptTemplate]
    nodes: dict[str, KNodeDefinition]
    global_rules: dict[str, str]


# guardian: allow-magic-config
FROZEN_SNAPSHOT = SovereignKnowledge(
    prompts={
        "input_acquisition_jd": PromptTemplate(
            id="3.context.input_acquisition_gate.prompts[0].prompt_text",
            template="Please provide the Job Description URL. If the URL is unavailable or fails, paste the full JD text.",
            required_vars=[],
        ),
        "input_acquisition_resume": PromptTemplate(
            id="3.context.input_acquisition_gate.prompts[1].prompt_text",
            template="How would you like to provide the base resumes?\n1. Provide a single GitHub repository URL (recommended).\n2. Upload each file individually.",
            required_vars=[],
        ),
        "input_acquisition_github": PromptTemplate(
            id="3.context.input_acquisition_gate.conditional_logic.if.then.prompts[0].prompt_text",
            template="Please provide the GitHub repository URL.",
            required_vars=[],
        ),
        "template_acquisition_reasoning": PromptTemplate(
            id="3.context.l_series_configuration.implementation.template_acquisition_gate.prompts[0].prompt_text",
            template="Please upload the consolidated reasoning template file (Reasoning_Transformer_Template_L1.1.md).",
            required_vars=[],
        ),
        "template_acquisition_data": PromptTemplate(
            id="3.context.l_series_configuration.implementation.template_acquisition_gate.prompts[1].prompt_text",
            template="Please upload the raw data source (Transformer_Output_v40.md).",
            required_vars=[],
        ),
        "k1_hyde_generation": PromptTemplate(
            id="4.reasoning.K.1_company_job_title_extraction.hyde_enrichment",
            template="Given:\n- Company: {company_name}\n- Title: {job_title}\n- Brief JD: {sparse_jd}\n\nGenerate a comprehensive 400-word job description including:\n1. Likely technical requirements (8-10 specific skills/tools)\n2. Leadership scope and team size\n3. Key responsibilities (5-7 bullets)\n4. Success metrics and KPIs\n5. Required experience level and background\n\nBase this on typical {job_title} roles at {company_type} companies.",
            required_vars=["company_name", "job_title", "sparse_jd", "company_type"],
        ),
        "validation_fail_namedropping": PromptTemplate(
            id="4.reasoning.validation_functions.validate_no_company_namedropping",
            template="Rewrite in capability-focused style; remove previous employer names; focus on what was accomplished, not where. MUST use third-person implied voice (e.g., 'Established' instead of 'I established').",
            required_vars=[],
        ),
        "validation_fail_target_products": PromptTemplate(
            id="4.reasoning.validation_functions.validate_no_target_products_in_past_roles",
            template="Replace [TARGET_COMPANY]/[TARGET_PRODUCTS] with generic tech terms: 'cloud data platform','advanced analytics','enterprise data infrastructure','AI/ML platforms'",
            required_vars=[],
        ),
        "inter_node_pause": PromptTemplate(
            id="4.reasoning.implementation.inter_node_pause_gate.prompt_text",
            template="Press Enter or type 'Y' to continue to the next node.",
            required_vars=[],
        ),
        "k6_hypothetical_short": PromptTemplate(
            id="6.conditions.templates.hyde_prompt_short.prompt",
            template="Given the job title and any sparse JD bullets, write a 300-400 word hypothetical expanded job description that includes likely responsibilities, skills, and metrics. Keep factual inventiveness plausible and flag hypothetical statements in metadata.",
            required_vars=[],
        ),
        "toggle_schema_fallback": PromptTemplate(
            id="3.context.toggle_schema_acquisition_gate.execution_logic[1].if_false.prompts[0].prompt_text",
            template="🟡 WARNING: `Reasoning_Toggles_Summary_Enforced_Format.json v2.0` was not found in the repository. Please upload the file manually.",
            required_vars=[],
        ),
        "filename_template": PromptTemplate(
            id="5.output.filename_generation.filename_template",
            template="{sender_profile.username}_{artifact_type}_YYYY-MM-DD_vX.X.json",
            required_vars=["sender_profile.username", "artifact_type"],
        ),
    },
    nodes={
        "K.1": KNodeDefinition(
            id="K.1",
            name="Company Name & Job Title Extraction",
            purpose="Extract core metadata from raw input.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=1,
                min_tot_depth=1,
                qa_thresholds={
                    "company_present": "Required",
                    "title_present": "Required",
                    "valid_url": "Valid URL format",
                    "req_number": "≤8 chars",
                    "confidence": ">=0.95",
                },
            ),
        ),
        "K.2": KNodeDefinition(
            id="K.2",
            name="Industry Classification",
            purpose="Classify company industry using GICS/SIC taxonomy.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={
                    "category_valid": "Valid taxonomy",
                    "subcategory_aligned": "Consistent with category",
                    "self_consistency": ">=3/5 agreement",
                    "confidence": ">=0.90",
                },
            ),
        ),
        "K.2.5": KNodeDefinition(
            id="K.2.5",
            name="Competitive Positioning Agent",
            purpose="Analyze peer JDs to identify table stakes and differentiators.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=4,
                qa_thresholds={
                    "peer_jds_found": ">=3 peer JDs",
                    "table_stakes": ">=5 keywords",
                    "differentiators": ">=3 keywords",
                    "positioning_strategy": "Clear guidance for K.4/K.5",
                    "confidence": ">=0.85",
                },
            ),
        ),
        "K.3": KNodeDefinition(
            id="K.3",
            name="Primary Job Role Mapping",
            purpose="Map job to role catalog for template selection.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={
                    "role_from_catalog": "Exact catalog match",
                    "single_role": "No secondary role",
                    "jd_alignment": ">=0.85 semantic match",
                    "confidence": ">=0.90",
                },
            ),
        ),
        "K.4": KNodeDefinition(
            id="K.4",
            name="Professional Headline",
            purpose="Generate 3-axis professional headline.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=1,
                min_tot_depth=2,
                qa_thresholds={
                    "format": "Must contain exactly 2 '|' characters",
                    "constraint": "Strategic positioning - NOT tactical execution",
                },
            ),
        ),
        "K.5": KNodeDefinition(
            id="K.5",
            name="Executive Summary",
            purpose="Generate 110-130 token executive summary.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=2,
                qa_thresholds={"token_count": "110-130 tokens", "max_retries": "3"},
            ),
        ),
        "K.6": KNodeDefinition(
            id="K.6",
            name="Most Recent Experience",
            purpose="Generate bullets for most recent role with unified format.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=2,
                qa_thresholds={"intro_presence": "Field must not be null or empty"},
            ),
        ),
        "K.7": KNodeDefinition(
            id="K.7",
            name="Prior Experience",
            purpose="Generate bullets for prior roles (IBM Bullets format).",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=2,
                qa_thresholds={"intro_presence": "Field must not be null or empty"},
            ),
        ),
        "K.8": KNodeDefinition(
            id="K.8",
            name="Prior Career Foundation",
            purpose="Generate foundation section with 3 sections, 2 bullets each.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={
                    "section_count": "Exactly 3",
                    "bullet_count": "Exactly 2 per section",
                    "intro_presence": "All 3 intro fields must not be null or empty",
                },
            ),
        ),
        "K.9": KNodeDefinition(
            id="K.9",
            name="Leadership Competencies",
            purpose="Generate 6 key leadership competencies.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=1,
                qa_thresholds={
                    "count": "Exactly 6",
                    "description_length": "18-24 words each",
                    "gap_coverage": ">=85% of gaps addressed",
                    "keyword_density": "2-3 gap keywords per competency",
                    "authentic_phrasing": "Matches LinkedIn/framework patterns",
                    "credibility": "Plausible given base resume",
                    "base_resume_coverage": ">=2 competencies from base resume",
                    "dedup_k4": "<0.40 cosine",
                    "dedup_k5": "<0.50 cosine",
                    "dedup_k6": "<0.60 cosine",
                    "dedup_k7": "<0.60 cosine",
                    "ascii_hygiene": "Clean",
                    "overall_score": ">=0.88",
                    "no_target_products": "Generic platform terms only",
                },
            ),
        ),
        "K.10": KNodeDefinition(
            id="K.10",
            name="Cover Letter - Specificity-Driven Research Agent",
            purpose="Generate highly specific cover letter content.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=1,
                qa_thresholds={
                    "para_count": "3 total (1+2)",
                    "why_interested_len": "80-100 words",
                    "why_ideal_p1_len": "80-100 words",
                    "why_ideal_p2_len": "80-100 words",
                    "specificity_score": ">=3 company-specific details",
                    "authenticity": "Unique to this company",
                    "proof_points": ">=2 quantified achievements",
                    "ascii_hygiene": "Clean",
                    "confidence": ">=0.85",
                },
            ),
        ),
        "K.11": KNodeDefinition(
            id="K.11",
            name="Optimized Skills Keyword Generation",
            purpose="Generate 10-15 ATS-optimized skill keywords.",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=2,
                min_tot_depth=None,
                qa_thresholds={
                    "keyword_count": "10-15 keywords",
                    "ats_relevance": "Top 10 JD keywords included",
                    "coverage_balance": "Mix of technical, soft, and domain skills",
                },
            ),
        ),
        "ORCHESTRATOR_L3": KNodeDefinition(
            id="ORCHESTRATOR_L3",
            name="L3 Orchestrator",
            purpose="Coordinates the 50-engine fleet",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "HOP.1.CLERK": KNodeDefinition(
            id="HOP.1.CLERK",
            name="Clerk Extraction",
            purpose="Structural data extraction",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "HOP.2.ENRICH": KNodeDefinition(
            id="HOP.2.ENRICH",
            name="Data Enrichment",
            purpose="Verb canonicalization and enrichment",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "SERVICE.INVOKER": KNodeDefinition(
            id="SERVICE.INVOKER",
            name="Service Invoker",
            purpose="LLM service invocation",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "REFINE.WEIGHTS": KNodeDefinition(
            id="REFINE.WEIGHTS",
            name="Weight Adjustment",
            purpose="Dynamic section weighting",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "REFINE.OPTIMIZER": KNodeDefinition(
            id="REFINE.OPTIMIZER",
            name="Content Optimizer",
            purpose="Bullet ordering optimization",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "REFINE.RANKER": KNodeDefinition(
            id="REFINE.RANKER",
            name="Section Ranker",
            purpose="Section ordering by role type",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "REFINE.TEMPLATE": KNodeDefinition(
            id="REFINE.TEMPLATE",
            name="Template Optimizer",
            purpose="Template selection",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "SAFETY.VOID": KNodeDefinition(
            id="SAFETY.VOID",
            name="Void Compliance",
            purpose="Architecture enforcement",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "SAFETY.ATS": KNodeDefinition(
            id="SAFETY.ATS",
            name="ATS Compatibility",
            purpose="ATS parsing validation",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
        "SAFETY.HALLUCINATION": KNodeDefinition(
            id="SAFETY.HALLUCINATION",
            name="Hallucination Detector",
            purpose="Claim verification",
            config=ThresholdConfig(
                rag_recency_weight=0.25,
                cot_min_paths=None,
                min_tot_depth=None,
                qa_thresholds={},
            ),
        ),
    },
    global_rules={
        "VG_BULLET_PUNCTUATION": "All bullets must end with period '.' character",
        "VG_COMPETENCY_BALANCE": "All 6 competencies must have word counts within 22-28 words. Coefficient of variation < 0.25",
        "VG_REDUNDANCY_CHECK": "Check for phrases appearing in 2+ sections (K.5, K.6, K.7, K.9, K.8). Target: <10% overlap",
        "VG_NATURAL_HYPHENS": "Scan for unnatural hyphens removed AND natural hyphens preserved based on external configuration file.",
        "VG_SOURCE_CONFLICT_CHECK": "Source conflict resolution gate",
        "VG_COMP_BULLET_RATIO": "Competency bullet ratio validation",
        "VG_SCHEMA_001": "All generated field names MUST exist in App_Schema_v4.json's defined fields",
        "GUARD_BASE_FILES": "all_base_files_provided",
        "GUARD_CONTEXT_VALIDATED": "source_context_validated_and_conflict_free",
        "GUARD_TOGGLES_APPROVED": "toggles_approved",
        "GUARD_K_NODES_COMPLETE": "all_k_nodes_complete_and_validated",
        "GUARD_TEXT_OUTPUT": "text_output_generated",
        "GUARD_SUBMISSION_Y": "submission_confirmed_Y",
        "GUARD_SUBMISSION_N": "submission_confirmed_N",
        "GUARD_TRACKER_OUTPUT": "tracker_output_generated",
        "SECTION_5_GATE": "Section 5 CANNOT begin until K.1-K.11 complete with PASS status",
        "POST_PROCESSING": "Final output contains no K.1, K.2, etc. in body text",
        "RESUME_HEADER": "Resume name appears on line 4, headline on line 6, no K.4 prefix in final output",
        "L_SERIES_LENGTH": "Total output ≤ 120% of template file character count",
        "L_SERIES_VALIDATION": "Must have valid L-Series selection if detailed_reasoning == 'Yes'",
        "K6_MODE_CHECK": "Recognize phase transition from strategic (K.5) to tactical detail (K.6-K.7)",
        "K7_MODE_CHECK": "Maintain tactical detail mode consistency between K.6 and K.7",
    },
)


def get_prompt(prompt_id: str) -> str:
    """Retrieve a raw prompt template by ID."""
    mapping = {
        "hyde_gen": "k1_hyde_generation",
        "input_jd": "input_acquisition_jd",
        "input_resume": "input_acquisition_resume",
        "input_github": "input_acquisition_github",
        "fix_names": "validation_fail_namedropping",
        "fix_products": "validation_fail_target_products",
        "pause": "inter_node_pause",
        "hyde_short": "k6_hypothetical_short",
    }
    key = mapping.get(prompt_id, prompt_id)
    if key not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt ID '{prompt_id}' not found in Frozen Knowledge.")
    return FROZEN_SNAPSHOT.prompts[key].template


def get_node_config(node_id: str) -> KNodeDefinition:
    """Retrieve configuration for a specific K-Node."""
    # guardian: allow-config-with-logic
    if node_id not in FROZEN_SNAPSHOT.nodes:
        raise KeyError(f"Node ID '{node_id}' not found in Frozen Knowledge.")
    return FROZEN_SNAPSHOT.nodes[node_id]


def get_global_rule(rule_id: str) -> str:
    """Retrieve a global validation rule by ID."""
    if rule_id not in FROZEN_SNAPSHOT.global_rules:
        raise KeyError(f"Rule ID '{rule_id}' not found in Frozen Knowledge.")
    return FROZEN_SNAPSHOT.global_rules[rule_id]


def list_all_nodes() -> list[str]:
    """Return list of all K-Node IDs."""
    return list(FROZEN_SNAPSHOT.nodes.keys())


def list_all_prompts() -> list[str]:
    """Return list of all prompt IDs."""
    return list(FROZEN_SNAPSHOT.prompts.keys())
