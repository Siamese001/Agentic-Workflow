e--
plan_id: apps-rg-proof-pool-c0-ssot-a7f3e2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg proof pool / C0.2 / C0.3 SSOT convergence

Close gaps between **resolver allowlist** (PA/L2/X2 enforcement), **C0 evidence room FEC** (enrichment), and **audit receipts** (claims). Legacy proof-pool *authority* is already retired; this plan addresses **split enforcement** and **receipt drift** found in multi-lane E2E traces.

**Audit machine output:** [proof_pool_c0_ssot_gap_audit.json](artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json)  
**Prior related plan:** [apps-rg-x2-dead-gates-burndown-c4e8f2.md](apps-rg-x2-dead-gates-burndown-c4e8f2.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: NOT_STARTED
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: none
LAST_UPDATED: 2026-05-23
NOTION_STATUS: Not Started
DISK_SSOT: .cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md

PLAN_CREATED: slug=apps-rg-proof-pool-c0-ssot-a7f3e2 path=.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md status=Not Started

---

## Context (SCQA)

- **Situation** — Product lanes use `evidence_authority=augmented_skills_graph` (C0.3 skills graph + candidate-fact ledger substrate). C0.2 hybrid enriches/reorders. `resolve_section_proof_pool()` still materializes `SectionProofPool` + `allowed_fact_ids` for PA/L2/X2.
- **Complication** — Cross-lane audit (latest real proof dirs, 2026-05-22) shows **6/6 comparable lanes** with pool vs FEC allowlist mismatch; **unify_narrative** has **disjoint ID namespaces** (pool `bul_*` vs FEC `fact_*`). Receipts disagree on `canonical_c0_*` claims; spine bundle omits FEC room; `lane_registry` still lists retired X2 gates.
- **Question** — What single allowlist is law for generation, and how do FEC/C0 receipts reflect that without false “canonical spine” signals?
- **Answer** — Five-wave convergence: design SSOT → implement allowlist sync → align receipts/spine → fix lane-specific namespace/C03 parity → governance + live proof.

---

## E2E traces executed (evidence)

| Lane | Latest proof dir | Pool IDs | FEC IDs | Mismatch |
|------|------------------|----------|---------|----------|
| executive_summary | `exec_summary_20260522_232006` | 7 | 9 | FEC ⊃ pool (`fact_solutions_002`, `fact_revenue_ops_001`) |
| headline | `headline_20260522_215119` | 3 | 7 | FEC ⊃ pool (+4 ledger facts) |
| competencies | `competencies_20260522_101716` | 17 | 18 | FEC ⊃ pool (`fact_solutions_002`) |
| unify_bullets | `unify_bullets_20260522_200653` | — | — | **Incomplete run** (spine only; no `selected_fact_plan.json`) |
| unify_narrative | `unify_narrative_20260522_102018` | 7 (`bul_*`) | 2 (`fact_*`) | **Disjoint namespaces** |
| ibm_bullets | `ibm_bullets_20260522_102059` | 6 | 7 | FEC ⊃ pool; **X2 active pool FAIL** |
| ibm_narrative | `ibm_narrative_20260522_102228` | 3 | 5 | FEC ⊃ pool |

**Authority fields (all traced lanes):** `evidence_authority=augmented_skills_graph`, `selected_role_fact_set_used=false`, `x2_srfs_gate_status=NOT_APPLICABLE`.

---

## Gap inventory (consolidated)

### P0 — Enforcement / SSOT

| ID | Gap | Evidence |
|----|-----|----------|
| G1 | **Dual allowlist:** FEC C04 expands beyond resolver pool; PA/L2/X2 use `runtime_payload.allowed_fact_ids` from pool only | All lanes above except unify_bullets |
| G2 | **unify_narrative ID split:** pool uses `bul_unify_*` / `unify_narrative_base_001`; FEC uses ledger `fact_*` | `unify_narrative_20260522_102018` |
| G3 | **ibm_bullets X2 pool gate FAIL** while authority PASS | `x2_active_pool: FAIL` in audit JSON |

### P1 — C0 path / receipts

| ID | Gap | Evidence |
|----|-----|----------|
| G4 | **C0.2 hybrid twice:** resolver `_maybe_apply_hybrid_informed_fact_plan_reorder` + evidence room `perform_product_hybrid_retrieval` | `executive_summary` selection_method suffix |
| G5 | **Receipt conflict:** `c0_fec_bridge_receipt.json` shows `canonical_c0_2/3/5=false`; evidence room `bridge_doc` shows c0_2/c0_5 true | `exec_summary_20260522_232006` |
| G6 | **C0.3 naming:** `c03_graphrag_bound_status=BOUND` but `canonical_c0_3_claimed=false`, `core_c03_graph_rag_used=false` | exec summary + competencies differ on `canonical_c0_3` |
| G7 | **Spine bundle drift:** `section_runtime_proof_bundle` omits `section_fec_bridge`; `is_canonical_c0_path=false` | exec summary bundle |
| G8 | **Incomplete proof dirs:** unify_bullets latest run lacks full lane artifacts | `unify_bullets_20260522_200653` |

### P2 — Governance / ops

| ID | Gap | Evidence |
|----|-----|----------|
| G9 | **`lane_registry` ghost:** `x2_exec_summary_sentence_count_2_3` retired but still critical | `RETIRED_EXEC_SUMMARY_X2_GATE_IDS` |
| G10 | **Vocabulary:** `proof_pool` carrier labels in C0 (`SOURCE_PROOF_POOL`, `source_class`) | `apps_rg/runtime/c0/constants.py` |
| G11 | **SRFS opaque:** internal `select_candidate_facts_for_role` while flags say SRFS off | resolver + fact rows `srfs_verification_status` |
| G12 | **native_c03 enrich** only on competencies resolver path | `proof_pool_resolver._resolve_section_proof_pool_inner` |
| G13 | **Chroma split-brain** (ops): runtime `fact_vectors` vs CI `process_docs` | `artifacts/apps_rg/c0_embedding_gap/` |

---

## Design decision (W0 — requires Author-Gate)

Pick **one** allowlist authority for PA/L2/X2/FEC (recommended: **resolver pool after C0 room**, with explicit sync step):

| Option | Behavior | Pros | Cons |
|--------|----------|------|------|
| **A — Pool wins** | C04/FEC `allowed_fact_ids` narrowed to ⊆ pool; hybrid may not add IDs | X2/PA aligned; minimal X2 change | Loses FEC “discovery” IDs |
| **B — FEC widens pool** | After evidence room, merge C04 `allowed_fact_ids` into `runtime_payload` + recompile PA if needed | Single expanded allowlist | PA regen; X2 surface grows |
| **C — Dual with explicit roles** | Pool = enforce; FEC = enrichment-only receipts | Clear semantics | Requires doc + gate renames; audit complexity |

**Recommended:** **A** for product golden path (fail-closed generation), **B** only for lanes that intentionally widen (document per lane).

**unify_narrative (G2):** require C04 stratify to emit same ID namespace as pool (`bul_*`) OR map `fact_*` ↔ `bul_*` in one normalization seam before FEC.

---

## Waves

### W0 — Design + audit SSOT (no runtime behavior change)

| Step | Deliverable |
|------|-------------|
| 0.1 | Author-Gate on allowlist option A/B/C |
| 0.2 | ADR snippet in plan receipt: chosen SSOT + unify_narrative ID policy |
| 0.3 | Keep [ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py](ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py) as regression comparator |

**DoD:** Decision recorded; audit JSON regenerated; no code merge.

---

### W1 — Allowlist convergence (implementation)

| Step | Deliverable |
|------|-------------|
| 1.1 | Implement chosen option in `wire_section_fec_bridge_for_lane` / `run_section_c0_evidence_room` exit path |
| 1.2 | Sync `runtime_payload.allowed_fact_ids`, `selected_fact_plan`, `section_fec_bridge.source_fact_ids` to one set |
| 1.3 | Fix **unify_narrative** namespace (G2) |
| 1.4 | Investigate **ibm_bullets** X2 active pool FAIL (G3) |

**Proof:** Re-run audit script → `allowlist_mismatch: false` per lane; lane CLI proof for exec_summary + unify_narrative + ibm_bullets.

---

### W2 — Receipt & spine alignment

| Step | Deliverable |
|------|-------------|
| 2.1 | Single writer for `c0_fec_bridge_receipt.json` after evidence room (copy from `bridge_doc`) |
| 2.2 | Document `canonical_c0_3_claimed` vs `apps_rg_c03_skills_graph_used` in `product_evidence_authority.py` docstring + receipt glossary |
| 2.3 | Update `section_runtime_proof_bundle` observed_chain to include `section_fec_bridge` |
| 2.4 | Consolidate or document dual C0.2 hybrid (G4) |

**Proof:** Diff receipts on one exec_summary run; spine chain includes FEC.

---

### W3 — Section parity & proof completeness

| Step | Deliverable |
|------|-------------|
| 3.1 | Align `enrich_proof_pool_with_native_c03` across lanes or document exceptions |
| 3.2 | Full **unify_bullets** live proof dir (G8) |
| 3.3 | Live proof sweep all 7 lanes (Brown & Brown JD fixture) |

**Proof:** 7 dirs with `selected_fact_plan.json`, `x2_gate_outputs.json`, audit JSON all green.

---

### W4 — Governance cleanup

| Step | Deliverable |
|------|-------------|
| 4.1 | Remove retired gate from `lane_registry.py` (G9) |
| 4.2 | Optional: rename `SOURCE_PROOF_POOL` → `SOURCE_SECTION_ALLOWLIST` in C0 constants (G10) |
| 4.3 | Chroma readiness ticket / separate ops plan if G13 blocks live C0.2 |

**Proof:** `test_section_gate_coverage` + complexity audit scripts pass.

---

## Definition of Done (plan-level)

| DoD | Criterion |
|-----|-----------|
| DoD-1 | Author-Gate decision captured for allowlist SSOT (W0) |
| DoD-2 | `proof_pool_c0_ssot_gap_audit.json` shows zero `allowlist_mismatch` on 7/7 live lanes |
| DoD-3 | unify_narrative pool/FEC IDs same namespace or explicit mapped |
| DoD-4 | ibm_bullets `x2_active_pool` PASS on fresh run |
| DoD-5 | `c0_fec_bridge_receipt` consistent with evidence room `bridge_doc` on exec_summary |
| DoD-6 | Notion Plans row `Exists On Disk=true`, Status honest |
| DoD-7 | Closeout receipt: `docs/reports/apps_rg/proof_pool_c0_ssot_convergence_closeout_receipt.md` |

---

## Out of scope

- Rewriting X3 judge soft-fail policy
- `agentic_core` canonical C0 spine migration
- Full Chroma collection unification (track as ops dependency unless blocking W3)

---

## Risks

| Risk | Mitigation |
|------|------------|
| PA regen if allowlist widens (option B) | Prefer option A; token budget re-check |
| unify_narrative bullet coupling | Coordinate with unify_bullets lane ordering |
| Live proof blocked on BM25/Chroma | Document BLOCKED in closeout; do not fake PASS |
