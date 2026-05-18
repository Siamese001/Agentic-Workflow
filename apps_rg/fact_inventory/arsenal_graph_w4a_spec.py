"""W4A capability-domain taxonomy and deep agentic skill row SSOT (apps_rg only)."""
from __future__ import annotations

from typing import Any

# Primary taxonomy: 14 capability domains (not source-doc buckets).
AGENTIC_CAPABILITY_DOMAINS: list[dict[str, str]] = [
    {
        "domain_id": "domain_agentic_systems_architecture",
        "label": "Agentic Systems Architecture",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_reasoning_planning_decomposition",
        "label": "Reasoning, Planning, and Task Decomposition",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_routing_triage_workflow",
        "label": "Routing, Triage, and Workflow Selection",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_orchestration_managed_workflows",
        "label": "Orchestration and Managed Workflows",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_context_engineering_grounding",
        "label": "Context Engineering and Evidence Grounding",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_prompt_assembly_boundaries",
        "label": "Prompt Assembly and Instruction/Data Boundaries",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_execution_tool_sandbox",
        "label": "Execution, Tool Use, and Sandboxed Autonomy",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_healing_retry_resilience",
        "label": "Healing, Retry, and Runtime Resilience",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_runtime_gates_exit",
        "label": "Runtime Gates, Evaluation, and Exit Control",
        "pillar": "pillar_regulatory_governance",
    },
    {
        "domain_id": "domain_security_governance_compliance",
        "label": "Security, Governance, Authority, and Compliance",
        "pillar": "pillar_regulatory_governance",
    },
    {
        "domain_id": "domain_replay_observability_audit",
        "label": "Replay, Observability, Audit, and Proof",
        "pillar": "pillar_regulatory_governance",
    },
    {
        "domain_id": "domain_learning_calibration",
        "label": "Learning, Calibration, and Future-Run Improvement",
        "pillar": "pillar_agentic_ai_platforms",
    },
    {
        "domain_id": "domain_hitl_escalation",
        "label": "Human-in-the-Loop and Escalation Design",
        "pillar": "pillar_regulatory_governance",
    },
    {
        "domain_id": "domain_productization_enterprise_adoption",
        "label": "Productization, Reuse, and Enterprise Adoption",
        "pillar": "pillar_revenue_commercialization",
    },
]

CAREER_EPOCHS: list[dict[str, Any]] = [
    {
        "node_id": "epoch_actuarial_financial_engineering",
        "label": "Actuarial & Financial Engineering",
        "pillars": ["pillar_actuarial_foundation", "pillar_derivatives_structured", "pillar_greeks_hedging", "pillar_capital_modeling", "pillar_risk_management"],
    },
    {
        "node_id": "epoch_enterprise_risk_governance",
        "label": "Enterprise Risk & Governance",
        "pillars": ["pillar_regulatory_governance", "pillar_enterprise_risk_controls", "pillar_risk_management"],
    },
    {
        "node_id": "epoch_cloud_data_platform_engineering",
        "label": "Cloud & Data Platform Engineering",
        "pillars": ["pillar_cloud_data_aws"],
    },
    {
        "node_id": "epoch_ai_platform_commercialization",
        "label": "AI Platform Commercialization",
        "pillars": ["pillar_revenue_commercialization", "pillar_executive_leadership"],
    },
    {
        "node_id": "epoch_agentic_ai_runtime_architecture",
        "label": "Agentic AI Runtime Architecture",
        "pillars": ["pillar_agentic_ai_platforms"],
        "capability_domain_ids": [d["domain_id"] for d in AGENTIC_CAPABILITY_DOMAINS],
    },
    {
        "node_id": "epoch_partner_gtm_revenue_leadership",
        "label": "Partner GTM & Revenue Leadership",
        "pillars": [
            "pillar_partner_gtm_alliances",
            "pillar_cosell_partner_engineering",
            "pillar_presales_solutioning",
            "pillar_cloud_data_aws",
            "pillar_revenue_commercialization",
            "pillar_customer_stakeholder",
        ],
    },
]

IDENTITY_NODE: dict[str, Any] = {
    "node_id": "identity_amit_ayer_governed_ai_platform_leader",
    "node_type": "identity_north_star",
    "label": "Amit Ayer — Governed AI Platform Leader",
    "description": (
        "Governed AI platform and agentic runtime engineering leader with actuarial, derivatives, "
        "risk, governance, AWS/cloud, partner GTM, revenue, and commercialization depth."
    ),
    "epoch_ids": [e["node_id"] for e in CAREER_EPOCHS],
}

# skill_id, capability label, source_concepts, snippet, fact_id_links (optional), repo files
_AGENTIC_ROW_TEMPLATE: list[tuple[str, str, list[str], str, list[str], list[str]]] = [
    # Domain 1
    ("skill_governed_agentic_systems_architecture", "Governed agentic systems architecture", ["GovernedAgenticRuntime", "L2ProposeL3Execute", "SpineContracts"], "Designed governed agentic AI platform capabilities with deterministic routing, orchestration, and policy gating.", ["fact_engineering_platform_001"], ["AGENTS.md", "docs/architecture/adr/"]),
    ("skill_layered_runtime_spine_design", "Layered runtime spine design", ["L0L6Spine", "LayerGravity", "ProfileResolver"], "Layered L0–L6 spine: L2 proposes, Exit clears, UWG commits, L4 stores, L6 learns after run boundary.", ["fact_engineering_platform_001"], [".cursor/rules/000-agentic-core-operating-contract.mdc"]),
    ("skill_agentic_control_plane_design", "Agentic control plane design", ["RoutePolicyInterpreter", "GateMesh", "ExitEnforcer"], "Control-plane routing, GateMesh enforcement, and Exit profile enforcer for generic runtime infrastructure.", ["fact_engineering_platform_001"], ["agentic_core/AGENTS.md"]),
    ("skill_app_overlay_runtime_binding", "App overlay runtime binding", ["U0RuntimeCustomization", "apps_rgOverlay"], "App-specific behavior in apps_* overlays via U0 runtime_customization_package; core stays generic.", ["fact_engineering_platform_001"], ["apps_rg/AGENTS.md"]),
    ("skill_reusable_agentic_platform_architecture", "Reusable agentic platform architecture", ["PlatformReuse", "EnterpriseAdoption"], "Reusable agentic platform patterns for regulated enterprise workflows and auditability.", ["fact_engineering_platform_004"], ["apps_rg/runtime/"]),
    # Domain 2
    ("skill_intent_interpretation_and_ambiguity_framing", "Intent interpretation and ambiguity framing", ["IntentFrame", "AmbiguityHITL"], "Frame ambiguous intents with bounded planning contracts before execution.", [], ["agentic_core/L2_execution/"]),
    ("skill_bounded_planning_contracts", "Bounded planning contracts", ["SRPlan", "PlanFirstExecuteSecond"], "Plan-first execute-second with explicit SR_INTAKE/SR_PLAN approval before edits on T2/T3 work.", [], [".cursor/rules/sequential-thinking-enforcement.mdc"]),
    ("skill_lowest_viable_agency_design", "Lowest viable agency design", ["LowestViableAgency", "BoundedAutonomy"], "Lowest-viable-agency design: agents propose; gates and humans authorize durable effects.", [], ["AGENTS.md"]),
    ("skill_task_decomposition_for_agentic_workflows", "Task decomposition for agentic workflows", ["TaskDecomposition", "WorkflowSteps"], "Decompose complex tasks into bounded steps with separate reasoning, routing, execution, verification.", [], ["agentic_core/"]),
    ("skill_planning_prior_and_policy_context_use", "Planning prior and policy context use", ["PolicyContext", "PrecedentLookup"], "Use policy context and precedent lookup before high-leverage decisions.", [], [".cursor/skills/refactor-decision-memory/"]),
    # Domain 3
    ("skill_deterministic_route_selection", "Deterministic route selection", ["L0RouteContract", "G07RoutePolicy"], "Deterministic route selection via L0 route contract; no JD/briefing as proof.", ["fact_engineering_platform_001"], ["apps_rg/runtime/orchestration/"]),
    ("skill_route_contract_design", "Route contract design", ["RouteContract", "CanonicalDispatch"], "Route contract design for canonical dispatch and profile-resolved lanes.", ["fact_engineering_platform_001"], ["apps_rg/runtime/orchestration/canonical_dispatch.py"]),
    ("skill_cache_fallback_grounded_action_routing", "Cache fallback grounded action routing", ["CacheFallback", "GroundedRouting"], "Cache-aware fallback routing grounded in approved facts, not free-text targeting.", ["fact_engineering_platform_003"], ["apps_rg/runtime/"]),
    ("skill_risk_and_hitl_route_posture", "Risk and HITL route posture", ["HITLRoute", "RiskPosture"], "Risk-weighted routing posture with HITL escalation on high-stakes paths.", ["fact_governance_003"], ["apps_rg/runtime/"]),
    ("skill_route_replay_and_idempotency_design", "Route replay and idempotency design", ["ReplayKey", "IdempotentRoute"], "Replayable routes with idempotency keys for audit reconstruction.", ["fact_engineering_platform_001"], ["apps_rg/runtime/proof_pool_resolver.py"]),
    # Domain 4
    ("skill_managed_workflow_orchestration", "Managed workflow orchestration", ["ManagedWorkflow", "MultiAgentOrchestration"], "Multi-agent orchestration with managed workflow joins and checkpoints.", ["fact_engineering_platform_001"], ["apps_rg/runtime/orchestration/"]),
    ("skill_dependency_and_join_control", "Dependency and join control", ["JoinControl", "DependencyGraph"], "Dependency join control using software dependency graph intelligence.", ["fact_engineering_platform_002"], ["artifacts/adg/"]),
    ("skill_bounded_fanout_and_retry_design", "Bounded fanout and retry design", ["BoundedFanout", "RetryPolicy"], "Bounded fan-out and retry policies with thrash guards.", ["fact_engineering_platform_003"], ["apps_rg/runtime/"]),
    ("skill_workflow_checkpointing_and_resumability", "Workflow checkpointing and resumability", ["Checkpoint", "ResumableWorkflow"], "Checkpointed workflows supporting resumability after failure.", [], ["agentic_core/"]),
    ("skill_multi_step_quality_loop_design", "Multi-step quality loop design", ["QualityLoop", "X1X2X3"], "Multi-step quality loops: L2 propose → X2 gates → X1D judges → X3 disposition.", ["fact_engineering_platform_003"], ["apps_rg/runtime/validators/"]),
    # Domain 5
    ("skill_context_engineering", "Context engineering", ["C0ContextEngineering", "FinalEvidenceContract", "G08G09"], "Context engineering with FinalEvidenceContract and dense/sparse retrieval boundaries.", ["fact_engineering_platform_003"], ["apps_rg/runtime/dispatch/input_authority_prompt_block.py"]),
    ("skill_dense_sparse_exact_retrieval_design", "Dense sparse exact retrieval design", ["GraphRAG", "DenseSparseRetrieval"], "GraphRAG and dense/sparse retrieval design for evidence grounding.", ["fact_engineering_platform_001"], ["apps_rg/"]),
    ("skill_metadata_acl_freshness_filtering", "Metadata ACL freshness filtering", ["ACLFreshness", "MetadataFilter"], "Metadata ACL and freshness filtering before context assembly.", ["fact_governance_003"], ["apps_rg/runtime/"]),
    ("skill_evidence_contract_design", "Evidence contract design", ["EvidenceContract", "ProofPool"], "Evidence contracts tying prompts to allowed fact_id proof pools only.", ["fact_governance_001"], ["apps_rg/runtime/proof_pool_resolver.py"]),
    ("skill_graph_aware_relationship_grounding", "Graph aware relationship grounding", ["ADGGraph", "DependencyGrounding"], "Graph-aware grounding via ADG structural queries for blast radius and deps.", ["fact_engineering_platform_002"], ["artifacts/adg/"]),
    ("skill_contradiction_and_lineage_handling", "Contradiction and lineage handling", ["Lineage", "ContradictionCheck"], "Contradiction and lineage handling across archive variants and ledger rows.", ["fact_governance_002"], ["apps_rg/fact_inventory/"]),
    # Domain 6
    ("skill_prompt_assembly_architecture", "Prompt assembly architecture", ["PromptAssembly", "SectionPromptAdapter"], "Section prompt adapter architecture with slot-based template compilation.", ["fact_engineering_platform_003"], ["apps_rg/runtime/dispatch/executive_summary_pa.py"]),
    ("skill_instruction_data_boundary_design", "Instruction data boundary design", ["InstructionDataBoundary", "AuthorityBlock"], "Strict instruction vs data boundaries; JD/briefing targeting-only.", ["fact_governance_003"], ["apps_rg/runtime/dispatch/input_authority_prompt_block.py"]),
    ("skill_authority_ordered_prompt_packaging", "Authority ordered prompt packaging", ["AuthorityOrder", "C0Appendix"], "Authority-ordered prompt packaging with SRFS appendix and allowed_source_fact_ids.", ["fact_engineering_platform_001"], ["apps_rg/runtime/dispatch/executive_summary_pa.py"]),
    ("skill_schema_bound_generation", "Schema bound generation", ["SchemaBoundOutput", "JSONSchema"], "Schema-bound generation with parse/repair gates on structured outputs.", ["fact_engineering_platform_003"], ["apps_rg/runtime/"]),
    ("skill_prompt_injection_airlock_design", "Prompt injection airlock design", ["PromptInjectionAirlock", "UntrustedInput"], "Airlock design separating untrusted targeting text from proof-bearing data blocks.", ["fact_governance_001"], ["apps_rg/runtime/dispatch/"]),
    # Domain 7
    ("skill_bounded_agent_execution", "Bounded agent execution", ["BoundedExecution", "L2Executor"], "Bounded L2 execution without direct durable writes from tools or Exit.", ["fact_engineering_platform_001"], ["AGENTS.md"]),
    ("skill_tool_and_model_registry_control", "Tool and model registry control", ["ToolRegistry", "ModelRegistry"], "Tool and model registry control with explicit provider resolution.", [], ["apps_rg/runtime/"]),
    ("skill_sandboxed_execution_design", "Sandboxed execution design", ["SandboxedExecution", "SideEffectBounds"], "Sandboxed execution with side-effect bounds and egress controls.", ["fact_engineering_platform_001"], ["apps_rg/runtime/"]),
    ("skill_external_egress_control", "External egress control", ["EgressControl", "ProviderGovernance"], "External egress control for provider calls and artifact writes.", ["fact_governance_004"], ["apps_rg/runtime/"]),
    ("skill_side_effect_bounded_action_design", "Side effect bounded action design", ["SideEffectBounds", "NoDirectWrite"], "Side-effect-bounded actions; no direct UWG/L4 write path from L2/L3/tools.", ["fact_engineering_platform_001"], [".cursor/rules/000-agentic-core-operating-contract.mdc"]),
    ("skill_no_direct_write_runtime_design", "No direct write runtime design", ["UWGWriteLaw", "L4Sovereignty"], "UWG/L4 write sovereignty: L2 proposes; Exit clears; no bypass durable writes.", ["fact_governance_003"], ["AGENTS.md"]),
    # Domain 8
    ("skill_same_authority_runtime_repair", "Same authority runtime repair", ["SameAuthorityRepair", "HealingChain"], "Same-authority runtime repair without cross-layer privilege escalation.", [], ["agentic_core/L2_execution/healers/"]),
    ("skill_retry_and_thrash_guard_design", "Retry and thrash guard design", ["RetryGuard", "ThrashPrevention"], "Retry and thrash guards on provider and gate failures.", ["fact_engineering_platform_003"], ["apps_rg/runtime/"]),
    ("skill_schema_and_output_repair", "Schema and output repair", ["OutputRepair", "SchemaRepair"], "Deterministic schema and output repair before re-judging.", [], ["apps_rg/runtime/sections/"]),
    ("skill_deterministic_trim_and_reformat", "Deterministic trim and reformat", ["DeterministicTrim", "Reformat"], "Deterministic trim/reformat for judge-safe narrative shape.", [], ["apps_rg/runtime/sections/exec_summary_srfs_judge_safe.py"]),
    ("skill_runtime_resilience_controls", "Runtime resilience controls", ["ResilienceControls", "FailClosed"], "Fail-closed resilience controls when providers or gates are unavailable.", ["fact_engineering_platform_003"], ["apps_rg/runtime/"]),
    # Domain 9
    ("skill_runtime_gate_mesh_design", "Runtime gate mesh design", ["GateMesh", "00CRuntimeGates"], "Runtime GateMesh with 00C gate semantics and GateVerdict contracts.", ["fact_governance_003"], ["apps_rg/runtime/validators/"]),
    ("skill_fail_closed_gate_semantics", "Fail closed gate semantics", ["FailClosed", "UNKNOWNNotPass"], "Fail-closed gate semantics: UNKNOWN is never PASS.", ["fact_governance_003"], ["AGENTS.md"]),
    ("skill_output_quality_and_schema_gates", "Output quality and schema gates", ["X2Gates", "SchemaGates"], "X2 output quality and schema gates on structured resume sections.", ["fact_engineering_platform_003"], ["apps_rg/runtime/validators/executive_summary_x2.py"]),
    ("skill_x1_x2_x3_exit_control", "X1 X2 X3 exit control", ["X1DJudge", "X2Gate", "X3Disposition"], "X1D judges assess; X2 enforces; X3 aggregates exactly one disposition.", ["fact_governance_003"], ["apps_rg/runtime/exit/executive_summary_x3.py"]),
    ("skill_llm_judge_packet_design", "LLM judge packet design", ["JudgePacket", "GradeOnlyJudge"], "LLM judge packet design with grade-only rubrics and allowed_fact_packet.", ["fact_governance_001"], ["apps_rg/runtime/judges/executive_summary_judge_packet.py"]),
    ("skill_multi_judge_calibration", "Multi judge calibration", ["MultiJudge", "Calibration"], "Multi-judge calibration across providers with soft-fail vs block semantics.", [], ["apps_rg/runtime/judges/"]),
    ("skill_exit_disposition_governance", "Exit disposition governance", ["ExitDisposition", "X3Aggregate"], "Exit disposition governance with single authoritative X3 outcome.", ["fact_governance_003"], ["apps_rg/runtime/exit/"]),
    # Domain 10
    ("skill_ai_governance_certification", "AI governance certification", ["L5CertificationPacket", "L5GovernanceContext"], "L5 governance certification packets and Fort Knox evidence discipline.", ["fact_governance_001"], ["artifacts/certification/"]),
    ("skill_authority_and_registry_binding", "Authority and registry binding", ["AuthorityBinding", "ProfileRegistry"], "Authority and registry binding via generic profile resolver.", ["fact_governance_002"], ["agentic_core/"]),
    ("skill_policy_bound_runtime_design", "Policy bound runtime design", ["PolicyBoundRuntime", "ConstitutionalRules"], "Policy-bound runtime aligned with constitutional rules and apps overlays.", ["fact_governance_003"], [".cursor/rules/constitutional.mdc"]),
    ("skill_origin_trust_and_content_boundary", "Origin trust and content boundary", ["OriginTrust", "ContentBoundary"], "Origin trust boundaries between base resume, ledger facts, and targeting text.", ["fact_governance_001"], ["apps_rg/fact_inventory/"]),
    ("skill_provider_and_egress_governance", "Provider and egress governance", ["ProviderGovernance", "EgressPolicy"], "Provider and egress governance for live vs mock generation paths.", ["fact_governance_004"], ["apps_rg/runtime/"]),
    ("skill_human_review_reclearance_controls", "Human review reclearance controls", ["HumanReview", "Reclearance"], "Human review and reclearance controls for MEDIUM confidence ledger rows.", ["fact_governance_002"], ["apps_rg/fact_inventory/selected_role_fact_set.py"]),
    ("skill_static_governance_drift_detection", "Static governance drift detection", ["GovernanceDrift", "ADGAudit"], "Static governance drift detection via ADG violations and CI gates.", ["fact_governance_003"], ["artifacts/adg/"]),
    # Domain 11
    ("skill_replayable_runtime_design", "Replayable runtime design", ["ReplayKey", "AuditManifestRef", "RuntimeProofBundle"], "Replayable runtime design with replay_key and RuntimeProofBundle artifacts.", ["fact_engineering_platform_001"], ["artifacts/apps_rg/runtime_proofs/"]),
    ("skill_audit_grade_observability", "Audit grade observability", ["OTelTraces", "AuditGradeObservability"], "Audit-grade observability with OTel traces and runtime ADG ingest.", ["fact_engineering_platform_003"], ["tools/mcp/"]),
    ("skill_receipt_and_artifact_chain_design", "Receipt and artifact chain design", ["ReceiptChain", "ArtifactProvenance"], "Receipt and artifact chain design with provenance discipline.", ["fact_governance_001"], [".cursor/rules/artifact-provenance-discipline.mdc"]),
    ("skill_no_bypass_proof_controls", "No bypass proof controls", ["NoBypassProof", "ProofContract"], "No-bypass proof controls: markers and narratives are not proof.", ["fact_governance_003"], [".cursor/rules/002-pass-blocked-proof-contract.mdc"]),
    ("skill_runtime_proof_bundle_design", "Runtime proof bundle design", ["RuntimeProofBundle", "RUN_BUNDLE_INDEX"], "Runtime proof bundle design with RUN_BUNDLE_INDEX and gate receipts.", ["fact_engineering_platform_004"], ["artifacts/apps_rg/runtime_proofs/"]),
    ("skill_trace_and_reconstruction_design", "Trace and reconstruction design", ["TraceReconstruction", "SpanAnalysis"], "Trace reconstruction for per-agent span analysis and healing chains.", [], ["agentic_core/L6_observability/"]),
    # Domain 12
    ("skill_shadow_learning_design", "Shadow learning design", ["L6Shadow", "NoCurrentRunRescue"], "L6 shadow learning after completed-run boundary; no current-run rescue.", [], ["apps_rg/runtime/shadow/"]),
    ("skill_completed_run_evaluation", "Completed run evaluation", ["CompletedRunEval", "L6Consumer"], "Completed-run evaluation consumer; L6 learns only after boundary.", [], ["AGENTS.md"]),
    ("skill_future_run_calibration", "Future run calibration", ["FutureRunCalibration", "L6Proposals"], "Future-run calibration proposals from shadow eval packages.", [], ["apps_rg/runtime/shadow/"]),
    ("skill_eval_regression_and_gauntlet_design", "Eval regression and gauntlet design", ["EvalRegression", "Gauntlet"], "Eval regression gauntlets for gate and judge threshold preservation.", [], ["tests/_apps_contract/"]),
    ("skill_learning_firewall_controls", "Learning firewall controls", ["LearningFirewall", "PromotionGate"], "Learning firewall: promotion gates block weakening X2/X3/judges.", ["fact_governance_003"], [".cursor/rules/evaluation-promotion-gate.mdc"]),
    # Domain 13
    ("skill_hitl_escalation_architecture", "HITL escalation architecture", ["HITLEscalation", "AuthorGate"], "HITL escalation via Author-Gate packets and ask_user_question discipline.", ["fact_governance_002"], [".cursor/rules/003-cursor-author-gate-hitl.mdc"]),
    ("skill_approval_gated_workflow_design", "Approval gated workflow design", ["ApprovalGated", "WaveLifecycle"], "Approval-gated workflows with wave lifecycle markers and human confirmation.", ["fact_governance_003"], [".cursor/rules/wave-completion-discipline.mdc"]),
    ("skill_human_review_freeze_and_resume", "Human review freeze and resume", ["ReviewFreeze", "ResumeAfterConfirm"], "Human review freeze/resume for MEDIUM facts before external use.", ["fact_governance_002"], ["apps_rg/fact_inventory/"]),
    ("skill_agent_to_human_handoff_design", "Agent to human handoff design", ["AgentHumanHandoff", "EscalationDesign"], "Agent-to-human handoff design on confidence and policy triggers.", ["fact_governance_003"], ["apps_rg/runtime/"]),
    ("skill_confidence_based_escalation", "Confidence based escalation", ["ConfidenceEscalation", "NEEDS_VERIFICATION"], "Confidence-based escalation for NEEDS_VERIFICATION and MEDIUM rows.", ["fact_governance_002"], ["apps_rg/fact_inventory/candidate_fact_ledger.py"]),
    # Domain 14
    ("skill_agentic_platform_productization", "Agentic platform productization", ["PlatformProductization", "EnterpriseAdoption"], "Agentic platform productization for enterprise regulated workflows.", ["fact_engineering_platform_004"], ["apps_rg/"]),
    ("skill_reusable_ai_ip_design", "Reusable AI IP design", ["ReusableAIIP", "OverlayDesign"], "Reusable AI IP via app overlays and generic core engines.", ["fact_engineering_platform_001"], ["apps_rg/AGENTS.md"]),
    ("skill_app_specific_runtime_overlay_design", "App specific runtime overlay design", ["apps_rgOverlay", "U0Package"], "apps_rg runtime overlay design without agentic_core leakage.", ["fact_engineering_platform_001"], ["apps_rg/"]),
    ("skill_enterprise_workflow_adoption", "Enterprise workflow adoption", ["EnterpriseAdoption", "OperatingModel"], "Enterprise workflow adoption with auditability and stakeholder alignment.", ["fact_exec_002"], ["apps_rg/runtime/"]),
    ("skill_operating_model_for_agentic_ai", "Operating model for agentic AI", ["OperatingModel", "GovernedDelivery"], "Operating model for governed agentic AI delivery at scale.", ["fact_exec_001"], ["apps_rg/"]),
    ("skill_ai_platform_commercialization", "AI platform commercialization", ["Commercialization", "RevenueStreams"], "AI platform commercialization and revenue stream expansion.", ["fact_exec_002", "fact_engineering_platform_004"], ["apps_rg/"]),
]

_DOMAIN_SLICES: list[tuple[str, slice]] = [
    ("domain_agentic_systems_architecture", slice(0, 5)),
    ("domain_reasoning_planning_decomposition", slice(5, 10)),
    ("domain_routing_triage_workflow", slice(10, 15)),
    ("domain_orchestration_managed_workflows", slice(15, 20)),
    ("domain_context_engineering_grounding", slice(20, 26)),
    ("domain_prompt_assembly_boundaries", slice(26, 31)),
    ("domain_execution_tool_sandbox", slice(31, 37)),
    ("domain_healing_retry_resilience", slice(37, 42)),
    ("domain_runtime_gates_exit", slice(42, 49)),
    ("domain_security_governance_compliance", slice(49, 56)),
    ("domain_replay_observability_audit", slice(56, 62)),
    ("domain_learning_calibration", slice(62, 67)),
    ("domain_hitl_escalation", slice(67, 72)),
    ("domain_productization_enterprise_adoption", slice(72, 78)),
]

_SKILL_TO_DOMAIN: dict[str, str] = {}
for domain_id, sl in _DOMAIN_SLICES:
    for tpl in _AGENTIC_ROW_TEMPLATE[sl]:
        _SKILL_TO_DOMAIN[tpl[0]] = domain_id

EXTERNAL_CLAIM_POLICIES: dict[str, dict[str, str]] = {
    "atomic_fact_default_external_proof": {
        "description": "Atomic candidate_fact_id rows are the default external proof layer.",
        "enforcement": "claim_ledger_fact_id_only",
    },
    "skill_projection_not_proof": {
        "description": "skill_id may rank and project but never becomes source_fact_id.",
        "enforcement": "reject_skill_id_in_claim_ledger",
    },
    "repo_evidence_portfolio_not_resume_default": {
        "description": "Repo-evidence skills are portfolio-eligible by default, not resume proof.",
        "enforcement": "block_external_unless_active_confirmed_fact",
    },
    "pending_source_internal_only": {
        "description": "USER_CONFIRMED_PENDING_SOURCE rows are internal until confirmed.",
        "enforcement": "block_external_pending_source",
    },
    "jd_briefing_targeting_only": {
        "description": "JD and briefing are targeting-only, never proof.",
        "enforcement": "reject_jd_briefing_fact_ids",
    },
    "derived_supported_requires_fact_links": {
        "description": "DERIVED_SUPPORTED requires fact_id_links.",
        "enforcement": "require_fact_links",
    },
    "skill_id_never_source_fact_id": {
        "description": "skill_id must not appear in claim_ledger source_fact_ids.",
        "enforcement": "reject_skill_id_prefix",
    },
    "metrics_require_metric_fact": {
        "description": "Numeric metrics require metric-bound fact_id derivatives.",
        "enforcement": "require_metric_derivative",
    },
    "ats_keywords_not_claims": {
        "description": "ATS keywords improve matching but are not standalone claims.",
        "enforcement": "ats_non_claim",
    },
    "blocked_phrase_fail_closed": {
        "description": "Forbidden phrases block external emission fail-closed.",
        "enforcement": "forbidden_phrase_block",
    },
    "weak_snippet_internal_only": {
        "description": "Rows with weak or missing snippets are internal-only.",
        "enforcement": "weak_snippet_block",
    },
    "external_resume_claim_requires_active_fact_or_confirmed_snippet": {
        "description": "External claims need active fact links or confirmed snippets.",
        "enforcement": "require_evidence",
    },
    "claim_ledger_fact_id_only": {
        "description": "Claim ledger accepts fact_id values only.",
        "enforcement": "fact_id_only",
    },
    "no_jd_briefing_source_fact_id": {
        "description": "JD/briefing cannot appear as source_fact_ids.",
        "enforcement": "reject_jd_briefing_ids",
    },
}

RESUME_GENERATION_POLICY: dict[str, Any] = {
    "l0_l9_flow": [
        "identity_north_star",
        "career_epoch",
        "domain_pillar",
        "capability_domain",
        "atomic_proof_fact",
        "skill_row",
        "role_family_projection",
        "resume_section_projection",
        "phrase_control",
        "evidence_risk_activation",
        "external_claim_policy",
        "final_output",
    ],
    "achievement_framing_default": "Use fact-backed outcomes; lead with scope, mechanism, and measurable impact when metric facts exist.",
    "quantification_default": "Numbers require metric-bound fact_id or approved metric derivative; never invent metrics.",
    "narrative_synthesis_default": "Synthesize across linked facts and approved bundles only; cite fact_id trace.",
    "zero_hallucination_default": "Fail closed when proof is missing; UNKNOWN is never PASS.",
}

GRAPH_LAYERS: list[dict[str, str]] = [
    {"layer_id": "identity_north_star", "order": "1"},
    {"layer_id": "career_epoch", "order": "2"},
    {"layer_id": "domain_pillar", "order": "3"},
    {"layer_id": "capability_domain", "order": "4"},
    {"layer_id": "capability", "order": "5"},
    {"layer_id": "atomic_proof_fact", "order": "6"},
    {"layer_id": "skill_row", "order": "7"},
    {"layer_id": "role_family_projection", "order": "8"},
    {"layer_id": "resume_section_projection", "order": "9"},
    {"layer_id": "phrase_control", "order": "10"},
    {"layer_id": "evidence_risk_activation", "order": "11"},
    {"layer_id": "external_claim_policy", "order": "12"},
]
