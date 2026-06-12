# Unify / IBM Skill-Emphasis Split — Proposal (for review)

_2026-06-11. Companion to [archive_skill_lane_alignment_audit.md](archive_skill_lane_alignment_audit.md) (498 archive skills mapped). Constraint set by operator: Unify mostly Agentic; IBM a mix of all; Partnerships is the most critical domain (Anthropic / OpenAI-class partner-role opportunities); JD + briefing decide final per-run highlighting._

> ⛔ **SUPERSEDED by the DYNAMIC model (2026-06-11, operator directive).** A static % per
> employer cannot work in an ATS-driven recruiting environment: the same profile must read
> ~100% agentic for an SVP-Agentic-Engineering JD and 70-80% partnerships for an Anthropic
> AI-Partnerships JD. The emphasis is now **computed per-JD from approved graph skills** — no
> hardcoded caps. Mechanism (shipped this session):
> 1. **Functional pillar-weight scoring** (`track_weighted_graph_expansion`): a skill's score =
>    career-track weight × `profile.top_weighted_pillars[skill.pillar]`. Fixed a dead lookup
>    (`role_family_weights` keyed by taxonomy id but looked up by projection key → always 0.0).
>    Drives exec_summary + competencies. **Proven swing: Anthropic-partnerships JD → 63% partner /
>    22% agentic; SVP-eng JD → 0% partner / 66% agentic** — same approved skill set.
> 2. **JD-fit bundle selection** (`jd_fit_bundle_selection`): experience-lane bullet slots rank
>    role-episode bundles by the same pillar weighting. **Unify bullets: partnerships JD → 2/6
>    partner; eng JD → 0/6 (identical to static, zero regression).**
> 3. **Calibration** lives in `role_family_projection_profiles[*].top_weighted_pillars` +
>    `deprioritize_pillars` — tune emphasis there, never with a static %.
>
> The tables below are retained as the **bundle-inventory** reference (what candidates exist per
> employer); the *shares* are now emergent, not prescribed.

## 1. How a "% split" actually manifests in apps_rg

There is no numeric weighting knob per lane. Emphasis materializes through three levers:

1. **Bundle inventory** — each employer lane selects ~3 of its role-episode bundles by JD fit. The bundle mix IS the ceiling: a domain with no bundle gets 0% no matter what the JD says.
2. **Base-bullet anchors** — each bundle anchors a base-resume bullet; 3 of N bullets ship per employer.
3. **JD-driven selection** — `format_jd_targeting_block` + selection plans choose which bundles/facts surface per run.

So the proposal below = target bundle-inventory shares + which bundles the selector should prefer per JD archetype.

## 2. Unify (current role) — target mix (OPERATOR-CONFIRMED 2026-06-11)

| Theme | Today (6 bundles) | Target share | Bundles |
|---|---|---|---|
| **Agentic / Deep Technical Engineering** | 5 of 6 bundles (~83%) | **70%** | agentic_platform_architecture, runtime_reliability_governance, production_adoption_lifecycle, platform_commercialization_leadership, dependency_graph_accelerator, distributed_ecosystem_engineering |
| **AI Partnerships / Co-sell Channel** | **0 bundles (0%)** | **30% (OPERATOR-CONFIRMED)** | **NEW: `reb_unify_partner_channel_cosell`** — global AI channel program from inception ($3M partner-derived revenue), Confluent/AWS co-sell bundling (+30% upsell), consumption-based SaaS licensing (93% renewal), $5M ACV CFO-aligned enterprise adoption. All four claims already exist as confirmed facts (`fact_partnerships_gtm_001`, `fact_sales_accounts_005/004/001`). |

> Data platform / retrieval / FSI grounding (dependency_graph_accelerator, distributed_ecosystem_engineering) folds INTO the 70% "Agentic / Deep Technical Engineering" bucket — it is the technical substrate of the agentic platform story, not a separate share.

## 3. IBM — target mix (OPERATOR-CONFIRMED 2026-06-11)

> ⛔ **Correction (operator, 2026-06-11): IBM = 0% risk / credit / regulatory — that domain is EY's story.** The IBM `hpc_risk_analytics` + Basel/CCAR-regulatory assets and `fact_credit_001` are dropped from IBM lane emphasis (re-homed to EY or de-emphasized — see open question §6).

| Theme | Today (7 bundles) | Target share | Bundles |
|---|---|---|---|
| **Partnerships / IBM-AWS alliance co-sell** | 1 bundle | **30%** | hyperscaler_alliance_partner (joint revenue, co-sell, accreditations) |
| **Pre-sales / GTM / enterprise deal leadership** | 1 bundle — **but its `section_eligibility` is EMPTY → effectively 0% today** | **30%** | technical_presales_gtm (discovery→qualification→solution mapping→executive buyer alignment→deal support; $15M deals, $10M ARR Salesforce pipeline) |
| Cloud / data platform modernization | 2 bundles | **25%** | cloud_modernization, streaming_realtime_analytics |
| DevSecOps / governance | 1–2 bundles | **15%** | devsecops_reliability, metadata_audit_rbac (RBAC/audit-trail half only — Basel/CCAR regulatory skill removed) |
| ~~FSI risk / credit / regulatory~~ | ~~2 bundles~~ | **0% → moved to EY** | hpc_risk_analytics dropped from IBM; Basel/CCAR → EY regulatory bundle; credit → see §6 |

## 4. JD-adaptive highlighting (the selector's preference order)

Baseline (operator-confirmed): **Unify 70 Agentic / 30 Partnerships**; **IBM 30 Partnerships / 30 Pre-sales-GTM / 25 Cloud-Data / 15 DevSecOps-Governance / 0 risk-credit-reg**. The selector nudges WITHIN these caps by JD fit:

| JD archetype | Unify nudge | IBM nudge |
|---|---|---|
| **Partner/alliances role (Anthropic, OpenAI, hyperscalers)** | Push Partnerships to the top of the 30% — lead with channel-program + co-sell bundle, agentic platform as the credibility spine | Lead **Partnerships 30 + Pre-sales 30** (60% partner-facing); Cloud-data 25; Governance 15 |
| **AIG (current JD/briefing)** | Agentic 70 forward (process re-engineering / governed autonomy); Partnerships surfaces via the JD's own "co-lead AI platform evaluations across Anthropic, AWS, Palantir" hook | Cloud-data + Pre-sales forward; Partnerships via hyperscaler-alliance; Governance steady |
| **Enterprise AI platform leadership (generic)** | Agentic 70 / Partnerships 30 as-is | Even across the four IBM themes |

_Note: insurance/FSI risk depth still surfaces strongly — but via the **EY** lane (Solvency II/AG43, ERM three-lines/BCBS 239, regulatory analytics), not IBM._

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

## 6. OPEN QUESTION — where does `fact_credit_001` belong? (blocks the IBM build)

I minted `fact_credit_001` (AI-driven credit adjudication, −15% default exposure) as an **IBM** fact. The operator directive "credit = EY" conflicts with that attribution, and I must not silently re-home a factual claim about where work was done. Three options:

1. **Re-attribute to EY** — the credit/risk work was EY consulting; move the fact + `skill_credit_adjudication_default_risk` into an EY bundle.
2. **Keep IBM-attributed, drop from IBM emphasis** — the engagement was IBM, but the resume shouldn't foreground it in the IBM lane.
3. **Early-career / other** — it belongs to a different period.

`hpc_risk_analytics` (Greek stress testing) traces to `fact_sales_accounts_002` ("$15M deals demonstrating ROI on HPC stress-testing simulations") — that is an **IBM sales/GTM** story (selling HPC), so it stays in IBM under Pre-sales/GTM, NOT risk. Basel/CCAR (`skill_sr_basel_ccar_lineage_regulatory`) is already shared with the EY regulatory bundle → cleanly removed from IBM.

_No gate, schema, or rubric changes anywhere in this proposal — content/bundle layer only._
