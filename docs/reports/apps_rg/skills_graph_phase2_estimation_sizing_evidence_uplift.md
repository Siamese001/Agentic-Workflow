# Phase 2 estimation/sizing — evidence uplift audit

**Promotion decision:** DO_NOT_PROMOTE
**Proof classification:** NO_PROMOTION_ADJACENT_EVIDENCE_WRONG_DOMAIN

## Candidate evidence table

| Theme | Evidence type | Supports target? | Confidence | linked_fact_id | Source |
|-------|---------------|------------------|------------|----------------|--------|
| estimation_models | financial_modeling | False | MEDIUM | `fact_revenue_ops_005` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| sizing_models | financial_modeling | False | MEDIUM | `fact_revenue_ops_003` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| architecture_sizing | delivery_estimation | False | LOW | `—` | master_skills_arsenal_ledger.json |
| capacity_planning | financial_modeling | False | MEDIUM | `fact_quant_hpc_001` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| cost_modeling | financial_modeling | False | MEDIUM | `fact_revenue_ops_004` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| cost_modeling | financial_modeling | False | HIGH | `bul_insurtech_001` | amit_ayer_base_resume_v1.json |
| migration_sizing | delivery_estimation | False | HIGH | `bul_ibm_002` | amit_ayer_base_resume_v1.json |
| cloud_workload_estimation | delivery_estimation | False | MEDIUM | `fact_engineering_platform_005` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| delivery_effort_estimation | delivery_estimation | False | LOW | `—` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| commercial_pursuit_sizing | commercial_sizing | False | MEDIUM | `fact_revenue_ops_001` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| roi_business_case_sizing | commercial_sizing | False | MEDIUM | `fact_solutions_001` | exec_summary_fact_ledger_expansion_audit.json |
| roi_business_case_sizing | commercial_sizing | False | MEDIUM | `fact_sales_accounts_002` | master_candidate_skills_fact_ledger_20260518T1100Z.json |
| estimation_models | financial_modeling | False | HIGH | `fact_ma_synergy_modeling_001` | master_experience_ledger_archive_audit.json |
| sizing_models | financial_modeling | False | HIGH | `—` | master_candidate_skills_fact_ledger_20260518T1100Z.json |

## Promotion decision

Repo contains financial/commercial modeling (synergy models, usage-based forecasting, ROI deal proof) and cost/TCO outcomes, but no source-backed technical pre-sales estimation or sizing methodology (architecture sizing, cloud workload estimation, migration sizing, delivery effort models). Adjacent evidence is already represented on other skill rows; bridging would over-claim.

## Next blocker

Ingest resume/archive text naming sizing methodology (e.g., cloud workload estimates, migration effort models, pursuit sizing worksheets) with role scope — then re-run audit before promoting skill_p2_tech_estimation_sizing_directional.
