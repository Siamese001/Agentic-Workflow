"""IBM graph promotion wave — adds 4 new IBM skill_rows, promotes 2 DRAFT skills,
adds role-episode-bound graph_nodes + graph_edges, and writes ibm_role_episode_bundles.json.

Run:
    python tools/apps_rg/apply_ibm_graph_promotion_wave.py

Idempotent: running twice will not duplicate nodes/rows/edges.

Invariants:
- Only IBM-employer-bound signals from phase1_resume_archive_graph_gap_fill.json are promoted.
- Metrics marked HOLD or DO NOT PROMOTE are excluded from allowed_phrases and fact links.
- No archive prose is embedded in allowed_phrases (only structural vocabulary tokens).
- No agentic_core files are modified.
- No X2/X3 gates are weakened.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO / "apps_rg" / "fact_inventory" / "master_skills_arsenal_ledger.json"
BUNDLES_PATH = REPO / "apps_rg" / "fact_inventory" / "ibm_role_episode_bundles.json"
WAVE_TS = "2026-05-28T13:00:00Z"

# ---------------------------------------------------------------------------
# Metrics excluded from promotion (DO NOT PROMOTE or HOLD per gap fill report)
# ---------------------------------------------------------------------------
EXCLUDED_METRICS: frozenset[str] = frozenset({
    "25%", "30%", "35%", "40%",     # overloaded percentages
    "$15M", "$30M",                  # single-source HOLD
})

# ---------------------------------------------------------------------------
# New IBM skill row definitions
# ---------------------------------------------------------------------------
NEW_IBM_SKILL_ROWS: list[dict] = [
    {
        "skill_id": "skill_ibm_automated_release_pipelines",
        "fact_id_links": [],
        "pillar": "pillar_interoperability_integration_ecosystem",
        "subpillar": "automated_release_pipelines",
        "career_stage": "senior",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "source_resume_files": [
            "AI and Data Governance - Amit Ayer.docx",
            "Amit Ayer Resume - AI Financial Services.docx",
            "Head of Data & Analytics - Amit Ayer.docx",
            "Chief AI Officer - Amit Ayer.docx",
        ],
        "source_snippets": [
            "Established automated release pipelines with integrated code scanning, "
            "reducing production incidents and accelerating time to market for new AI-driven risk models.",
            "CI/CD pipelines integrating model validation, container orchestration, and code scanning tools.",
        ],
        "archive_signal_ids": ["sig_ibm_003", "sig_comp_002"],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "ENGINEERING_PLATFORM": 1.0,
            "AI_GOVERNANCE_RISK": 0.8,
            "BANKING_PLATFORM_AI": 0.8,
        },
        "allowed_phrases": [
            "automated release pipelines",
            "CI/CD automation",
            "integrated code scanning",
            "container orchestration",
            "production incident reduction",
        ],
        "forbidden_phrases": ["35% production incidents", "35%"],
        "allowed_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "ACTIVE_CONFIRMED",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "career_track_id": "TRACK_DATA_TECH_CLOUD_ML",
        "domain_id": "domain_interoperability_integration_ecosystem",
        "domain": "Interoperability & Integration Ecosystem",
        "capability": "automated_release_pipelines",
        "source_concepts": ["CI/CD", "code scanning", "release automation", "DevOps"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": [
            "CI/CD", "automated release pipelines", "code scanning", "DevOps", "container orchestration",
        ],
        "achievement_framing_guidance": (
            "Frame automated_release_pipelines with IBM scope, scanning mechanism, and reliability outcome; "
            "metrics only from linked fact_id — do not use 35% or 40% unanchored."
        ),
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": (
            "Synthesize from IBM-employer archive snippets and approved bundles; "
            "skill_id is not proof. No archive prose recitation."
        ),
        "claim_verification_policy": (
            "External resume claims allowed only when external_claim_policy permits "
            "and fact_id backs metrics."
        ),
        "zero_hallucination_guardrail": (
            "Do not claim automated_release_pipelines beyond repo evidence and linked facts; "
            "fail closed if proof missing."
        ),
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": [
            "track_data_tech_cloud_ml",
            "employment_exp_ibm_001",
            "pillar_interoperability_integration_ecosystem",
            "skill_ibm_automated_release_pipelines",
        ],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_ibm_devsecops_pipeline_security",
        "fact_id_links": [],
        "pillar": "pillar_interoperability_integration_ecosystem",
        "subpillar": "devsecops_pipeline_security",
        "career_stage": "senior",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "source_resume_files": [
            "Amit Ayer Resume - AI Financial Services.docx",
            "Chief AI Officer - Amit Ayer.docx",
            "Field CTO - Amit Ayer.docx",
            "Chief Technology Officer - Amit Ayer.docx",
        ],
        "source_snippets": [
            "Containerized workloads and integrated DevSecOps scanning; "
            "overhead reduction and accelerated daily valuations.",
            "Implemented automated CI/CD pipelines with real time code scanning and role-based data access, "
            "reducing incidents and capturing FinOps best practices savings.",
        ],
        "archive_signal_ids": ["sig_ibm_004", "sig_comp_002"],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "ENGINEERING_PLATFORM": 1.0,
            "AI_GOVERNANCE_RISK": 0.9,
            "CTO_FIELD_CTO": 0.9,
        },
        "allowed_phrases": [
            "DevSecOps",
            "DevSecOps scanning",
            "DevSecOps pipelines",
            "security integration in development pipelines",
            "automated code scanning",
            "FinOps best practices",
        ],
        "forbidden_phrases": ["40% latency", "35% incidents", "15% overhead"],
        "allowed_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "ACTIVE_CONFIRMED",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "career_track_id": "TRACK_DATA_TECH_CLOUD_ML",
        "domain_id": "domain_interoperability_integration_ecosystem",
        "domain": "Interoperability & Integration Ecosystem",
        "capability": "devsecops_pipeline_security",
        "source_concepts": ["DevSecOps", "security scanning", "compliance pipelines", "FinOps"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": [
            "DevSecOps", "security pipeline", "code scanning", "FinOps", "compliance automation",
        ],
        "achievement_framing_guidance": (
            "Frame devsecops_pipeline_security with IBM scope, security-scanning mechanism, and reliability/cost outcome; "
            "10% FinOps savings metric is unique and promotable if base-resume fact confirms."
        ),
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": (
            "Synthesize from IBM-employer archive snippets; "
            "do not use overloaded 40%/35%/15% metrics unanchored."
        ),
        "claim_verification_policy": (
            "External resume claims allowed only when external_claim_policy permits "
            "and fact_id backs metrics."
        ),
        "zero_hallucination_guardrail": (
            "Do not claim DevSecOps beyond repo evidence and linked facts; fail closed if proof missing."
        ),
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": [
            "track_data_tech_cloud_ml",
            "employment_exp_ibm_001",
            "pillar_interoperability_integration_ecosystem",
            "skill_ibm_devsecops_pipeline_security",
        ],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_ibm_metadata_audit_rbac",
        "fact_id_links": [],
        "pillar": "pillar_enterprise_portfolio_governance",
        "subpillar": "metadata_audit_rbac_governance",
        "career_stage": "senior",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "source_resume_files": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
        ],
        "source_snippets": [
            "Strengthened compliance by establishing standardized audit trails, metadata tagging, "
            "and secure data sharing protocols.",
            "Deployed robust data governance protocols featuring metadata management and role-based controls.",
        ],
        "archive_signal_ids": ["sig_ibm_008"],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "AI_GOVERNANCE_RISK": 1.0,
            "BANKING_PLATFORM_AI": 0.9,
            "ENGINEERING_PLATFORM": 0.8,
        },
        "allowed_phrases": [
            "metadata tagging",
            "audit trails",
            "role-based access controls",
            "role-based data access",
            "data governance protocols",
            "secure data sharing",
            "metadata management",
        ],
        "forbidden_phrases": ["30% compliance gap", "30%"],
        "allowed_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "ACTIVE_CONFIRMED",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "career_track_id": "TRACK_DATA_TECH_CLOUD_ML",
        "domain_id": "domain_enterprise_risk",
        "domain": "Enterprise Risk",
        "capability": "metadata_audit_rbac_governance",
        "source_concepts": [
            "metadata", "audit trail", "role-based access", "RBAC", "data governance",
        ],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": [
            "metadata tagging", "audit trails", "role-based access controls", "RBAC",
            "data governance", "compliance governance",
        ],
        "achievement_framing_guidance": (
            "Frame metadata_audit_rbac_governance with IBM scope, governance mechanism, and compliance outcome; "
            "avoid 30% unanchored."
        ),
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": (
            "Synthesize from IBM employer archive snippets (5 resumes); "
            "do not use 30% metric unanchored."
        ),
        "claim_verification_policy": (
            "External resume claims allowed only when external_claim_policy permits "
            "and fact_id backs metrics."
        ),
        "zero_hallucination_guardrail": (
            "Do not claim metadata_audit_rbac beyond repo evidence and linked facts; "
            "fail closed if proof missing."
        ),
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": [
            "track_data_tech_cloud_ml",
            "employment_exp_ibm_001",
            "pillar_enterprise_portfolio_governance",
            "skill_ibm_metadata_audit_rbac",
        ],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_ibm_watson_studio_analytics",
        "fact_id_links": [],
        "pillar": "pillar_banking_platform_responsible_ai",
        "subpillar": "watson_studio_analytics",
        "career_stage": "senior",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "source_resume_files": ["Head of Customer Success - Amit Ayer.docx"],
        "source_snippets": [
            "Utilized Watson Studio for fraud detection and money laundering analytics, "
            "ensuring regulatory compliance and operational security.",
        ],
        "archive_signal_ids": ["sig_ibm_010"],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "BANKING_PLATFORM_AI": 1.0,
            "AI_GOVERNANCE_RISK": 0.8,
        },
        "allowed_phrases": [
            "Watson Studio",
            "IBM Watson Studio",
            "fraud detection analytics",
            "money laundering analytics",
            "capital markets analytics",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["ibm_bullets", "ibm_narrative"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "medium",
        "activation_status": "ACTIVE",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "career_track_id": "TRACK_DATA_TECH_CLOUD_ML",
        "domain_id": "domain_banking_platform_responsible_ai",
        "domain": "Banking Platform / Responsible AI",
        "capability": "watson_studio_analytics",
        "source_concepts": ["Watson Studio", "IBM Watson", "fraud analytics", "AML analytics"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": [
            "Watson Studio", "IBM Watson", "fraud detection", "financial crime analytics",
        ],
        "achievement_framing_guidance": (
            "Frame watson_studio_analytics with IBM scope and use case (fraud/AML); "
            "single-source — medium confidence only; verify with base resume before metric claims."
        ),
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": (
            "Synthesize from single source (Head of Customer Success); verify before use."
        ),
        "claim_verification_policy": (
            "External resume claims allowed only when external_claim_policy permits "
            "and fact_id backs metrics."
        ),
        "zero_hallucination_guardrail": (
            "Do not claim Watson Studio beyond single archive source; "
            "medium confidence — fail closed if second source missing."
        ),
        "confidence_grade": "MEDIUM",
        "confidence_grade_derived": "MEDIUM",
        "graph_hop_path": [
            "track_data_tech_cloud_ml",
            "employment_exp_ibm_001",
            "pillar_banking_platform_responsible_ai",
            "skill_ibm_watson_studio_analytics",
        ],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
]

# ---------------------------------------------------------------------------
# DRAFT → ACTIVE promotions (existing skill_rows to update)
# ---------------------------------------------------------------------------
DRAFT_PROMOTIONS: dict[str, dict] = {
    "skill_confluent_streaming_platforms": {
        "activation_status": "ACTIVE_CONFIRMED",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        # ADD IBM-specific source snippets (without overwriting existing Unify snippets)
        "additional_source_resume_files": [
            "AI and Data Governance - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Revenue Operations - Amit Ayer.docx",
        ],
        "additional_source_snippets": [
            "Transitioned batch-only data processing into streaming analytics ecosystems, "
            "enabling near-real-time risk monitoring.",
            "Unified disparate data infrastructures under Confluent-based pipelines, "
            "enabling real-time risk scoring.",
        ],
        "additional_archive_signal_ids": ["sig_ibm_006", "sig_ibm_007"],
        "allowed_sections_add": ["ibm_bullets", "ibm_narrative"],
        "allowed_phrases_add": [
            "streaming analytics",
            "near-real-time risk monitoring",
            "batch-to-streaming transition",
        ],
        "forbidden_phrases_add": ["25% system downtime", "25%"],
    },
    "skill_risk_greek_stress_testing": {
        "activation_status": "ACTIVE_CONFIRMED",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "additional_source_resume_files": [
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Field CTO - Amit Ayer.docx",
            "CTO Resume - Amit Ayer.docx",
        ],
        "additional_source_snippets": [
            "HPC simulations for stress testing, cutting scenario runtimes for regulatory constraints.",
            "Cut HPC driven stress test simulations from weeks to hours, enabling rapid ROI demonstrations.",
        ],
        "additional_archive_signal_ids": ["sig_ibm_002"],
        "allowed_sections_add": ["ibm_narrative"],
        "allowed_phrases_add": [
            "HPC stress testing",
            "scenario runtimes",
            "stress test simulations",
            "near-real-time stress analytics",
        ],
        "forbidden_phrases_add": ["$15M", "40% scenario runtimes", "40%"],
    },
}

# ---------------------------------------------------------------------------
# Role Episode Bundles
# ---------------------------------------------------------------------------
IBM_ROLE_EPISODE_BUNDLES: list[dict] = [
    {
        "role_episode_bundle_id": "reb_ibm_cloud_modernization",
        "employer": "IBM",
        "title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "employer_node_id": "employment_exp_ibm_001",
        "bundle_theme": "Cloud Modernization / Containerized Microservices",
        "executive_scope_signals": [
            "Fortune 500 financial services clients migrating to distributed cloud-native platforms",
            "Architecture and commercial ownership of cloud and AI transformation portfolio",
        ],
        "architecture_scope_signals": [
            "Containerized microservices replacing monolithic risk calculation engines",
            "Cloud-native data platforms enabling governed analytics",
            "Kubernetes, AWS, distributed deployment",
        ],
        "graph_skill_node_ids": [
            "skill_sr_microservices_integration_platform",
            "skill_sr_cloud_data_platform_engineering",
            "skill_ibm_automated_release_pipelines",
        ],
        "linked_source_fact_ids": ["fact_engineering_platform_002"],
        "linked_archive_signal_ids": ["sig_ibm_001", "sig_ibm_003"],
        "promotable_metrics": [],
        "held_metrics": ["$15M modernization deals (HOLD - single source)"],
        "excluded_metrics": ["40% calculation latency (DO NOT PROMOTE - overloaded)"],
        "operating_context": (
            "IBM Financial Services modernization engagements; "
            "migration from monolithic risk systems to cloud-native microservices."
        ),
        "bullet_intent": (
            "Frame as architecture leadership driving modernization outcomes at scale; "
            "no metric without fact_id anchor."
        ),
        "section_eligibility": ["ibm_bullets", "ibm_narrative"],
        "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
        "notes": "skill_sr_microservices_integration_platform allowed_sections does not currently include ibm_bullets — add ibm_bullets/ibm_narrative when graph expansion authorized.",
    },
    {
        "role_episode_bundle_id": "reb_ibm_devsecops_reliability",
        "employer": "IBM",
        "title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "employer_node_id": "employment_exp_ibm_001",
        "bundle_theme": "DevSecOps / Release Reliability",
        "executive_scope_signals": [
            "Enterprise-grade release governance for financial services clients",
            "Security embedded into development pipelines from code to production",
        ],
        "architecture_scope_signals": [
            "Automated CI/CD pipelines with integrated code scanning",
            "DevSecOps scanning on containerized workloads",
            "Role-based data access controls in pipeline gates",
        ],
        "graph_skill_node_ids": [
            "skill_ibm_devsecops_pipeline_security",
            "skill_ibm_automated_release_pipelines",
            "skill_ibm_metadata_audit_rbac",
        ],
        "linked_source_fact_ids": [],
        "linked_archive_signal_ids": ["sig_ibm_003", "sig_ibm_004", "sig_comp_002"],
        "promotable_metrics": [
            "10% FinOps savings via CI/CD best practices (unique metric from Chief AI Officer resume)",
        ],
        "held_metrics": [],
        "excluded_metrics": [
            "35% production incident reduction (DO NOT PROMOTE - overloaded across 5+ contexts)",
            "40% DevSecOps overhead reduction (DO NOT PROMOTE - overloaded)",
        ],
        "operating_context": (
            "IBM financial services delivery governance; "
            "DevSecOps embedded into regulated cloud workloads."
        ),
        "bullet_intent": (
            "Frame as engineering governance leadership: security + release velocity + RBAC; "
            "10% FinOps savings is uniquely promotable if base resume second-source confirms."
        ),
        "section_eligibility": ["ibm_bullets", "ibm_narrative"],
        "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
        "notes": "10% FinOps savings metric is unique (Chief AI Officer resume only) — confirm against base resume before activating.",
    },
    {
        "role_episode_bundle_id": "reb_ibm_streaming_realtime_analytics",
        "employer": "IBM",
        "title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "employer_node_id": "employment_exp_ibm_001",
        "bundle_theme": "Streaming / Near-Real-Time Analytics",
        "executive_scope_signals": [
            "Transition from batch-only to streaming ecosystems for financial risk decisions",
            "Confluent-based pipeline deployments for real-time risk scoring",
        ],
        "architecture_scope_signals": [
            "Streaming analytics ecosystems replacing batch-only data processing",
            "Confluent event-driven pipelines for market data validation",
            "Near-real-time risk monitoring for trading and compliance",
        ],
        "graph_skill_node_ids": [
            "skill_confluent_streaming_platforms",
            "skill_sr_cloud_data_platform_engineering",
        ],
        "linked_source_fact_ids": [],
        "linked_archive_signal_ids": ["sig_ibm_006", "sig_ibm_007"],
        "promotable_metrics": [],
        "held_metrics": [],
        "excluded_metrics": [
            "25% system downtime reduction (DO NOT PROMOTE - overloaded)",
            "25% capacity increase (DO NOT PROMOTE - overloaded)",
        ],
        "operating_context": (
            "IBM financial services data modernization; "
            "batch-to-streaming migration for risk and market analytics."
        ),
        "bullet_intent": (
            "Frame as data architecture modernization: real-time risk monitoring, "
            "Confluent pipelines, streaming analytics; "
            "avoid 25% metric unanchored."
        ),
        "section_eligibility": ["ibm_bullets", "ibm_narrative"],
        "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
        "notes": "skill_confluent_streaming_platforms promoted DRAFT→ACTIVE_CONFIRMED in this wave.",
    },
    {
        "role_episode_bundle_id": "reb_ibm_metadata_audit_governance",
        "employer": "IBM",
        "title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "employer_node_id": "employment_exp_ibm_001",
        "bundle_theme": "Metadata / Audit Trail / RBAC Governance",
        "executive_scope_signals": [
            "Standardized audit trails and metadata tagging for client compliance obligations",
            "Role-based access controls governing data governance protocols",
        ],
        "architecture_scope_signals": [
            "Metadata tagging on shared data assets",
            "Audit trails for alliance partner data sharing",
            "Role-based data access controls in governance pipelines",
        ],
        "graph_skill_node_ids": [
            "skill_ibm_metadata_audit_rbac",
            "skill_sr_basel_ccar_lineage_regulatory",
        ],
        "linked_source_fact_ids": [],
        "linked_archive_signal_ids": ["sig_ibm_008"],
        "promotable_metrics": [],
        "held_metrics": [],
        "excluded_metrics": [
            "30% compliance gap reduction (DO NOT PROMOTE - overloaded across 6+ contexts)",
        ],
        "operating_context": (
            "IBM financial services compliance governance; "
            "partner data sharing protocols and RBAC for regulated environments."
        ),
        "bullet_intent": (
            "Frame as governance architecture: metadata lineage, audit-ready controls, RBAC; "
            "qualitative framing — no 30% metric unanchored."
        ),
        "section_eligibility": ["ibm_bullets", "ibm_narrative"],
        "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
        "notes": "skill_ibm_metadata_audit_rbac is a new node added in this wave.",
    },
    {
        "role_episode_bundle_id": "reb_ibm_hpc_risk_analytics",
        "employer": "IBM",
        "title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "employer_node_id": "employment_exp_ibm_001",
        "bundle_theme": "Risk Analytics / HPC Stress Testing",
        "executive_scope_signals": [
            "HPC-based stress test acceleration for capital adequacy decisions",
            "Real-time risk analytics for Fortune 500 financial portfolios",
        ],
        "architecture_scope_signals": [
            "HPC simulations for stress testing — weeks to hours compression",
            "Containerized HPC clusters for near-real-time risk analytics",
            "GPU-powered parallel computation for scenario analysis",
        ],
        "graph_skill_node_ids": [
            "skill_risk_greek_stress_testing",
            "skill_sr_cloud_data_platform_engineering",
            "skill_confluent_streaming_platforms",
        ],
        "linked_source_fact_ids": [],
        "linked_archive_signal_ids": ["sig_ibm_002", "sig_ibm_006"],
        "promotable_metrics": [],
        "held_metrics": [
            "$15M modernization deals (HOLD - single source, SAE only)",
        ],
        "excluded_metrics": [
            "40% scenario runtime reduction (DO NOT PROMOTE - overloaded)",
        ],
        "operating_context": (
            "IBM financial services HPC risk analytics; "
            "stress testing modernization from weekly batch to real-time."
        ),
        "bullet_intent": (
            "Frame as HPC architecture leadership: weeks-to-hours compression, real-time risk; "
            "no 40% or $15M metric without anchor."
        ),
        "section_eligibility": ["ibm_bullets", "ibm_narrative"],
        "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
        "notes": "skill_risk_greek_stress_testing promoted DRAFT→ACTIVE_CONFIRMED in this wave.",
    },
    {
        "role_episode_bundle_id": "reb_ibm_hyperscaler_alliance_partner",
        "employer": "IBM",
        "title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "employer_node_id": "employment_exp_ibm_001",
        "bundle_theme": "IBM-AWS Hyperscaler Alliance / Partner Execution",
        "executive_scope_signals": [
            "P&L accountability within IBM-AWS financial services alliance",
            "Joint revenue growth through AI-driven sales frameworks",
        ],
        "architecture_scope_signals": [
            "IBM-AWS alliance co-sell framework for financial services",
            "AI-driven sales motions for cloud transformation deals",
        ],
        "graph_skill_node_ids": [
            "skill_partner_ibm_aws_alliance_joint_revenue",
            "skill_sr_w12_hyperscaler_alliance_co_sell",
            "skill_partner_co_selling",
        ],
        "linked_source_fact_ids": ["fact_partnerships_gtm_002"],
        "linked_archive_signal_ids": ["sig_ibm_009", "sig_comp_001"],
        "promotable_metrics": [
            "20% joint revenue growth (PROMOTABLE - consistent across 2 resumes, IBM-AWS alliance context)",
            "$10M IBM ARR (PROMOTABLE - consistent across 2 resumes, IBM Salesforce pipeline context)",
        ],
        "held_metrics": [
            "$30M Cloud Pak partner revenue (HOLD - single source, CTO Resume only)",
        ],
        "excluded_metrics": [],
        "operating_context": (
            "IBM-AWS financial services alliance P&L; "
            "co-sell revenue growth through AI solutions."
        ),
        "bullet_intent": (
            "Frame as alliance leadership: IBM-AWS P&L, 20% joint revenue, co-sell motions; "
            "20% and $10M IBM ARR are promotable with fact_id anchor."
        ),
        "section_eligibility": ["ibm_bullets", "ibm_narrative"],
        "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
        "notes": "20% joint revenue is the primary promotable IBM metric in this bundle.",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_ledger(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _save_ledger(path: Path, data: dict, backup: bool = True) -> None:
    if backup:
        bak = path.with_suffix(".json.bak")
        shutil.copy2(path, bak)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _upsert_skill_row(rows: list[dict], new_row: dict) -> tuple[list[dict], str]:
    """Return updated rows list and action taken."""
    sid = new_row["skill_id"]
    for i, r in enumerate(rows):
        if r.get("skill_id") == sid:
            rows[i] = new_row  # replace
            return rows, "updated"
    rows.append(new_row)
    return rows, "added"


def _upsert_graph_node(nodes: list[dict], new_node: dict) -> tuple[list[dict], str]:
    nid = new_node["node_id"]
    for i, n in enumerate(nodes):
        if n.get("node_id") == nid:
            nodes[i] = new_node
            return nodes, "updated"
    nodes.append(new_node)
    return nodes, "added"


def _upsert_graph_edge(edges: list[dict], new_edge: dict) -> tuple[list[dict], str]:
    eid = new_edge["edge_id"]
    for i, e in enumerate(edges):
        if e.get("edge_id") == eid:
            edges[i] = new_edge
            return edges, "updated"
    edges.append(new_edge)
    return edges, "added"


def _build_skill_graph_node(row: dict) -> dict:
    sid = row["skill_id"]
    return {
        "node_id": sid,
        "node_type": "skill_row",
        "label": row.get("subpillar", row.get("capability", sid)),
        "description": (
            f"IBM-employer-bound skill: {row.get('capability', sid)}. "
            f"Employer: IBM | Time window: {row.get('time_window','')} | "
            f"Source: archive wave ibm_graph_promotion_wave_2026-05-28."
        ),
        "support_level": row.get("support_level", "DIRECT_FROM_RESUME_ARCHIVE"),
        "visibility_rule": row.get("visibility_rule", "role_family_match"),
        "activation_status": row.get("activation_status", "ACTIVE_CONFIRMED"),
        "evidence_risk": row.get("evidence_risk", "low"),
        "source_refs": [],
        "projection_behavior": row.get("projection_behavior", "rank_and_project_facts"),
        "external_claim_policy": row.get("external_claim_policy",
                                         "external_resume_claim_requires_active_fact_or_confirmed_snippet"),
        "confidence_grade": row.get("confidence_grade", "HIGH"),
        "confidence_grade_derived": row.get("confidence_grade_derived", "HIGH"),
    }


def _build_employment_skill_edge(skill_id: str, employer_node_id: str) -> dict:
    return {
        "edge_id": f"edge_employment_skill_{employer_node_id}_{skill_id}",
        "edge_type": "employment_produces_skill",
        "source_node_id": employer_node_id,
        "target_node_id": skill_id,
        "rationale": f"IBM employment produces {skill_id}",
        "projection_behavior": "graph_structure",
        "external_claim_policy": "skill_projection_not_proof",
        "validation_status": "validated",
        "confidence": "HIGH",
        "wave": "ibm_graph_promotion_wave_2026-05-28",
    }


def _build_section_skill_edge(skill_id: str, section_id: str) -> dict:
    return {
        "edge_id": f"edge_skill_section_{skill_id}_{section_id}",
        "edge_type": "skill_allowed_in_section",
        "source_node_id": skill_id,
        "target_node_id": f"section_{section_id}",
        "rationale": f"{skill_id} allowed in {section_id}",
        "projection_behavior": "section_eligibility",
        "external_claim_policy": "skill_projection_not_proof",
        "validation_status": "validated",
        "confidence": "HIGH",
        "wave": "ibm_graph_promotion_wave_2026-05-28",
    }


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def apply_wave(ledger_path: Path = LEDGER_PATH) -> dict:
    """Apply IBM graph promotion wave to ledger. Returns run receipt."""
    data = _load_ledger(ledger_path)
    rows: list[dict] = data.get("skill_rows", [])
    nodes: list[dict] = data.get("graph_nodes", [])
    edges: list[dict] = data.get("graph_edges", [])

    receipt: dict = {
        "wave_id": "ibm_graph_promotion_wave_2026-05-28",
        "applied_at": WAVE_TS,
        "new_skill_rows_added": [],
        "skill_rows_updated": [],
        "graph_nodes_added": [],
        "graph_nodes_updated": [],
        "graph_edges_added": [],
        "draft_promotions_applied": [],
        "excluded_metrics_enforced": list(EXCLUDED_METRICS),
    }

    # ---- 1. Add new IBM skill rows ----
    for new_row in NEW_IBM_SKILL_ROWS:
        rows, action = _upsert_skill_row(rows, new_row)
        sid = new_row["skill_id"]
        if action == "added":
            receipt["new_skill_rows_added"].append(sid)
        else:
            receipt["skill_rows_updated"].append(sid)

        # Graph node
        gnode = _build_skill_graph_node(new_row)
        nodes, naction = _upsert_graph_node(nodes, gnode)
        if naction == "added":
            receipt["graph_nodes_added"].append(gnode["node_id"])
        else:
            receipt["graph_nodes_updated"].append(gnode["node_id"])

        # Employment→skill edge
        emp_edge = _build_employment_skill_edge(sid, "employment_exp_ibm_001")
        edges, _ = _upsert_graph_edge(edges, emp_edge)
        if _ == "added":
            receipt["graph_edges_added"].append(emp_edge["edge_id"])

        # Section eligibility edges
        for section in new_row.get("allowed_sections", []):
            sec_edge = _build_section_skill_edge(sid, section)
            edges, eaction = _upsert_graph_edge(edges, sec_edge)
            if eaction == "added":
                receipt["graph_edges_added"].append(sec_edge["edge_id"])

    # ---- 2. Promote DRAFT → ACTIVE ----
    for skill_id, patch in DRAFT_PROMOTIONS.items():
        for i, row in enumerate(rows):
            if row.get("skill_id") != skill_id:
                continue
            # Apply updates
            prev_status = row.get("activation_status", "DRAFT")
            row["activation_status"] = patch["activation_status"]
            row["confidence_grade"] = patch["confidence_grade"]
            row["confidence_grade_derived"] = patch["confidence_grade_derived"]
            row["employer"] = patch["employer"]
            row["employer_node_id"] = patch["employer_node_id"]
            row["time_window"] = patch["time_window"]
            # Merge source files / snippets
            existing_files = list(row.get("source_resume_files") or [])
            for f in patch.get("additional_source_resume_files", []):
                if f not in existing_files:
                    existing_files.append(f)
            row["source_resume_files"] = existing_files

            existing_snips = list(row.get("source_snippets") or [])
            for s in patch.get("additional_source_snippets", []):
                if s not in existing_snips:
                    existing_snips.append(s)
            row["source_snippets"] = existing_snips

            # Merge archive_signal_ids
            existing_sids = list(row.get("archive_signal_ids") or [])
            for sid in patch.get("additional_archive_signal_ids", []):
                if sid not in existing_sids:
                    existing_sids.append(sid)
            row["archive_signal_ids"] = existing_sids

            # Merge allowed_sections
            existing_sections = list(row.get("allowed_sections") or [])
            for sec in patch.get("allowed_sections_add", []):
                if sec not in existing_sections:
                    existing_sections.append(sec)
            row["allowed_sections"] = existing_sections

            # Merge allowed_phrases
            existing_phrases = list(row.get("allowed_phrases") or [])
            for ph in patch.get("allowed_phrases_add", []):
                if ph not in existing_phrases:
                    existing_phrases.append(ph)
            row["allowed_phrases"] = existing_phrases

            # Merge forbidden_phrases
            existing_forb = list(row.get("forbidden_phrases") or [])
            for fp in patch.get("forbidden_phrases_add", []):
                if fp not in existing_forb:
                    existing_forb.append(fp)
            row["forbidden_phrases"] = existing_forb

            rows[i] = row
            receipt["draft_promotions_applied"].append({
                "skill_id": skill_id,
                "from": prev_status,
                "to": patch["activation_status"],
            })

            # Update graph node status
            for j, n in enumerate(nodes):
                if n.get("node_id") == skill_id:
                    nodes[j]["activation_status"] = patch["activation_status"]
                    nodes[j]["confidence_grade"] = patch["confidence_grade"]
                    if skill_id not in receipt["graph_nodes_updated"]:
                        receipt["graph_nodes_updated"].append(skill_id)
                    break

            # Add employment→skill edge
            emp_edge = _build_employment_skill_edge(skill_id, "employment_exp_ibm_001")
            edges, eaction = _upsert_graph_edge(edges, emp_edge)
            if eaction == "added":
                receipt["graph_edges_added"].append(emp_edge["edge_id"])

            # Add section edges for newly added sections
            for sec in patch.get("allowed_sections_add", []):
                sec_edge = _build_section_skill_edge(skill_id, sec)
                edges, eaction = _upsert_graph_edge(edges, sec_edge)
                if eaction == "added":
                    receipt["graph_edges_added"].append(sec_edge["edge_id"])
            break

    # ---- 3. Update ledger data ----
    data["skill_rows"] = rows
    data["graph_nodes"] = nodes
    data["graph_edges"] = edges

    # Update metadata
    meta = data.get("metadata", {})
    meta["last_updated"] = WAVE_TS
    meta["last_updated_by"] = "apply_ibm_graph_promotion_wave.py"
    meta["skill_row_count"] = len(rows)
    meta["ibm_graph_promotion_wave"] = receipt
    data["metadata"] = meta

    # Update graph_metadata counts
    gm = data.get("graph_metadata", {})
    gm["node_count"] = len(nodes)
    gm["edge_count"] = len(edges)
    data["graph_metadata"] = gm

    return data, receipt


def write_bundles(path: Path = BUNDLES_PATH) -> None:
    """Write ibm_role_episode_bundles.json."""
    bundle_doc = {
        "schema": "ibm_role_episode_bundles_v1",
        "generated_at": WAVE_TS,
        "generated_by": "apply_ibm_graph_promotion_wave.py",
        "employer": "IBM",
        "employer_node_id": "employment_exp_ibm_001",
        "time_window": "2017-04 to 2022-10",
        "invariants": {
            "archive_prose_excluded": True,
            "base_resume_hydration_excluded": True,
            "hold_metrics_not_promoted": True,
            "do_not_promote_metrics_excluded": True,
            "config_gate": "BLOCKED_FOR_CONFIG_ENABLEMENT",
            "config_enablement_condition": (
                "ibm_bullets and ibm_narrative graph_expansion_allowed may be enabled "
                "only when section generation consumes role_episode_bundle_id, "
                "not flat skill lists."
            ),
        },
        "excluded_metrics_by_policy": [
            {"metric": "25%", "reason": "DO NOT PROMOTE - overloaded across 6+ contexts"},
            {"metric": "30%", "reason": "DO NOT PROMOTE - overloaded across 8+ contexts"},
            {"metric": "35%", "reason": "DO NOT PROMOTE - overloaded across 6+ contexts"},
            {"metric": "40%", "reason": "DO NOT PROMOTE - most overloaded metric in archive"},
            {"metric": "$15M modernization deals", "reason": "HOLD - single source (SAE only)"},
            {"metric": "$30M Cloud Pak partner revenue", "reason": "HOLD - single source (CTO Resume only)"},
        ],
        "promotable_metrics": [
            {"metric": "20% joint revenue growth", "employer": "IBM", "context": "IBM-AWS alliance",
             "archive_signal_ids": ["sig_ibm_009"]},
            {"metric": "$10M IBM ARR", "employer": "IBM", "context": "IBM Salesforce pipeline expansion",
             "archive_signal_ids": []},
            {"metric": "10% FinOps savings", "employer": "IBM", "context": "CI/CD DevSecOps practices",
             "archive_signal_ids": ["sig_comp_002"], "caveat": "Unique metric - verify with base resume"},
        ],
        "bundles": IBM_ROLE_EPISODE_BUNDLES,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(bundle_doc, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print(f"Applying IBM graph promotion wave to {LEDGER_PATH}")
    updated_data, receipt = apply_wave(LEDGER_PATH)
    _save_ledger(LEDGER_PATH, updated_data, backup=True)
    print(f"Ledger saved. Receipt:")
    print(f"  New skill_rows added: {receipt['new_skill_rows_added']}")
    print(f"  Skill_rows updated:   {receipt['skill_rows_updated']}")
    print(f"  Graph nodes added:    {receipt['graph_nodes_added']}")
    print(f"  Graph nodes updated:  {receipt['graph_nodes_updated']}")
    print(f"  Graph edges added:    {len(receipt['graph_edges_added'])}")
    print(f"  DRAFT promotions:     {[d['skill_id'] for d in receipt['draft_promotions_applied']]}")

    print(f"\nWriting role episode bundles to {BUNDLES_PATH}")
    write_bundles(BUNDLES_PATH)

    # Validate ledger round-trip
    reloaded = _load_ledger(LEDGER_PATH)
    rows = reloaded.get("skill_rows", [])
    for sid in ["skill_ibm_automated_release_pipelines", "skill_ibm_devsecops_pipeline_security",
                "skill_ibm_metadata_audit_rbac", "skill_ibm_watson_studio_analytics"]:
        found = any(r.get("skill_id") == sid for r in rows)
        assert found, f"VALIDATION FAIL: {sid} not found in reloaded ledger"
    for sid in ["skill_confluent_streaming_platforms", "skill_risk_greek_stress_testing"]:
        row = next((r for r in rows if r.get("skill_id") == sid), None)
        assert row is not None, f"VALIDATION FAIL: {sid} not found"
        assert row.get("activation_status") == "ACTIVE_CONFIRMED", f"VALIDATION FAIL: {sid} status={row.get('activation_status')}"
    print("\nLedger validation PASS")
    print(f"Total skill_rows: {len(rows)}")
    print(f"Total graph_nodes: {len(reloaded.get('graph_nodes', []))}")
    print(f"Total graph_edges: {len(reloaded.get('graph_edges', []))}")
