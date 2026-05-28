"""Phase I Resume Archive Graph Gap Fill Analysis Report Generator."""
import json
import os
import datetime

REPORT_TS = "2026-05-28T12:55:00Z"

CANDIDATE_SIGNALS = [
    # ========== IBM GAP FILLS ==========
    {
        "signal_id": "sig_ibm_001",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "AI and Data Governance - Amit Ayer.docx",
            "Amit Ayer Resume - AI Financial Services.docx",
            "Chief AI Officer - Amit Ayer.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
            "Field CTO - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Spearheaded the re-architecture of monolithic risk analytics, introducing containerized "
            "microservices that trimmed calculation by 40% and facilitated real-time stress testing "
            "under regulatory constraints."
        ),
        "proposed_graph_skill_node_id": "skill_sr_microservices_integration_platform",
        "linked_source_fact_id": "fact_engineering_platform_002",
        "metric_outcome": "40% calculation latency reduction via containerized microservices",
        "confidence": "HIGH",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "ibm_gap_addressed": "containerized microservices",
        "notes": (
            "skill_sr_microservices_integration_platform already ACTIVE with fact_engineering_platform_002. "
            "Archive reinforces with IBM-employer-specific snippet and 40% metric. IBM-employer attribution "
            "in fact needed. Metric conflict: 40% used across 10+ other contexts - require canonical "
            "selection before promotion."
        ),
    },
    {
        "signal_id": "sig_ibm_002",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
            "Field CTO - Amit Ayer.docx",
            "CTO Resume - Amit Ayer.docx",
            "Chief Technology Officer - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Closed multi-year modernization deals exceeding 15 million dollars by demonstrating ROI on "
            "HPC simulations for stress testing, cutting scenario runtimes by 40 percent."
        ),
        "proposed_graph_skill_node_id": "skill_risk_greek_stress_testing",
        "linked_source_fact_id": None,
        "metric_outcome": "$15M modernization deals; 40% scenario runtime reduction via HPC stress testing",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative"],
        "ibm_gap_addressed": "HPC stress testing / risk analytics",
        "notes": (
            "skill_risk_greek_stress_testing currently DRAFT with no source facts. Archive provides strong "
            "IBM-employer HPC stress testing signal across 5 resumes. $15M modernization deal metric is "
            "unique to SAE resume (single-source). Before full promotion: second-source $15M; select "
            "canonical 40% context. Node activation DRAFT->ACTIVE_CONFIRMED possible after reconciliation."
        ),
    },
    {
        "signal_id": "sig_ibm_003",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "AI and Data Governance - Amit Ayer.docx",
            "Amit Ayer Resume - AI Financial Services.docx",
            "Head of Data & Analytics - Amit Ayer.docx",
            "Chief AI Officer - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Established automated release pipelines with integrated code scanning, reducing production "
            "incidents by 35% and accelerating time to market for new AI-driven risk models."
        ),
        "proposed_graph_skill_node_id": "skill_ibm_automated_release_pipelines",
        "linked_source_fact_id": None,
        "metric_outcome": "35% production incident reduction via automated release pipelines with integrated code scanning",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "ibm_gap_addressed": "automated release pipelines + integrated code scanning",
        "notes": (
            "NEW proposed node - not currently in ledger. Covers both automated release pipelines AND "
            "integrated code scanning IBM gaps (co-addressed). Consistent snippet across AI&DG and AI "
            "FinSvcs resumes (4 files). Metric 35% appears in 5+ other contexts - select canonical "
            "context (IBM production incidents) before promoting metric."
        ),
    },
    {
        "signal_id": "sig_ibm_004",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "Amit Ayer Resume - AI Financial Services.docx",
            "Chief AI Officer - Amit Ayer.docx",
            "Field CTO - Amit Ayer.docx",
            "Chief Technology Officer - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Detected a 40% latency in monolithic risk calculations; containerized those workloads and "
            "integrated DevSecOps scanning; trimmed overhead by 15% and sped up daily valuations. "
            "[Also: Elevated Governance Standards: Implemented automated CI/CD pipelines with real time "
            "code scanning and role-based data access, reducing incidents by 35%.]"
        ),
        "proposed_graph_skill_node_id": "skill_ibm_devsecops_pipeline_security",
        "linked_source_fact_id": None,
        "metric_outcome": "15% overhead reduction via DevSecOps scanning (IBM); 35% incident reduction via CI/CD+RBAC (IBM)",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "ibm_gap_addressed": "DevSecOps + integrated code scanning",
        "notes": (
            "NEW proposed node. IBM-employer DevSecOps signal present across 4 resumes. IMPORTANT: "
            "CTO Resume DevSecOps ('company-wide DevSecOps program') is attributed to UNIFY context, not IBM. "
            "IBM-specific DevSecOps signal is AI FinSvcs + Chief AI Officer + Field CTO. "
            "Do NOT blend employer contexts. Create separate IBM node vs Unify node if needed."
        ),
    },
    {
        "signal_id": "sig_ibm_005",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "AI and Data Governance - Amit Ayer.docx",
            "Amit Ayer Resume - AI Financial Services.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
        ],
        "source_snippet": (
            "Developed cost-performance dashboards linking cloud spending to strategic risk priorities, "
            "promoting transparency for executive stakeholders and improving budget allocations."
        ),
        "proposed_graph_skill_node_id": "skill_finance_cost_optimization_dashboards",
        "linked_source_fact_id": "fact_revenue_ops_004",
        "metric_outcome": "IBM cloud cost transparency linked to strategic risk; CFO-level budget visibility",
        "confidence": "HIGH",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["ibm_bullets", "ibm_narrative"],
        "ibm_gap_addressed": "cost-performance dashboards",
        "notes": (
            "skill_finance_cost_optimization_dashboards already ACTIVE with fact_revenue_ops_004. Archive "
            "provides IBM-employer-specific snippet. Reconcile: existing fact may cover Unify context; IBM "
            "context needs separate attribution or fact enrichment with IBM employer flag."
        ),
    },
    {
        "signal_id": "sig_ibm_006",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "AI and Data Governance - Amit Ayer.docx",
            "Chief AI Officer - Amit Ayer.docx",
            "Head of Data & Analytics - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
        ],
        "source_snippet": (
            "Transitioned batch-only data processing into streaming analytics ecosystems, empowering "
            "faster market data validation and enabling near-real-time risk monitoring."
        ),
        "proposed_graph_skill_node_id": "skill_confluent_streaming_platforms",
        "linked_source_fact_id": None,
        "metric_outcome": "Near-real-time risk monitoring enabled; 25% capacity increase for faster decisions (AI FinSvcs)",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative", "competencies"],
        "ibm_gap_addressed": "streaming analytics ecosystems + near-real-time risk monitoring",
        "notes": (
            "skill_confluent_streaming_platforms currently DRAFT with no source facts. Archive provides "
            "strong IBM employer streaming signal across 4 resumes. Co-addresses near-real-time risk "
            "monitoring gap. SAE explicitly names Confluent (see sig_ibm_007). Strong DRAFT->ACTIVE "
            "promotion candidate. 25% capacity metric shares same percentage pool as 6+ other contexts."
        ),
    },
    {
        "signal_id": "sig_ibm_007",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Unified disparate data infrastructures under Confluent-based pipelines, enabling real-time "
            "risk scoring that elevated market responsiveness and reduced system downtime by 25 percent."
        ),
        "proposed_graph_skill_node_id": "skill_confluent_streaming_platforms",
        "linked_source_fact_id": None,
        "metric_outcome": "25% system downtime reduction; real-time risk scoring via Confluent pipelines",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative"],
        "ibm_gap_addressed": "Confluent / event-driven pipelines",
        "notes": (
            "Confluent explicitly named in SAE, Revenue Ops (Confluent+CPQ Unify context), and Sales "
            "competencies. IBM context: Confluent for real-time risk scoring. Unify context: Confluent for "
            "CPQ/upsell. Keep employer contexts separate in graph fact attribution."
        ),
    },
    {
        "signal_id": "sig_ibm_008",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Strengthened compliance by establishing standardized audit trails, metadata tagging, and "
            "secure data sharing protocols, reinforcing trust among clients and alliance partners."
        ),
        "proposed_graph_skill_node_id": "skill_ibm_metadata_audit_rbac",
        "linked_source_fact_id": None,
        "metric_outcome": "30% compliance gap reduction via metadata management and role-based controls (SAE/Revenue Ops)",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative"],
        "ibm_gap_addressed": "metadata tagging + audit trails + role-based controls",
        "notes": (
            "NEW proposed node covering three IBM gaps in one. Highly consistent across 5 resumes. "
            "30% compliance gap metric in SAE and Revenue Ops IBM sections. "
            "Metric 30% is used in 6+ other contexts - disambiguate before promoting. "
            "IBM EY context also has role-based controls (Partner Dev/P&A EY: encryption+RBAC) - "
            "distinguish IBM employer attribution from EY."
        ),
    },
    {
        "signal_id": "sig_ibm_009",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
            "CTO Resume - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Drove partial P&L accountability within the IBM-AWS alliance by designing AI-driven sales "
            "frameworks that boosted joint revenue by 20 percent, leveraging deep learning for real-time "
            "risk scoring and portfolio optimization."
        ),
        "proposed_graph_skill_node_id": "skill_partner_ibm_aws_alliance_joint_revenue",
        "linked_source_fact_id": "fact_partnerships_gtm_002",
        "metric_outcome": "20% joint revenue growth via IBM-AWS alliance; $30M Cloud Pak partner revenue (CTO Resume, single-source)",
        "confidence": "HIGH",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["ibm_bullets", "ibm_narrative"],
        "ibm_gap_addressed": "IBM-AWS / hyperscaler alliance + co-sell / partner revenue",
        "notes": (
            "skill_partner_ibm_aws_alliance_joint_revenue ACTIVE with fact_partnerships_gtm_002. "
            "Archive reinforces with explicit IBM-AWS naming and 20% joint revenue (2 resumes, consistent). "
            "CTO Resume adds $30M Cloud Pak partner revenue (single-source, IBM context). "
            "Do NOT mix 20% alliance growth with $30M Cloud Pak without separate fact attribution."
        ),
    },
    {
        "signal_id": "sig_ibm_010",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": ["Head of Customer Success - Amit Ayer.docx"],
        "source_snippet": (
            "Optimized Capital Markets Applications: Utilized Watson Studio for fraud detection and "
            "money laundering analytics, ensuring regulatory compliance and operational security."
        ),
        "proposed_graph_skill_node_id": "skill_ibm_watson_studio_analytics",
        "linked_source_fact_id": None,
        "metric_outcome": "Watson Studio for fraud detection and money laundering analytics (qualitative)",
        "confidence": "MEDIUM",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "ibm_narrative"],
        "ibm_gap_addressed": None,
        "notes": (
            "NEW proposed node. Watson Studio single-source (Head of Customer Success only). Medium "
            "confidence - single resume only. IBM product specificity adds value for IBM-targeted roles. "
            "Before promotion: verify Watson Studio appears in base resume or fact ledger."
        ),
    },
    # ========== UNIFY GAP FILLS ==========
    {
        "signal_id": "sig_unify_001",
        "employer": "Unify",
        "role_title": "Chief AI Officer",
        "time_window": "2023-02 to present",
        "source_files": ["CTO Resume - Amit Ayer.docx"],
        "source_snippet": (
            "Defined technology roadmap and built distributed engineering team, accelerating product "
            "iteration by 50% while meeting 99.99% uptime SLAs."
        ),
        "proposed_graph_skill_node_id": "skill_unify_runtime_stability_uptime",
        "linked_source_fact_id": None,
        "metric_outcome": "99.99% uptime SLA; 50% product iteration acceleration (Unify CTO context)",
        "confidence": "MEDIUM",
        "promotion_decision": "PROMOTE",
        "target_sections": ["unify_bullets", "unify_narrative"],
        "unify_gap_addressed": "runtime stability",
        "notes": (
            "NEW proposed node. Single-source (CTO Resume). 99.99% uptime directly addresses Unify "
            "runtime stability gap. 50% iteration metric is unique to CTO Resume Unify context - "
            "distinct from TraderSense 50% HPC latency. Platform framing appropriate for Unify bullets."
        ),
    },
    {
        "signal_id": "sig_unify_002",
        "employer": "Unify",
        "role_title": "Chief AI Officer",
        "time_window": "2023-02 to present",
        "source_files": ["CTO Resume - Amit Ayer.docx"],
        "source_snippet": (
            "Instituted company-wide DevSecOps program and CI/CD automation; cut incident recovery "
            "time by 40% and release defects by 35%."
        ),
        "proposed_graph_skill_node_id": "skill_ibm_devsecops_pipeline_security",
        "linked_source_fact_id": None,
        "metric_outcome": "40% incident recovery improvement; 35% release defect reduction (Unify context)",
        "confidence": "HIGH",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["unify_bullets", "unify_narrative"],
        "unify_gap_addressed": "AI CI/CD",
        "notes": (
            "Unify CTO context for DevSecOps. Partially addresses AI CI/CD gap. Metric 40% is used in "
            "10+ other contexts; 35% in 5+ contexts. Must select canonical context before promoting. "
            "Consider whether shared node with IBM DevSecOps is appropriate or separate Unify node needed."
        ),
    },
    {
        "signal_id": "sig_unify_003",
        "employer": "Unify",
        "role_title": "Chief AI Officer",
        "time_window": "2023-02 to present",
        "source_files": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Built a global AI channel program from inception, co-developing advanced analytics "
            "frameworks with strategic partners, bundling consulting packages with LLM-driven compliance "
            "analysis, and leveraging co-marketing campaigns to generate 3 million dollars in "
            "partner-derived revenue."
        ),
        "proposed_graph_skill_node_id": "skill_ai_platform_commercialization",
        "linked_source_fact_id": "fact_engineering_platform_004",
        "metric_outcome": "$3M partner-derived revenue (Unify; consistent across 2 resumes)",
        "confidence": "HIGH",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["unify_bullets", "unify_narrative"],
        "unify_gap_addressed": "platform commercialization",
        "notes": (
            "skill_ai_platform_commercialization ACTIVE with fact_engineering_platform_004. $3M is "
            "CONSISTENT across Partner Dev and P&A resumes (same employer, same context). Good promotion "
            "candidate. Review whether base resume already claims this metric."
        ),
    },
    {
        "signal_id": "sig_unify_004",
        "employer": "Unify",
        "role_title": "Chief AI Officer",
        "time_window": "2023-02 to present",
        "source_files": ["CTO Resume - Amit Ayer.docx"],
        "source_snippet": (
            "Defined technology roadmap and built distributed engineering team, accelerating product "
            "iteration by 50% while meeting 99.99% uptime SLAs. Led cloud migration to microservices "
            "(Kubernetes, Terraform, AWS), reducing infrastructure cost by 30% and improving deployment "
            "velocity."
        ),
        "proposed_graph_skill_node_id": "skill_reusable_agentic_platform_architecture",
        "linked_source_fact_id": "fact_engineering_platform_006",
        "metric_outcome": "Distributed engineering team build; 30% infra cost reduction; Kubernetes/Terraform/AWS stack",
        "confidence": "MEDIUM",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["unify_bullets", "unify_narrative"],
        "unify_gap_addressed": "team scale",
        "notes": (
            "skill_reusable_agentic_platform_architecture ACTIVE_CONFIRMED with fact_engineering_platform_006. "
            "CTO Resume provides Unify employer team scale signal. 30% infra cost reduction metric appears "
            "in multiple other contexts (SAE IBM 30% containerization, Head D&A IBM 30% processing time). "
            "Distinguish Unify 30% context carefully from IBM 30% contexts."
        ),
    },
    {
        "signal_id": "sig_unify_005",
        "employer": "Unify",
        "role_title": "Chief AI Officer",
        "time_window": "2023-02 to present",
        "source_files": [
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
            "Head of Customer Success - Amit Ayer.docx",
            "Strategic Finance - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Drove an additional 5 million dollars in annual contract value by aligning generative AI "
            "workflows with CFO priorities, facilitating enterprise-wide adoption of data-driven "
            "decision making."
        ),
        "proposed_graph_skill_node_id": "skill_ai_platform_commercialization",
        "linked_source_fact_id": None,
        "metric_outcome": "$5M Unify (ACV/ARR/new revenue - LABEL CONFLICT across 6 resumes)",
        "confidence": "MEDIUM",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["unify_bullets", "unify_narrative"],
        "unify_gap_addressed": "platform commercialization",
        "notes": (
            "METRIC CONFLICT: 6 Unify resumes all claim $5M with different labels: "
            "VP Finance=new revenue, Head CS=ARR, Rev Ops=ARR subscription, "
            "Strategic Finance=ARR, Sales=ACV, SAE=ACV. "
            "DO NOT PROMOTE until canonical label selected. Amount is consistent; "
            "label must be resolved before graph promotion."
        ),
    },
    # ========== EY SIGNALS ==========
    {
        "signal_id": "sig_ey_001",
        "employer": "EY",
        "role_title": "Principal",
        "time_window": "2009-10 to 2014-03",
        "source_files": [
            "Amit Ayer Resume - AI Financial Services.docx",
            "Head of Data & Analytics - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Realized derivative fraud slipped past manual reviews; launched AI-based anomaly detection; "
            "saved over $10M a year by catching risky trades earlier."
        ),
        "proposed_graph_skill_node_id": "skill_ml_fraud_detection_anomaly",
        "linked_source_fact_id": None,
        "metric_outcome": "$10M annual savings from AI anomaly detection for derivative fraud (EY context)",
        "confidence": "MEDIUM",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["competencies"],
        "ibm_gap_addressed": None,
        "notes": (
            "EY $10M fraud detection - appears in AI FinSvcs and Head of D&A. This is EY-era claim "
            "(2009-2014). Do NOT attribute to IBM section. If EY section or competencies, can promote "
            "after canonical fact confirmation. EY section is locked deterministic - review before "
            "any edit."
        ),
    },
    # ========== TRADERSENSE SIGNALS ==========
    {
        "signal_id": "sig_ts_001",
        "employer": "TraderSense",
        "role_title": "Chief Technology Officer",
        "time_window": "2014-04 to 2017-03",
        "source_files": ["All 17 archive resumes (consistent)"],
        "source_snippet": (
            "Engineered an AI-Driven Automated Trading Platform leveraging parallel HPC workflows, "
            "reducing end-to-end latency by 50% while enabling real-time ML insights and "
            "dynamic risk monitoring."
        ),
        "proposed_graph_skill_node_id": "skill_trading_hpc_latency_optimization",
        "linked_source_fact_id": None,
        "metric_outcome": "50% HPC end-to-end latency reduction for AI trading platform (TraderSense)",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["competencies"],
        "ibm_gap_addressed": None,
        "notes": (
            "50% HPC latency at TraderSense is the MOST CONSISTENT metric in archive - present across "
            "all 17 resumes with near-identical phrasing. Distinct from Unify CTO 50% product iteration "
            "(different employer, different context). Highly credible for promotion."
        ),
    },
    # ========== HEADLINE / COMPETENCY DOMAIN ==========
    {
        "signal_id": "sig_comp_001",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": [
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
        ],
        "source_snippet": (
            "Forged alliances with cloud, streaming, and analytics vendors (AWS, Confluent, Databricks) "
            "to expand solution portfolios for high-potential accounts."
        ),
        "proposed_graph_skill_node_id": "skill_partner_co_selling",
        "linked_source_fact_id": None,
        "metric_outcome": "Alliance with Confluent, AWS, Databricks; $15M modernization deals",
        "confidence": "HIGH",
        "promotion_decision": "RECONCILE_METRIC",
        "target_sections": ["headline", "competencies"],
        "ibm_gap_addressed": "co-sell / partner revenue",
        "notes": (
            "skill_partner_co_selling ACTIVE_CONFIRMED. Archive strengthens Confluent/AWS/Databricks "
            "co-sell at IBM. Consistent with SAE headline targeting. $15M single-source - hold."
        ),
    },
    {
        "signal_id": "sig_comp_002",
        "employer": "IBM",
        "role_title": "Lead Client Partner",
        "time_window": "2017-04 to 2022-10",
        "source_files": ["Chief AI Officer - Amit Ayer.docx"],
        "source_snippet": (
            "Elevated Governance Standards: Implemented automated CI/CD pipelines with real time code "
            "scanning and role-based data access, reducing incidents by 35 percent and capturing "
            "10 percent savings through FinOps best practices."
        ),
        "proposed_graph_skill_node_id": "skill_ibm_devsecops_pipeline_security",
        "linked_source_fact_id": None,
        "metric_outcome": "35% incident reduction + 10% FinOps savings via CI/CD+code scanning+RBAC",
        "confidence": "HIGH",
        "promotion_decision": "PROMOTE",
        "target_sections": ["ibm_bullets", "competencies"],
        "ibm_gap_addressed": "automated release pipelines + integrated code scanning + role-based controls",
        "notes": (
            "Chief AI Officer resume provides most comprehensive co-addressing of 3 IBM gaps in one "
            "snippet: CI/CD + code scanning + RBAC. 35% incident metric consistent with sig_ibm_003. "
            "10% FinOps savings metric is UNIQUE across archive - not duplicated elsewhere. "
            "Good canonical anchor for IBM DevSecOps node."
        ),
    },
]

METRIC_RECONCILIATION = [
    {
        "metric": "$3M partner-derived revenue",
        "employer": "Unify",
        "sources": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
        ],
        "context": "Global AI channel program; LLM-driven compliance bundles + co-marketing at Unify",
        "consistency": "CONSISTENT (2 resumes, same employer, same context)",
        "promotion_status": "PROMOTABLE - single amount, consistent employer/context",
        "conflicts": "None identified",
        "canonical_recommendation": "Use as Unify partner-revenue metric after base resume confirmation",
    },
    {
        "metric": "$5M ACV / ARR (label conflict)",
        "employer": "Unify",
        "sources": [
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
            "Head of Customer Success - Amit Ayer.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Strategic Finance - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
        ],
        "context": "Unify AI revenue: VP Finance=new revenue, Head CS=ARR, Rev Ops=ARR subscription, Strategic Finance=ARR, Sales=ACV",
        "consistency": "AMOUNT CONSISTENT; LABEL CONFLICTING (new revenue vs ARR vs ACV)",
        "promotion_status": "DO NOT PROMOTE - conflicting labels require canonical selection",
        "conflicts": "ACV vs ARR label conflict; VP Finance says new revenue others say recurring",
        "canonical_recommendation": "Select one label (recommend ARR if multi-year SaaS context); update all before graph promotion",
    },
    {
        "metric": "$10M ARR (IBM)",
        "employer": "IBM",
        "sources": [
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
            "Strategic Finance - Amit Ayer.docx",
        ],
        "context": "IBM Salesforce pipeline; net-new revenue / ARR from expanded client portfolio (50% pipeline expansion)",
        "consistency": "CONSISTENT (2 resumes, IBM employer)",
        "promotion_status": "PROMOTABLE - after fact attribution",
        "conflicts": "Minor: VP Finance=net-new revenue; Strategic Finance=new annual recurring revenue",
        "canonical_recommendation": "Use IBM ARR label; confirm fact attribution for IBM section",
    },
    {
        "metric": "$15M modernization deals",
        "employer": "IBM",
        "sources": ["Amit Ayer Resume - Strategic Account Executive.docx"],
        "context": "Multi-year HPC modernization deals with stress testing ROI demonstration",
        "consistency": "SINGLE SOURCE",
        "promotion_status": "HOLD - single source; verify with base resume or IBM fact ledger",
        "conflicts": "Single source only; high specificity but not corroborated",
        "canonical_recommendation": "Needs second-source confirmation before graph promotion",
    },
    {
        "metric": "$30M Cloud Pak / partner revenue",
        "employer": "IBM",
        "sources": ["CTO Resume - Amit Ayer.docx"],
        "context": "Platform engineering for IBM Cloud Pak supporting $30M in partner revenue",
        "consistency": "SINGLE SOURCE",
        "promotion_status": "HOLD - single source; not corroborated in other IBM resumes",
        "conflicts": "Appears only in CTO Resume; no corroboration",
        "canonical_recommendation": "Needs base resume fact confirmation before graph promotion",
    },
    {
        "metric": "20% joint revenue growth",
        "employer": "IBM",
        "sources": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
        ],
        "context": "IBM-AWS alliance P&L; AI-driven sales frameworks for financial services",
        "consistency": "CONSISTENT (2 resumes, same employer+context)",
        "promotion_status": "PROMOTABLE - after fact attribution",
        "conflicts": "None",
        "canonical_recommendation": "Link to skill_partner_ibm_aws_alliance_joint_revenue or skill_sr_w12_hyperscaler_alliance_co_sell",
    },
    {
        "metric": "25% improvements (various - OVERLOADED)",
        "employer": "Multiple",
        "sources": ["Multiple resumes across Unify + IBM + EY"],
        "context": (
            "Used for: anomaly detection resolution times (Unify AI&DG), MLOps pipeline accuracy (Unify Partner Dev), "
            "system downtime (IBM SAE Confluent), NLP alert times (IBM Industry Solutions), "
            "manual data interventions (IBM VP Finance), cross-border approvals (IBM Quant Research)"
        ),
        "consistency": "AMOUNT CONSISTENT; CONTEXT CONFLICTING across 6+ distinct outcomes",
        "promotion_status": "DO NOT PROMOTE - overloaded percentage across contexts",
        "conflicts": "Same % used for unrelated outcomes across employers and sections",
        "canonical_recommendation": "Select one canonical context per employer-section before promoting; retire others",
    },
    {
        "metric": "30% improvements (various - OVERLOADED)",
        "employer": "Multiple",
        "sources": ["Multiple resumes across Unify + IBM + EY"],
        "context": (
            "Used for: compliance errors (Unify Partner Dev), containerization advance (IBM Partner Dev), "
            "joint revenue (IBM-AWS Alliance), cost efficiency (IBM VP Finance / Strategic Finance), "
            "upsell conversions (Unify SAE / Rev Ops), subscription increase (IBM Industry Solutions), "
            "processing time (IBM Head CS)"
        ),
        "consistency": "AMOUNT CONSISTENT; CONTEXT CONFLICTING across 8+ distinct outcomes",
        "promotion_status": "DO NOT PROMOTE without context disambiguation",
        "conflicts": "Same % across revenue, cost, compliance, technical contexts",
        "canonical_recommendation": "Map each 30% to specific context before promoting; do not mix",
    },
    {
        "metric": "35% improvements (various - OVERLOADED)",
        "employer": "Multiple",
        "sources": ["Multiple resumes across Unify + IBM"],
        "context": (
            "Used for: regulatory findings (Unify AI&DG), production incidents (IBM AI&DG and AI FinSvcs), "
            "operational inconsistency (IBM Field CTO and Chief AI Officer), release defects (Unify CTO), "
            "CI/CD incidents (IBM Chief AI Officer and Head D&A), fraud detection accuracy (IBM Chief AI Officer)"
        ),
        "consistency": "AMOUNT CONSISTENT; CONTEXT CONFLICTING across 6+ distinct outcomes",
        "promotion_status": "DO NOT PROMOTE without context disambiguation",
        "conflicts": "Same % across compliance, engineering, operational contexts",
        "canonical_recommendation": (
            "IBM 35% production incidents (AI&DG/AI FinSvcs) is the most stable IBM context (3 resumes). "
            "Unify 35% regulatory findings (AI&DG) is unique. Evaluate each separately."
        ),
    },
    {
        "metric": "40% improvements (various - MOST OVERLOADED)",
        "employer": "Multiple",
        "sources": ["All major resumes (10+ instances)"],
        "context": (
            "HPC calculation latency (IBM microservices), compliance processing (Unify multiple), "
            "scenario runtimes (IBM SAE HPC), DevSecOps incident recovery (Unify CTO), "
            "DevSecOps code scanning latency (IBM AI FinSvcs), CI/CD speedup (IBM Head D&A), "
            "reporting errors (EY multiple), model accuracy (IBM Chief AI Officer HPC)"
        ),
        "consistency": "AMOUNT CONSISTENT; CONTEXT CONFLICTING across 10+ distinct outcomes",
        "promotion_status": "DO NOT PROMOTE - most overloaded metric in archive",
        "conflicts": "Same % used across every employer and outcome type in archive",
        "canonical_recommendation": (
            "Treat 40% as corpus-wide percentage baseline. Select single most credible context per "
            "section before promoting. Avoid using in isolation without context anchor."
        ),
    },
    {
        "metric": "50% improvements (two distinct contexts)",
        "employer": "TraderSense + Unify",
        "sources": [
            "All 17 archive resumes (TraderSense HPC)",
            "CTO Resume - Amit Ayer.docx (Unify product iteration)",
        ],
        "context": (
            "Context A: TraderSense HPC end-to-end latency reduction (consistent across ALL 17 resumes). "
            "Context B: Unify CTO product iteration acceleration (single source)."
        ),
        "consistency": "Context A HIGHLY CONSISTENT (17/17 resumes); Context B SINGLE SOURCE",
        "promotion_status": "PROMOTABLE for TraderSense context (A). Verify Unify context (B) separately.",
        "conflicts": "Two distinct 50% claims with different employers and contexts - must attribute separately",
        "canonical_recommendation": (
            "TraderSense 50% HPC latency: promote as canonical (highest archive consistency). "
            "Unify CTO 50% product iteration: promote separately with distinct fact attribution."
        ),
    },
]

GRAPH_READINESS = {
    "headline": {
        "archive_materially_improves": False,
        "rationale": (
            "Headline is a positioning statement. Archive provides domain vocabulary (HPC, DevSecOps, "
            "streaming, Confluent, IBM-AWS) that enriches targeting keywords. No headline-specific "
            "graph nodes are unresolved. Competencies section feeds headline vocabulary."
        ),
        "config_graph_expansion_allowed": False,
        "config_assessment": "CORRECT - dense C0 only is appropriate for headline",
        "recommendation": "No change. New ACTIVE nodes will surface via competencies which feeds headline targeting.",
    },
    "competencies": {
        "archive_materially_improves": True,
        "rationale": (
            "Archive fills DevSecOps, Confluent/streaming, metadata+RBAC, and HPC stress testing vocabulary "
            "gaps. Four new/DRAFT nodes (skill_confluent_streaming_platforms, skill_risk_greek_stress_testing, "
            "skill_ibm_automated_release_pipelines, skill_ibm_devsecops_pipeline_security) can be promoted "
            "to ACTIVE after metric reconciliation. Expands competency keyword coverage for IBM/CTO/Field CTO roles."
        ),
        "config_graph_expansion_allowed": False,
        "config_assessment": "CORRECT - competencies is fact-pull only; graph expansion not needed",
        "recommendation": (
            "PROMOTE 4 nodes to ACTIVE. No config change needed. New ACTIVE nodes reachable via dense C0."
        ),
    },
    "unify_bullets": {
        "archive_materially_improves": True,
        "rationale": (
            "Archive provides Unify-employer signals for: 99.99% uptime/runtime stability, DevSecOps/AI CI/CD, "
            "$3M partner revenue, platform commercialization, distributed team scale. "
            "skill_unify_runtime_stability_uptime (new) and reinforcement of skill_ai_platform_commercialization "
            "with $3M metric are the material improvements."
        ),
        "config_graph_expansion_allowed": False,
        "config_assessment": (
            "POTENTIAL GAP - unify_bullets needs graph-backed platform engineering claims. Without graph "
            "expansion, Unify platform nodes (sandboxed execution, deterministic routing, etc.) cannot "
            "surface even if ACTIVE."
        ),
        "recommendation": (
            "PROMOTE skill_unify_runtime_stability_uptime (new). Reconcile $5M label conflict. "
            "Review authorization to enable graph_expansion_allowed for unify_bullets in next wave. "
            "DO NOT change config in this inventory wave."
        ),
    },
    "unify_narrative": {
        "archive_materially_improves": True,
        "rationale": (
            "Archive provides Unify narrative anchors: CTO-level platform build, distributed team, "
            "DevSecOps, commercialization arc. Useful for narrative coherence across Unify tenure."
        ),
        "config_graph_expansion_allowed": False,
        "config_assessment": "SAME AS unify_bullets - narrative coherence benefits from graph expansion",
        "recommendation": (
            "Same as unify_bullets. Review graph_expansion_allowed authorization. "
            "DO NOT change config in this wave."
        ),
    },
    "ibm_bullets": {
        "archive_materially_improves": True,
        "rationale": (
            "Archive is the PRIMARY fill source for all 14 IBM gaps. Every IBM gap has strong archive "
            "coverage: containerized microservices, HPC stress testing, automated release pipelines, "
            "DevSecOps, code scanning, cost dashboards, streaming ecosystems, Confluent pipelines, "
            "near-real-time risk monitoring, metadata tagging, audit trails, RBAC, IBM-AWS alliance, "
            "co-sell partner revenue. Material improvement requires: 4 node promotions + 3 metric "
            "reconciliations + 1 second-source needed ($30M Cloud Pak)."
        ),
        "config_graph_expansion_allowed": False,
        "config_assessment": (
            "SIGNIFICANT GAP - ibm_bullets has the most graph-node-fillable content from this archive "
            "wave. Without graph expansion, 4+ new IBM nodes cannot surface in section output. "
            "This directly limits the return on investment from node promotions."
        ),
        "recommendation": (
            "HIGH PRIORITY: Evaluate authorization to enable graph_expansion_allowed for ibm_bullets. "
            "DO NOT change config in this inventory wave. Promote 4 nodes first."
        ),
    },
    "ibm_narrative": {
        "archive_materially_improves": True,
        "rationale": (
            "Archive provides IBM narrative connective tissue: IBM-AWS alliance framing, HPC-to-cloud "
            "transformation arc, streaming modernization story, DevSecOps governance narrative. "
            "All IBM gap signals feed narrative coherence."
        ),
        "config_graph_expansion_allowed": False,
        "config_assessment": (
            "SAME AS ibm_bullets - IBM narrative needs graph expansion to surface alliance, DevSecOps, "
            "and streaming arc signals."
        ),
        "recommendation": "Same priority as ibm_bullets. DO NOT change config in this wave.",
    },
}

UNRESOLVED_GAPS = {
    "ibm_gaps_unresolved": [],
    "ibm_gaps_all_resolved_by_archive": True,
    "unify_gaps_unresolved": [
        {
            "gap": "deterministic routing",
            "status": "KEEP_INTERNAL",
            "reason": (
                "Archive has no deterministic routing engineering signal. skill_cache_fallback_grounded_action_routing "
                "ACTIVE but platform-level, not archive-backed."
            ),
        },
        {
            "gap": "GraphRAG",
            "status": "REJECT - not in archive",
            "reason": "No GraphRAG mention anywhere in 17 archive resumes. Entirely absent.",
        },
        {
            "gap": "sandboxed execution",
            "status": "KEEP_INTERNAL",
            "reason": (
                "skill_sandboxed_execution_design ACTIVE but no archive snippet. "
                "Platform engineering claim without employer-era source."
            ),
        },
        {
            "gap": "replayable execution traces",
            "status": "KEEP_INTERNAL",
            "reason": "skill_replayable_runtime_design ACTIVE but no archive source signal.",
        },
        {
            "gap": "validation controls",
            "status": "KEEP_INTERNAL",
            "reason": "CI/CD validation present but not explicit agentic validation controls. No direct archive signal.",
        },
        {
            "gap": "dependency graph accelerator",
            "status": "KEEP_INTERNAL",
            "reason": "No archive mention. Platform-specific capability not in any employer-era resume.",
        },
        {
            "gap": "architecture visibility",
            "status": "KEEP_INTERNAL",
            "reason": (
                "Cost dashboards and governance dashboards present but not agentic architecture "
                "visibility specifically. Partial at best."
            ),
        },
        {
            "gap": "dependency chains",
            "status": "KEEP_INTERNAL",
            "reason": "skill_dependency_and_join_control ACTIVE but no archive source signal.",
        },
        {
            "gap": "refactor risk",
            "status": "KEEP_INTERNAL",
            "reason": "No archive signal for refactor risk as a Unify platform capability.",
        },
        {
            "gap": "telemetry",
            "status": "KEEP_INTERNAL",
            "reason": (
                "IBM-level monitoring/observability present but no explicit Unify platform telemetry "
                "engineering signal in archive."
            ),
        },
        {
            "gap": "rollback",
            "status": "KEEP_INTERNAL",
            "reason": "No explicit rollback mention in any of 17 archive resumes.",
        },
        {
            "gap": "vector services",
            "status": "REJECT - not in archive",
            "reason": "No vector database or vector services mention. Entirely absent from archive.",
        },
        {
            "gap": "API gateways",
            "status": "REJECT - not in archive",
            "reason": "No API gateway mention. Absent from archive.",
        },
        {
            "gap": "identity controls",
            "status": "KEEP_INTERNAL (partial)",
            "reason": (
                "Role-based access controls present at IBM/EY level but not as Unify platform "
                "identity controls. IBM RBAC covered by sig_ibm_008; Unify platform identity absent."
            ),
        },
        {
            "gap": "AI CI/CD (partial fill only)",
            "status": "PARTIAL - KEEP_INTERNAL for platform-level; IBM/Unify DevSecOps covered",
            "reason": (
                "DevSecOps + CI/CD present for IBM and Unify (employer level) but specific AI model CI/CD "
                "pipeline engineering for agentic platform not explicitly in archive."
            ),
        },
        {
            "gap": "runtime stability (partial fill)",
            "status": "PARTIAL FILL via sig_unify_001",
            "reason": (
                "CTO Resume provides 99.99% uptime SLA at Unify. Single source but directly relevant. "
                "Promoted via skill_unify_runtime_stability_uptime (new node)."
            ),
        },
        {
            "gap": "platform commercialization (partial fill)",
            "status": "PARTIAL FILL via sig_unify_003 ($3M) and sig_unify_005 ($5M pending reconciliation)",
            "reason": (
                "$3M promotable after base resume check. $5M label conflict blocks promotion. "
                "skill_ai_platform_commercialization ACTIVE reinforced."
            ),
        },
        {
            "gap": "team scale (partial fill)",
            "status": "PARTIAL FILL via sig_unify_004",
            "reason": (
                "CTO Resume distributed engineering team build. Single source but credible. "
                "skill_reusable_agentic_platform_architecture reinforced."
            ),
        },
    ],
}

CONFIG_GAP_ANALYSIS = {
    "analyzed_file": "apps_rg/config/domain_contract/section_retrieval_profile.yaml",
    "schema_version": "2.1",
    "sections_with_graph_expansion_disabled": [
        "headline",
        "competencies",
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
    ],
    "sections_with_graph_expansion_enabled": ["executive_summary"],
    "findings": [
        {
            "section": "headline",
            "graph_expansion_allowed": False,
            "assessment": "CORRECT",
            "recommendation": "No change needed",
        },
        {
            "section": "competencies",
            "graph_expansion_allowed": False,
            "assessment": "CORRECT - new ACTIVE nodes will be reachable via dense C0",
            "recommendation": "No config change. Promote DRAFT nodes to ACTIVE.",
        },
        {
            "section": "unify_bullets",
            "graph_expansion_allowed": False,
            "assessment": "POTENTIAL GAP - Unify platform nodes need graph expansion to surface",
            "recommendation": "Review authorization to enable. DO NOT change in this inventory wave.",
        },
        {
            "section": "unify_narrative",
            "graph_expansion_allowed": False,
            "assessment": "SAME AS unify_bullets",
            "recommendation": "Same. DO NOT change in this wave.",
        },
        {
            "section": "ibm_bullets",
            "graph_expansion_allowed": False,
            "assessment": (
                "SIGNIFICANT GAP - ibm_bullets has the most graph-fillable content from this archive wave. "
                "Without graph expansion, 4+ new IBM nodes cannot surface."
            ),
            "recommendation": "HIGH PRIORITY: Evaluate authorization. DO NOT change in this wave.",
        },
        {
            "section": "ibm_narrative",
            "graph_expansion_allowed": False,
            "assessment": "SAME AS ibm_bullets",
            "recommendation": "Same priority. DO NOT change in this wave.",
        },
    ],
    "authorization_note": (
        "No config changes made in this inventory wave. All graph_expansion_allowed assessments "
        "are for next-wave planning only. Separate authorization required before editing "
        "section_retrieval_profile.yaml."
    ),
}

REPORT_JSON = {
    "report_metadata": {
        "report_id": "phase1_resume_archive_graph_gap_fill",
        "generated_at": REPORT_TS,
        "archive_source": "Phase I Resumes Archive.zip",
        "archive_file_count": 17,
        "archive_files_analyzed": [
            "AI and Data Governance - Amit Ayer.docx",
            "Amit Ayer Resume - AI Financial Services.docx",
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
            "CTO Resume - Amit Ayer.docx",
            "Chief AI Officer - Amit Ayer.docx",
            "Chief Technology Officer - Amit Ayer.docx",
            "Field CTO - Amit Ayer.docx",
            "Head of Customer Success - Amit Ayer.docx",
            "Head of Data & Analytics - Amit Ayer.docx",
            "Industry Solutions - Amit Ayer.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
            "Quantitative Research & Trading - Amit Ayer.docx",
            "Revenue Operations - Amit Ayer.docx",
            "Sales - Amit Ayer.docx",
            "Strategic Finance - Amit Ayer.docx",
        ],
        "rules_applied": [
            "Archive resumes treated as candidate signal inventory only - NOT final hydration source",
            "Archive prose NOT copied or paraphrased into resume bullets",
            "Base resume remains seniority and rigor baseline",
            "Graph skills + linked source facts remain content/proof authority",
            "JD/briefing remain targeting only",
            "E0 examples remain style only",
        ],
        "no_agentic_core_diff": True,
        "no_x2_x3_weakening": True,
        "no_live_runtime_proof_claimed": True,
    },
    "summary": {
        "ibm_gaps_total": 14,
        "ibm_gaps_archive_fills": 14,
        "ibm_gaps_unresolved_post_archive": 0,
        "unify_gaps_total": 18,
        "unify_gaps_fully_filled_by_archive": 0,
        "unify_gaps_partially_filled": 4,
        "unify_gaps_unresolved_post_archive": 14,
        "candidate_signals_total": len(CANDIDATE_SIGNALS),
        "promote_count": sum(
            1 for s in CANDIDATE_SIGNALS if s["promotion_decision"] == "PROMOTE"
        ),
        "reconcile_metric_count": sum(
            1 for s in CANDIDATE_SIGNALS
            if s["promotion_decision"] == "RECONCILE_METRIC"
        ),
        "keep_internal_count": sum(
            1 for s in CANDIDATE_SIGNALS if s["promotion_decision"] == "KEEP_INTERNAL"
        ),
        "reject_count": sum(
            1 for s in CANDIDATE_SIGNALS if s["promotion_decision"] == "REJECT"
        ),
        "metrics_in_reconciliation_table": len(METRIC_RECONCILIATION),
        "metrics_promotable": 3,
        "metrics_do_not_promote": 6,
        "metrics_hold": 2,
        "new_skill_nodes_proposed": 5,
        "draft_nodes_promotable_to_active": 2,
    },
    "candidate_signals": CANDIDATE_SIGNALS,
    "metric_reconciliation": METRIC_RECONCILIATION,
    "graph_readiness": GRAPH_READINESS,
    "unresolved_gaps": UNRESOLVED_GAPS,
    "config_gap_analysis": CONFIG_GAP_ANALYSIS,
}


def write_json_report(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(REPORT_JSON, fh, indent=2, ensure_ascii=False)


def write_md_report(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    a = lines.append

    a("# Phase I Resume Archive — Graph Skill Gap Fill Analysis & Promotion Planning")
    a("")
    a(f"**Generated:** {REPORT_TS}  ")
    a(f"**Archive:** Phase I Resumes Archive.zip ({REPORT_JSON['report_metadata']['archive_file_count']} files)  ")
    a(f"**Status:** Inventory and promotion planning only — no live runtime proof claimed  ")
    a(f"**agentic_core diff:** NONE  ")
    a(f"**X2/X3 weakening:** NONE  ")
    a("")
    a("---")
    a("")
    a("## Rules Applied")
    a("")
    for r in REPORT_JSON["report_metadata"]["rules_applied"]:
        a(f"- {r}")
    a("")
    a("---")
    a("")
    a("## Executive Summary")
    a("")
    s = REPORT_JSON["summary"]
    a(f"| Dimension | Value |")
    a(f"|---|---|")
    a(f"| IBM gaps total | {s['ibm_gaps_total']} |")
    a(f"| IBM gaps covered by archive | {s['ibm_gaps_archive_fills']} |")
    a(f"| IBM gaps unresolved after archive | {s['ibm_gaps_unresolved_post_archive']} |")
    a(f"| Unify gaps total | {s['unify_gaps_total']} |")
    a(f"| Unify gaps partially filled | {s['unify_gaps_partially_filled']} |")
    a(f"| Unify gaps unresolved after archive | {s['unify_gaps_unresolved_post_archive']} |")
    a(f"| Candidate signals total | {s['candidate_signals_total']} |")
    a(f"| PROMOTE decisions | {s['promote_count']} |")
    a(f"| RECONCILE_METRIC decisions | {s['reconcile_metric_count']} |")
    a(f"| Metrics requiring reconciliation (do-not-promote) | {s['metrics_do_not_promote']} |")
    a(f"| Metrics promotable | {s['metrics_promotable']} |")
    a(f"| New skill nodes proposed | {s['new_skill_nodes_proposed']} |")
    a(f"| DRAFT nodes promotable to ACTIVE | {s['draft_nodes_promotable_to_active']} |")
    a("")
    a("---")
    a("")
    a("## 1. Archive Signal Inventory by Domain")
    a("")
    domain_map = {
        "AI/Data Governance": [
            "AI and Data Governance - Amit Ayer.docx",
            "Chief AI Officer - Amit Ayer.docx",
        ],
        "AI Financial Services": ["Amit Ayer Resume - AI Financial Services.docx"],
        "CTO / Chief Technology Officer": [
            "CTO Resume - Amit Ayer.docx",
            "Chief Technology Officer - Amit Ayer.docx",
        ],
        "Field CTO": ["Field CTO - Amit Ayer.docx"],
        "Head of Data & Analytics": ["Head of Data & Analytics - Amit Ayer.docx"],
        "Industry Solutions": ["Industry Solutions - Amit Ayer.docx"],
        "Partnerships & Alliances": [
            "Amit Ayer Resume - Partner Development Manager.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
        ],
        "Revenue Operations": ["Revenue Operations - Amit Ayer.docx"],
        "Sales / Strategic Account Executive": [
            "Sales - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.docx",
        ],
        "Strategic Finance": [
            "Strategic Finance - Amit Ayer.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.docx",
        ],
        "Quantitative Research & Trading": [
            "Quantitative Research & Trading - Amit Ayer.docx",
        ],
        "Customer Success": ["Head of Customer Success - Amit Ayer.docx"],
    }
    a("| Domain | Archive Files |")
    a("|---|---|")
    for domain, files in domain_map.items():
        a(f"| {domain} | {'; '.join(files)} |")
    a("")
    a("---")
    a("")
    a("## 2. Candidate Signals by Employer")
    a("")
    for employer in ["Unify", "IBM", "TraderSense", "EY"]:
        emp_sigs = [
            s for s in CANDIDATE_SIGNALS if s["employer"] == employer
        ]
        if not emp_sigs:
            continue
        a(f"### {employer}")
        a("")
        for sig in emp_sigs:
            gap_label = sig.get("ibm_gap_addressed") or sig.get("unify_gap_addressed") or "general signal"
            a(f"#### `{sig['signal_id']}` — {gap_label}")
            a("")
            a(f"- **Role:** {sig['role_title']} | {sig['time_window']}")
            a(f"- **Source files:** {', '.join(sig['source_files'][:3])}{' + more' if len(sig['source_files']) > 3 else ''}")
            a(f"- **Snippet:** _{sig['source_snippet'][:200]}{'...' if len(sig['source_snippet']) > 200 else ''}_")
            a(f"- **Proposed node:** `{sig['proposed_graph_skill_node_id']}`")
            a(f"- **Linked fact:** `{sig['linked_source_fact_id'] or 'NONE - new fact needed'}`")
            a(f"- **Metric:** {sig['metric_outcome']}")
            a(f"- **Confidence:** {sig['confidence']}")
            a(f"- **Promotion decision:** **{sig['promotion_decision']}**")
            a(f"- **Target sections:** {', '.join(sig['target_sections'])}")
            a(f"- **Notes:** {sig['notes']}")
            a("")
        a("")
    a("---")
    a("")
    a("## 3. IBM Gap Fill Evaluation")
    a("")
    ibm_gaps = [
        "containerized microservices",
        "HPC stress testing / risk analytics",
        "automated release pipelines",
        "DevSecOps",
        "integrated code scanning",
        "cost-performance dashboards",
        "streaming analytics ecosystems",
        "Confluent / event-driven pipelines",
        "near-real-time risk monitoring",
        "metadata tagging",
        "audit trails",
        "role-based controls",
        "IBM-AWS / hyperscaler alliance",
        "co-sell / partner revenue",
    ]
    a("| IBM Gap | Archive Coverage | Signal IDs | Promotion Decision |")
    a("|---|---|---|---|")
    gap_to_signal = {}
    for sig in CANDIDATE_SIGNALS:
        gap = sig.get("ibm_gap_addressed")
        if gap:
            for g in gap.split(" + "):
                gap_to_signal.setdefault(g.strip(), []).append(sig)
    for gap in ibm_gaps:
        sigs = gap_to_signal.get(gap, [])
        if sigs:
            coverage = "COVERED"
            sig_ids = ", ".join(f"`{s['signal_id']}`" for s in sigs)
            decisions = ", ".join(set(s["promotion_decision"] for s in sigs))
        else:
            coverage = "NOT IN SIGNALS TABLE"
            sig_ids = "—"
            decisions = "—"
        a(f"| {gap} | {coverage} | {sig_ids} | {decisions} |")
    a("")
    a("**Result: All 14 IBM gaps have archive coverage. 0 IBM gaps remain unresolved.**")
    a("")
    a("---")
    a("")
    a("## 4. Unify Gap Fill Evaluation")
    a("")
    unify_gaps_all = UNRESOLVED_GAPS["unify_gaps_unresolved"]
    a("| Unify Gap | Archive Status | Notes |")
    a("|---|---|---|")
    for g in unify_gaps_all:
        a(f"| {g['gap']} | {g['status']} | {g['reason'][:120]}{'...' if len(g['reason']) > 120 else ''} |")
    a("")
    a("**Result: 4 Unify gaps partially filled (runtime stability, AI CI/CD, platform commercialization, team scale). 14 remain unresolved. 3 rejected (GraphRAG, vector services, API gateways).**")
    a("")
    a("---")
    a("")
    a("## 5. Metric Reconciliation Table")
    a("")
    a("| Metric | Employer | Consistency | Promotion Status | Recommendation |")
    a("|---|---|---|---|---|")
    for m in METRIC_RECONCILIATION:
        a(f"| {m['metric']} | {m['employer']} | {m['consistency'][:60]} | {m['promotion_status'][:60]} | {m['canonical_recommendation'][:80]} |")
    a("")
    a("### Metric Reconciliation Summary")
    a("")
    a("- **PROMOTABLE (3):** $3M partner revenue (Unify), $10M ARR (IBM), 20% joint revenue (IBM-AWS alliance), TraderSense 50% HPC latency")
    a("- **DO NOT PROMOTE (6 overloaded %):** 25%, 30%, 35%, 40%, 50% (Unify CTO context pending), $5M label conflict")
    a("- **HOLD (2 single-source):** $15M modernization deals, $30M Cloud Pak revenue")
    a("")
    a("---")
    a("")
    a("## 6. Graph Readiness Decision by Section")
    a("")
    a("| Section | Archive Improves | `graph_expansion_allowed` | Config Assessment | Recommendation |")
    a("|---|---|---|---|---|")
    for section, data in GRAPH_READINESS.items():
        improves = "YES" if data["archive_materially_improves"] else "NO"
        ge = str(data["config_graph_expansion_allowed"])
        assessment = data["config_assessment"][:70]
        rec = data["recommendation"][:80]
        a(f"| {section} | {improves} | {ge} | {assessment} | {rec} |")
    a("")
    a("---")
    a("")
    a("## 7. Config Gap Analysis")
    a("")
    cfg = CONFIG_GAP_ANALYSIS
    a(f"**File:** `{cfg['analyzed_file']}`  ")
    a(f"**Schema version:** {cfg['schema_version']}  ")
    a("")
    a("### Sections with `graph_expansion_allowed: false`")
    a("")
    for section in cfg["sections_with_graph_expansion_disabled"]:
        a(f"- `{section}`")
    a("")
    a("### Sections with `graph_expansion_allowed: true`")
    a("")
    for section in cfg["sections_with_graph_expansion_enabled"]:
        a(f"- `{section}`")
    a("")
    a("### Section-by-Section Assessment")
    a("")
    for finding in cfg["findings"]:
        a(f"**{finding['section']}:** {finding['assessment']}  ")
        a(f"Recommendation: {finding['recommendation']}")
        a("")
    a(f"> **Authorization note:** {cfg['authorization_note']}")
    a("")
    a("---")
    a("")
    a("## 8. Remaining Gaps After Archive Review")
    a("")
    a("### IBM Gaps Remaining: **NONE**")
    a("")
    a("All 14 IBM gaps have candidate signals in the archive with HIGH or MEDIUM confidence.")
    a("")
    a("### Unify Gaps Remaining (14 of 18 unresolved):")
    a("")
    keep_internal = [
        g for g in unify_gaps_all
        if "KEEP_INTERNAL" in g["status"]
    ]
    rejected = [g for g in unify_gaps_all if "REJECT" in g["status"]]
    a("**KEEP_INTERNAL (10)** — exist as ACTIVE skill nodes but lack archive-employer-level source evidence:")
    for g in keep_internal:
        a(f"- `{g['gap']}`: {g['reason'][:100]}")
    a("")
    a("**REJECTED (3)** — not present anywhere in archive:")
    for g in rejected:
        a(f"- `{g['gap']}`: {g['reason']}")
    a("")
    a("---")
    a("")
    a("## Non-Claims")
    a("")
    a("- This report does NOT claim live runtime proof.")
    a("- No archive prose has been copied or paraphrased into final resume bullets.")
    a("- No agentic_core files were modified.")
    a("- No X2 or X3 gates were weakened.")
    a("- No config files were modified.")
    a("- Promotion decisions in this report are planning outputs only; execution requires separate authorization.")
    a("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    json_path = "docs/reports/apps_rg/phase1_resume_archive_graph_gap_fill.json"
    md_path = "docs/reports/apps_rg/phase1_resume_archive_graph_gap_fill.md"
    write_json_report(json_path)
    write_md_report(md_path)
    print(f"JSON written: {json_path}")
    print(f"MD  written: {md_path}")
    # Validate JSON round-trip
    with open(json_path, encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["report_metadata"]["report_id"] == "phase1_resume_archive_graph_gap_fill"
    assert len(loaded["candidate_signals"]) == len(CANDIDATE_SIGNALS)
    assert len(loaded["metric_reconciliation"]) == len(METRIC_RECONCILIATION)
    print(f"JSON validates OK: {len(loaded['candidate_signals'])} signals, {len(loaded['metric_reconciliation'])} metrics")
