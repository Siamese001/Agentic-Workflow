# Master Skills Arsenal Ledger — Design

Generated: 2026-05-18T19:28:28Z

## Design principles

- Arsenal != two-page resume: skills inventory is superset; section generation projects subsets.
- Phase I variants are evidence artifacts, not SSOT—base resume + confirmed facts are SSOT.
- USER_CONFIRMED_PENDING_SOURCE blocks external activation until snippet attached.
- No JD/briefing as proof; TARGETING_ONLY for emphasis.

## Arsenal taxonomy summary

**18** capability pillars.

### Agentic AI Platforms (`pillar_agentic_ai_platforms`)
Governed agentic runtime, routing, orchestration, GraphRAG, policy gates, validation, replayable traces.

### Cloud / Data / AWS (`pillar_cloud_data_aws`)
AWS/Databricks lakehouse, microservices, vector services, API gateways, identity, HPC on cloud.
- **Pending source:** azure_depth_beyond_archive_snippets

### Partner GTM / Alliances (`pillar_partner_gtm_alliances`)
Channel programs, strategic alliances, ecosystem GTM, IBM–AWS alliance motions.
- **Pending source:** anthropic_style_applied_ai_partnership_motion

### Co-selling / Partner Engineering (`pillar_cosell_partner_engineering`)
Co-sell frameworks, partner engineering delivery, bundled partner offers, technical enablement for partners.
- **Pending source:** partner_engineering_depth_beyond_co_sell_wording

### Pre-sales / Solutioning (`pillar_presales_solutioning`)
Executive workshops, pilots, ROI validation, solution architecture in pursuit cycles.
- **Pending source:** pre_sales_quota_carrying

### Revenue Ownership / Commercialization (`pillar_revenue_commercialization`)
IP-led revenue, margins, ARR growth, sales targets, P&L/partner revenue accountability.
- **Pending source:** owning_sales_and_revenue_targets_as_primary_role

### Executive Leadership / Operating Model (`pillar_executive_leadership`)
C-suite alignment, cross-functional scale-out, operating model, org design.

### Actuarial Foundation (`pillar_actuarial_foundation`)
FSA, early-career actuarial depth, stochastic modeling, actuarial software—not credential label only.
- **Pending source:** actuarial_depth_beyond_archive_employer_detail

### Embedded Options / Insurance Liabilities (`pillar_embedded_options_insurance`)
Insurance liability and embedded-options valuation context from actuarial career.
- **Pending source:** embedded_options, insurance_liabilities, embedded_options_in_insurance_products

### Derivatives / Structured Derivatives (`pillar_derivatives_structured`)
Derivatives pricing, complex/structured derivatives, exotic options.
- **Pending source:** structured_derivatives_explicit

### Greeks / Hedging (`pillar_greeks_hedging`)
Multi-Greek hedging, Greek stress tests, hedging frameworks.
- **Pending source:** delta, rho, convexity_as_individual_claims

### Risk Management (`pillar_risk_management`)
Enterprise risk analytics, portfolio risk, market risk, model risk themes.
- **Pending source:** enterprise_risk_management_officer_title

### Enterprise Risk / Controls (`pillar_enterprise_risk_controls`)
Usage controls, compliance checkpoints, encryption, access controls, audit readiness.

### Regulatory Governance (`pillar_regulatory_governance`)
Basel, CCAR, FINRA/SEC alignment, regulatory reporting, lineage/cataloging.

### Capital Modeling / Reserving / Pricing (`pillar_capital_modeling`)
Capital models, reserving, pricing, capital adequacy, regulatory capital.
- **Pending source:** reserving_signoff_authority

### Trading / HPC / Market Forecasting (`pillar_trading_hpc`)
Algorithmic trading, HPC, sub-ms latency, GPU forecasting, market-making.

### Strategic Finance / SaaS Metrics (`pillar_strategic_finance_saas`)
FP&A, ARR, churn, LTV/CAC, M&A synergy, investor relations.

### Customer / Enterprise Stakeholder Leadership (`pillar_customer_stakeholder`)
CFO/CRO alignment, enterprise negotiations, customer success motions, renewal/expansion.

## Actuarial career matrix

22 rows in JSON (`actuarial_career_matrix`). **9** rows are `USER_CONFIRMED_PENDING_SOURCE`.

| Skill | Support | Archive evidence | Exec use |
|-------|---------|------------------|----------|
| derivatives_pricing | DIRECT | Towers Perrin / ING / Aetna | yes |
| multi_greek_hedging | DIRECT | exotic options hedges | yes |
| exotic_options | DIRECT | Quant Research exec summary | competencies |
| gamma / vega / theta | DIRECT | AI Financial Services | competencies |
| capital_modeling | DIRECT | AI Governance early career | yes |
| FSA fellowship | DIRECT | FSA earned 2010 | yes |
| embedded_options | PENDING | user-confirmed | early_career after source |
| structured_derivatives | PENDING | user-confirmed | early_career after source |
| delta / rho / convexity | PENDING | user-confirmed | after source |

## Partner / GTM matrix

16 rows in JSON (`partner_gtm_matrix`). Archive-backed co-sell, AWS/IBM–AWS alliance, workshops, revenue targets; **partner_engineering** and **product_feedback_loops** are PENDING.

| Skill | Support | Notes |
|-------|---------|-------|
| co_selling | DIRECT | SIs and ISVs |
| aws_ecosystem | DIRECT | AWS Partner accreditation block |
| partner_motions | DIRECT | global AI channel program |
| pre_sales / workshops | DIRECT | executive workshops, pilots |
| sales_revenue_targets | DIRECT | 110% (TraderSense context) |
| partner_engineering | PENDING | user-confirmed |

## Schema extension

See JSON `schema_extension.skill_row_fields`.

## Role-family projection map

- **SVP Engineering / AI Platform**: pillar_agentic_ai_platforms, pillar_cloud_data_aws, pillar_executive_leadership
- **AI Financial Services**: pillar_regulatory_governance, pillar_enterprise_risk_controls, pillar_agentic_ai_platforms
- **Anthropic-style Partnerships / Applied AI**: pillar_partner_gtm_alliances, pillar_cosell_partner_engineering, pillar_presales_solutioning
- **Field CTO**: pillar_presales_solutioning, pillar_cloud_data_aws, pillar_agentic_ai_platforms
- **Chief AI Officer**: pillar_agentic_ai_platforms, pillar_regulatory_governance, pillar_executive_leadership
- **Strategic Finance**: pillar_strategic_finance_saas, pillar_capital_modeling, pillar_actuarial_foundation
- **Quant / Trading**: pillar_trading_hpc, pillar_greeks_hedging, pillar_derivatives_structured
- **Governance / Risk**: pillar_regulatory_governance, pillar_enterprise_risk_controls, pillar_risk_management

## Executive summary impact

Exec SRFS treats FSA as cert label; omits quant_hpc_003 and partner/co-sell depth.


## Caveat

Embedded options, structured derivatives, insurance liabilities, delta/rho/convexity, and partner engineering are USER_CONFIRMED_PENDING_SOURCE—no dedicated archive lines found. Archive 'embedded' elsewhere means DevSecOps/embedded analytics, not insurance embedded options. Revenue-target claims are context-specific (e.g., TraderSense 110%); verify employer scope before activation.
