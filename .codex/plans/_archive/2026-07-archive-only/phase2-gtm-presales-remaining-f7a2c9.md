---
plan_id: phase2-gtm-presales-remaining-f7a2c9
plan_type: apps_rg_evidence
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Phase 2 GTM / Pre-Sales Skills Graph — Remaining Work (Zero-Loss Plan)

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: ACTIVE
GRAPH_SCOPE_STATUS: GRAPH_SCOPE_COMPLETE
CURRENT_WAVE: post-graph (W1 or W4-runtime)
LAST_COMPLETED_GRAPH_WAVE: W4/W14
LAST_UPDATED: 2026-05-20
SENIOR_ROLE_GAP_AUDIT_SSOT: `senior_role_graph_gap_analysis_20260520` — [senior_role_graph_gap_analysis.md](docs/reports/apps_rg/senior_role_graph_gap_analysis.md) · [senior_role_graph_gap_analysis.json](docs/reports/apps_rg/senior_role_graph_gap_analysis.json)
GRAPH_SCOPE_CLOSEOUT: [phase2_graph_scope_closeout_receipt.json](docs/reports/apps_rg/phase2_graph_scope_closeout_receipt.json) · [phase2_graph_scope_closeout_receipt.md](docs/reports/apps_rg/phase2_graph_scope_closeout_receipt.md)
PRIOR_CLOSEOUT: [skills_graph_phase2_gtm_presales_closeout.json](docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json)
PRIOR_RUNTIME_PROOF: [exec_summary_20260520_094345](artifacts/apps_rg/runtime_proofs/executive_summary/mock/exec_summary_20260520_094345)

---

## STATUS

**GRAPH_SCOPE_COMPLETE** — Senior-role skills graph phase is **closed** for this plan. Graph taxonomy, pillars/skills/bridge edges, seven archetype fixtures, offline traversal (W14/W14b), and multilane section projection (49/49) are complete. **No** graph, prompt, runtime, or SRFS policy change is required before HITL or minimum runtime proof.

**Scoped supersession note (2026-06-12):** Future typed-edge / role-family traversal design is superseded by [typed-edge-role-facet-guardrails-a6f3d2](../../plans/typed-edge-role-facet-guardrails-a6f3d2.md). This note does **not** reopen or retire the completed Phase 2 graph scope; it preserves this plan as historical proof while moving future traversal design to the successor.

**Plan remainder (non-graph):** W1 HITL, W2a/2b evidence decisions, W3 X2 diagnosis, W4 **runtime** proof, W5 ADR, W6 conditional DRAFT activation, W7 certification.

---

## GRAPH WAVES COMPLETED (2026-05-20)

| Wave | Status | Receipt |
|------|--------|---------|
| W0 | COMPLETE | GTM closeout + inventory lock |
| W0.5 | COMPLETE | [phase2_senior_role_implementation_backlog.json](docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json) |
| W0.5b | COMPLETE | [phase2_w05b_taxonomy_track_weight_receipt.json](docs/reports/apps_rg/phase2_w05b_taxonomy_track_weight_receipt.json) |
| W8–W11-graph | COMPLETE | [phase2_w8_w11_senior_role_graph_receipt.json](docs/reports/apps_rg/phase2_w8_w11_senior_role_graph_receipt.json) |
| W12-graph | COMPLETE | [phase2_w12_partner_hyperscaler_graph_receipt.json](docs/reports/apps_rg/phase2_w12_partner_hyperscaler_graph_receipt.json) |
| W13 | COMPLETE | [phase2_w13_archetype_fixtures_receipt.json](docs/reports/apps_rg/phase2_w13_archetype_fixtures_receipt.json) |
| W14 | COMPLETE | [phase2_w14_offline_traversal_receipt.json](docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.json) |
| W14b | COMPLETE | [phase2_w14b_taxonomy_track_weight_wiring_receipt.json](docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.json) |
| W4/W14 (projection) | COMPLETE | [phase2_w4_w14_multilane_section_projection_receipt.json](docs/reports/apps_rg/phase2_w4_w14_multilane_section_projection_receipt.json) |

**Graph inventory (final):** 29 pillars · 162 skills · 1,406 edges · 16 phase-bridge edges · 7 archetype fixtures.

**Scope boundary:** Do not add pillars, skills, edges, archetypes, or fixtures unless a new role exposes a documented P0 traversal failure.

**Known deferred:** `pillar_insurance_brokerage_distribution` — no source evidence; do not fabricate.

## PLAN_ID

`phase2-gtm-presales-remaining-f7a2c9`

## OBJECTIVE

Close the remaining Phase 2 GTM/pre-sales work with **zero loss of evidence discipline**: prove where P2 skills and GTM facts **should** appear by section policy, obtain human decisions on MEDIUM facts, complete read-only or evidence-gated uplift for blocked anchors, diagnose X2 blocks without weakening exec_summary policy, run canonical runtime proofs on GTM-suited lanes, document exec_summary policy as SSOT (not ad hoc), define a ladder to **release-eligible** proof, and **before any graph edits** convert the senior-role gap audit into a taxonomy/bridge/fixture implementation sequence (Wave 0.5).

## CURRENT_STATE_SUMMARY

| Area | State |
|------|--------|
| **GRAPH_SCOPE_STATUS** | **GRAPH_SCOPE_COMPLETE** — see [phase2_graph_scope_closeout_receipt.json](docs/reports/apps_rg/phase2_graph_scope_closeout_receipt.json) |
| Graph SSOT | **29 pillars, 162 skills**; P2 + senior-role pillars; GTM baseline preserved |
| Authority | `augmented_skills_graph` (`master_skills_arsenal_ledger.json`); `broad_skills_ledger` deprecated/reference-only |
| Senior fixtures | **7** archetypes; manifest [senior_role_fixture_manifest.json](docs/reports/apps_rg/fixtures/senior_roles/senior_role_fixture_manifest.json) |
| Offline traversal | W14/W14b **PASS** (7/7); no `weight_override` required (W14b) |
| Section projection | W4/W14 **49/49** PASS (offline SRFS + graph; not runtime) |
| Exec_summary policy | **Unchanged** — HIGH-only; MEDIUM blocked from exec_summary by design |
| Blocked nodes | Airline anchor, estimation/sizing INTERNAL_ONLY; brokerage pillar **deferred** (no evidence) |
| Non-graph open | W1 HITL, W4 runtime, W2a/2b, W3 X2, W5 ADR, W6, W7 |
| Proof class (graph) | Offline receipts only; runtime X3_ALLOW not claimed |

## NON_NEGOTIABLE_GUARDRAILS

1. Evidence hierarchy unchanged: atomic facts → SRFS → claim ledger → output; skills are competency authority, not proof.
2. Do **not** weaken executive_summary claim policy (no automatic MEDIUM promotion).
3. Do **not** admit LOW / INTERNAL_ONLY / DRAFT nodes into external claims without explicit evidence + activation path.
4. Do **not** claim major airline, ~$100M engagement ownership, or technical estimation/sizing without hard evidence promotion.
5. Do **not** conflate IBM ~$30M portfolio with airline anchor.
6. JD and briefing are targeting only — never proof.
7. Do **not** restore `broad_skills_ledger` as authority.
8. No `agentic_core` edits.
9. No section prompt edits unless a wave proves a defect and documents why prompt change is unavoidable.
10. SRFS active file must match targeting `binding_digest` before runtime proof (stale `selected_role_fact_set_active.json` invalidates GTM claims).

---

## WORKSTREAMS

| ID | Workstream | Primary outcome |
|----|------------|-----------------|
| WS-1 | Human-confirmation packet (MEDIUM GTM / queue facts) | Signed HITL decisions + optional exec elevation |
| WS-2a | Airline anchor evidence uplift | Promote or permanently fence `skill_p2_anchor_major_airline_devops_aws` |
| WS-2b | Estimation/sizing evidence uplift | Promote or permanently fence `skill_p2_tech_estimation_sizing_directional` |
| WS-3 | `x2_srfs_claim_business_metrics_substrate` diagnosis | Root cause + fix class (ledger attribution vs policy) |
| WS-4 | Multi-section GTM runtime materialization proof | Per-lane receipts for bullets/narratives/competencies |
| WS-5 | Executive_summary policy SSOT | Written decision; no silent drift |
| WS-6 | DRAFT P2 skill activation (conditional) | ACTIVE only with archive trace + fact links |
| WS-7 | Release-eligible certification path | Live provider + X3_ALLOW + proof_eligible |
| WS-8 | Insurance carrier transformation and actuarial-to-agentic bridge | Carrier vs generic FS taxonomy + `actuarial_to_*` bridge-edge spec |
| WS-9 | Insurer IT strategy / AI enablement / enterprise architecture bridge | IT-strategy pillar family + `insurtech_to_insurer_it_strategy` edges |
| WS-10 | Banking, risk, Basel, CCAR, regulatory governance, responsible AI bridge | Banking-platform pillar + regulatory↔agentic domain separation |
| WS-11 | Insurance brokerage / distribution technology bridge | Brokerage pillar distinct from carrier; interoperability ecosystem |
| WS-12 | Hyperscaler / marketplace / partner ecosystem GTM bridge | Partner DRAFT activation criteria + marketplace/applied-AI pillars |
| WS-13 | Senior-role fixture suite and traversal proof | Six sanitized JD/brief fixtures + offline track-expansion receipts |
| WS-14 | Cross-section materialization and anti-overclaim proof | Per-role lane matrix; exec undermatch vs bullet MEDIUM; no LOW/DRAFT leakage |

---

## WAVES

### Wave 0 — Plan freeze and inventory lock (read-only)

**Purpose:** Zero-loss baseline; no scope drift from closeout.

**Scope:** Reconcile plan against closeout JSON, section projection audit, exec_summary GTM run, evidence uplift JSONs.

**Files likely inspected:**
[skills_graph_phase2_gtm_presales_closeout.json](docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json),
[skills_graph_phase2_section_projection_audit.json](docs/reports/apps_rg/skills_graph_phase2_section_projection_audit.json),
[exec_summary_20260520_094345](artifacts/apps_rg/runtime_proofs/executive_summary/mock/exec_summary_20260520_094345),
[selected_role_fact_set_active_manifest.json](artifacts/apps_rg/fact_inventory/selected_role_fact_set_active_manifest.json)

**Files likely changed:** NONE

**Canonical commands expected:**
```bash
python -m apps_rg.fact_inventory.validate_p2_graph_skills_accelerated_closeout  # if present; else read closeout JSON only
python apps_rg/fact_inventory/validate_commercial_srfs_projection.py
```

**Expected artifacts:** Wave-0 inventory note under `docs/reports/apps_rg/phase2_gtm_remaining_w0_inventory.json` (optional).

**Pass criteria:** All 17 P2 skill IDs mapped to `{ACTIVE|DRAFT|INTERNAL_ONLY}` and section eligibility from projection audit.

**Fail/block criteria:** Closeout status not PASS; graph digest mismatch vs runtime proof.

**Explicit non-claims:** No new external claims in this wave.

---

### Wave 0.5 — Senior-role taxonomy, bridge-edge, and fixture backlog

**Purpose:** Convert the completed [senior_role_graph_gap_analysis](docs/reports/apps_rg/senior_role_graph_gap_analysis.md) (`STATUS: PASS`, `proof_classification: audit_only_readonly`) into an **implementation-ready backlog** before any graph edits. Preserve GTM/pre-sales baseline proof; sequence corrections for AIG, Lincoln, Citi, Brown & Brown, and Anthropic traversal failures.

**Scope:** Plan-update and backlog/spec artifacts only. **No** patches to `master_skills_arsenal_ledger.json`, runtime, SRFS, section prompts, validators, or `agentic_core`.

**Audit findings preserved (SSOT):**

| Finding | Detail |
|---------|--------|
| GTM baseline | Phase 2 GTM/pre-sales graph augmentation and consumption **proven** (closeout PASS; 10 ACTIVE P2 skills under GTM JD weighting) |
| Senior-role traversal | **Fails** — missing taxonomy, 0 phase-bridge edges, partner skills predominantly DRAFT, Phase 1 actuarial buried |
| Audit SSOT | `audit_id`: **`senior_role_graph_gap_analysis_20260520`** · STATUS: **PASS** · `proof_classification`: **audit_only_readonly** |
| Gap counts | **18** total: **6 P0**, **8 P1**, **3 P2**, **1 P3** |
| Graph inventory | 21 pillars · 148 skills · 1,281 edges · 94 ACTIVE/ACTIVE_CONFIRMED · 54 DRAFT · **0** actuarial/insurance/reg → agentic/GTM/partner bridge edges · **0** pillar-to-pillar edges |
| Authority | `augmented_skills_graph` only; `broad_skills_ledger` deprecated/reference-only |

**P0 gaps carried forward (implementation sequence drivers):**

| Gap ID | Correction class | Title |
|--------|------------------|-------|
| GAP-001 | TAXONOMY_GAP | No carrier-insurance vs brokerage-distribution taxonomy |
| GAP-002 | EDGE_GAP | Zero phase-bridge edges from actuarial/insurance/regulatory → agentic/GTM/partner |
| GAP-003 | CONFIDENCE_GAP | Partner hyperscaler ecosystem skills predominantly DRAFT |
| GAP-004 | TAXONOMY_GAP | Phase 1 actuarial/insurance skills trapped in DRAFT or early-career-only sections |
| GAP-005 | SECTION_POLICY_GAP | Executive_summary SRFS blocks core MEDIUM domain facts by design (undermatch; policy correct) |
| GAP-006 | RUNTIME_OBSERVABILITY_GAP | X2 `x2_srfs_claim_business_metrics_substrate` failure on mock exec_summary run |

**P1 gaps carried forward:**

| Gap ID | Correction class | Title |
|--------|------------------|-------|
| GAP-007 | TAXONOMY_GAP | No IT strategy / AI enablement / EA / portfolio governance pillar family |
| GAP-008 | TAXONOMY_GAP | Banking productization not separated from generic FS governance |
| GAP-009 | TAXONOMY_GAP | Marketplace GTM / GSI / joint solution dev not distinct from generic partnerships |
| GAP-010 | SRFS_SELECTION_GAP | Default track weights favor `track_genai_agentic` (0.65) over actuarial (0.10) |
| GAP-011 | TAXONOMY_GAP | Role-family taxonomy lacks insurer-carrier, brokerage, banking-platform slices |
| GAP-012 | CONFIDENCE_GAP | P2 HIGH skills without fact links remain DRAFT |
| GAP-013 | EVIDENCE_GAP | Blocked anchors INTERNAL_ONLY but create narrative holes |
| GAP-014 | EDGE_GAP | Regulatory governance skills route through agentic capability domain (swamping risk) |

**Files likely inspected:**
[senior_role_graph_gap_analysis.md](docs/reports/apps_rg/senior_role_graph_gap_analysis.md),
[senior_role_graph_gap_analysis.json](docs/reports/apps_rg/senior_role_graph_gap_analysis.json),
[master_skills_arsenal_ledger.json](apps_rg/fact_inventory/master_skills_arsenal_ledger.json),
[master_role_family_taxonomy.yaml](apps_rg/config/domain_contract/master_role_family_taxonomy.yaml),
[track_weighted_graph_expansion.py](apps_rg/fact_inventory/track_weighted_graph_expansion.py),
[commercial_claim_eligibility.yaml](apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml),
[skills_graph_phase2_section_projection_audit.json](docs/reports/apps_rg/skills_graph_phase2_section_projection_audit.json)

**Files likely changed:**
- [phase2-gtm-presales-remaining-f7a2c9.md](.codex/plans/phase2-gtm-presales-remaining-f7a2c9.md) (Wave 0.5 section)
- [phase2_senior_role_implementation_backlog.json](docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json) (implementation backlog from audit SSOT)
- `docs/reports/apps_rg/fixtures/senior_roles/` (Wave 0.5b execution — sanitized JD/brief; **not** in plan-only pass)
- `apps_rg/config/domain_contract/master_role_family_taxonomy.yaml` (W0.5b — after backlog approval; **not** in plan-only pass)

**No changes in Wave 0.5:** graph ledger, runtime, SRFS, section prompts, validators, `agentic_core`.

**Canonical commands expected (read-only validation):**
```bash
python apps_rg/fact_inventory/validate_commercial_srfs_projection.py
# Optional: offline track expansion dry-run per fixture (no graph write)
python -c "from apps_rg.fact_inventory.track_weighted_graph_expansion import ..."  # per implementation spec script TBD in W0.5 artifacts
```

**Expected artifacts:**
`docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json` (correction-class grouping + gap map)
`docs/reports/apps_rg/phase2_senior_role_implementation_spec.md` (human-readable mirror)
`docs/reports/apps_rg/fixtures/senior_roles/<role_slug>_jd.txt` (×6)
`docs/reports/apps_rg/fixtures/senior_roles/<role_slug>_brief.txt` (×6)
`docs/reports/apps_rg/fixtures/senior_roles/senior_role_fixture_manifest.json`

**Pass criteria:**
- Implementation backlog published grouped by all 10 correction classes (TAXONOMY_GAP … NO_ACTION_NEEDED).
- All 18 gaps mapped to WS-8..WS-14 with correction class and severity.
- All 9 proposed pillar families documented with evidence gate (`existing_evidence` \| `evidence_search_required` \| `human_confirmation_required`).
- All 12 bridge-edge families documented with `evidence_required: true` metadata.
- All 7 role-family taxonomy additions documented with JD signal keywords (targeting only).
- Six role fixtures fully specified (forbidden claims + proof artifacts).
- Section impact plan covers all 7 sections with policy alignment (exec HIGH/HITL only).
- Implementation sequence lists graph-edit waves **after** W0.5 with explicit dependencies.
- Original Waves 0–7 preserved unchanged in intent.

**Fail/block criteria:**
- Any spec proposes weakening executive_summary MEDIUM policy or auto-promoting MEDIUM.
- Any spec admits LOW/INTERNAL_ONLY/DRAFT into external claims without promotion path.
- Any spec uses JD/briefing as proof.
- Any spec restores `broad_skills_ledger` as authority.
- Graph ledger edited in Wave 0.5.

**Explicit non-claims (Wave 0.5):**
Underwriting, claims, policy admin, billing, brokerage ownership, transaction banking, payments, liquidity, trade, investor/issuer services, fraud operations, Fed/regulator-facing work, marketplace co-sell, Databricks, Snowflake, GCP, Azure partner exclusivity, partner sales, airline ~$100M engagement, technical estimation/sizing methodology — unless source-backed and promoted (see audit [explicit_non_claims](docs/reports/apps_rg/senior_role_graph_gap_analysis.json)).

---

#### Implementation backlog by correction class (W0.5 deliverable #1)

| Correction class | Gap IDs | Backlog items | Exec wave (post–W0.5) |
|------------------|---------|---------------|------------------------|
| **TAXONOMY_GAP** | GAP-001, GAP-004, GAP-007, GAP-008, GAP-009, GAP-011 | Split carrier / brokerage / banking-platform / marketplace vs generic FS; add 9 proposed pillars; forward-project actuarial beyond early-career-only; separate banking productization from governance-only | W0.5b → W8–W11-graph |
| **EDGE_GAP** | GAP-002, GAP-014 | Add 12 evidence-gated bridge-edge families; **0** pillar-to-pillar edges today; split `pillar_regulatory_governance` traversal from agentic runtime-gate domain | W8–W12-graph |
| **CONFIDENCE_GAP** | GAP-003, GAP-012 | Partner hyperscaler DRAFT activation criteria; P2 HIGH → fact link → ACTIVE (not snippet-only) | W12-graph, W6 |
| **FACT_LINK_GAP** | GAP-015 | Link InsurTech employment → `insurtech_to_insurer_it_strategy` / forward skills | W9-graph |
| **HUMAN_CONFIRMATION_REQUIRED** | GAP-016 (+ GAP-001 underwriting pillar) | Partner engineering pending source; brokerage pillar; optional domain MEDIUM exec elevation (Wave 1 Tier C) | W1, W11-graph |
| **SECTION_POLICY_GAP** | GAP-005 | Exec_summary HIGH/HITL only — **undermatch by design**; bullets/narratives carry MEDIUM | W5 ADR (document); **no** policy weaken |
| **SRFS_SELECTION_GAP** | GAP-010 | Per–role-family track weights in taxonomy + fixtures (reduce default genai 0.65 dominance) | W0.5b |
| **RUNTIME_OBSERVABILITY_GAP** | GAP-006 | X2 `x2_srfs_claim_business_metrics_substrate` — ledger attribution fix | W3, W3b |
| **EVIDENCE_GAP** | GAP-013 | Airline / sizing anchors remain INTERNAL_ONLY unless v2 uplift PROMOTE | W2a, W2b |
| **NO_ACTION_NEEDED** | GAP-017, GAP-018 | Exec suppression correct; GTM P2 consumption proven — **do not redo** baseline | — |

**P2 gaps carried forward:**

| Gap ID | Correction class | Title |
|--------|------------------|-------|
| GAP-015 | FACT_LINK_GAP | InsurTech carrier modernization not linked to forward-projecting skills |
| GAP-016 | HUMAN_CONFIRMATION_REQUIRED | Partner engineering / product feedback loops pending source |
| GAP-017 | NO_ACTION_NEEDED | Executive_summary correctly suppresses unsupported domain claims |

**P3 gaps carried forward:**

| Gap ID | Correction class | Title |
|--------|------------------|-------|
| GAP-018 | NO_ACTION_NEEDED | GTM P2 graph consumption proven — **preserve baseline; do not redo** |

Machine-readable backlog: [phase2_senior_role_implementation_backlog.json](docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json)

---

#### Proposed pillars / pillar families (W0.5 deliverable #2 — spec only)

| Proposed pillar ID | WS | Role examples | Evidence gate |
|--------------------|-----|---------------|---------------|
| `pillar_insurance_carrier_transformation` | WS-8 | AIG | `evidence_search_required` + InsurTech/base-resume trace review |
| `pillar_underwriting_claims_ops_ai` | WS-8 | AIG | `human_confirmation_required` — archive has underwriting **tokens**, not ops-transformation facts |
| `pillar_insurer_it_strategy_ai_enablement` | WS-9 | Lincoln | `evidence_search_required` — map InsurTech CTO + FS IT transformation facts |
| `pillar_enterprise_portfolio_governance` | WS-9 | Lincoln, Brown & Brown | `evidence_search_required` — no IT portfolio facts today |
| `pillar_banking_platform_responsible_ai` | WS-10 | Citi | `existing_evidence` partial — `fact_governance_003` HIGH; product-line skills `evidence_search_required` |
| `pillar_insurance_brokerage_distribution` | WS-11 | Brown & Brown | `human_confirmation_required` — no brokerage-specific archive hits |
| `pillar_interoperability_integration_ecosystem` | WS-11 | Brown & Brown | `evidence_search_required` |
| `pillar_hyperscaler_marketplace_partner_gtm` | WS-12 | Anthropic | `existing_evidence` partial — AWS HIGH; marketplace/Snowflake/GCP/Azure `evidence_search_required` |
| `pillar_applied_ai_partner_architecture` | WS-12 | Anthropic | `existing_evidence` partial — co_selling ACTIVE_CONFIRMED; partner_engineering `human_confirmation_required` |

---

#### Proposed bridge-edge families (spec only — all `evidence_required: true`)

| Bridge edge family | Source domain | Target domain | WS |
|--------------------|---------------|---------------|-----|
| `actuarial_to_insurer_ai_strategy` | `pillar_actuarial_foundation`, `epoch_actuarial_financial_engineering` | `pillar_insurer_it_strategy_ai_enablement` | WS-8, WS-9 |
| `actuarial_to_agentic_transformation` | Phase 1 actuarial/insurance | `pillar_agentic_ai_platforms`, `pillar_insurance_carrier_transformation` | WS-8 |
| `insurance_to_underwriting_claims_ops` | `pillar_embedded_options_insurance` | `pillar_underwriting_claims_ops_ai` | WS-8 |
| `insurtech_to_insurer_it_strategy` | InsurTech employment (base resume) | `pillar_insurer_it_strategy_ai_enablement` | WS-9 |
| `basel_ccar_to_ai_auditability` | `pillar_regulatory_governance`, `fact_governance_003` | `pillar_banking_platform_responsible_ai`, traceability skills | WS-10 |
| `regulatory_governance_to_responsible_ai` | `pillar_regulatory_governance` | Responsible AI skills (not runtime-gate-only) | WS-10 |
| `data_lineage_to_ai_traceability` | regulatory/data lineage facts | AI auditability / lineage skills | WS-10 |
| `hyperscaler_to_applied_ai_architecture` | `pillar_partner_gtm_alliances`, partner epoch | `pillar_applied_ai_partner_architecture` | WS-12 |
| `marketplace_to_partner_gtm` | `pillar_hyperscaler_marketplace_partner_gtm` | `pillar_gtm_presales_motion` | WS-12 |
| `partner_engineering_to_reference_architecture` | `skill_partner_partner_engineering` (pending source) | `skill_p2_tech_reference_architecture` | WS-12 |
| `partner_ecosystem_to_ai_adoption` | partner epoch | `skill_p2_tech_adoption_derisking` (DRAFT) | WS-12 |
| `domain_expertise_to_section_eligibility` | domain pillars | `skill_allowed_in_section` edges (forward-project actuarial beyond early_career) | WS-8, WS-14 |

**Constraint:** No pillar-to-pillar edges without documented evidence metadata; prefer `skill_bridge` / `domain_bridge` edges with fact backing.

---

#### Role-family taxonomy additions (JD targeting only — not proof)

| Role family ID | JD signal keywords (sample) | Maps to track-weight profile | WS |
|----------------|----------------------------|-------------------------------|-----|
| `INSURANCE_CARRIER_TRANSFORMATION` | carrier transformation, underwriting, claims, insurance operations, agentic AI | Elevate `track_actuarial_risk_derivatives` + `track_genai_agentic`; reduce blind GTM-only | WS-8 |
| `INSURER_IT_AI_ENABLEMENT` | IT strategy, AI enablement, enterprise architecture, App Dev, DevSecOps, data governance | Elevate `track_data_tech_cloud_ml`; actuarial forward bridge | WS-9 |
| `INSURANCE_BROKERAGE_IT_INNOVATION` | brokerage, distribution, interoperability, innovation incubation | Distinct from carrier; no carrier-underwriting claims | WS-11 |
| `BANKING_PLATFORM_AI` | banking platform, PDS, model risk, regulated AI productization | Elevate `AI_GOVERNANCE_RISK` / new family; forbid payment/liquidity without facts | WS-10 |
| `REGULATED_AI_GOVERNANCE` | Basel, CCAR, lineage, auditability, responsible AI, model risk | Split from generic `ENGINEERING_PLATFORM` | WS-10 |
| `PARTNER_APPLIED_AI_ARCHITECTURE` | applied AI architecture, partner engineering, joint solutions, reference architectures | Partner track weight ↑; separate from generic `PARTNERSHIPS_GTM` | WS-12 |
| `HYPERSCALER_MARKETPLACE_GTM` | marketplace, co-sell, GSI, hyperscaler, cloud partner | AWS/GCP/Azure only where evidence exists | WS-12 |

**Taxonomy edit wave:** W0.5b (after spec review) → update [master_role_family_taxonomy.yaml](apps_rg/config/domain_contract/master_role_family_taxonomy.yaml) and [track_weighted_graph_expansion.py](apps_rg/fact_inventory/track_weighted_graph_expansion.py) `ROLE_FAMILY_TRACK_WEIGHTS`.

---

#### Role fixture plan (W0.5 deliverable #5 — sanitized; JD/briefing = targeting only)

Fixture root: `docs/reports/apps_rg/fixtures/senior_roles/`
Manifest: `senior_role_fixture_manifest.json`

##### Fixture 1 — AIG-style insurance agentic transformation

| Field | Value |
|-------|--------|
| **Target role** | Global Head of Agentic AI Transformation (insurance carrier) |
| **Target role family** | `INSURANCE_CARRIER_TRANSFORMATION` |
| **JD / brief paths** | `aig_carrier_agentic_jd.txt`, `aig_carrier_agentic_brief.txt` |
| **Expected pillars** | `pillar_insurance_carrier_transformation`, `pillar_agentic_ai_platforms`, `pillar_regulatory_governance`, `pillar_actuarial_foundation` (forward) |
| **Expected bridge edges** | `actuarial_to_agentic_transformation`, `actuarial_to_insurer_ai_strategy`, `insurance_to_underwriting_claims_ops` (human-gated), `domain_expertise_to_section_eligibility` |
| **Expected selected skill families** | governed_agentic, ai_governance, FSA fellowship, model_risk; **not** GTM-only slice |
| **Forbidden claims** | Underwriting/claims/policy-admin **ownership**; ops transformation without facts |
| **Priority sections** | competencies, unify_narrative, executive_summary (HIGH/HITL only) |
| **Pass** | Offline traversal selects actuarial + agentic pillars; ≥1 carrier-domain fact/skill in bullets/competencies; no forbidden ops claims |
| **Fail** | GTM-only traversal; agentic swamps with zero actuarial forward rank; DRAFT/LOW in external claims |

##### Fixture 2 — Lincoln-style insurer IT strategy / AI enablement

| Field | Value |
|-------|--------|
| **Target role** | SVP IT Strategy & AI Enablement (insurer) |
| **Target role family** | `INSURER_IT_AI_ENABLEMENT` |
| **JD / brief paths** | `lincoln_insurer_it_ai_jd.txt`, `lincoln_insurer_it_ai_brief.txt` |
| **Expected pillars** | `pillar_insurer_it_strategy_ai_enablement`, `pillar_enterprise_portfolio_governance`, `pillar_cloud_data_aws`, `pillar_actuarial_foundation` |
| **Expected bridge edges** | `insurtech_to_insurer_it_strategy`, `actuarial_to_insurer_ai_strategy`, `domain_expertise_to_section_eligibility` |
| **Expected selected skill families** | FSA, reference_architecture, ai_governance, cloud_data; **not** early-career-only FSA |
| **Forbidden claims** | Full SVP IT strategy / App Dev CoE **ownership** without employment facts |
| **Priority sections** | executive_summary, competencies, ibm_narrative |
| **Pass** | FSA/projects visible outside early_career; IT-enablement pillar ranked above raw genai-only |
| **Fail** | Actuarial buried in early_career only; generic agentic executive with no IT-strategy pillar |

##### Fixture 3 — Citi-style banking AI platform / responsible AI

| Field | Value |
|-------|--------|
| **Target role** | MD Head of AI, Platform & Data Services (banking) |
| **Target role family** | `BANKING_PLATFORM_AI`, `REGULATED_AI_GOVERNANCE` |
| **JD / brief paths** | `citi_banking_platform_ai_jd.txt`, `citi_banking_platform_ai_brief.txt` |
| **Expected pillars** | `pillar_banking_platform_responsible_ai`, `pillar_regulatory_governance`, `pillar_agentic_ai_platforms` |
| **Expected bridge edges** | `basel_ccar_to_ai_auditability`, `regulatory_governance_to_responsible_ai`, `data_lineage_to_ai_traceability` |
| **Expected selected skill families** | model_risk, ai_governance, `fact_governance_003` path; **not** runtime-gate-only agentic skills |
| **Forbidden claims** | Payments, liquidity, trade, investor/issuer services, fraud **product** ownership |
| **Priority sections** | executive_summary, competencies, unify_bullets |
| **Pass** | Basel/CCAR HIGH traceable in exec or bullets; regulatory skills without agentic-gate swamping in competencies |
| **Fail** | Banking product lines appear without facts; agentic runtime gates dominate competencies |

##### Fixture 4 — Brown & Brown-style insurance brokerage IT strategy

| Field | Value |
|-------|--------|
| **Target role** | SVP IT Strategy & Innovation (insurance brokerage) |
| **Target role family** | `INSURANCE_BROKERAGE_IT_INNOVATION` |
| **JD / brief paths** | `brown_brokerage_it_jd.txt`, `brown_brokerage_it_brief.txt` |
| **Expected pillars** | `pillar_insurance_brokerage_distribution`, `pillar_interoperability_integration_ecosystem`, `pillar_gtm_presales_motion`, `pillar_cloud_data_aws` |
| **Expected bridge edges** | `domain_expertise_to_section_eligibility` (brokerage ≠ carrier) |
| **Expected selected skill families** | gtm_motion, executive_buyer, joint_vendor_roadmaps, cloud; **no** carrier-underwriting families |
| **Forbidden claims** | Brokerage platform **ownership**; carrier underwriting/claims narrative |
| **Priority sections** | competencies, unify_bullets |
| **Pass** | Brokerage pillar distinct from carrier in traversal receipt; no carrier conflation in output |
| **Fail** | InsurTech/carrier facts drive brokerage fixture; underwriting language in competencies |

##### Fixture 5 — Anthropic-style partner applied AI architecture

| Field | Value |
|-------|--------|
| **Target role** | Manager, Applied AI Architecture & Partnerships |
| **Target role family** | `PARTNER_APPLIED_AI_ARCHITECTURE`, `HYPERSCALER_MARKETPLACE_GTM` |
| **JD / brief paths** | `anthropic_partner_applied_ai_jd.txt`, `anthropic_partner_applied_ai_brief.txt` |
| **Expected pillars** | `pillar_applied_ai_partner_architecture`, `pillar_hyperscaler_marketplace_partner_gtm`, `pillar_partner_gtm_alliances`, `pillar_presales_solutioning` |
| **Expected bridge edges** | `hyperscaler_to_applied_ai_architecture`, `marketplace_to_partner_gtm`, `partner_engineering_to_reference_architecture`, `partner_ecosystem_to_ai_adoption` |
| **Expected selected skill families** | co_selling, solution_architecture, aws_modernization (ACTIVE); partner_engineering after HITL |
| **Forbidden claims** | Snowflake/GCP/Azure/marketplace **exclusivity**; partner sales; marketplace co-sell without evidence |
| **Priority sections** | competencies, ibm_bullets, unify_narrative |
| **Pass** | ≥3 ACTIVE_CONFIRMED partner skills in offline traversal; partner rank above default genai-only |
| **Fail** | Partner epoch mostly DRAFT in selected set; hyperscaler claims without archive trace |

##### Fixture 6 — GTM/pre-sales baseline (proven — keep)

| Field | Value |
|-------|--------|
| **Target role** | SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions |
| **Target role family** | `PARTNERSHIPS_GTM` + P2 technical presales |
| **JD / brief paths** | [exec_summary_gtm_presales_jd.txt](artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_jd.txt), [exec_summary_gtm_presales_brief.txt](artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_brief.txt) |
| **Expected pillars** | `pillar_gtm_presales_motion`, `pillar_technical_presales_accelerators` |
| **Expected bridge edges** | Existing P2 edges only (no senior-role bridge required for baseline PASS) |
| **Expected selected skill families** | 10 ACTIVE P2 skills (closeout); GTM MEDIUM in bullet/narrative lanes |
| **Forbidden claims** | Airline, ~$100M, estimation/sizing (INTERNAL_ONLY) |
| **Priority sections** | unify_bullets, unify_narrative, competencies |
| **Pass** | Reproduce closeout: ≥1 registry MEDIUM GTM fact in bullets/narratives; P2 in C03 metadata; exec HIGH-only |
| **Fail** | Regression vs [skills_graph_phase2_gtm_presales_closeout.json](docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json); MEDIUM in exec without HITL |

##### Fixture 7 — AI/data platform professional services (generalized)

| Field | Value |
|-------|--------|
| **Target role** | VP Global Professional Services — AI and enterprise data platform (generalized) |
| **Target role families** | `CONSULTING_DELIVERY_LEADERSHIP`, `EXECUTIVE_LEADERSHIP`, `DATA_ANALYTICS_LEADERSHIP`, `ENGINEERING_PLATFORM`, `PARTNERSHIPS_GTM` (JD targeting only) |
| **JD / brief / notes** | `ai_data_platform_professional_services_jd.txt`, `ai_data_platform_professional_services_brief.txt`, `ai_data_platform_professional_services_regression_notes.txt` |
| **Regression example** | EDB-style VP Global Professional Services — **not** a company-specific hiring target |
| **Expected pillars** | `pillar_agentic_ai_platforms`, `pillar_cloud_data_aws`, `pillar_executive_leadership`, `pillar_enterprise_portfolio_governance`, `pillar_revenue_commercialization`, `pillar_revenue_operations`, `pillar_gtm_presales_motion`, `pillar_technical_presales_accelerators`, `pillar_hyperscaler_marketplace_partner_gtm`, `pillar_applied_ai_partner_architecture` |
| **Expected bridge edges** | `partner_ecosystem_to_ai_adoption`, `hyperscaler_to_applied_ai_architecture`, `domain_expertise_to_section_eligibility` |
| **Expected skills** | P2 handoff + tech accelerators; W12 joint solution + reference architecture; `skill_ai_platform_commercialization`; `skill_sr_insurtech_cto_it_enablement`; revops forecasting; commercial stakeholder alignment |
| **Excluded skills** | `skill_partner_product_feedback_loops`, `skill_partner_partner_engineering`, `skill_customer_nrr_predictive_analytics_20pct`, `skill_customer_satisfaction_nps_25pct` |
| **Forbidden claims** | VP Global PS title ownership; **services P&L**; utilization/margin ownership; **customer success** ownership; **product roadmap** / **product feedback loops** external; marketplace co-sell without evidence |
| **Distinction** | Not pure GTM/pre-sales; not pure CS — post-sales implementation, value realization, services-led growth |
| **Graph gap** | None for W13 — no new pillar/skill unless W14 traversal fails manifest-only run |
| **Priority sections** | unify_bullets, unify_narrative, competencies, executive_summary |
| **Manifest** | [senior_role_fixture_manifest.json](docs/reports/apps_rg/fixtures/senior_roles/senior_role_fixture_manifest.json) · receipt [phase2_w13_archetype_fixtures_receipt.md](docs/reports/apps_rg/phase2_w13_archetype_fixtures_receipt.md) |

**W13 counts:** 7 archetype fixtures · 7 regression examples (see receipt).

---

#### Section impact plan (Wave 0.5 policy — no prompt edits)

| Section | Policy | Risk (senior roles) | Expected correction (post-graph waves) |
|---------|--------|---------------------|----------------------------------------|
| **headline** | HIGH-only concise domain framing | Generic agentic headline | Role-family-specific HIGH facts only; domain keyword from taxonomy match |
| **executive_summary** | HIGH or human-confirmed facts only | Undermatch (GAP-005); X2 substrate (GAP-006) | HITL Tier C elevations; Wave 3 attribution fix; **no** auto-MEDIUM |
| **unify_bullets** | Registry `claim_eligible_medium` where allowed | Best lane for domain MEDIUM | Forward-project actuarial/governance MEDIUM facts |
| **unify_narrative** | Same as bullets | Agentic narrative dominance | Bridge edges increase domain fact rank |
| **ibm_bullets** | P2 tech + partner facts | IBM portfolio vs airline conflation | Keep anchors fenced; P2 ACTIVE promotion per WS-6 |
| **ibm_narrative** | Snippet + HIGH paths | DRAFT P2/adoption skills | Conditional ACTIVE with fact links |
| **competencies** | Domain skills visible; separate claim-eligible vs directional/internal | Agentic swamping (GAP-014) | Split regulatory domain from agentic runtime-gate domain |

**NO_ACTION_NEEDED:** Executive_summary suppression of unsupported MEDIUM/LOW/DRAFT is correct (GAP-017).

---

#### Recommended implementation sequence (W0.5 deliverable #7 — canonical 8-step order)

| Step | Action | Plan wave(s) |
|------|--------|--------------|
| 1 | **Taxonomy split** — role-family additions + track-weight profiles (no graph nodes yet) | W0.5b |
| 2 | **Evidence-gated bridge-edge design** — 12 bridge families + 9 proposed pillars (carrier → brokerage → banking) | W8–W11-graph |
| 3 | **Partner/hyperscaler DRAFT activation criteria** — CONFIDENCE_GAP; no mass ACTIVE without fact links | W12-graph |
| 4 | **Human-confirmation packets** — domain MEDIUM exec elevation; partner engineering source | W1 |
| 5 | **Senior-role fixtures** — six sanitized JD/brief files + offline traversal receipts | W13 |
| 6 | **Section projection / runtime proof** — multilane + anti-overclaim matrix per role | W4, W14 |
| 7 | **X2 substrate fix** — `x2_srfs_claim_business_metrics_substrate` (ledger attribution) | W3, W3b |
| 8 | **Release-eligible proof** — live provider + X3_ALLOW + certification ladder | W7 |

**W0.5 complete (plan-only):** Backlog + spec in [phase2_senior_role_implementation_backlog.json](docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json) — **no graph edits in this wave.**

**Parallel (non-blocking):** W2a/2b evidence uplifts · W5 exec_summary ADR · W6 P2 DRAFT activation.

**GTM baseline (GAP-018):** Do **not** redo P2 augmentation; fixture 6 is regression guard only.

**Dependencies added:**

| Dependency | Blocks |
|------------|--------|
| Wave 0.5 spec approved | Any graph ledger edit (W8–W12-graph) |
| Role-family taxonomy W0.5b | Fixture track-weight overrides in W13 |
| WS-8..WS-12 graph specs | W13 traversal proof |
| W13 traversal receipts | W14 cross-section proof per role |
| Wave 1 HITL | Domain MEDIUM exec elevation (unchanged) |
| Wave 3b | Exec_summary X3_ALLOW (unchanged) |

**Risks added (senior-role):**

1. **Taxonomy overreach** — Adding pillars without evidence mints false traversal paths.
2. **Bridge edges without facts** — Creates ranking without claim substrate (forbidden).
3. **Brokerage/carrier conflation** — Brown & Brown fixture could inherit carrier language from shared facts.
4. **Partner DRAFT mass activation** — Would overclaim hyperscaler exclusivity.
5. **Weakening exec policy to fix undermatch** — Must use HITL + HIGH paths only.

**WHAT_NOT_TO_DO (Wave 0.5 + downstream graph waves):**

- Do not implement graph changes in Wave 0.5.
- Do not patch runtime, SRFS, section prompts, or validators until W13/W14 prove seam vs graph defect.
- Do not weaken executive_summary policy or auto-promote MEDIUM.
- Do not admit LOW / INTERNAL_ONLY / DRAFT into external claims.
- Do not use JD or briefing as proof.
- Do not restore `broad_skills_ledger`.
- Do not touch `agentic_core`.
- Do not claim explicit non-claims list without source-backed promotion.

**Wave 0.5 FINAL_ACCEPTANCE_CRITERIA:**

1. `phase2_senior_role_implementation_spec.json` lists all gaps, pillars, bridges, fixtures, sections.
2. Six fixture files + manifest exist (sanitized targeting text only).
3. WS-8..WS-14 each have scope, dependencies, and proof artifact names.
4. P0/P1 gaps trace to at least one workstream.
5. Original Waves 0–7 text preserved (this insert does not delete W1–W7).
6. No graph/runtime/prompt/validator files changed in Wave 0.5 execution.

---

### Wave 1 — Human-confirmation packet (MEDIUM GTM / SRFS queue)

**Purpose:** Separate **registry-eligible MEDIUM** (bullet/narrative lanes) from **exec_summary elevation** and **confirmation-queue** facts.

**Scope:** Produce HITL packet (markdown + machine-readable) for Amit confirmation — not auto-promotion.

**Packet tiers:**

| Tier | Fact IDs | Current gate | Decision asked |
|------|----------|--------------|----------------|
| A — Registry MEDIUM (bullets/narratives) | `fact_revenue_ops_001`, `fact_sales_accounts_001`, `fact_partnerships_gtm_002`, `fact_partnerships_gtm_004`, (+ 001/003/005 per registry) | `claim_eligible_medium` + archive trace | Confirm for **unify_*/ibm_*** only; Y/N per fact |
| B — SRFS confirmation queue | `fact_solutions_001`, `fact_solutions_002`, `fact_partnerships_gtm_005` | `MEDIUM_FACT_REQUIRES_AMIT_CONFIRMATION` | Confirm archive wording + allowed sections |
| C — Exec_summary elevation (optional) | Subset of Tier A/B | Not in `CLAIM_ELIGIBLE_MEDIUM_SECTIONS` today | Explicit per-fact: promote to HIGH / exec slice / deny |
| D — Metric-bearing HIGH | `fact_engineering_platform_006` | In exec slice; X2 substrate risk | Confirm $22M / 20% margin / 8→28 wording + source trace |

**Files likely inspected:**
[commercial_claim_eligibility.yaml](apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml),
[selected_role_fact_set.py](apps_rg/fact_inventory/selected_role_fact_set.py),
[apply_commercial_fact_promotion.py](apps_rg/fact_inventory/apply_commercial_fact_promotion.py),
phase_i archive under `artifacts/apps_rg/fact_inventory/phase_i_resumes_archive_extracted/`

**Files likely changed (after HITL only, Wave 1b):**
`apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml` (new confirmations),
`artifacts/apps_rg/fact_inventory/human_confirmation_receipts/phase2_gtm_medium_<ts>.json`,
optional ledger row `verification_status` updates via existing promotion scripts — **not in planning wave**

**Canonical commands expected (Wave 1 read-only draft):**
```bash
python apps_rg/fact_inventory/validate_commercial_srfs_projection.py
python apps_rg/fact_inventory/validate_commercial_medium_claim_output_containment.py
```

**Expected artifacts:**
`docs/reports/apps_rg/phase2_gtm_medium_human_confirmation_packet.md`
`docs/reports/apps_rg/phase2_gtm_medium_human_confirmation_packet.json`

**Pass criteria:** Every excluded GTM fact from exec run has tier + decision field + archive excerpt pointer.

**Fail/block criteria:** Missing archive trace for a fact marked confirm; conflating IBM portfolio with airline.

**Explicit non-claims:** Packet does not mint facts from JD/briefing.

---

### Wave 2a — Major-airline DevOps/AWS anchor evidence uplift

**Purpose:** Close `skill_p2_anchor_major_airline_devops_aws` — promote only with hard evidence or re-affirm INTERNAL_ONLY.

**Scope:** Read-only repo/archive scan unless new primary source is supplied by human.

**Files likely inspected:**
[skills_graph_phase2_airline_anchor_evidence_uplift.json](docs/reports/apps_rg/skills_graph_phase2_airline_anchor_evidence_uplift.json),
[master_skills_arsenal_ledger.json](apps_rg/fact_inventory/master_skills_arsenal_ledger.json),
resume archive paths cited in uplift report

**Files likely changed:** NONE unless promotion approved → `master_skills_arsenal_ledger.json` skill row + new `fact_*` with `source_trace_archive_relpaths` (Wave 2a-exec, Author-Gate)

**Canonical commands expected:**
```bash
# Re-run readonly uplift validator if exists; else manual audit per uplift JSON
```

**Expected artifacts:**
`docs/reports/apps_rg/skills_graph_phase2_airline_anchor_evidence_uplift_v2.json` with `promotion_decision` ∈ {`PROMOTE`, `DO_NOT_PROMOTE`, `DEFER`}

**Pass criteria:** Decision recorded; if PROMOTE: new fact_id + ACTIVE skill + no forbidden phrases without support.

**Fail/block criteria:** PROMOTE without airline-named primary source; ~$100M TCV without contract/trace.

**Explicit non-claims:** Until PROMOTE: no major-airline client, no ~$100M engagement ownership in any lane output.

---

### Wave 2b — Estimation/sizing directional evidence uplift

**Purpose:** Close `skill_p2_tech_estimation_sizing_directional` — technical sizing methodology vs adjacent financial ROI.

**Scope:** Same discipline as 2a; adjacent synergy/TCO evidence cannot bridge.

**Files likely inspected:**
[skills_graph_phase2_estimation_sizing_evidence_uplift.json](docs/reports/apps_rg/skills_graph_phase2_estimation_sizing_evidence_uplift.json)

**Files likely changed:** NONE unless PROMOTE path approved (Wave 2b-exec)

**Expected artifacts:**
`docs/reports/apps_rg/skills_graph_phase2_estimation_sizing_evidence_uplift_v2.json`

**Pass criteria:** `promotion_decision` documented; skill remains INTERNAL_ONLY if insufficient.

**Fail/block criteria:** Promotion from forecasting/ROI facts only (wrong domain).

**Explicit non-claims:** No “sizing model” or “effort estimation methodology” claims without primary trace.

---

### Wave 3 — Diagnose `x2_srfs_claim_business_metrics_substrate` block

**Purpose:** Prove whether failure is **claim-ledger attribution** vs **exec_summary policy**.

**Known failure (GTM run):**
`gross margin in claim row cites fact_exec_002 without substrate support` — `fact_exec_002` substrate is team-scale only; $22M/20% margin belong to `fact_engineering_platform_006`.

**Scope:** Read-only analysis of `canonical_claim_ledger_v2.json`, `text_claim_coverage.json`, `selected_fact_plan.json`, gate implementation in [executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) (`check_srfs_claim_business_metrics_substrate`).

**Files likely changed:** NONE in planning wave. Fix wave (3b) likely: **ledger binding / generator attribution** or **metric row splitting** — **not** prompt weakening, **not** disabling gate.

**Canonical commands expected:**
```bash
# Re-run single exec_summary mock after SRFS rematerialize; inspect x2 only
python -m apps_rg --section executive_summary ... --provider mock --allow-non-allow-exit-zero
```

**Expected artifacts:**
`docs/reports/apps_rg/phase2_gtm_x2_srfs_metrics_substrate_diagnosis.json`

**Pass criteria:** Root cause enum + recommended fix class + acceptance test (gate passes with unchanged facts when attribution corrected).

**Fail/block criteria:** “Fix” proposed by dropping gate or allowing unsupported metrics.

**Explicit non-claims:** Diagnosis does not authorize new metrics in output.

---

### Wave 4 — Multi-section GTM runtime materialization proof

**Purpose:** Prove P2 skills + GTM MEDIUM facts materialize in lanes where policy allows.

**Precondition:** GTM fixtures + **fresh** `selected_role_fact_set_active.json` (`binding_digest` matches JD/brief/role).

**Fixture SSOT:**
[exec_summary_gtm_presales_jd.txt](artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_jd.txt)
[exec_summary_gtm_presales_brief.txt](artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_brief.txt)

**Canonical command pattern (each lane):**
```bash
python -m apps_rg --section <SECTION> \
  --target-company "Unify Consulting" \
  --target-role "SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions" \
  --jd artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_jd.txt \
  --manual-brief artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_brief.txt \
  --provider mock \
  --allow-non-allow-exit-zero
```

**Sections (order):** `unify_bullets` → `unify_narrative` → `ibm_bullets` → `ibm_narrative` → `competencies`

**Files likely inspected per run:**
`run_manifest.json`, `runtime_payload.json`, `selected_fact_plan.json`, `compiled_prompt.txt`, `section_input_usage_ledger.json`, `x2_gate_outputs.json`, `x3_disposition.json`, `canonical_claim_ledger_v2.json`

**Files likely changed:** NONE (proof-only wave)

**Expected artifacts:**
`artifacts/apps_rg/runtime_proofs/<section>/mock/<run_id>/` (5 dirs)
`docs/reports/apps_rg/phase2_gtm_multilane_materialization_closeout.json`

**Per-lane pass criteria (minimum):**
- `skills_authority_source_type` = `augmented_skills_graph`
- `legacy_broad_skills_ledger_skills_authority` = false
- At least one of: `fact_revenue_ops_001`, `fact_sales_accounts_001`, `fact_partnerships_gtm_002` in `selected_fact_plan` / `ALLOWED_SOURCE_FACT_IDS` (bullets/narratives)
- P2 skill IDs present in `track_weighted` / C03 metadata when lane embeds graph expansion
- No airline / $100M / estimation sizing in output unless promoted

**Fail/block criteria:** MEDIUM facts absent in bullets/narratives despite registry + trace; INTERNAL_ONLY skills in allowed set; stale SRFS digest.

**Explicit non-claims:** Mock proof ≠ release-eligible.

---

### Wave 5 — Executive_summary policy recommendation (SSOT)

**Purpose:** Document policy so exec lane behavior is intentional, not “graph bug.”

**Recommendation (default — preserve current code intent):**

| Policy element | Recommendation |
|----------------|----------------|
| Default exec slice | **HIGH-only** via `allocate_executive_summary_with_arsenal` / SRFS exec quotas |
| MEDIUM GTM facts | **Never automatic** in exec_summary; use [commercial_claim_eligibility.yaml](apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml) (`CLAIM_ELIGIBLE_MEDIUM_SECTIONS` excludes exec) |
| MEDIUM in exec_summary | **Only after explicit human confirmation** (Wave 1 Tier C) → promote to HIGH or add exec-specific confirmation receipt — not registry alone |
| MEDIUM phrasing in exec | If ever elevated: **non-metric / non-ownership** clauses only unless fact has verified metrics + trace |
| Bullets/narratives/competencies | **Primary lanes** for P2 GTM MEDIUM and partnership/sales facts |
| Graph track expansion on SRFS path | Skills authority yes; C03 expansion may not appear in `runtime_payload` — document as observability gap, not authority gap |

**Deliverable:** ADR-style doc `docs/reports/apps_rg/phase2_gtm_executive_summary_policy_adr.md` — **no code change** unless product owner rejects recommendation (then Author-Gate).

**Files likely changed:** Documentation only (Wave 5); code only if ADR approves exec MEDIUM path (separate gated wave).

**Pass criteria:** ADR signed; aligns with `commercial_claim_eligibility.py` and exec_summary SRFS arsenal.

**Fail/block criteria:** ADR proposes auto-promotion of MEDIUM or broad_skills_ledger authority.

---

### Wave 6 — DRAFT P2 skill activation (conditional)

**Purpose:** Move HIGH-confidence DRAFT skills to ACTIVE only when fact-linked or archive-backed.

**Candidate skills (from closeout):**
`skill_p2_gtm_commercial_validation_pilots`, `skill_p2_gtm_presales_delivery_handoff`, `skill_p2_tech_demoable_accelerator`, `skill_p2_tech_adoption_derisking`, `skill_p2_tech_ibm_cloud_portfolio_anchor`

**Scope:** Per-skill evidence table → ACTIVE + `fact_id_links` or remain DRAFT.

**Files likely changed:** [master_skills_arsenal_ledger.json](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) — **exec wave only**

**Pass criteria:** Re-run track expansion offline; newly ACTIVE skills appear in `c03_selected_skill_ids` without INTERNAL_ONLY leakage.

**Explicit non-claims:** Snippet-only skills must not produce metrics without facts.

---

### Wave 7 — Release-eligible certification path

**Purpose:** Define what upgrades proof from mock/plumbing to release-eligible.

**Requirements ladder:**
1. All Wave 4 lanes: `proof_eligible=true`, `product_quality_status=PASS`, `x3_code=X3_ALLOW` (or documented ALLOW-with-review if policy exists).
2. Provider: **live** configured provider (not `TEST_MOCK` / `proof_scope=plumbing_only`); judges model-backed pass per `proof_eligible_allow_requires`.
3. SRFS: `binding_digest` matches targeting on every run; no stale active JSON.
4. X2: zero failed gates on certification sections; Wave 3 substrate fix merged for exec_summary if exec in certification bundle.
5. Human confirmations applied where MEDIUM used in output.
6. Fortknox / RTC requirements if executive_summary in release bundle — invoke [fortknox-evidence](.codex/skills/fortknox-evidence/SKILL.md) when scope includes certification compiler.

**Files likely changed:** CI manifest, certification receipts — out of Phase 2 graph scope unless explicitly in release wave.

**Pass criteria:** `RUNTIME_CERTIFICATION=true` run dir + compiler signoff artifacts listed in fortknox skill.

---

## DEPENDENCIES

| Dependency | Blocks |
|------------|--------|
| Wave 0.5 spec + fixture manifest approved | W0.5b taxonomy; W8–W12-graph ledger edits; W13 traversal proof |
| Wave 0.5b role-family taxonomy | Fixture track-weight overrides; offline C03 receipts (W13) |
| WS-8..WS-12 graph implementation | W13/W14 per-role proof |
| W13 traversal receipts | W14 cross-section anti-overclaim matrix |
| Wave 1 HITL decisions | Wave 1b ledger/commercial promotion; optional exec MEDIUM |
| Wave 2a/2b promotion decision | Any airline/sizing external language |
| Wave 3 diagnosis | Exec_summary X3_ALLOW under SRFS |
| Wave 3b fix (attribution) | Release-eligible exec_summary |
| Wave 4 SRFS rematerialize | Valid GTM multilane proof |
| Wave 5 ADR acceptance | Any exec_summary policy code change |
| Live provider + API keys | Wave 7 |

## RISKS

1. **Stale SRFS active file** — GTM proof invalid if `binding_digest` ≠ targeting (observed on `exec_summary_20260520_094051`).
2. **Metric substrate X2** — Model may merge `fact_engineering_platform_006` metrics onto wrong `source_fact_ids` in claim ledger.
3. **Over-claim from track expansion** — Offline C03 selects MEDIUM GTM facts that SRFS/exec slice correctly reject; do not “fix” by weakening exec.
4. **DRAFT activation without facts** — Creates skill projection without claim substrate.
5. **Mock proof false confidence** — `proof_eligible=false` runs must not be labeled PASS for product.

## RECOMMENDED_ORDER

```
W0 → W0.5 (senior-role spec + fixtures) → W0.5b (taxonomy/track weights)
  → [W8-graph ∥ W9-graph ∥ W10-graph; W11-graph after human confirm; W12-graph]
  → W13 (traversal proof) → W1 (packet) → W2a ∥ W2b → W3 → [W3b] → W4/W14 (multilane per role) → W5 (ADR) → [W1b] → W6 → W7
```

Parallel: W2a and W2b; W4/W14 lanes per fixture; W8–W10 graph specs can draft in parallel after W0.5 approval (execution still evidence-gated).

## WHAT_NOT_TO_DO

- Do not patch SRFS/exec selection to force MEDIUM GTM facts into exec_summary for demo PASS.
- Do not disable `x2_srfs_claim_business_metrics_substrate` or weaken metric gates.
- Do not set `broad_skills_ledger_used_as_authority=true`.
- Do not promote airline/sizing nodes without Wave 2 evidence.
- Do not edit section prompts before Wave 3 proves prompt defect (vs ledger/generator).
- Do not treat JD/brief GTM keywords as new facts.
- Do not conflate IBM $30M portfolio with airline anchor.
- Do not skip human confirmation for `fact_solutions_001/002` and queue MEDIUM rows.

## FINAL_ACCEPTANCE_CRITERIA

Phase 2 GTM/pre-sales graph work is **complete** when all are true:

1. Wave 0.5 senior-role implementation spec + six fixtures on file; P0/P1 gaps mapped to WS-8..WS-14.
2. Senior-role traversal proof (W13) for AIG, Lincoln, Citi, Brown & Brown, Anthropic + GTM baseline receipt.
3. Closeout JSON status PASS maintained after any ledger edits.
4. Human-confirmation receipts on file for all MEDIUM GTM/domain facts used externally.
5. Airline and sizing nodes have v2 uplift decision ≠ PROMOTE unless evidence exists.
6. Multilane closeout proves ≥1 registry MEDIUM GTM fact in `ALLOWED_SOURCE_FACT_IDS` for unify/ibm bullets or narratives (GTM baseline); per-role W14 matrix for senior fixtures.
7. Exec_summary ADR published; behavior matches implementation.
8. Exec_summary X2 substrate passes on certification run OR exec excluded from release bundle with documented rationale.
9. No LOW/INTERNAL_ONLY/DRAFT leakage in external claims across probed lanes.
10. Release-eligible proof (Wave 7) recorded separately from mock closeout.
11. Carrier / brokerage / banking-platform taxonomy separated in graph (no conflation in competencies output).

## PROOF_CLASSIFICATION LADDER

| Class | Meaning | Phase 2 applicability |
|-------|---------|------------------------|
| **audit-only** | Read-only JSON/MD reports, no CLI runtime | W0, **W0.5**, W1 draft, W2a/2b, W5 ADR |
| **mock runtime proof** | `python -m apps_rg --provider mock`; artifacts collected | W4 default |
| **non-certifying runtime proof** | Exit 0 inspection override; `proof_eligible=false`; X3 may BLOCK | Completed exec GTM run |
| **live runtime proof** | Real provider; judges attempted; may still be non-certifying if X3 BLOCK | Wave 7 precursor |
| **release-eligible proof** | `proof_eligible=true`, X3_ALLOW, product_quality PASS, live provider, certification receipts | Wave 7 only |

---

## EXECUTIVE_SUMMARY POLICY (summary for Wave 5 ADR)

**Recommended SSOT:**

- **HIGH-only default** for exec_summary SRFS slice.
- **MEDIUM never auto-in exec_summary** — registry `claim_eligible_medium` explicitly excludes executive_summary ([commercial_claim_eligibility.py](apps_rg/fact_inventory/commercial_claim_eligibility.py) lines 16–18).
- **Human-confirmed MEDIUM only** if product owner approves per-fact exec elevation (Wave 1 Tier C) with archive trace.
- **MEDIUM in bullets/narratives/competencies** — yes, when registry + `eligible_medium_with_source_trace` + lane policy satisfied.
- **Never** MEDIUM in exec with metric/ownership language unless fact is HIGH with verified `metric_values` and trace (e.g. `fact_engineering_platform_006` already HIGH but needs correct ledger attribution).

---

---

## WAVE 0.5 PLAN UPDATE RECEIPT (2026-05-20)

| Field | Value |
|-------|--------|
| **STATUS** | PASS (plan-update only) |
| **PLAN_ID** | `phase2-gtm-presales-remaining-f7a2c9` |
| **WAVE_ADDED** | `Wave 0.5 — Senior-role taxonomy, bridge-edge, and fixture backlog` |
| **SOURCE_AUDIT_ARTIFACTS** | [senior_role_graph_gap_analysis.md](docs/reports/apps_rg/senior_role_graph_gap_analysis.md), [senior_role_graph_gap_analysis.json](docs/reports/apps_rg/senior_role_graph_gap_analysis.json) |
| **GAP_COUNTS** | 18 total · 6 P0 · 8 P1 · 3 P2 · 1 P3 |
| **GAPS_CARRIED_FORWARD_COUNT** | 18 |
| **P0_GAPS_CARRIED_FORWARD** | GAP-001, GAP-002, GAP-003, GAP-004, GAP-005, GAP-006 |
| **P1_GAPS_CARRIED_FORWARD** | GAP-007, GAP-008, GAP-009, GAP-010, GAP-011, GAP-012, GAP-013, GAP-014 |
| **UPDATED_WORKSTREAMS** | WS-8 … WS-14 added |
| **RECOMMENDED_NEXT_WAVE** | Execute W0.5 artifacts (`phase2_senior_role_implementation_backlog.json` + fixture files), then W0.5b taxonomy |
| **PROOF_CLASSIFICATION** | `plan-update-only` |
| **ORIGINAL_PLAN_PRESERVED** | yes (Waves 0–7 intent unchanged) |
| **WAVE_0_5_ADDED** | yes |
| **FILES_CHANGED** | [phase2-gtm-presales-remaining-f7a2c9.md](.codex/plans/phase2-gtm-presales-remaining-f7a2c9.md) |
| **COMMANDS_RUN** | none |
| **ARTIFACTS_WRITTEN** | [phase2-gtm-presales-remaining-f7a2c9.md](.codex/plans/phase2-gtm-presales-remaining-f7a2c9.md), [phase2_senior_role_implementation_backlog.json](docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json) (fixture `.txt` files deferred to W0.5b) |

**EXPLICIT_NON_CLAIMS:** Underwriting, claims, policy admin, billing, brokerage ownership, transaction banking, payments, liquidity, trade, investor/issuer services, fraud operations, Fed/regulator-facing work, marketplace co-sell, Databricks, Snowflake, GCP, Azure partner exclusivity, partner sales, airline ~$100M engagement, technical estimation/sizing methodology — unless source-backed and promoted.

---

*Wave 0.5 added 2026-05-20 from [senior_role_graph_gap_analysis](docs/reports/apps_rg/senior_role_graph_gap_analysis.md). Waves 0–7 preserved. Graph/runtime/prompt/validator edits deferred to post–W0.5 gated sequence.*

---

## GRAPH SCOPE CLOSEOUT RECEIPT (2026-05-20)

| Field | Value |
|-------|--------|
| **STATUS** | GRAPH_SCOPE_COMPLETE |
| **PLAN_ID** | `phase2-gtm-presales-remaining-f7a2c9` |
| **GRAPH_SCOPE_STATUS** | GRAPH_SCOPE_COMPLETE |
| **FILES_CHANGED** | [phase2-gtm-presales-remaining-f7a2c9.md](phase2-gtm-presales-remaining-f7a2c9.md), [phase2_graph_scope_closeout_receipt.json](docs/reports/apps_rg/phase2_graph_scope_closeout_receipt.json), [phase2_graph_scope_closeout_receipt.md](docs/reports/apps_rg/phase2_graph_scope_closeout_receipt.md) |
| **ARTIFACTS_WRITTEN** | Graph scope closeout JSON/MD; plan updated; Notion Plans row synced |
| **SECTION_PROJECTION** | 49/49 PASS |
| **W14B_TRAVERSAL** | 7/7 without weight_override |
| **KNOWN_DEFERRED** | `pillar_insurance_brokerage_distribution` (no evidence — do not fabricate) |
| **NEXT_RECOMMENDED_WAVE** | W1 human-confirmation packet or `python -m apps_rg --section <lane>` minimum runtime |
| **PROOF_CLASSIFICATION** | graph_scope_closeout_offline_receipts_not_runtime_release_proof |

**EXPLICIT_NON_CLAIMS:** Graph closeout does not authorize new external claims, brokerage pillar fabrication, airline/~$100M/estimation sizing promotion, or runtime X3_ALLOW.
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
