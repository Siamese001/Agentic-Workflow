# Skills graph commercial expansion closeout

**Status:** PASS
**Generated:** 2026-05-18T23:33:34Z

## Before / after

| Metric | Before | After |
|--------|--------|-------|
| pillar_count | 19 | 19 |
| skill_row_count | 121 | 131 |
| projection_profile_count | 9 | 9 |

## New skill rows

- `skill_sales_modernization_deals_15m` — Amit_Ayer_Resume_-_Strategic_Account_Executive.txt — pillar `pillar_revenue_commercialization`
- `skill_sales_global_financial_institutions_leadership` — Sales_-_Amit_Ayer.txt — pillar `pillar_customer_stakeholder`
- `skill_partner_ibm_aws_alliance_joint_revenue` — Partnerships_Alliances_-_Amit_Ayer.txt — pillar `pillar_partner_gtm_alliances`
- `skill_partner_cloud_vendor_joint_gtm` — Sales_-_Amit_Ayer.txt — pillar `pillar_partner_gtm_alliances`
- `skill_finance_cost_optimization_dashboards` — Strategic_Finance_-_Amit_Ayer.txt — pillar `pillar_strategic_finance_saas`
- `skill_finance_ma_synergy_due_diligence` — Strategic_Finance_-_Amit_Ayer.txt — pillar `pillar_strategic_finance_saas`
- `skill_customer_nrr_predictive_analytics_20pct` — Head_of_Customer_Success_-_Amit_Ayer.txt — pillar `pillar_customer_stakeholder`
- `skill_customer_satisfaction_nps_25pct` — Head_of_Customer_Success_-_Amit_Ayer.txt — pillar `pillar_customer_stakeholder`
- `skill_commercial_board_level_stakeholder_alignment` — Sales_-_Amit_Ayer.txt — pillar `pillar_executive_leadership`
- `skill_commercial_gtm_investment_pipeline` — Amit_Ayer_Resume_-_VP_Finance_Sales_Marketing.txt — pillar `pillar_revenue_operations`

## Patched existing skill row

- `skill_partner_partner_revenue_3m` → `fact_partnerships_gtm_001` (`DERIVED_SUPPORTED`)

## Verification

| Command | Result |
|---------|--------|
| `apply_cro_projection_hardening.py` | exit 0 |
| `apply_commercial_skills_expansion.py` | exit 0 |
| `python -m json.tool master_skills_arsenal_ledger.json` | exit 0 |
| `pytest tests/unit/apps_rg/fact_inventory` | 81 passed |
| `pytest -k "skills or arsenal or srfs or role_family"` | 197 passed, 1 skipped |

## Rejected facts

- `fact_customer_success_001`: LOW confidence; archive-backed CS skills used instead of authoritative fact link
- `fact_sales_accounts_004`: NEEDS_VERIFICATION; 93% renewal rate not wired
- `fact_sales_accounts_005`: NEEDS_VERIFICATION; CRM forecasting uplift not wired

## Unsupported gaps

- **marketing_demand_generation**: No MEDIUM/HIGH candidate facts; only narrative marketing language in variants
- **primary_quota_carrying_ae**: No confirmed personal quota scope as primary AE accountability
- **board_investor_relations_primary**: Board alignment phrasing only; no investor-relations primary role evidence
- **marketing_org_pnl**: VP Finance Sales & Marketing title does not establish marketing org P&L ownership
