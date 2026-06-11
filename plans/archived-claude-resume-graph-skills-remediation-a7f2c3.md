---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\resume-graph-skills-remediation-a7f2c3.md'
original_relative_path: 'resume-graph-skills-remediation-a7f2c3.md'
source_sha256: fbe562af0295b1041985e59d9a299c51eae17ee1912a9a7e4a0c4eaf1e4d63bb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: resume-graph-skills-remediation-a7f2c3
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Phase I Resume → Graph Skills Remediation

Audit 17 Phase I archived resumes against the augmented skills graph, repair missing source linkages,
promote stale DRAFT nodes, and add 10 new skill_row nodes for competencies present in resumes but
absent from the graph.

> **plan_id discipline**: file `resume-graph-skills-remediation-a7f2c3.md` → `plan_id: resume-graph-skills-remediation-a7f2c3` → markers use `plan=resume-graph-skills-remediation-a7f2c3`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: In Progress
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-27

---

## Context (SCQA)

- **Situation** — The augmented skills graph (`master_skills_arsenal_ledger.json`) contains 163 skill nodes mapped to 20 role families. 17 Phase I customized resumes exist in `C:\Users\amita\Downloads\Phase I Resumes Archive\` covering roles from Chief AI Officer to Quantitative Research & Trading.
- **Complication** — 89 skills have no `source_resume_files` entry. Several role families with resumes have skills stuck in DRAFT status. 10 skills present with quantifiable evidence in the resumes (MEDDPICC, CPQ, SOC2/zero-trust, ARR/LTV/CAC, Confluent, Watson Studio, algo-trading, NPS, FINRA/SEC, credit adjudication) have no corresponding graph node.
- **Question** — How do we ensure all Phase I resume capabilities are reflected in the skills graph with correct source linkages, activation status, and node coverage?
- **Answer** — Two-wave remediation: W1 repairs linkages and promotes existing nodes; W2 adds the 10 missing skill nodes.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Linkage fixes + DRAFT promotion | 🔄 IN PROGRESS | — | — |
| W2 | Add 10 new skill_row nodes | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | skill_capital_reserving + quant DRAFT source linkage | 🔲 TODO |
| W1.2 | Promote CUSTOMER_SUCCESS + DATA_ANALYTICS DRAFT → ACTIVE | 🔲 TODO |
| W2.1 | Add 10 new skill_row nodes | 🔲 TODO |
| W2.2 | Validate ledger integrity | 🔲 TODO |

---

## Out Of Scope

- Agentic platform skills (pillar_agentic_ai_platforms / pillar_regulatory_governance) that legitimately have no resume source — these come from building the system, not business resumes.
- Phase II insurance-specific resumes (INSURANCE_CARRIER_TRANSFORMATION, INSURER_IT_AI_ENABLEMENT) — existing sources sufficient.
- Modifying any graph edges or graph_nodes (ADG) — only `skill_rows` in the arsenal ledger.
- Any change to `agentic_core`.

---

## Wave 1 — Linkage Fixes and DRAFT Promotion

WAVE_ID: W1
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — edits confined to `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` skill_rows only; no schema change, no deletion.

**Phases**:
- **W1.1** — skill_capital_reserving + quant DRAFT source linkage | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Promote CUSTOMER_SUCCESS + DATA_ANALYTICS DRAFT → ACTIVE | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `skill_capital_reserving.source_resume_files` lists Chief AI Officer, CTO Resume, Strategic Finance
- Greek DRAFT skills (delta, rho, convexity) have Quantitative Research & Trading in source_resume_files
- CUSTOMER_SUCCESS skills are ACTIVE (not DRAFT)
- DATA_ANALYTICS_LEADERSHIP skills are ACTIVE_CONFIRMED
- `python apps_rg/fact_inventory/master_skills_arsenal_ledger.py` exits 0

---

## Wave 2 — New Skill Nodes

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Add 10 new skill_row nodes to master_skills_arsenal_ledger.json | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Validate ledger via master_skills_arsenal_ledger.py + validate_p2_w0_graph_skills_gap_inventory.py | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**New nodes** (10):
1. `skill_meddpicc_sales_qualification` — pillar_gtm_presales_motion — SALES_STRATEGIC_ACCOUNTS, REVENUE_OPERATIONS
2. `skill_cpq_deal_velocity_automation` — pillar_revenue_operations — REVENUE_OPERATIONS
3. `skill_soc2_zero_trust_security` — pillar_regulatory_governance — ENGINEERING_PLATFORM, EXECUTIVE_LEADERSHIP
4. `skill_saas_arr_ltv_cac_metrics` — pillar_strategic_finance_saas — STRATEGIC_FINANCE, REVENUE_OPERATIONS
5. `skill_confluent_streaming_platforms` — pillar_interoperability_integration_ecosystem — PARTNERSHIPS_GTM, SALES_STRATEGIC_ACCOUNTS
6. `skill_watson_studio_fraud_aml` — pillar_banking_platform_responsible_ai — BANKING_PLATFORM_AI, CUSTOMER_SUCCESS
7. `skill_algo_trading_sub_ms_inference` — pillar_derivatives_structured — QUANT_TRADING_HPC
8. `skill_nps_customer_health_scoring` — pillar_customer_stakeholder — CUSTOMER_SUCCESS
9. `skill_finra_sec_regulatory_compliance` — pillar_regulatory_governance — QUANT_TRADING_HPC, AI_GOVERNANCE_RISK
10. `skill_credit_adjudication_default_risk` — pillar_risk_management — BANKING_PLATFORM_AI, CONSULTING_DELIVERY_LEADERSHIP

**Acceptance**:
- `len(skill_rows)` increases from 163 to 173
- All 10 new nodes have `activation_status=DRAFT`, `source_resume_files` populated, `allowed_phrases` non-empty
- `python apps_rg/fact_inventory/master_skills_arsenal_ledger.py` exits 0

---

## Execution Details

### W1.1 — Quant DRAFT Source Linkage

**Scope**: Update `source_resume_files` on `skill_capital_reserving`, `skill_greeks_delta`, `skill_greeks_rho`, `skill_greeks_convexity`, `skill_insurance_liabilities_*`.

**Commands**:
```bash
python apps_rg/fact_inventory/master_skills_arsenal_ledger.py
```

### W1.2 — DRAFT Promotion

**Scope**: Set `activation_status=ACTIVE` on `skill_customer_nrr_predictive_analytics_*` and `skill_customer_satisfaction_nps_25pct`. Set `activation_status=ACTIVE_CONFIRMED` on `skill_customer_nrr_predictive_analytics_*` and the DATA_ANALYTICS DRAFT.

**Commands**:
```bash
python apps_rg/fact_inventory/master_skills_arsenal_ledger.py
```

### W2.1 — Add New Skill Nodes

**Scope**: Add 10 new entries to `skill_rows` array in the JSON ledger.

### W2.2 — Validate

**Commands**:
```bash
python apps_rg/fact_inventory/master_skills_arsenal_ledger.py
python apps_rg/fact_inventory/validate_p2_w0_graph_skills_gap_inventory.py 2>&1 || true
```

---

## Gap Register

**GAP-1: AI_SOLUTIONS_ARCHITECTURE has no Phase I resume** — 96 skills mapped, 81 with src=NONE. Root cause: these are agentic engineering skills, not business resume skills. Correctly unlinked. Deferred — no action in this plan.

**GAP-2: 10 competencies in resumes not in graph** — MEDDPICC, CPQ, SOC2/zero-trust, ARR/LTV/CAC, Confluent, Watson Studio, algo trading, NPS, FINRA/SEC, credit adjudication. Addressed in W2.

**GAP-3: skill_capital_reserving src=NONE** — phrase found in 3 resumes. Fixed in W1.1.

**GAP-4: QUANT DRAFT skills (14 nodes, 6 with src=NONE)** — Greeks and insurance liabilities not linked. Partially fixed in W1.1.

---

## Definition of Done

DoD-1: W1 linkage repairs applied — skill_capital_reserving + 4 Greek/insurance skills have source_resume_files populated.
- Evidence: `python -c "import json; d=json.load(open('apps_rg/fact_inventory/master_skills_arsenal_ledger.json')); print([r['source_resume_files'] for r in d['skill_rows'] if r['skill_id']=='skill_capital_reserving'])"` returns non-empty list
- Status: TODO

DoD-2: DRAFT promotion confirmed — CUSTOMER_SUCCESS and DATA_ANALYTICS skills are ACTIVE.
- Evidence: `python -c "import json; d=json.load(open('apps_rg/fact_inventory/master_skills_arsenal_ledger.json')); print([(r['skill_id'],r['activation_status']) for r in d['skill_rows'] if 'customer' in r['skill_id'] or 'data_analytics' in r.get('pillar','')])"` shows ACTIVE
- Status: TODO

DoD-3: 10 new skill nodes added — ledger has 173 skill_rows.
- Evidence: `python -c "import json; d=json.load(open('apps_rg/fact_inventory/master_skills_arsenal_ledger.json')); print(len(d['skill_rows']))"` prints 173
- Status: TODO

DoD-4: Ledger loads cleanly.
- Evidence: `python apps_rg/fact_inventory/master_skills_arsenal_ledger.py` exits 0
- Status: TODO

DoD-5: Memory writeback — session observation captured.
- Evidence: `mem_add_observations` called with plan summary
- Status: TODO
