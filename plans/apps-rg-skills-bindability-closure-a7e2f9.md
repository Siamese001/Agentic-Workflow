---
plan_id: apps-rg-skills-bindability-closure-a7e2f9
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg Skills Bindability Closure — Make Every Selected Skill Surfaceable

Close the gap class found by the 2026-06-10 omission audit: graph skills that targeting correctly selects but that **no competency bundle can bind**, so they silently drop before the resume surface. Fill the quant/derivatives-ALM depth cluster, the empty `cloud_hpc_modernization` family, unlinked HIGH facts, and the RevOps/regulated-governance clusters — then add the CI liveness gate whose absence let all of this sit invisible.

> **plan_id discipline**: `plan_id` matches the filename stem `apps-rg-skills-bindability-closure-a7e2f9`. Wave markers use `plan=apps-rg-skills-bindability-closure-a7e2f9`.

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | (Sibling, not successor, of `skills-graph-hardening-gap-closure-53576c` — that plan hardens graph construction; this one closes selection→bundle bindability.) |

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** — The 2026-06-10 omission audit (run after the user asked "where is my insurance/ERM expertise?") traced the full selection chain and found the pipeline was **3-for-4**: the skills graph is rich (~30 actuarial/quant nodes, 166 skill nodes total); targeting is conditional and **fired correctly** (the AIG run resolved `role_family_key = INSURANCE_CARRIER_TRANSFORMATION`, actuarial track weight 0.35); the track-weighted expansion **selected** `fsa_fellowship`, `capital_modeling`, `regulatory_capital` — and then the chain broke at the **binding hop**: no competency bundle could bind those selected skills to a taxonomy category, so `stamp_competency_bundle_bindings` silently dropped them. `ccb_insurance_domain_erm` (committed `c53d62609e`) fixed that one instance.
- **Complication** — The audit shows the instance was a class. 104/166 skill nodes are bound by no bundle file; after subtracting nodes served by other channels, four real clusters remain unreachable: (1) **quant depth ×16** — all 7 Greeks, derivatives_pricing, exotic/structured derivatives, multi_greek_hedging, insurance_liabilities, embedded_options, reserving, market_risk, actuarial_software — unreachable even for role families that weight actuarial at 0.35–0.55 (QUANT_TRADING, GOVERNANCE_RISK, INSURANCE_CARRIER_TRANSFORMATION); (2) **RevOps/GTM ×10** (salesforce pipeline analytics, forecasting, NRR/NPS, $15M modernization deals, global-FI sales leadership) absent from competencies; (3) **regulated-industry governance ×6** (banking_ai_governance_controls, regulated_financial_institution_modernization, enterprise_portfolio_data_governance, insurtech_cto_it_enablement); (4) **partner/pre-sales residue ×15**. Plus: the declared `cloud_hpc_modernization` family is still empty (second live instance of the born-empty-family defect); 6/13 HIGH-confidence ledger facts are linked by no bundle, including `fact_quant_hpc_001` on the IBM `hpc_risk_analytics` episode whose `linked_source_fact_ids` is an **empty list**, and `fact_quant_hpc_002` (TraderSense AI trading platform — an entire employer reachable only via locked sections). Root cause (RCA'd): bundle-file family metadata is decorative (zero code consumers), enforcement lives in a differently-spelled validator constant, and nothing requires expansion-selected skills to be bindable — omission-class defects are invisible to the presence-oriented X2/X1D stack.
- **Question** — How do we make every targeting-selected skill actually surfaceable on the resume, fill the audited clusters with real (never fabricated) proof bindings, and install the invariant that prevents the class from recurring?
- **Answer** — (W1) author the quant/derivatives-ALM competency bundle + fill `cloud_hpc_modernization` + repair the empty/missing HIGH-fact linkages (highest severity, all HIGH-confidence-proof-backed); (W2) author the RevOps/GTM and regulated-governance bundles (medium severity); (W3) add `check_competency_family_bindability.py` — the CI liveness/parity gate: declared families populated-or-dormant, JSON↔validator family vocabulary parity, and **every expansion-selectable skill bindable by ≥1 bundle** (the exact missed invariant); (W4) live verification on insurer- and quant-weighted targets plus the regression slice.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | **Quant-depth + HPC bindability (High)** — `ccb_quant_derivatives_alm` bundle; fill `cloud_hpc_modernization`; repair empty `linked_source_fact_ids` on IBM `hpc_risk_analytics` (+ `fact_quant_hpc_001/002`, `fact_governance_003` linkage) | ~35K | Quant skills/facts already exist in graph+ledger (audited 2026-06-10); no fabrication needed — binding only | 🔲 TODO | Greeks/derivatives/ALM + HPC skills bindable; no empty `linked_source_fact_ids` on metric-bearing episode bundles; both born-empty families populated |
| W2 | W2.1, W2.2 | **RevOps/GTM + regulated-governance bundles (Medium)** | ~30K | Existing facts (`fact_revenue_ops_*`, governance facts) suffice as anchors | 🔲 TODO | RevOps and regulated-governance skill clusters bindable to existing taxonomy categories; partner/pre-sales residue triaged (bind or mark dormant) |
| W3 | W3.1, W3.2 | **CI bindability/liveness gate** — `ops_scripts/ci/check_competency_family_bindability.py` | ~30K | Pattern: `check_prompt_gate_numeric_parity.py`; advisory first, fail-closed via env flag | 🔲 TODO | Gate fails on: declared family with 0 bundles and no `dormant: true`; JSON↔validator family vocabulary drift; expansion-selectable skill with 0 binding bundles. Green on post-W2 tree; red when any W1/W2 bundle is reverted (negative test) |
| W4 | W4.1 | **Live verify + regression** — insurer-profile and quant-profile competencies runs surface the new clusters; full unit slice | ~25K | W1–W3 landed; external Claude key present | 🔲 TODO | Insurer-target run surfaces insurance/ERM + quant terms with bundle lineage; no X2 regression (coverage, lineage, orphan-category gates all green); 11-lane full run unaffected |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Author `ccb_quant_derivatives_alm` + `cloud_hpc_modernization` fill (skills verified to graph-resolve) | 🔲 TODO |
| W1.2 | Repair HIGH-fact linkages (IBM hpc episode empty list; quant_hpc_001/002; governance_003 EY check) | 🔲 TODO |
| W2.1 | RevOps/GTM competency bundle (commercial_operating_impact / partnerships categories) | 🔲 TODO |
| W2.2 | Regulated-governance bundle + partner/pre-sales residue triage (bind or dormant-mark) | 🔲 TODO |
| W3.1 | Bindability gate: family liveness + JSON↔validator vocabulary parity | 🔲 TODO |
| W3.2 | Bindability gate: expansion-selectable skills must be bundle-bindable (+ negative test) | 🔲 TODO |
| W4.1 | Live insurer/quant-profile verification + regression slice | 🔲 TODO |

---

## Out Of Scope

- **Fabricating any skill, fact, or metric** — every binding in this plan attaches *existing* graph nodes to *existing* HIGH/claim-eligible ledger facts. If a cluster lacks a real proof anchor, it gets `dormant: true`, not an invented fact.
- Changing the 8-category competencies taxonomy, the 7-family validator constant's membership, or any X2 threshold — W3 adds a *parity/liveness* check, never edits enforcement values.
- The TraderSense employer as a generated lane (early-career stays locked-section by design; W1 only links its fact for competencies enrichment eligibility).
- The IBM slot-fact grounding/judge tail and headline stochastic miss (tracked in `apps-rg-aig-remaining-lanes-closeout-d4e1f7`).
- `agentic_core` and other `apps_*`.

---

## Wave 1 — Quant-Depth + HPC Bindability (High severity)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Author quant/HPC bundles | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Repair HIGH-fact linkages | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W1.1 — Add `ccb_quant_derivatives_alm` to `competency_capability_bundles.json`: skills = `skill_derivatives_derivatives_pricing`, `skill_greeks_hedging_multi_greek_hedging`, `skill_risk_greek_stress_testing`, `skill_insurance_liabilities_insurance_liabilities`, `skill_insurance_liabilities_embedded_options`, `skill_capital_reserving`, `skill_capital_pricing_actuarial`, `skill_risk_market_risk` (audited to graph-resolve); anchor `fact_quant_hpc_003` (HIGH: "quantitative rigor through derivatives pricing, capital modeling, portfolio…"); categories `governance_risk_compliance` + `data_analytics_modernization`; family `insurance_domain_modernization` or a `dormant`-cleared `cloud_hpc_modernization` sibling as fits. Add `ccb_cloud_hpc_modernization` (family `cloud_hpc_modernization` — second born-empty family): skills `skill_quant_hpc_*` / `sr_cloud_data_platform_engineering` adjacents per graph audit, anchored on `fact_quant_hpc_001` (HIGH, IBM HPC risk re-architecture).
- W1.2 — IBM `hpc_risk_analytics` episode bundle: `linked_source_fact_ids` is currently `[]` — link `fact_quant_hpc_001`. Verify `fact_governance_003` (Basel/CCAR) is linked from the EY `regulatory_analytics_modernization` episode (link if absent). Link `fact_quant_hpc_002` (TraderSense) wherever the early-career-adjacent competency bundle can carry it (enrichment eligibility only; identity stays locked-section). Re-run the bundle node-resolution + coverage tests after each edit.

**Acceptance**:
- Every Greeks/derivatives/ALM/HPC skill node has ≥1 binding bundle; both formerly-empty families populated; zero empty `linked_source_fact_ids` on metric-bearing episode bundles; all referenced node/fact ids resolve (existing resolution tests green).

---

## Wave 2 — RevOps/GTM + Regulated-Governance Bundles (Medium severity)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — RevOps/GTM competency bundle | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Regulated-governance bundle + residue triage | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W2.1 — `ccb_revops_gtm_analytics`: bind `skill_revops_salesforce_pipeline_analytics`, `skill_revops_salesforce_forecast_pipeline`, forecasting/NRR/NPS nodes, `skill_sales_modernization_deals_15m`, `skill_sales_global_financial_institutions_sales_leadership`, `skill_commercial_gtm_investment_pipeline_decisions` → categories `commercial_operating_impact` (+ `cloud_partner_ecosystems` where apt); anchors from `fact_revenue_ops_*`.
- W2.2 — `ccb_regulated_industry_governance`: bind `skill_sr_banking_ai_governance_controls`, `skill_sr_regulated_financial_institution_modernization`, `skill_sr_enterprise_portfolio_data_governance`, `skill_sr_insurtech_cto_it_enablement` → `governance_risk_compliance`; anchors from governance/consulting facts. Triage the remaining ~15 partner/pre-sales nodes: bind the resume-relevant ones into the existing IBM pre-sales surface or mark the graph row `dormant`-class (no invented competency).

**Acceptance**:
- RevOps + regulated-governance clusters bindable; partner residue has zero ambiguous rows (each either bound or explicitly dormant); coverage/orphan-category gates stay green.

---

## Wave 3 — CI Bindability / Liveness Gate

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Family liveness + vocabulary parity | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Selected-skill bindability check + negative test | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W3.1 — New `ops_scripts/ci/check_competency_family_bindability.py` (constitutional §31 routing; advisory by default, `COMPETENCY_BINDABILITY_FAIL_CLOSED=1` to enforce; bypass env per house pattern): (a) every family in `required_capability_families` + `optional_supporting_families` has ≥1 `activation_status: active` bundle OR carries an explicit `dormant: true` marker; (b) the JSON required-family list and the validator's `REQUIRED_CAPABILITY_FAMILIES` constant reconcile through an explicit alias map — fail on unmapped drift (today: 8 JSON names vs 7 differently-spelled constant keys, silently divergent).
- W3.2 — (c) For each role-family profile in `ROLE_FAMILY_TRACK_WEIGHTS`, every skill the track-weighted expansion can select must be bindable by ≥1 bundle (the exact invariant whose absence dropped the AIG run's selected actuarial skills). Implement against the expansion's selectable set, not a live LLM run — deterministic. Negative test: temporarily filtering out `ccb_insurance_domain_erm` must turn the gate red. Register in `run_contract_gates.py`.

**Acceptance**:
- Gate green on the post-W2 tree; red under the negative test; wired into CI; zero enforcement-value changes to existing gates.

---

## Wave 4 — Live Verification + Regression

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Insurer/quant-profile live runs + regression slice | ~25K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W4.1 — Standalone competencies runs against (a) the AIG insurer target (resolves `INSURANCE_CARRIER_TRANSFORMATION`) and (b) a quant/governance-weighted target: assert the output carries insurance/ERM and quant-depth terms with `competency_bundle_id` + `graph_skill_node_ids` lineage. Re-run the omission audit script — unreached-cluster count for the four named clusters reaches zero-or-dormant. Full regression: `python -m pytest -q tests/unit/apps_rg -k "competenc or bundle"` + one full 11-lane AIG run to confirm no lane regression.

**Acceptance**:
- Insurance/ERM + quant terms surface with full lineage on insurer-weighted runs; audit re-run clean; no new X2/X1D failures anywhere.

---

## Definition of Done

| # | Definition of Done | Verification |
|---|---|---|
| 1 | Quant/derivatives/ALM + HPC clusters bindable; both born-empty families populated | bundle node-resolution test + audit script re-run |
| 2 | Zero empty `linked_source_fact_ids` on metric-bearing episode bundles; the 6 unlinked HIGH facts linked or explicitly dispositioned | audit script section B clean |
| 3 | RevOps/GTM + regulated-governance clusters bindable; partner residue fully triaged | audit script cluster report |
| 4 | CI gate enforces family liveness, vocabulary parity, and selected-skill bindability | gate green; negative test red; registered in `run_contract_gates.py` |
| 5 | **Smoke run (executable surface):** insurer-target competencies run surfaces insurance/ERM + quant terms with bundle lineage | `python -m apps_rg --target-company AIG ... --section competencies` artifact inspection |
| 6 | No regression: coverage/lineage/orphan gates green; full 11-lane AIG run unchanged or better | regression slice + full run matrix |

Verification vs Deferral:

| Item | Verified in-plan | Deferred (follow-up) |
|---|---|---|
| Cluster bindability · fact linkage · CI gate · live insurer/quant verification | Yes — W1–W4 | — |
| Per-track selection-cap tuning (actuarial track yields 3 rows vs genai 12 even at weight 0.35 — ranking depth, not bindability) | — | Follow-up: selection-depth calibration, own scoped effort |
| TraderSense as a generated employer lane | — | Locked-section by design; revisit only on explicit user authorization |

---

## Safety / Invariants

- **No fabrication**: bindings attach existing graph nodes to existing HIGH/claim-eligible facts only; unprovable clusters become `dormant`, never invented.
- **No gate weakening**: W3 adds checks; it never edits thresholds, category counts, or family membership of existing enforcement.
- Locked sections (FSA cert, early-career actuarial identity) stay verbatim; this plan only widens *generated-lane* reachability.
- Root-cause traceability: this plan operationalizes the 2026-06-10 RCA ("declared-intent-without-consumer" pattern — see session memory) — the W3 gate is the recurrence-prevention for that genus.
