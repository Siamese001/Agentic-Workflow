# Senior-Role Augmented Skills Graph — Read-Only Gap Analysis

**AUDIT_ID:** `senior_role_graph_gap_analysis_20260520`  
**PLAN_ID:** `phase2-gtm-presales-remaining-f7a2c9`  
**Generated:** 2026-05-20 (UTC)  
**Authority:** `augmented_skills_graph` (`master_skills_arsenal_ledger.json`)  
**Proof class:** Audit-only / read-only — no graph, runtime, prompt, or validator patches in this wave.

---

## Executive summary

Phase 2 GTM/pre-sales **graph augmentation and consumption are proven** for `TRACK_DATA_TECH_CLOUD_ML`, but the graph is **too narrow for senior-role traversal** across Phase 1 (actuarial/insurance/risk), Phase 2 (GTM/partner/presales), and Phase 3 (agentic AI platform). The dominant failure modes are **taxonomy conflation** (carrier vs brokerage vs banking vs generic FS), **missing phase-bridge edges** (0 edges from actuarial/insurance/regulatory pillars to agentic/GTM pillars), **DRAFT partner/hyperscaler skills**, and **executive_summary SRFS policy** that correctly blocks MEDIUM facts but causes **undermatch** for domain-heavy roles.

---

## STATUS / receipt

| Field | Value |
|-------|--------|
| **STATUS** | PASS (audit complete; no implementation) |
| **SCOPE_MATCH** | Yes — diagnostic only per plan guardrails |
| **FILES_CHANGED** | None (reports only) |
| **GAPS_FOUND_COUNT** | 18 |
| **P0_GAPS** | 6 |
| **P1_GAPS** | 8 |
| **P2_GAPS** | 3 |
| **P3_GAPS** | 1 |
| **PROOF_CLASSIFICATION** | `audit_only_readonly` |
| **RECOMMENDED_NEXT_WAVE** | Plan update Wave 0.5: senior-role taxonomy + edge backlog + HITL/evidence gates **before** graph edits |

### COMMANDS_RUN

| Command | Exit code | Notes |
|---------|-----------|--------|
| `python apps_rg/fact_inventory/validate_commercial_srfs_projection.py` | 0 | Wrote [commercial_skills_srfs_projection_validation.json](docs/reports/apps_rg/commercial_skills_srfs_projection_validation.json) |
| `python apps_rg/fact_inventory/validate_commercial_medium_claim_output_containment.py` | 1 | `SectionFrontSpinePreconditionError` — needs runtime spine fixtures; not a graph defect |
| `python -m apps_rg.fact_inventory.validate_p2_graph_skills_accelerated_closeout` | 1 | Module not on path; used [skills_graph_phase2_gtm_presales_closeout.json](docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json) instead |

### ARTIFACTS_WRITTEN

- [senior_role_graph_gap_analysis.md](docs/reports/apps_rg/senior_role_graph_gap_analysis.md)
- [senior_role_graph_gap_analysis.json](docs/reports/apps_rg/senior_role_graph_gap_analysis.json)

### INPUTS_INSPECTED

- [master_skills_arsenal_ledger.json](apps_rg/fact_inventory/master_skills_arsenal_ledger.json)
- [skills_graph_phase2_gtm_presales_closeout.json](docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json)
- [skills_graph_phase2_section_projection_audit.json](docs/reports/apps_rg/skills_graph_phase2_section_projection_audit.json)
- [skills_graph_phase2_airline_anchor_evidence_uplift.json](docs/reports/apps_rg/skills_graph_phase2_airline_anchor_evidence_uplift.json)
- [skills_graph_phase2_estimation_sizing_evidence_uplift.json](docs/reports/apps_rg/skills_graph_phase2_estimation_sizing_evidence_uplift.json)
- [commercial_claim_eligibility.yaml](apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml)
- [master_role_family_taxonomy.yaml](apps_rg/config/domain_contract/master_role_family_taxonomy.yaml)
- [track_weighted_graph_expansion.py](apps_rg/fact_inventory/track_weighted_graph_expansion.py)
- [master_candidate_skills_fact_ledger_20260518T1100Z.json](artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json)
- [selected_role_fact_set_active_manifest.json](artifacts/apps_rg/fact_inventory/selected_role_fact_set_active_manifest.json)
- [exec_summary_20260520_094345](artifacts/apps_rg/runtime_proofs/executive_summary/mock/exec_summary_20260520_094345) (mock, non-certifying)

---

## CURRENT_GRAPH_SUMMARY

| Dimension | Value |
|-----------|--------|
| Pillars | 21 (incl. `pillar_gtm_presales_motion`, `pillar_technical_presales_accelerators`) |
| Skill rows | 148 |
| Graph edges | 1,281 |
| Career tracks | `track_actuarial_risk_derivatives`, `track_data_tech_cloud_ml`, `track_genai_agentic` |
| Active / ACTIVE_CONFIRMED skills | 94 |
| DRAFT skills | 54 |
| Pillar→pillar edges | **0** |
| Actuarial/insurance/reg → agentic/GTM/partner edges | **0** |
| Default track weight (genai) | **0.65** vs actuarial **0.10** |

**Proven (GTM baseline):** Closeout PASS; C03 track expansion selects **10** ACTIVE P2 skills under GTM-heavy JD; graph authority is `augmented_skills_graph` only.

**Open (all senior examples):** Claim materialization, phase bridges, role-family targeting slices, partner DRAFT activation, exec_summary MEDIUM/HITL path, X2 substrate on mock exec run.

---

## ROLE_GAP_MATRIX

| Role | Current coverage | Missing pillars | Missing skill families | Missing edges | Weak / muddled facts | Human confirm | Evidence uplift | Section most likely to fail | Overclaim risk | Undermatch risk | Correction type |
|------|------------------|-----------------|------------------------|---------------|----------------------|---------------|-----------------|----------------------------|----------------|-----------------|-----------------|
| **AIG** | Partial — agentic + governance + generic GTM | Carrier transformation; underwriting/claims/ops AI | Operating-model redesign; agent inventory; insurance ops telemetry | P1→P3 bridge; carrier≠generic FS | Archive mentions insurers/underwriting in MEDIUM facts but no carrier pillar | MEDIUM GTM + domain exec elevation | None for unsupported ops claims | `executive_summary` | Underwriting/claims/policy-admin | Actuarial buried; agentic swamps domain | TAXONOMY_GAP, EDGE_GAP, SRFS_SELECTION_GAP |
| **Lincoln** | Partial — cloud + agentic + FSA | Insurer IT strategy; AI-for-IT; portfolio/EA | App Dev CoE; DevSecOps; data strategy; IT financial mgmt | Actuarial→IT strategy forward projection | “Banks and insurers” generic in facts | FSA forward bridge confirmation | InsurTech employment → skill links | `executive_summary` | Full SVP IT strategy without facts | Actuarial only early-career path | TAXONOMY_GAP, EDGE_GAP |
| **Citi** | Partial — Basel/CCAR HIGH + model_risk + agentic | Banking platform AI; responsible AI productization | Payments, liquidity, trade, fraud product lines | Basel/CCAR → AI auditability product bridge | `fact_governance_001` banking MEDIUM; no product-line facts | Banking MEDIUM exec queue | No payment/fraud claims without facts | `executive_summary` | Transaction banking / payments ownership | Banking AI productization thin | TAXONOMY_GAP, SECTION_POLICY_GAP (expected) |
| **Brown & Brown** | Partial — GTM + cloud + executive | Brokerage distribution; interoperability ecosystem | Brokerage tech; innovation incubation | Carrier vs brokerage separation | InsurTech narrative is **carrier** middle-market, not brokerage | Brokerage taxonomy decision | None without brokerage evidence | `competencies` | Brokerage platform ownership | Carrier/broker conflated | TAXONOMY_GAP |
| **Anthropic** | Partial — co_sell ACTIVE_CONFIRMED; many partner DRAFT | Hyperscaler marketplace GTM; applied AI partner architecture | Marketplace, GSI, Snowflake/Databricks, partner sales eng | Partner engineering → joint solution arch | AWS HIGH; Azure/GCP/Snowflake **no skill nodes** | Partner engineering pending source | Archive trace for DRAFT partner skills | `competencies` | Hyperscaler exclusivity, marketplace co-sell | Partner engineering invisible (DRAFT) | CONFIDENCE_GAP, TAXONOMY_GAP, HUMAN_CONFIRMATION_REQUIRED |
| **GTM baseline** | **Strong** for P2 slice | — (by design) | Airline anchor; estimation/sizing | — | MEDIUM GTM SRFS-blocked in exec | WS-1 HITL packet | Airline + sizing audits = DO_NOT_PROMOTE | `executive_summary` | LOW airline/$100M if promoted | MEDIUM GTM underweighted in exec | SECTION_POLICY_GAP (expected), EVIDENCE_GAP |

---

## PILLAR_GAP_MATRIX

| Pillar (existing) | Senior roles served | Gap |
|-------------------|---------------------|-----|
| `pillar_agentic_ai_platforms` | All | **Over-selected** — default genai weight 0.65 swamps domain JDs |
| `pillar_regulatory_governance` | Citi, AIG, Lincoln | Skills overlap agentic **runtime-gate** domain — muddles Basel/CCAR vs platform gates |
| `pillar_actuarial_foundation` / `pillar_embedded_options_insurance` | AIG, Lincoln | On `track_data_tech_cloud_ml` but skills mostly **DRAFT**; no forward IT/strategy bridge |
| `pillar_partner_gtm_alliances` / `pillar_cosell_partner_engineering` | Anthropic, GTM | Partner hyperscaler skills **DRAFT**; no marketplace pillar |
| `pillar_gtm_presales_motion` / `pillar_technical_presales_accelerators` | GTM, partial Anthropic | Proven for GTM; **not** insurer transformation or banking platform |
| **Missing:** `pillar_insurance_carrier_transformation` | AIG | TAXONOMY_GAP — no node |
| **Missing:** `pillar_insurance_brokerage_distribution` | Brown & Brown | TAXONOMY_GAP |
| **Missing:** `pillar_insurer_it_strategy_ai_enablement` | Lincoln | TAXONOMY_GAP |
| **Missing:** `pillar_banking_platform_responsible_ai` | Citi | TAXONOMY_GAP |
| **Missing:** `pillar_hyperscaler_marketplace_partner_gtm` | Anthropic | TAXONOMY_GAP |

---

## SKILL_FAMILY_GAP_MATRIX

| Skill family (required by examples) | Graph state | Evidence | Correction class |
|------------------------------------|-------------|----------|------------------|
| Underwriting / claims / policy-admin AI (AIG) | **NONE** as skills | Archive has underwriting/fraud **tokens** in MEDIUM facts — not carrier-transformation skills | TAXONOMY_GAP + EVIDENCE_GAP |
| Insurer IT strategy / AI enablement (Lincoln) | **NONE** (`it_strategy`, `ai_enablement` → no nodes) | InsurTech CTO in base resume — not linked to forward skills | TAXONOMY_GAP + FACT_LINK_GAP |
| Banking product lines (Citi) | **NONE** for payments/liquidity/trade/fraud | `fact_governance_001` banking MEDIUM; `fact_governance_003` Basel HIGH | TAXONOMY_GAP |
| Brokerage / distribution tech (Brown & Brown) | **NONE** | No brokerage-specific archive hits | TAXONOMY_GAP |
| Hyperscaler marketplace / co-sell (Anthropic) | Partial — `skill_partner_co_selling` ACTIVE_CONFIRMED; AWS modernization HIGH | `skill_partner_aws_ecosystem`, `cloud_partner_ecosystem` **DRAFT**; no Snowflake/GCP/Azure/marketplace nodes | CONFIDENCE_GAP + TAXONOMY_GAP |
| Partner engineering / joint solutions (Anthropic) | `skill_partner_partner_engineering` **DRAFT**, pending source | HUMAN_CONFIRMATION_REQUIRED | |
| Phase 1 actuarial forward projection | FSA ACTIVE_CONFIRMED; 13/20 actuarial-epoch skills DRAFT | Archive FSA/quant HIGH facts exist | CONFIDENCE_GAP + EDGE_GAP |
| GTM P2 (baseline) | 9 ACTIVE P2 + 1 ACTIVE_CONFIRMED; 7 DRAFT | Closeout PASS | NO_ACTION_NEEDED (consumption proven) |

---

## EDGE_GAP_MATRIX

| Bridge (required) | Present? | Notes |
|-------------------|----------|--------|
| Actuarial / insurance foundation → insurer AI strategy | **No** | 0 cross-pillar edges |
| Actuarial / insurance → agentic transformation | **No** | Traversal only via shared track weights, not semantic bridge |
| Insurance domain → underwriting / claims / ops AI | **No** | No ops skill nodes |
| Insurance domain → IT strategy / AI enablement | **No** | |
| Banking/risk/regulatory → responsible AI governance | **Weak** | `skill_risk_model_risk` + `skill_ai_governance_certification` exist but agentic domain overlap |
| Basel / CCAR / lineage → AI auditability | **Partial** | `fact_governance_003` HIGH; edges to governance skills, not banking **product** skills |
| Hyperscaler / partner ecosystem → applied AI architecture | **Weak** | Partner epoch mostly DRAFT |
| Marketplace / co-sell → partner-led GTM | **Partial** | co_selling confirmed; marketplace skill missing |
| Partner engineering → reference architectures | **Weak** | `skill_p2_tech_reference_architecture` ACTIVE but partner_engineering DRAFT |
| Phase 3 agentic → regulated FS / insurance / banking context | **Implicit only** | “Regulated enterprise” narrative; no domain-specific regulated **context** edges |

---

## FACT_LINK_GAP_MATRIX

| Fact / evidence | Ledger | Skill link | Issue |
|-----------------|--------|------------|--------|
| `fact_governance_003` Basel/CCAR HIGH | Yes | `skill_risk_model_risk`, governance skills | Strong for Citi **governance** — not banking productization |
| `fact_governance_001` banking MEDIUM | Yes | `skill_ai_governance_certification` | Exec_summary blocked without HITL |
| InsurTech CTO narrative (base resume) | Employment node | **No** `insurtech_*` ACTIVE skill | FACT_LINK_GAP |
| Underwriting/fraud tokens (archive) | MEDIUM facts | No distinct underwriting/claims skills | TAXONOMY_GAP |
| Partner archive (Partner Development Manager) | MEDIUM `fact_partnerships_gtm_*` | Many partner skills still DRAFT | CONFIDENCE_GAP |
| Airline / ~$100M anchor | Inference only in ledger | `skill_p2_anchor_*` INTERNAL_ONLY | EVIDENCE_GAP (correct fence) |
| P2 HIGH without `linked_fact_id` | Resume archive snippets | DRAFT — track expansion blocked | CONFIDENCE_GAP |

---

## PHASE_BRIDGE_GAP_MATRIX

| Bridge | Supported? | Severity |
|--------|------------|----------|
| Actuarial → insurer AI strategy | **No** | P0 |
| Actuarial → agentic transformation | **No** | P0 |
| Insurance → underwriting/claims/ops AI | **No** | P0 |
| Insurance → IT strategy / AI enablement | **No** | P0 |
| Banking/regulatory → responsible AI governance | **Partial** | P1 |
| Basel/CCAR/lineage → AI auditability/traceability | **Partial** | P1 |
| Hyperscaler/partner → applied AI architecture | **Weak** | P0 (Anthropic) |
| Marketplace/co-sell → partner GTM | **Partial** | P1 |
| Partner engineering → reference / joint solutions | **Weak** | P1 |
| Agentic governed AI → regulated industry context | **Generic only** | P1 |

Mechanism: Traversal uses `career_track_contains_pillar` + `epoch_contains_skill` + track weights — **not** explicit cross-domain bridge edges. Senior JDs that span epochs will rank agentic skills unless weights/fixtures override (see `track_weighted_graph_expansion.py`).

---

## SECTION_OUTPUT_RISK_MATRIX

| Section | AIG | Lincoln | Citi | Brown & Brown | Anthropic | GTM baseline |
|---------|-----|---------|------|---------------|-----------|--------------|
| **headline** | Agentic-forward; weak carrier signal | Generic executive + cloud | Governance possible via HIGH facts | GTM buyer alignment possible | Partner labels if ACTIVE skills surface | P2 buyer alignment eligible; SRFS may block fact |
| **executive_summary** | **Fail undermatch** — MEDIUM domain blocked; agentic default | **Fail undermatch** — IT strategy absent | Basel may appear (mock repair did); banking products absent | Brokerage absent | Partner DRAFT → thin | **Fail** — 1 P2 HIGH fact; MEDIUM blocked; X2 substrate FAIL |
| **unify_bullets** | Better for MEDIUM registry facts | Actuarial/FS MEDIUM possible | Basel/CCAR + governance MEDIUM | GTM MEDIUM eligible | Partner MEDIUM if active | Strongest lane for MEDIUM GTM |
| **unify_narrative** | Risk agentic narrative dominance | Same | Governance + platform mix | Commercial narrative ok | Co-sell / joint GTM possible | Good for P2 narrative facts |
| **ibm_bullets** | Locked IBM + tech accelerators | Reference arch / DevOps blueprint | AWS patterns | IBM portfolio anchor DRAFT | AWS modernization HIGH | P2 tech skills map here |
| **ibm_narrative** | Agentic + IBM portfolio | Actuarial software allowed (DRAFT) | Regulatory capital themes | Weak brokerage story | Adoption derisking DRAFT | Draft anchors blocked |
| **competencies** | **Agentic swamps** regulatory domain overlap | Mixed cloud + executive | Model risk + agentic gates conflated | **Brokerage gap** | **Partner gap** if DRAFT | P2 + partner mix |

**Policy note (NO_ACTION_NEEDED):** Executive_summary suppression of MEDIUM and LOW/INTERNAL_ONLY is **correct** for overclaim prevention — it causes undermatch until HITL/evidence/taxonomy fixes land.

---

## HUMAN_CONFIRMATION_REQUIRED

| Item | Tier | Roles affected |
|------|------|----------------|
| MEDIUM GTM facts (`fact_sales_accounts_*`, `fact_partnerships_gtm_*`, `fact_revenue_ops_*`, `fact_solutions_*`) | Exec elevation vs bullet-only | GTM, Anthropic, Brown & Brown |
| `skill_partner_partner_engineering` | USER_CONFIRMED_PENDING_SOURCE | Anthropic |
| `skill_partner_product_feedback_loops` | USER_CONFIRMED_PENDING_SOURCE | Anthropic |
| Banking client rollout (`fact_governance_001`) | Optional exec elevation | Citi |
| InsurTech → forward insurer strategy bridge | New taxonomy decision | AIG, Lincoln |

---

## EVIDENCE_UPLIFT_REQUIRED

| Node | Audit result | Action |
|------|--------------|--------|
| `skill_p2_anchor_major_airline_devops_aws` | DO_NOT_PROMOTE | Keep INTERNAL_ONLY or supply operator source |
| `skill_p2_tech_estimation_sizing_directional` | DO_NOT_PROMOTE | Keep fenced; adjacent financial modeling ≠ technical sizing |
| Partner hyperscaler DRAFT skills | Archive snippets exist | Activation path: fact links + ACTIVE (not auto-promote) |
| Brokerage / carrier-specific claims | No source-backed nodes | **Do not claim** until archive trace + facts |

---

## OVERCLAIM_RISK_REGISTER

| Risk | Roles | Mitigation (existing) |
|------|-------|------------------------|
| Underwriting / claims / policy-admin transformation | AIG | No skill nodes; exec MEDIUM blocked |
| Payments / liquidity / trade / fraud product ownership | Citi | No skill nodes |
| Brokerage distribution platform leadership | Brown & Brown | No brokerage pillar |
| Marketplace / Snowflake / GCP / Azure exclusivity | Anthropic | Missing or DRAFT skills |
| Major airline / ~$100M engagement | GTM | INTERNAL_ONLY + uplift DO_NOT_PROMOTE |
| IT strategy / portfolio management for insurer | Lincoln | No employment-backed facts |
| Gross margin / business metrics without substrate | GTM exec run | X2 gate FAIL (observed) |

---

## UNDERMATCH_RISK_REGISTER

| Risk | Roles | Cause |
|------|-------|--------|
| Actuarial/FSA buried in early-career | Lincoln, AIG | DRAFT actuarial skills; section bias |
| Basel/CCAR not in exec_summary | Citi | SRFS/HIGH path works in mock repair but not default GTM SRFS slice |
| Partner ecosystem invisible | Anthropic | 23/48 partner-epoch skills DRAFT |
| GTM MEDIUM strengths only in bullets/narratives | GTM | `commercial_claim_eligibility.yaml` excludes exec_summary |
| InsurTech carrier story not projected | AIG, Lincoln | FACT_LINK_GAP + no carrier pillar |
| Agentic platform dominates competencies | All regulated examples | track_genai_agentic weight + 62 ACTIVE agentic-epoch skills |

---

## CORRECTION_CLASSIFICATION (gap backlog)

| ID | Severity | Class | Title |
|----|----------|-------|-------|
| GAP-001 | P0 | TAXONOMY_GAP | No carrier vs brokerage taxonomy |
| GAP-002 | P0 | EDGE_GAP | Zero phase-bridge edges |
| GAP-003 | P0 | CONFIDENCE_GAP | Partner hyperscaler skills mostly DRAFT |
| GAP-004 | P0 | TAXONOMY_GAP | Phase-1 actuarial trapped DRAFT / early-career |
| GAP-005 | P0 | SECTION_POLICY_GAP | Exec_summary MEDIUM block (correct policy) |
| GAP-006 | P0 | RUNTIME_OBSERVABILITY_GAP | X2 business-metrics substrate FAIL |
| GAP-007 | P1 | TAXONOMY_GAP | No IT strategy / AI enablement pillar |
| GAP-008 | P1 | TAXONOMY_GAP | Banking productization not separated |
| GAP-009 | P1 | TAXONOMY_GAP | Marketplace / hyperscaler not distinct |
| GAP-010 | P1 | SRFS_SELECTION_GAP | Default genai track dominance |
| GAP-011 | P1 | TAXONOMY_GAP | Role-family taxonomy missing insurer/broker/bank slices |
| GAP-012 | P1 | CONFIDENCE_GAP | P2 HIGH skills DRAFT without fact links |
| GAP-013 | P1 | EVIDENCE_GAP | Blocked airline/sizing anchors |
| GAP-014 | P1 | EDGE_GAP | Regulatory skills overlap agentic domain |
| GAP-015 | P2 | FACT_LINK_GAP | InsurTech not linked forward |
| GAP-016 | P2 | HUMAN_CONFIRMATION_REQUIRED | Partner engineering pending source |
| GAP-017 | P2 | NO_ACTION_NEEDED | Exec policy correctly suppresses unsupported claims |
| GAP-018 | P3 | NO_ACTION_NEEDED | GTM P2 consumption proven |

---

## PRIORITIZED_GAP_BACKLOG

### P0 (senior-role matching materially fails or overclaim)

1. Split **carrier insurance**, **brokerage**, **banking platform**, and **generic FS** in taxonomy (GAP-001, GAP-011).  
2. Add **evidence-gated phase-bridge edges** (GAP-002) — not prompt weakening.  
3. **Partner/hyperscaler activation criteria** before Anthropic-style targeting (GAP-003).  
4. **Forward-project actuarial/insurance** with ACTIVE paths beyond early-career (GAP-004).  
5. Keep exec_summary policy; add **HITL elevation path** for confirmed domain MEDIUM (GAP-005).  
6. Fix **X2 substrate attribution** for metrics claims (GAP-006).

### P1 (differentiator buried)

7. IT strategy / AI-enablement pillar family (GAP-007).  
8. Banking product-line skill families only with facts (GAP-008).  
9. Marketplace / multi-hyperscaler taxonomy (GAP-009).  
10. Role-specific **track weight overrides** in taxonomy/fixtures (GAP-010).  
11. P2 HIGH → fact link → ACTIVE pipeline (GAP-012).  
12. Regulatory vs agentic domain separation in competencies (GAP-014).

### P2–P3

13. InsurTech fact links (GAP-015).  
14. Partner engineering confirmation (GAP-016).  
15. Document GTM consumption as proven baseline (GAP-018).

---

## RECOMMENDED_NEXT_PLAN_UPDATE

Extend [phase2-gtm-presales-remaining-f7a2c9](.cursor/plans/phase2-gtm-presales-remaining-f7a2c9.md) with **Wave 0.5 — Senior-role graph gap closure (plan-only)**:

1. Add role-family IDs: `INSURANCE_CARRIER_TRANSFORMATION`, `INSURANCE_BROKERAGE_IT`, `BANKING_PLATFORM_AI` (JD targeting only).  
2. Define phase-bridge edge types with `evidence_required` metadata — no implementation in 0.5.  
3. Sequence: taxonomy → fact links → ACTIVE promotion → HITL exec elevations → multi-lane runtime proof per role fixture.  
4. **Do not** weaken executive_summary claim policy or auto-promote MEDIUM.

---

## EXPLICIT_NON_CLAIMS

Do not assert (unless future evidence + ACTIVE + gates): underwriting, claims, policy administration, billing, brokerage distribution ownership, transaction banking, payments, liquidity, trade, investor/issuer services, fraud operations, Fed/regulator-facing work, marketplace co-sell, Databricks, Snowflake, GCP, Azure partner exclusivity, partner sales, major airline ~$100M engagement ownership, or technical estimation/sizing methodology.

JD and briefing remain **targeting only** — never proof. `broad_skills_ledger` remains deprecated.

---

## Machine-readable companion

Full matrices and gap IDs: [senior_role_graph_gap_analysis.json](docs/reports/apps_rg/senior_role_graph_gap_analysis.json).
