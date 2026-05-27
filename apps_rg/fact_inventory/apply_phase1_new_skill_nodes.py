"""
apply_phase1_new_skill_nodes.py

Wave 2: Add 10 new skill_row nodes representing competencies found in
Phase I archived resumes but absent from master_skills_arsenal_ledger.json.

New skills:
  1.  skill_meddpicc_sales_qualification
  2.  skill_cpq_deal_velocity_automation
  3.  skill_soc2_zero_trust_security
  4.  skill_saas_arr_ltv_cac_metrics
  5.  skill_confluent_streaming_platforms
  6.  skill_watson_studio_fraud_aml
  7.  skill_algo_trading_sub_ms_inference
  8.  skill_nps_customer_health_scoring
  9.  skill_finra_sec_regulatory_compliance
  10. skill_credit_adjudication_default_risk

Run:
    python apps_rg/fact_inventory/apply_phase1_new_skill_nodes.py
    python apps_rg/fact_inventory/apply_phase1_new_skill_nodes.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "apps_rg" / "fact_inventory" / "master_skills_arsenal_ledger.json"

# ── New skill_row definitions ─────────────────────────────────────────────────

NEW_SKILL_ROWS: list[dict] = [
    {
        "skill_id": "skill_meddpicc_sales_qualification",
        "fact_id_links": [],
        "pillar": "pillar_gtm_presales_motion",
        "subpillar": "enterprise_deal_qualification",
        "career_stage": "senior",
        "source_resume_files": [
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Sales - Amit Ayer.docx",
        ],
        "source_snippets": [
            "applying MEDDPICC principles to qualify complex opportunities and build consensus among key decision makers",
            "using MEDDPICC and incremental consumption models that demonstrated ROI through real-time analytics",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "SALES_STRATEGIC_ACCOUNTS": 1.0,
            "REVENUE_OPERATIONS": 0.7,
            "PARTNERSHIPS_GTM": 0.6,
        },
        "allowed_phrases": [
            "MEDDPICC",
            "deal qualification",
            "enterprise deal qualification",
            "opportunity qualification",
            "MEDDIC",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_ibm_client_partner_consulting",
        "domain_id": "domain_gtm_presales_motion",
        "domain": "GTM & Presales Motion",
        "capability": "enterprise_deal_qualification",
        "source_concepts": ["MEDDPICC", "enterprise sales", "deal qualification"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["MEDDPICC", "MEDDIC", "deal qualification", "sales methodology"],
        "achievement_framing_guidance": "Frame MEDDPICC with deal complexity, stakeholder breadth, and revenue outcome.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from linked fact_id_links and approved snippets; do not invent deal sizes.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits and fact_id_links non-empty or snippet confirmed.",
        "zero_hallucination_guardrail": "Do not claim MEDDPICC beyond resume snippets; fail closed on unverified deal specifics.",
        "career_track_id": "TRACK_ENTERPRISE_GTM_SALES",
        "confidence_grade": "MEDIUM",
        "confidence_grade_derived": "MEDIUM",
        "graph_hop_path": ["pillar_gtm_presales_motion", "skill_meddpicc_sales_qualification"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_cpq_deal_velocity_automation",
        "fact_id_links": [],
        "pillar": "pillar_revenue_operations",
        "subpillar": "cpq_and_deal_automation",
        "career_stage": "senior",
        "source_resume_files": [
            "Revenue Operations - Amit Ayer.docx",
        ],
        "source_snippets": [
            "integrating CPQ automations with real-time data ingestion, collaborating with Confluent and AWS to unify customer intelligence across finance, risk, and compliance teams",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "REVENUE_OPERATIONS": 1.0,
            "SALES_STRATEGIC_ACCOUNTS": 0.6,
        },
        "allowed_phrases": [
            "CPQ",
            "Configure Price Quote",
            "deal automation",
            "quote automation",
            "CPQ integration",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_unify_chief_ai_officer",
        "domain_id": "domain_revenue_operations",
        "domain": "Revenue Operations",
        "capability": "cpq_and_deal_automation",
        "source_concepts": ["CPQ", "deal velocity", "quote automation"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["CPQ", "Configure Price Quote", "deal velocity", "revenue operations"],
        "achievement_framing_guidance": "Frame CPQ with throughput improvement, deal cycle reduction, and revenue impact.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; do not invent CPQ platform names.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim CPQ platform expertise beyond resume evidence.",
        "career_track_id": "TRACK_REVENUE_OPERATIONS",
        "confidence_grade": "MEDIUM",
        "confidence_grade_derived": "MEDIUM",
        "graph_hop_path": ["pillar_revenue_operations", "skill_cpq_deal_velocity_automation"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_soc2_zero_trust_security",
        "fact_id_links": [],
        "pillar": "pillar_regulatory_governance",
        "subpillar": "cloud_security_compliance",
        "career_stage": "senior",
        "source_resume_files": [
            "CTO Resume - Amit Ayer.docx",
            "Head of Data & Analytics - Amit Ayer.docx",
        ],
        "source_snippets": [
            "Embedded zero-trust security and compliance (SOC2, GDPR, CCPA), enabling sales to Fortune 100 clients",
            "Accelerated Regulatory Filings through LLM-based document parsing tailored for SaaS compliance (SOC 2, GDPR)",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "ENGINEERING_PLATFORM": 1.0,
            "EXECUTIVE_LEADERSHIP": 0.8,
            "REGULATED_AI_GOVERNANCE": 0.9,
            "AI_GOVERNANCE_RISK": 0.8,
        },
        "allowed_phrases": [
            "SOC2",
            "SOC 2",
            "zero-trust",
            "zero trust security",
            "GDPR compliance",
            "CCPA",
            "cloud security compliance",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_unify_chief_ai_officer",
        "domain_id": "domain_regulatory_governance",
        "domain": "Regulatory Governance",
        "capability": "cloud_security_compliance",
        "source_concepts": ["SOC2", "zero-trust", "GDPR", "CCPA", "cloud security"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["SOC2", "zero trust", "GDPR", "CCPA", "cloud security", "compliance"],
        "achievement_framing_guidance": "Frame SOC2/zero-trust with audit outcomes, client trust, and compliance acceleration.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; cite specific compliance frameworks.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim specific audit findings beyond resume evidence.",
        "career_track_id": "TRACK_ENGINEERING_PLATFORM",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": ["pillar_regulatory_governance", "skill_soc2_zero_trust_security"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_saas_arr_ltv_cac_metrics",
        "fact_id_links": [],
        "pillar": "pillar_strategic_finance_saas",
        "subpillar": "saas_growth_metrics",
        "career_stage": "senior",
        "source_resume_files": [
            "Strategic Finance - Amit Ayer.docx",
            "Revenue Operations - Amit Ayer.docx",
        ],
        "source_snippets": [
            "SaaS metric optimization (ARR, churn, LTV/CAC), enterprise data governance — driving recurring revenue growth",
            "Drove an additional 5 million dollars in annual recurring subscription contract value by forging multi-year deals aligned with CFO priorities",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "STRATEGIC_FINANCE": 1.0,
            "REVENUE_OPERATIONS": 0.9,
        },
        "allowed_phrases": [
            "ARR",
            "annual recurring revenue",
            "LTV/CAC",
            "LTV CAC",
            "churn rate",
            "SaaS metrics",
            "MRR",
            "net revenue retention",
            "NRR",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_unify_chief_ai_officer",
        "domain_id": "domain_strategic_finance_saas",
        "domain": "Strategic Finance & SaaS",
        "capability": "saas_growth_metrics",
        "source_concepts": ["ARR", "LTV/CAC", "churn", "SaaS metrics", "NRR"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["ARR", "LTV/CAC", "churn", "NRR", "SaaS metrics", "annual recurring revenue"],
        "achievement_framing_guidance": "Frame SaaS metrics with specific ARR growth, churn reduction, or LTV improvement outcomes.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; tie metrics to business outcomes.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim specific ARR/churn values beyond resume evidence.",
        "career_track_id": "TRACK_STRATEGIC_FINANCE",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": ["pillar_strategic_finance_saas", "skill_saas_arr_ltv_cac_metrics"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_confluent_streaming_platforms",
        "fact_id_links": [],
        "pillar": "pillar_interoperability_integration_ecosystem",
        "subpillar": "streaming_data_platforms",
        "career_stage": "senior",
        "source_resume_files": [
            "Revenue Operations - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
        ],
        "source_snippets": [
            "integrating CPQ automations with real-time data ingestion, collaborating with Confluent and AWS to unify customer intelligence",
            "partnering with Confluent and AWS, enhancing real-time data ingestion for financial risk assessments",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "PARTNERSHIPS_GTM": 0.8,
            "SALES_STRATEGIC_ACCOUNTS": 0.7,
            "ENGINEERING_PLATFORM": 0.8,
            "BANKING_PLATFORM_AI": 0.7,
        },
        "allowed_phrases": [
            "Confluent",
            "Apache Kafka",
            "streaming data",
            "real-time data ingestion",
            "event-driven",
            "streaming platform",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_unify_chief_ai_officer",
        "domain_id": "domain_interoperability_integration_ecosystem",
        "domain": "Interoperability & Integration Ecosystem",
        "capability": "streaming_data_platforms",
        "source_concepts": ["Confluent", "Kafka", "streaming", "real-time data"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["Confluent", "Apache Kafka", "streaming data", "real-time ingestion", "event-driven"],
        "achievement_framing_guidance": "Frame Confluent/streaming with latency improvement, throughput, and business impact.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; name specific platform when verified.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim deep Confluent engineering expertise beyond partnership/integration evidence.",
        "career_track_id": "TRACK_PARTNERSHIPS_GTM",
        "confidence_grade": "MEDIUM",
        "confidence_grade_derived": "MEDIUM",
        "graph_hop_path": ["pillar_interoperability_integration_ecosystem", "skill_confluent_streaming_platforms"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_watson_studio_fraud_aml",
        "fact_id_links": [],
        "pillar": "pillar_banking_platform_responsible_ai",
        "subpillar": "fraud_and_aml_detection",
        "career_stage": "senior",
        "source_resume_files": [
            "Head of Customer Success - Amit Ayer.docx",
        ],
        "source_snippets": [
            "Utilized Watson Studio for fraud detection and money laundering analytics, ensuring regulatory compliance and operational security",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "BANKING_PLATFORM_AI": 1.0,
            "CUSTOMER_SUCCESS": 0.6,
            "AI_GOVERNANCE_RISK": 0.7,
        },
        "allowed_phrases": [
            "Watson Studio",
            "IBM Watson",
            "fraud detection",
            "AML",
            "anti-money laundering",
            "money laundering analytics",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_ibm_client_partner_consulting",
        "domain_id": "domain_banking_platform_responsible_ai",
        "domain": "Banking Platform & Responsible AI",
        "capability": "fraud_and_aml_detection",
        "source_concepts": ["Watson Studio", "fraud detection", "AML", "money laundering"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["Watson Studio", "fraud detection", "AML", "anti-money laundering", "IBM Watson"],
        "achievement_framing_guidance": "Frame Watson Studio/AML with false positive reduction, compliance outcomes, and operational security improvements.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; cite Watson Studio specifically when verified.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim Watson Studio certifications or deep IBM tooling beyond resume evidence.",
        "career_track_id": "TRACK_BANKING_PLATFORM_AI",
        "confidence_grade": "MEDIUM",
        "confidence_grade_derived": "MEDIUM",
        "graph_hop_path": ["pillar_banking_platform_responsible_ai", "skill_watson_studio_fraud_aml"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_algo_trading_sub_ms_inference",
        "fact_id_links": [],
        "pillar": "pillar_derivatives_structured",
        "subpillar": "algorithmic_trading_hpc",
        "career_stage": "senior",
        "source_resume_files": [
            "Quantitative Research & Trading - Amit Ayer.docx",
        ],
        "source_snippets": [
            "enabling sub-millisecond inference for algorithmic trading",
            "cutting data preparation cycles by 40% and enabling sub-millisecond inference for algorithmic trading",
            "Optimized Model Tuning: Advanced time series forecasting techniques to continuously recalibrate trading algorithms under high market volatility",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "QUANT_TRADING_HPC": 1.0,
        },
        "allowed_phrases": [
            "algorithmic trading",
            "algo trading",
            "sub-millisecond inference",
            "market making",
            "trading algorithm",
            "HPC trading",
            "low-latency trading",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_actuarial_financial_engineering",
        "domain_id": "domain_actuarial_foundation",
        "domain": "Actuarial Foundation",
        "capability": "algorithmic_trading_hpc",
        "source_concepts": ["algo trading", "HPC", "sub-millisecond inference", "market making"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["algorithmic trading", "algo trading", "HPC", "sub-millisecond", "market making"],
        "achievement_framing_guidance": "Frame algo trading with latency reduction, accuracy improvement, and risk management outcomes.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; tie inference latency to measurable trading outcomes.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim specific trading P&L or strategy performance beyond resume evidence.",
        "career_track_id": "TRACK_ACTUARIAL_RISK_DERIVATIVES",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": ["pillar_derivatives_structured", "skill_algo_trading_sub_ms_inference"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_nps_customer_health_scoring",
        "fact_id_links": [],
        "pillar": "pillar_customer_stakeholder",
        "subpillar": "customer_health_and_retention",
        "career_stage": "senior",
        "source_resume_files": [
            "Head of Customer Success - Amit Ayer.docx",
        ],
        "source_snippets": [
            "integrated anomaly detection with a structured NPS feedback process that reinforced trust and maximized platform utilization",
            "Increased Customer Satisfaction by 25%: Integrated anomaly detection with a structured NPS feedback process",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "CUSTOMER_SUCCESS": 1.0,
            "REVENUE_OPERATIONS": 0.6,
        },
        "allowed_phrases": [
            "NPS",
            "Net Promoter Score",
            "customer health score",
            "customer health scoring",
            "customer satisfaction",
            "CSAT",
            "churn risk",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_unify_chief_ai_officer",
        "domain_id": "domain_customer_stakeholder",
        "domain": "Customer & Stakeholder",
        "capability": "customer_health_and_retention",
        "source_concepts": ["NPS", "customer health", "CSAT", "retention"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["NPS", "Net Promoter Score", "customer health", "CSAT", "customer satisfaction"],
        "achievement_framing_guidance": "Frame NPS/health scoring with satisfaction improvement, retention rate, and platform utilization outcomes.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; tie NPS to specific business retention outcomes.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim specific NPS scores beyond the 25% satisfaction improvement in resume.",
        "career_track_id": "TRACK_CUSTOMER_SUCCESS",
        "confidence_grade": "MEDIUM",
        "confidence_grade_derived": "MEDIUM",
        "graph_hop_path": ["pillar_customer_stakeholder", "skill_nps_customer_health_scoring"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_finra_sec_regulatory_compliance",
        "fact_id_links": [],
        "pillar": "pillar_regulatory_governance",
        "subpillar": "securities_regulatory_compliance",
        "career_stage": "senior",
        "source_resume_files": [
            "Quantitative Research & Trading - Amit Ayer.docx",
        ],
        "source_snippets": [
            "satisfying rigorous FINRA and SEC mandates",
            "Strengthened Regulatory Alignment: Implemented generative AI-driven documentation workflows, trimming compliance overhead by 30% while satisfying rigorous FINRA and SEC mandates",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "QUANT_TRADING_HPC": 1.0,
            "AI_GOVERNANCE_RISK": 0.8,
            "REGULATED_AI_GOVERNANCE": 0.9,
        },
        "allowed_phrases": [
            "FINRA",
            "SEC compliance",
            "securities compliance",
            "securities regulation",
            "FINRA compliance",
            "regulatory submissions",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_actuarial_financial_engineering",
        "domain_id": "domain_regulatory_governance",
        "domain": "Regulatory Governance",
        "capability": "securities_regulatory_compliance",
        "source_concepts": ["FINRA", "SEC", "securities compliance", "regulatory mandates"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["FINRA", "SEC", "securities compliance", "regulatory compliance", "securities regulation"],
        "achievement_framing_guidance": "Frame FINRA/SEC compliance with overhead reduction and documentation efficiency outcomes.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; cite specific regulatory bodies when verified.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim FINRA/SEC registration or examination experience beyond resume evidence.",
        "career_track_id": "TRACK_ACTUARIAL_RISK_DERIVATIVES",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": ["pillar_regulatory_governance", "skill_finra_sec_regulatory_compliance"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
    {
        "skill_id": "skill_credit_adjudication_default_risk",
        "fact_id_links": [],
        "pillar": "pillar_risk_management",
        "subpillar": "credit_risk_and_adjudication",
        "career_stage": "senior",
        "source_resume_files": [
            "Industry Solutions - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
        ],
        "source_snippets": [
            "AI-driven credit adjudication project that cut default exposure by 15% through dynamic risk profiling and improved underwriting accuracy",
            "Increased Portfolio Profitability Through Predictive Analytics: Introduced advanced deep learning risk models that lowered default exposure by up to 25%",
        ],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {
            "BANKING_PLATFORM_AI": 1.0,
            "CONSULTING_DELIVERY_LEADERSHIP": 0.8,
            "AI_GOVERNANCE_RISK": 0.7,
        },
        "allowed_phrases": [
            "credit adjudication",
            "credit risk",
            "default risk",
            "underwriting accuracy",
            "loan adjudication",
            "credit scoring",
            "credit default",
        ],
        "forbidden_phrases": [],
        "allowed_sections": ["competencies", "executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_ibm_client_partner_consulting",
        "domain_id": "domain_risk_management",
        "domain": "Risk Management",
        "capability": "credit_risk_and_adjudication",
        "source_concepts": ["credit adjudication", "default risk", "underwriting", "credit scoring"],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": ["credit adjudication", "credit risk", "default risk", "underwriting", "credit scoring"],
        "achievement_framing_guidance": "Frame credit adjudication with default exposure reduction, underwriting accuracy, and portfolio profitability metrics.",
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": "Synthesize only from confirmed snippets; tie credit risk to measurable default reduction.",
        "claim_verification_policy": "External resume claims allowed only when external_claim_policy permits.",
        "zero_hallucination_guardrail": "Do not claim credit underwriting authority or loan origination volumes beyond resume evidence.",
        "career_track_id": "TRACK_BANKING_PLATFORM_AI",
        "confidence_grade": "HIGH",
        "confidence_grade_derived": "HIGH",
        "graph_hop_path": ["pillar_risk_management", "skill_credit_adjudication_default_risk"],
        "link_class_by_fact": {},
        "source_ledger_ref": "",
    },
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] would write {path}")
        return
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    print(f"[SAVED] {path}")


def run(dry_run: bool = False) -> None:
    data = _load(LEDGER_PATH)
    skill_rows: list[dict] = data.get("skill_rows", [])

    existing_ids = {r.get("skill_id") for r in skill_rows if isinstance(r, dict)}
    added = 0
    skipped = 0

    for new_row in NEW_SKILL_ROWS:
        sid = new_row["skill_id"]
        if sid in existing_ids:
            print(f"  SKIP (already exists): {sid}")
            skipped += 1
            continue
        skill_rows.append(new_row)
        existing_ids.add(sid)
        added += 1
        print(f"  ADDED: {sid} [{new_row['pillar']}]")

    data["skill_rows"] = skill_rows
    print(f"\nAdded: {added}, Skipped (already present): {skipped}")
    print(f"Total skill_rows after: {len(skill_rows)}")

    # Update metadata
    meta = data.get("metadata", {})
    if isinstance(meta, dict):
        meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        meta["last_updated_by"] = "apply_phase1_new_skill_nodes.py"
        data["metadata"] = meta

    _save(LEDGER_PATH, data, dry_run)
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
