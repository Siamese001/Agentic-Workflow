# Unify / IBM Skill-Emphasis Split — Proposal (for review)

_2026-06-11. Companion to [archive_skill_lane_alignment_audit.md](archive_skill_lane_alignment_audit.md) (498 archive skills mapped). Constraint set by operator: Unify mostly Agentic; IBM a mix of all; Partnerships is the most critical domain (Anthropic / OpenAI-class partner-role opportunities); JD + briefing decide final per-run highlighting._

## 1. How a "% split" actually manifests in apps_rg

There is no numeric weighting knob per lane. Emphasis materializes through three levers:

1. **Bundle inventory** — each employer lane selects ~3 of its role-episode bundles by JD fit. The bundle mix IS the ceiling: a domain with no bundle gets 0% no matter what the JD says.
2. **Base-bullet anchors** — each bundle anchors a base-resume bullet; 3 of N bullets ship per employer.
3. **JD-driven selection** — `format_jd_targeting_block` + selection plans choose which bundles/facts surface per run.

So the proposal below = target bundle-inventory shares + which bundles the selector should prefer per JD archetype.

## 2. Unify (current role) — target mix

| Theme | Today (6 bundles) | Target share | Bundles |
|---|---|---|---|
| Agentic AI platform, governance, productization | 5 of 6 bundles (~83%) | **55–60%** | agentic_platform_architecture, runtime_reliability_governance, production_adoption_lifecycle, platform_commercialization_leadership |
| **Partnerships / Co-sell / Channel GTM** | **0 bundles (0%)** | **25–30%** | **NEW: `reb_unify_partner_channel_cosell`** — global AI channel program from inception ($3M partner-derived revenue), Confluent/AWS co-sell bundling (+30% upsell), consumption-based SaaS licensing (93% renewal), $5M ACV CFO-aligned enterprise adoption. All four claims already exist as confirmed facts (`fact_partnerships_gtm_001`, `fact_sales_accounts_005/004/001`). |
| Data platform / retrieval / FSI grounding | 1–2 bundles | **15%** | dependency_graph_accelerator, distributed_ecosystem_engineering |

## 3. IBM — target mix (mix of all)

| Theme | Today (7 bundles) | Target share | Bundles |
|---|---|---|---|
| **Partnerships / IBM-AWS alliance co-sell** | 1 bundle | **25%** | hyperscaler_alliance_partner (joint revenue, co-sell, accreditations) |
| **Pre-sales / GTM / enterprise deal leadership** | 1 bundle — **but its `section_eligibility` is EMPTY → effectively 0% today** | **20%** | technical_presales_gtm (discovery→qualification→solution mapping→executive buyer alignment→deal support; $15M deals, $10M ARR Salesforce pipeline) |
| Cloud / data platform modernization | 2 bundles | **20%** | cloud_modernization, streaming_realtime_analytics |
| FSI risk / credit / regulatory | 2 bundles | **20%** | hpc_risk_analytics, metadata_audit_governance (+ credit adjudication −15% default via `fact_credit_001`) |
| DevSecOps / governance | 1 bundle | **15%** | devsecops_reliability |

## 4. JD-adaptive highlighting (the selector's preference order)

| JD archetype | Unify preference | IBM preference |
|---|---|---|
| **Partner/alliances role (Anthropic, OpenAI, hyperscalers)** | Agentic 45% / **Partnerships-GTM 40%** / Data-FSI 15% — lead with channel-program + co-sell bundle, agentic platform as the credibility spine | **Partnerships 35% / Pre-sales GTM 30%** / Cloud-data 15% / FSI 10% / Governance 10% |
| **AIG (current JD/briefing)** | Agentic 60% / FSI+process 25% / Partnerships 15% — partnerships surfaces via the JD's own "co-lead AI platform evaluations across Anthropic, AWS, Palantir" hook | FSI 30% / Cloud-data 20% / Partnerships 20% / Pre-sales 15% / Governance 15% |
| **Enterprise AI platform leadership (generic)** | Agentic 60% / Partnerships 20% / Data-FSI 20% | Balanced 20×5 |

## 5. What blocks this split today (ranked by yield)

| # | Blocker | Fix | Yield |
|---|---|---|---|
| 1 | `reb_ibm_technical_presales_gtm.section_eligibility` is **EMPTY** | one-line bundle edit (`["ibm_bullets","ibm_narrative"]`) | unlocks the entire IBM pre-sales/GTM theme (7 bound skills) |
| 2 | **No Unify partner bundle** — 92 PARTIAL rows trace to "not bundle-bound"; every Unify partnerships claim is unreachable in unify lanes | mint `reb_unify_partner_channel_cosell` + one Unify base bullet anchor | unlocks the entire Unify partnerships theme (~13 archive skills) |
| 3 | Partner skills section-listed but bundle-orphaned (`partner_engineering`, `partner_led_ai_solutions`, `partner_revenue_3m`, `cloud_vendor_joint_gtm`, `gtm_joint_vendor_roadmaps`, `aws_ecosystem`…) | bind into the new Unify bundle + `ccb_partnerships_ecosystem_execution` competency bundle | partnerships density in competencies + exec summary |
| 4 | Customer-success skills have **empty `fact_id_links`** (NRR-20%, CSAT-25%/NPS, churn-risk) → exec-ineligible | link the existing renewal/churn facts where they genuinely back the claim; mint CS facts otherwise (needs confirmation) | unlocks CUSTOMER_SUCCESS (today 1 of 22 fully mapped) |
| 5 | 3 DRAFT skills: MEDDPICC, CPQ, SaaS ARR/LTV/CAC metrics | confirm + activate + fact-link | sales-ops depth for partner/sales JDs |
| 6 | Employer-attribution mismatches (Salesforce/CRM analytics ledger says IBM, archive says Unify too; `co_selling` bound only to IBM lanes) | add Unify-attributed fact / bind co_selling into Unify bundle | removes WRONG_EMPLOYER_LANE class (32 rows) |
| 7 | 21 MISSING claims (variable-comp design, sales playbooks/enablement, engagement-profitability, Gainsight cert, partner-delivered automation −25%, investor-relations/cap-structure set…) | mint facts **only after operator confirmation** (no fabrication) | closes the long tail |

_No gate, schema, or rubric changes anywhere in this proposal — content/bundle layer only._
