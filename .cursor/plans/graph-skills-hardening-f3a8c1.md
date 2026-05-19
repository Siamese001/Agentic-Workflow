---
plan_id: graph-skills-hardening-f3a8c1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Graph skills hardening — Part 1 (career graph) + Part 2 (competencies)

Two-part plan on **`augmented_skills_graph`** (`master_skills_arsenal_ledger.json`):

| Part | Focus | Outcome |
|------|--------|---------|
| **Part 1** | Multi-career **nodes, edges, flow** (3 tracks, years, employment spine, activation, track-weighted expansion) | Graph represents 4–5 career arcs with proof-safe traversal |
| **Part 2** | **Competencies** lane missing graph-skills (today: `broad_skills_ledger`) | Parity with [exec-summary-graph-only-b5a963](exec-summary-graph-only-b5a963.md) PASS on `python -m apps_rg --section competencies` |

> **plan_id:** `graph-skills-hardening-f3a8c1`  
> **Predecessor (completed):** [exec-summary-graph-only-b5a963](exec-summary-graph-only-b5a963.md) · [exec_summary_20260519_122505](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_122505)  
> **Taxonomy SSOT:** [career_track_taxonomy_operator_confirmed.md](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.md) · [career_track_taxonomy_operator_confirmed.json](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_PART: PART_2
CURRENT_WAVE: P2-W10
LAST_COMPLETED_WAVE: P2-W9-UNIFY-BULLETS-FINAL-CLOSEOUT
LAST_UPDATED: 2026-05-19
COMPLETED_AT: 2026-05-19
CLOSEOUT_RECEIPT: docs/reports/apps_rg/graph_skills_hardening_p2_accelerated_closeout.json

**Execution order:** Complete **Part 1** (graph asset + traversal policy), then **Part 2** (competencies runtime proof). Part 2 can prototype against the existing graph before P1-W5, but production proof should run after P1-W2 minimum (`career_track` nodes materialized).

---

## Context (SCQA)

- **Situation** — Executive summary already proves graph-only generation (REAL_LLM, X3_ALLOW, C0.3 BOUND). The arsenal graph has 6 `career_epoch` nodes and 131 skill rows but competencies still uses `broad_skills_ledger_competencies` for product proof.
- **Complication** — Multi-career experience (actuarial → tech/ML → agentic) is not selectable in proof expansion; 47/131 skill rows lack `fact_id_links`; competencies has no graph-only repair, validator, or X2 metric-locality gates.
- **Question** — How do we model three career tracks in the graph **and** harden the competencies lane to consume graph skills authority?
- **Answer** — **Part 1** materializes operator-confirmed career tracks and employment/spine/activation/expansion. **Part 2** ports exec-summary graph-only discipline to competencies end-to-end.

---

# Part 1 — Multi-career graph (nodes, edges, flow)

## Operator-confirmed career tracks

| Track ID | Label | Years | Narrative |
|----------|--------|-------|-----------|
| `TRACK_ACTUARIAL_RISK_DERIVATIVES` | Actuarial / risk / derivatives | **2002–2010** | Foundation |
| `TRACK_DATA_TECH_CLOUD_ML` | Data / tech / Cloud / ML | **2010–2022** | Career change; includes **trading/HPC** + **partner GTM** |
| `TRACK_GENAI_AGENTIC` | GenAI / Agentic | **2022–present** | Specialization |

**Confirmed:** `pillar_trading_hpc` → track 2 · partner GTM → track 2 only · sequence `1 → 2 → 3` (non-causal).

### Epoch → track map

| `career_epoch` | → Track |
|----------------|---------|
| `epoch_actuarial_financial_engineering` | 1 |
| `epoch_enterprise_risk_governance` | 1 |
| `epoch_cloud_data_platform_engineering` | 2 |
| `epoch_ai_platform_commercialization` | 2 (bridge to 3 where agentic-specific) |
| `epoch_partner_gtm_revenue_leadership` | 2 |
| `epoch_agentic_ai_runtime_architecture` | 3 |

### Pillar → track map

| Track | Pillars |
|-------|---------|
| **1** | actuarial foundation, derivatives, embedded options, greeks/hedging, risk management, enterprise risk controls, regulatory governance, capital modeling |
| **2** | cloud/AWS, **trading/HPC**, executive leadership, revenue/commercialization, revenue ops, presales, **partner GTM**, co-sell, customer/stakeholder, strategic finance |
| **3** | agentic AI platforms (+ deep-agentic capability_domain rows) |

### Part 1 wave progress

| Wave | Focus | Status | Success criteria |
|------|-------|--------|------------------|
| **P1-W0** | Taxonomy SSOT on disk (operator-confirmed) | ✅ DONE | [career_track_taxonomy_operator_confirmed.md](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.md) |
| **P1-W1** | Materialize `career_track` nodes + remap edges | ✅ DONE | [career_track_materialization_receipt.json](docs/reports/apps_rg/career_track_materialization_receipt.json) |
| **P1-W2** | Employment spine (`employment_in_career_track`) | ✅ DONE | [career_track_p1_w2_employment_receipt.json](docs/reports/apps_rg/career_track_p1_w2_employment_receipt.json) |
| **P1-W3** | Per-track skill activation (DRAFT→ACTIVE + `fact_id_links`) | ✅ DONE | [career_track_p1_w3_activation_receipt.json](docs/reports/apps_rg/career_track_p1_w3_activation_receipt.json) |
| **P1-W4** | Track-weighted proof pool + C0.3 binding | ✅ DONE | [career_track_p1_w4_closeout_receipt.json](docs/reports/apps_rg/career_track_p1_w4_closeout_receipt.json) |
| **P1-W5** | Track-balanced exec summary + competencies grouping | ✅ DONE | [career_track_p1_w5_track_balanced_sections_receipt.json](docs/reports/apps_rg/career_track_p1_w5_track_balanced_sections_receipt.json) |

### P1-W0 — Taxonomy SSOT ✅ DONE

**Deliverables:** [career_track_taxonomy_operator_confirmed.md](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.md), [career_track_taxonomy_operator_confirmed.json](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json)

---

### P1-W1 — Materialize career tracks in graph

WAVE_ID: P1-W1 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Scope:**
- Add `career_track` nodes: `track_actuarial_risk_derivatives` (2002–2010), `track_data_tech_cloud_ml` (2010–2022), `track_genai_agentic` (2022–present)
- Edges: `career_track_contains_epoch`, `career_track_contains_pillar` (**`pillar_trading_hpc` → track 2**)
- Edge: `career_track_precedes_career_track` ×2 (`career_sequence`, non-causal)
- Receipt: `docs/reports/apps_rg/career_track_materialization_receipt.json`

**Acceptance:** Every epoch has one primary track; `graph_metadata.career_track_count: 3`

---

### P1-W2 — Employment spine

WAVE_ID: P1-W2 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Scope:** `employment` nodes from [amit_ayer_base_resume_v1.json](apps_rg/resume/base/amit_ayer_base_resume_v1.json); `employment_in_career_track`; `employment_hosts_fact`

**Acceptance:** Each stint maps to primary track by year overlap (2002–2010 → track 1, etc.)

---

### P1-W3 — Activation burndown per track

WAVE_ID: P1-W3 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Scope:** Resolve 47 skill rows with empty `fact_id_links`; attach pending sources from design doc per track; `ACTIVE` only with facts + confirmation

**Targets:** ~15 ACTIVE skills per track (see taxonomy report)

---

### P1-W4 — Track-weighted graph expansion (+ P1-W4-CLOSEOUT C0.3 binding)

WAVE_ID: P1-W4 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES · CLOSEOUT: P1-W4-CLOSEOUT DONE

**Scope:** JD + role_family → track weights; proof pool union SRFS ∪ weighted track facts/skills; C0.3 multi-hop along `career_track_contains_pillar` → `skill_supported_by_fact`

**Default weights (SVP Agentic):** track 1: 0.10 · track 2: 0.25 · track 3: 0.65

---

### P1-W5 — Track-balanced section modes

WAVE_ID: P1-W5 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Scope:** Exec summary optional one sentence per track; competencies grouped by `career_track_id`; no cross-track causal prose

**Receipts:** [career_track_p1_w5_track_balanced_sections_receipt.json](docs/reports/apps_rg/career_track_p1_w5_track_balanced_sections_receipt.json) · [career_track_p1_w5_track_balanced_sections.md](docs/reports/apps_rg/career_track_p1_w5_track_balanced_sections.md)

**Module:** `apps_rg/fact_inventory/track_balanced_section_projection.py`

---

### Part 1 — Definition of Done

| DoD | Evidence | Status |
|-----|----------|--------|
| P1-DoD-1 | Taxonomy SSOT published | ✅ DONE |
| P1-DoD-2 | `career_track` nodes in `master_skills_arsenal_ledger.json` | ✅ DONE |
| P1-DoD-3 | Employment spine edges present | ✅ DONE |
| P1-DoD-4 | ≥30 ACTIVE skills with `fact_id_links` across 3 tracks | ✅ DONE (84 activated) |
| P1-DoD-5 | Track-weighted expansion fixture test passes | ✅ DONE |

---

# Part 2 — Competencies graph-skills hardening (missing today)

## What competencies is missing (vs executive_summary PASS)

| Capability | executive_summary | competencies (today) |
|------------|-------------------|----------------------|
| Proof pool | `augmented_skills_graph` + C0.3 | `broad_skills_ledger_competencies` |
| Skills authority | graph SSOT | ledger slice |
| Post-parse repair | `exec_summary_graph_only_quality.py` | **none** |
| Live validator | `validate_exec_summary_graph_only_generation.py` | **none** |
| X2 metric locality | repair + gates | ID-only risk |
| X1D rubric | `GRAPH_ONLY_GRADE_ONLY_RUBRIC` | generic |
| Live proof | X3_ALLOW, proof_eligible | **not proven** |

Gap detail: [graph_skills_hardening_gap_inventory.md](docs/reports/apps_rg/graph_skills_hardening_gap_inventory.md)

### Part 2 wave progress

| Wave | Focus | Status | Success criteria |
|------|-------|--------|------------------|
| **P2-W0** | Gap inventory (competencies vs exec_summary) | ✅ DONE | [gap_inventory.json](docs/reports/apps_rg/graph_skills_hardening_gap_inventory.json) |
| **P2-W1** | Graph-only proof pool for competencies | ✅ DONE | [competencies_graph_proof_pool_p2_w1_receipt.json](docs/reports/apps_rg/competencies_graph_proof_pool_p2_w1_receipt.json) |
| **P2-W2** | C0.3 GraphRAG binding (all sections) | ✅ DONE | [all_sections_c03_graph_binding_p2_w2_receipt.json](docs/reports/apps_rg/all_sections_c03_graph_binding_p2_w2_receipt.json) |
| **P2-W3** | Shared validator + `graph_skills_proof_common.py` | ✅ DONE | [shared_graph_proof_infrastructure_p2_w3_receipt.json](docs/reports/apps_rg/shared_graph_proof_infrastructure_p2_w3_receipt.json) |
| **P2-W4** | Section X2 graph locality gates | ✅ DONE | [section_x2_graph_locality_p2_w4_receipt.json](docs/reports/apps_rg/section_x2_graph_locality_p2_w4_receipt.json) |
| **P2-W5** | PA graph authority guardrails | ✅ DONE | [section_pa_graph_authority_p2_w5_receipt.json](docs/reports/apps_rg/section_pa_graph_authority_p2_w5_receipt.json) |
| **P2-W6** | Graph-only quality repair | ✅ DONE | [graph_only_quality_repair_p2_w6_receipt.json](docs/reports/apps_rg/graph_only_quality_repair_p2_w6_receipt.json) |
| **P2-W7** | X1D graph-only judge packets | ✅ DONE | [x1d_graph_only_judge_packets_p2_w7_receipt.json](docs/reports/apps_rg/x1d_graph_only_judge_packets_p2_w7_receipt.json) |
| **P2-W8** | Validators + contract tests | ✅ DONE | [all_sections_graph_skills_validators_p2_w8_receipt.json](docs/reports/apps_rg/all_sections_graph_skills_validators_p2_w8_receipt.json) |
| **P2-W9** | Live canonical proof (7/7 sections) | ✅ DONE | [canonical_live_section_proofs_p2_w9_receipt.json](docs/reports/apps_rg/canonical_live_section_proofs_p2_w9_receipt.json) |
| **P2-W10** | Cross-lane graph authority audit | ✅ DONE | [cross_section_graph_authority_audit_p2_w10_receipt.json](docs/reports/apps_rg/cross_section_graph_authority_audit_p2_w10_receipt.json) |

### Lessons from executive_summary (apply in Part 2)

| Failure mode | Exec-summary fix | Competencies action |
|--------------|------------------|---------------------|
| Invented % | allowed_percent_tokens + repair | P2-W4, P2-W6 |
| Causal merge | separate claim rows | P2-W4, P2-W6 |
| Credential inventory | omit | P2-W6 |
| X2 passes on ID only | repair + judges | P2-W4, P2-W6, P2-W7 |

---

### P2-W0 — Gap inventory

WAVE_ID: P2-W0 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Deliverable:** [graph_skills_hardening_gap_inventory.md](docs/reports/apps_rg/graph_skills_hardening_gap_inventory.md) · [graph_skills_hardening_gap_inventory.json](docs/reports/apps_rg/graph_skills_hardening_gap_inventory.json) · validator `validate_p2_w0_graph_skills_gap_inventory.py`

---

### P2-W1 — Graph-only proof pool (competencies)

WAVE_ID: P2-W1 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Scope:** `_resolve_competencies_graph_skills_proof_pool()` in [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py); [competencies_graph_skills_proof_pool.py](apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py)

**Acceptance:** `proof_pool_metadata.proof_pool_type=augmented_skills_graph`; `assert_skills_not_broad_ledger_authority()` passes

---

### P2-W1A — Default graph authority (remove ledger product path)

WAVE_ID: P2-W1A · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Scope:** Default `resolve_section_proof_pool(section=competencies)` → `augmented_skills_graph` only; `_build_competencies_ledger_plan` unreachable; fail closed (no silent fallback)

**Receipt:** [competencies_graph_proof_pool_p2_w1a_default_graph_authority_receipt.json](docs/reports/apps_rg/competencies_graph_proof_pool_p2_w1a_default_graph_authority_receipt.json)

---

### P2-W2 — C0.3 GraphRAG (all sections)

WAVE_ID: P2-W2 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [all_sections_c03_graph_binding_p2_w2_receipt.json](docs/reports/apps_rg/all_sections_c03_graph_binding_p2_w2_receipt.json)

---

### P2-W3 — Shared graph proof infrastructure

WAVE_ID: P2-W3 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [shared_graph_proof_infrastructure_p2_w3_receipt.json](docs/reports/apps_rg/shared_graph_proof_infrastructure_p2_w3_receipt.json)

---

### P2-W4 — Section X2 graph locality

WAVE_ID: P2-W4 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [section_x2_graph_locality_p2_w4_receipt.json](docs/reports/apps_rg/section_x2_graph_locality_p2_w4_receipt.json)

---

### P2-W5 — PA graph authority

WAVE_ID: P2-W5 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [section_pa_graph_authority_p2_w5_receipt.json](docs/reports/apps_rg/section_pa_graph_authority_p2_w5_receipt.json)

---

### P2-W6 — Graph-only quality repair

WAVE_ID: P2-W6 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [graph_only_quality_repair_p2_w6_receipt.json](docs/reports/apps_rg/graph_only_quality_repair_p2_w6_receipt.json)

---

### P2-W7 — X1D graph-only judge packets

WAVE_ID: P2-W7 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [x1d_graph_only_judge_packets_p2_w7_receipt.json](docs/reports/apps_rg/x1d_graph_only_judge_packets_p2_w7_receipt.json)

---

### P2-W8 — Validators + contract tests

WAVE_ID: P2-W8 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [all_sections_graph_skills_validators_p2_w8_receipt.json](docs/reports/apps_rg/all_sections_graph_skills_validators_p2_w8_receipt.json)

---

### P2-W9 — Live canonical proof (7/7 sections)

WAVE_ID: P2-W9 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [canonical_live_section_proofs_p2_w9_receipt.json](docs/reports/apps_rg/canonical_live_section_proofs_p2_w9_receipt.json) · RCA: [p2_w9_unify_bullets_final_rca_receipt.json](docs/reports/apps_rg/p2_w9_unify_bullets_final_rca_receipt.json)

**PASS:** All seven sections REAL_LLM · X2 PASS · X3_ALLOW · proof_eligible · C0.3 BOUND · no `broad_skills_ledger` authority

---

### P2-W10 — Cross-lane graph authority audit

WAVE_ID: P2-W10 · WAVE_STATUS: DONE · WAVE_COMPLETE: YES

**Receipt:** [cross_section_graph_authority_audit_p2_w10_receipt.json](docs/reports/apps_rg/cross_section_graph_authority_audit_p2_w10_receipt.json)

---

### Part 2 — Definition of Done

| DoD | Evidence | Status |
|-----|----------|--------|
| P2-DoD-1 | Gap inventory for competencies | ✅ DONE |
| P2-DoD-2 | Accelerated closeout validators → PASS | ✅ DONE |
| P2-DoD-3 | All seven sections live → X3_ALLOW | ✅ DONE |
| P2-DoD-4 | Contract tests green (`test_p2_graph_skills_accelerated_closeout.py` 12/12) | ✅ DONE |
| P2-DoD-5 | No `agentic_core` edits in Part 2 scope | ✅ DONE |

---

## Out of scope (both parts)

- `agentic_core` edits
- Weakening X2 / X3 / X1D
- Inventing graph metrics/skills to satisfy bad output
- `broad_skills_ledger` or base résumé as **skills authority** for product proof
- Full IBM/unify graph migration (P2-W10 audit only)

---

## Gap register

| ID | Part | Gap |
|----|------|-----|
| GAP-P1-1 | 1 | Six epochs vs three operator career narratives |
| GAP-P1-2 | 1 | 47 skill rows without `fact_id_links` |
| GAP-P2-1 | 2 | Competencies uses ledger proof pool |
| GAP-P2-2 | 2 | No competencies graph-only repair/validator |
| GAP-P2-3 | 2 | Competencies JSON shape ≠ exec summary sentences |

---

## ADG_GRAPH_LAYER_EVIDENCE

| Primitive | Part 2 use |
|-----------|------------|
| `mv_hotspot_centrality` | competencies lane + proof_pool_resolver |
| `flows_to` | graph authority → competencies runtime |
| `reads_from` | C0.3 bound artifact only |
| `v_p1_apps_rg_surface` | competencies overlay |

---

## Notion Summary

**Part 1 (DONE):** Multi-career graph — 3 tracks materialized; employment spine; 84 skills activated; track-weighted expansion + P1-W5 track-balanced sections.

**Part 2 (DONE):** All seven product sections on `augmented_skills_graph` with C0.3 BOUND, graph-only repair/X2/X1D, validators, and live matrix PASS (2026-05-19). Closeout: [graph_skills_hardening_p2_accelerated_closeout.json](docs/reports/apps_rg/graph_skills_hardening_p2_accelerated_closeout.json).

**Status:** Completed · **Slug:** `graph-skills-hardening-f3a8c1` · **Plan file:** `.cursor/plans/graph-skills-hardening-f3a8c1.md`
