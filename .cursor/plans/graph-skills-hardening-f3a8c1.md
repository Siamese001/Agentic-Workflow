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
PLAN_STATUS: TODO
CURRENT_PART: PART_1
CURRENT_WAVE: P1-W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-19

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
| **P1-W1** | Materialize `career_track` nodes + remap edges | 🔲 TODO | 3 nodes with years; receipt JSON |
| **P1-W2** | Employment spine (`employment_in_career_track`) | 🔲 TODO | base résumé stints → tracks |
| **P1-W3** | Per-track skill activation (DRAFT→ACTIVE + `fact_id_links`) | 🔲 TODO | ~15 ACTIVE skills per track |
| **P1-W4** | Track-weighted proof pool + C0.3 multi-hop | 🔲 TODO | hybrid JD gets facts from ≥2 tracks |
| **P1-W5** | Track-balanced exec summary + competencies grouping | 🔲 TODO | ≤1 sentence/track; competencies by track |

### P1-W0 — Taxonomy SSOT ✅ DONE

**Deliverables:** [career_track_taxonomy_operator_confirmed.md](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.md), [career_track_taxonomy_operator_confirmed.json](docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json)

---

### P1-W1 — Materialize career tracks in graph

WAVE_ID: P1-W1 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:**
- Add `career_track` nodes: `track_actuarial_risk_derivatives` (2002–2010), `track_data_tech_cloud_ml` (2010–2022), `track_genai_agentic` (2022–present)
- Edges: `career_track_contains_epoch`, `career_track_contains_pillar` (**`pillar_trading_hpc` → track 2**)
- Edge: `career_track_precedes_career_track` ×2 (`career_sequence`, non-causal)
- Receipt: `docs/reports/apps_rg/career_track_materialization_receipt.json`

**Acceptance:** Every epoch has one primary track; `graph_metadata.career_track_count: 3`

---

### P1-W2 — Employment spine

WAVE_ID: P1-W2 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** `employment` nodes from [amit_ayer_base_resume_v1.json](apps_rg/resume/base/amit_ayer_base_resume_v1.json); `employment_in_career_track`; `employment_hosts_fact`

**Acceptance:** Each stint maps to primary track by year overlap (2002–2010 → track 1, etc.)

---

### P1-W3 — Activation burndown per track

WAVE_ID: P1-W3 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** Resolve 47 skill rows with empty `fact_id_links`; attach pending sources from design doc per track; `ACTIVE` only with facts + confirmation

**Targets:** ~15 ACTIVE skills per track (see taxonomy report)

---

### P1-W4 — Track-weighted graph expansion

WAVE_ID: P1-W4 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** JD + role_family → track weights; proof pool union SRFS ∪ weighted track facts/skills; C0.3 multi-hop along `career_track_contains_pillar` → `skill_supported_by_fact`

**Default weights (SVP Agentic):** track 1: 0.10 · track 2: 0.25 · track 3: 0.65

---

### P1-W5 — Track-balanced section modes

WAVE_ID: P1-W5 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** Exec summary optional one sentence per track; competencies grouped by `career_track_id`; no cross-track causal prose

---

### Part 1 — Definition of Done

| DoD | Evidence | Status |
|-----|----------|--------|
| P1-DoD-1 | Taxonomy SSOT published | ✅ DONE |
| P1-DoD-2 | `career_track` nodes in `master_skills_arsenal_ledger.json` | TODO |
| P1-DoD-3 | Employment spine edges present | TODO |
| P1-DoD-4 | ≥30 ACTIVE skills with `fact_id_links` across 3 tracks | TODO |
| P1-DoD-5 | Track-weighted expansion fixture test passes | TODO |

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
| **P2-W0** | Gap inventory (competencies vs exec_summary) | 🔲 TODO | gap matrix complete |
| **P2-W1** | Graph-only proof pool for competencies | 🔲 TODO | `proof_source=augmented_skills_graph` |
| **P2-W2** | C0.3 GraphRAG binding (competencies) | 🔲 TODO | `c03_graphrag_bound_status=BOUND` |
| **P2-W3** | Shared validator + `graph_skills_proof_common.py` | 🔲 TODO | DRY with exec validator |
| **P2-W4** | Competencies X2 metric/skill gates | 🔲 TODO | synthetic bad fixtures fail |
| **P2-W5** | PA guardrails + skill inventory projection | 🔲 TODO | graph authority in compiled prompt |
| **P2-W6** | `competencies_graph_only_quality.py` repair | 🔲 TODO | repair artifact per run |
| **P2-W7** | X1D GRADE_ONLY + allowed_skill_rows | 🔲 TODO | all judges MODEL_BACKED pass |
| **P2-W8** | Validator + contract tests | 🔲 TODO | `test_competencies_graph_skills_live_proof.py` |
| **P2-W9** | Live canonical proof PASS | 🔲 TODO | X3_ALLOW, proof_eligible |
| **P2-W10** | Optional cross-lane audit (IBM/unify/headline) | 🔲 TODO | read-only report only |

### Lessons from executive_summary (apply in Part 2)

| Failure mode | Exec-summary fix | Competencies action |
|--------------|------------------|---------------------|
| Invented % | allowed_percent_tokens + repair | P2-W4, P2-W6 |
| Causal merge | separate claim rows | P2-W4, P2-W6 |
| Credential inventory | omit | P2-W6 |
| X2 passes on ID only | repair + judges | P2-W4, P2-W6, P2-W7 |

---

### P2-W0 — Gap inventory

WAVE_ID: P2-W0 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Deliverable:** Update [graph_skills_hardening_gap_inventory.md](docs/reports/apps_rg/graph_skills_hardening_gap_inventory.md) with file-level targets for each P2 wave.

---

### P2-W1 — Graph-only proof pool (competencies)

WAVE_ID: P2-W1 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** `resolve_competencies_graph_skills_proof_pool()` in [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py); stop `_build_competencies_ledger_plan` for product proof; wire [proof_pool_lane_integration.py](apps_rg/runtime/proof_pool_lane_integration.py)

**Acceptance:** `proof_pool_metadata.proof_pool_type=augmented_skills_graph`; `assert_skills_not_broad_ledger_authority()` passes

---

### P2-W2 — C0.3 GraphRAG for competencies

WAVE_ID: P2-W2 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** Competencies `c03_graphrag_bound.json`; skill_row anchors; `non_graph_evidence_items_count=0`

---

### P2-W3 — Shared graph proof infrastructure

WAVE_ID: P2-W3 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** [graph_skills_proof_common.py](apps_rg/runtime/validators/graph_skills_proof_common.py); wrappers for exec + competencies validators

---

### P2-W4 — Competencies X2 hardening

WAVE_ID: P2-W4 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** Metric literal allowlist; `skill_id` granularity; anti-causal across skill rows ([competencies_x2.py](apps_rg/runtime/validators/competencies_x2.py))

---

### P2-W5 — Prompt guardrails

WAVE_ID: P2-W5 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** Guardrails in [competencies_pa.py](apps_rg/runtime/dispatch/competencies_pa.py); `build_verified_skill_inventory_projection()` in prompt

---

### P2-W6 — Generation quality repair

WAVE_ID: P2-W6 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** New [competencies_graph_only_quality.py](apps_rg/runtime/sections/competencies_graph_only_quality.py); `graph_only_generation_quality_repair.json` artifact

---

### P2-W7 — X1D judge packet

WAVE_ID: P2-W7 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** GRADE_ONLY rubric; allowed_skill_rows packet; [competencies_x1d.py](apps_rg/runtime/judges/competencies_x1d.py) provider hygiene

---

### P2-W8 — Validator + contract tests

WAVE_ID: P2-W8 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

**Scope:** `validate_competencies_graph_skills_generation.py`; [competencies_graph_skills_live_proof.json](docs/reports/apps_rg/competencies_graph_skills_live_proof.json) (create on PASS)

---

### P2-W9 — Live canonical proof

WAVE_ID: P2-W9 · WAVE_STATUS: TODO · WAVE_COMPLETE: NO

```bash
docker start local-qwen-vllm || true
python -m apps_rg --section competencies --allow-non-allow-exit-zero
python apps_rg/runtime/validators/validate_competencies_graph_skills_generation.py --latest --write-report
python -m pytest tests/_apps_contract/test_competencies_graph_skills_live_proof.py -q --tb=short -p no:xdist -o addopts=
```

**PASS:** REAL_LLM · X2 PASS · X3_ALLOW · proof_eligible · graph-only PASS · C0.3 BOUND · all X1D MODEL_BACKED pass

---

### P2-W10 — Cross-lane audit (optional)

WAVE_ID: P2-W10 · AUTHORIZATION_STATUS: NOT_REQUIRED · read-only

---

### Part 2 — Definition of Done

| DoD | Evidence | Status |
|-----|----------|--------|
| P2-DoD-1 | Gap inventory for competencies | TODO |
| P2-DoD-2 | `validate_competencies_graph_skills_generation.py --latest` → PASS | TODO |
| P2-DoD-3 | `python -m apps_rg --section competencies` → X3_ALLOW | TODO |
| P2-DoD-4 | Contract tests green; exec_summary regression tests still pass | TODO |
| P2-DoD-5 | No `agentic_core` edits in Part 2 scope | TODO |

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

**Part 1:** Multi-career graph — 3 tracks (2002–2010 actuarial/risk/deriv · 2010–2022 data/cloud/ML incl trading/HPC + partner GTM · 2022–present GenAI/Agentic). Materialize nodes/edges, employment spine, activation, track-weighted expansion.

**Part 2:** Competencies missing graph-skills — graph-only proof pool, C0.3, X2/repair/judges/validator, live PASS like executive_summary.

**Status:** Not Started · **Order:** Part 1 then Part 2 · **Slug:** `graph-skills-hardening-f3a8c1`
