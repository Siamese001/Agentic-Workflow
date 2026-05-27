# DRAFT Skill Triage Report — 2026-05-27

Total DRAFT skills: **56**  
Action required: for each row select PROMOTE | DEFER | BLOCK

## Column Guide
- **PROMOTE**: provide a `linked_fact_id` and mark `ACTIVE_CONFIRMED`
- **DEFER**: skill is real but no source evidence yet — leave DRAFT
- **BLOCK**: skill is not externally claimable — set `activation_status: BLOCKED`

---

## Triage Table

| # | skill_id | pillar | support_level | has_facts | suggested_fact | Decision |
|---|----------|--------|---------------|-----------|----------------|----------|
| 1 | `skill_derivatives_exotic_options` | derivatives_structured | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 2 | `skill_derivatives_structured_derivatives` | derivatives_structured | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 3 | `skill_insurance_liabilities_embedded_options` | embedded_options_insuranc | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 4 | `skill_insurance_liabilities_insurance_liabilities` | embedded_options_insuranc | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 5 | `skill_greeks_gamma` | greeks_hedging | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 6 | `skill_greeks_vega` | greeks_hedging | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 7 | `skill_greeks_theta` | greeks_hedging | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 8 | `skill_greeks_delta` | greeks_hedging | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 9 | `skill_greeks_rho` | greeks_hedging | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 10 | `skill_greeks_convexity` | greeks_hedging | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 11 | `skill_risk_greek_stress_testing` | risk_management | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 12 | `skill_capital_reserving` | capital_modeling | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 13 | `skill_capital_pricing_actuarial` | capital_modeling | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 14 | `skill_actuarial_actuarial_software` | actuarial_foundation | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 15 | `skill_risk_market_risk` | risk_management | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 16 | `skill_partner_aws_ecosystem` | cloud_data_aws | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 17 | `skill_partner_cloud_partner_ecosystem` | cloud_data_aws | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 18 | `skill_partner_partner_motions` | partner_gtm_alliances | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 19 | `skill_partner_partner_engineering` | cosell_partner_engineerin | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 20 | `skill_partner_pre_sales` | presales_solutioning | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 21 | `skill_partner_workshops` | presales_solutioning | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 22 | `skill_partner_enterprise_negotiations` | customer_stakeholder | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 23 | `skill_partner_gtm_enablement` | partner_gtm_alliances | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 24 | `skill_partner_product_feedback_loops` | partner_gtm_alliances | USER_CONFIRMED_PENDING_SOURCE | ✗ | — | ? |
| 25 | `skill_partner_pnl_oversight` | revenue_commercialization | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 26 | `skill_revops_sales_forecasting_frameworks` | revenue_operations | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 27 | `skill_revops_multi_channel_gtm_alignment` | revenue_operations | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 28 | `skill_customer_nrr_predictive_analytics_20pct` | customer_stakeholder | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 29 | `skill_customer_satisfaction_nps_25pct` | customer_stakeholder | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 30 | `skill_commercial_board_level_stakeholder_alignment` | executive_leadership | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 31 | `skill_commercial_gtm_investment_pipeline` | revenue_operations | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 32 | `skill_p2_gtm_commercial_validation_pilots` | gtm_presales_motion | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 33 | `skill_p2_gtm_presales_delivery_handoff` | gtm_presales_motion | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 34 | `skill_p2_tech_demoable_accelerator` | technical_presales_accele | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 35 | `skill_p2_tech_adoption_derisking` | technical_presales_accele | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 36 | `skill_p2_tech_ibm_cloud_portfolio_anchor` | technical_presales_accele | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 37 | `skill_p2_tech_estimation_sizing_directional` | technical_presales_accele | INTERNAL_ONLY | ✗ | — | ? |
| 38 | `skill_p2_anchor_major_airline_devops_aws` | technical_presales_accele | INTERNAL_ONLY | ✗ | — | ? |
| 39 | `skill_sr_insurance_systems_resilience_internal` | underwriting_claims_ops_a | INTERNAL_ONLY | ✓ | — | ? |
| 40 | `skill_sr_regulated_financial_institutions_fluency` | banking_platform_responsi | DIRECT_FROM_RESUME_ARCHIVE | ✗ | — | ? |
| 41 | `skill_intent_interpretation_and_ambiguity_framing` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 42 | `skill_bounded_planning_contracts` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 43 | `skill_lowest_viable_agency_design` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 44 | `skill_task_decomposition_for_agentic_workflows` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 45 | `skill_planning_prior_and_policy_context_use` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 46 | `skill_workflow_checkpointing_and_resumability` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 47 | `skill_tool_and_model_registry_control` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 48 | `skill_same_authority_runtime_repair` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 49 | `skill_schema_and_output_repair` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 50 | `skill_deterministic_trim_and_reformat` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 51 | `skill_multi_judge_calibration` | regulatory_governance | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 52 | `skill_trace_and_reconstruction_design` | regulatory_governance | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 53 | `skill_shadow_learning_design` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 54 | `skill_completed_run_evaluation` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 55 | `skill_future_run_calibration` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |
| 56 | `skill_eval_regression_and_gauntlet_design` | agentic_ai_platforms | REPO_EVIDENCE_PORTFOLIO | ✗ | — | ? |

---

## Instructions

1. Fill the Decision column for each row.
2. For PROMOTE rows: add `linked_fact_id` to the `apply_draft_skill_promotions_20260527.py` script.
3. Run `python apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py` after promotions.
4. Run `python apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py` to rebuild SQLite.

Human confirmation required: `human_confirmed_by: Amit Ayer` with timestamp on each promoted skill.