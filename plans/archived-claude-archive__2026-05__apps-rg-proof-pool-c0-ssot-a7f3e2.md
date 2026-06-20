---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-proof-pool-c0-ssot-a7f3e2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-proof-pool-c0-ssot-a7f3e2.md'
source_sha256: f207dcb5d15e2a08437cd494566635ebf18cf1be39dc18b8ac511de5584d7c35
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
PLAN_STATUS: COMPLETE
CURRENT_WAVE: Track-C-containment
LAST_COMPLETED_WAVE: Track-C-containment
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-25
PLAN_COMPLETED: 2026-05-25
CLOSEOUT_CLASS: TRACK_B_AND_C_CONTAINMENT_DONE
PLAN_COMPLETE: plan=apps-rg-proof-pool-c0-ssot-a7f3e2 note="Track B W23; Track C code; targeting parity 233409"
DEFERRED_SCOPE: Track_C5_X3_ALLOW,W0_W4_FEC_allowlist_convergence
CLOSEOUT_RECEIPT: docs/reports/plans/active_backlog_closeout_receipt_20260525.md
PROOF_RECEIPT: docs/reports/apps_rg/exec_summary_targeting_parity_live_proof_20260524_233409_receipt.md
NOTION_PAGE_ID: 36927693-f55c-8173-99c1-c25da5321677
NOTION_PLANS_ROW: page_id=36927693-f55c-8173-99c1-c25da5321677
NOTION_RECONCILED: 2026-05-24
ACTIVE_BACKLOG_MANIFEST: docs/reports/plans/active_in_progress_plans_manifest_20260524.md
ACTIVE_BACKLOG_ROLE: spine_child_p0
PARENT_PLAN: apps-rg-spine-only-unification-d8f4a2
DISK_SSOT: .cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md

PLAN_CREATED: slug=apps-rg-proof-pool-c0-ssot-a7f3e2 path=.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md status=Not Started

**Machine audit (regenerate after sweeps):** [proof_pool_c0_ssot_gap_audit.json](artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json)  
**Modular sweep root:** `artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes`  
**Sweep manifest:** [w23_lane_sweep_manifest.json](artifacts/apps_rg/plans/w23_lane_sweep/w23_lane_sweep_manifest.json)

---

## Integrated remediation map (two tracks)

| Track | Scope | Status |
|-------|--------|--------|
| **Track B** | W23 debugger RCAs RCA-1…4 (bullets, modular sweep, competencies, IBM anchors) + audit script | **DONE** (2026-05-23 modular sweep) |
| **Track C** | Executive-summary synthesis RCA (X2 pass + X1D soft-fail; graph-only regen; regen authority) | **PARTIAL** — code **DONE** ([track_c_exec_summary_remediation_receipt.md](docs/reports/apps_rg/track_c_exec_summary_remediation_receipt.md)); live 3× `X3_ALLOW` pending (Track C5) |
| **W0–W4** | Proof-pool / FEC / digest SSOT convergence (this plan’s original waves) | **W0 design open**; W1+ pending |

**Cross-link:** Track B **does not** fix Track C. Fresh audit shows `executive_summary` with `x2_all_pass: true`, `lane_proof_ok: true`, `x3_outcome: X3_REVIEW_JUDGE_SOFT_FAIL` (`rca_fix_reference: RCA-6-related-not-fixed`). Same root class as Brown & Brown runs (proof-safe prose, judges &lt; 4.0).

---

## Track B — W23 RCA fixes (completed 2026-05-23)

### RCA fix order (implemented)

| RCA | Fix | Key files | Proof |
|-----|-----|-----------|-------|
| **RCA-1** (P0) | `repair_unify_bullet_surface_id()` — `bul_unify_.003` → `bul_unify_003` on bullet ids + `source_fact_ids` | [fact_id_typo_repair.py](apps_rg/runtime/validators/fact_id_typo_repair.py), [unify_bullets_lane.py](apps_rg/runtime/sections/unify_bullets_lane.py) | [unify_bullets_20260523_125754](artifacts/apps_rg/runtime_proofs/unify_bullets/real/unify_bullets_20260523_125754) — `PRODUCT_QUALITY_STATUS: PASS`, canonical `bul_unify_003` |
| **RCA-2** (P0) | Modular sweep: `APPS_RG_MODULAR_R4_SECTIONS_ROOT`, manifest emit, upstream-first lane order | [run_w23_windows_lane_sweep.ps1](ops_scripts/apps_rg/run_w23_windows_lane_sweep.ps1) | `companion_unify_bullets_context.json` → **ACCEPTED_FINALIZED** |
| **RCA-3** (P1) | `expand_structured_competencies_min_two_terms` runs **after** final dedupe | [competencies_lane_execution.py](apps_rg/runtime/sections/competencies_lane_execution.py) | Audit: competencies `x2_all_pass: true`, `lane_proof_ok: true` |
| **RCA-4** (P1) | `inject_ibm_locked_metric_anchors()` + foreign-metric scrub for granularity gate | [ibm_bullets_lane.py](apps_rg/runtime/sections/ibm_bullets_lane.py) | [ibm_bullets_20260523_131013](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260523_131013) — product quality PASS |
| **Audit** | `_latest_run_dir` prefers modular root when env set | [proof_pool_c0_ssot_gap_audit.py](ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py) | Audit JSON at modular root |

**Sweep hygiene (same pass):** repaired broken module docstrings that blocked mid-run — [__main__.py](apps_rg/__main__.py), [embedding_settings.py](apps_rg/runtime/embedding_settings.py), [conftest.py](tests/conftest.py), [test_unify_bullet_surface_id_repair.py](tests/unit/apps_rg/test_unify_bullet_surface_id_repair.py), [test_ibm_metric_repair_from_plan.py](tests/unit/apps_rg/test_ibm_metric_repair_from_plan.py).

### Fresh modular sweep evidence (2026-05-23)

`proof_classification.track_b_rca_remediation: RCA_FIXES_PROVEN_ON_MODULAR_SWEEP`  
`all_lanes_proof_ok: false` · `release_eligible_proof_claimed: false` (unchanged).

| Lane | x2_all_pass | lane_proof_ok | x3 |
|------|-------------|---------------|-----|
| executive_summary | true | true | **X3_REVIEW_JUDGE_SOFT_FAIL** |
| headline | false | false | X3_BLOCK |
| competencies | true | true | X3_BLOCK |
| unify_bullets | true | true | X3_REVIEW_JUDGE_SOFT_FAIL |
| unify_narrative | false | false | X3_BLOCK |
| ibm_bullets | true | true | X3_BLOCK |
| ibm_narrative | false | false | X3_BLOCK |

**Notes**

- P0 RCA-1/2/4 proven on live modular runs (unify + IBM bullets X2/product PASS; companion ACCEPTED).
- RCA-3 lifted competencies to `x2_all_pass` in audit; X3 still BLOCK on judges (separate from expand/dedupe).
- Narrative lanes still fail deterministic narrative X2 (parse / one-sentence / finalized-bullets chain).
- Headline regressed on X2 (`x2_headline_word_count_10_to_13`) in this sweep — not reopened this pass.
- WSL remains **ENVIRONMENT_BLOCKED** per audit; not a product regression.

### Track B completion receipt

```text
STATUS: PARTIAL
PROOF_CLASSIFICATION: RCA_FIXES_PROVEN_ON_MODULAR_SWEEP
COMMANDS_RUN:
- pytest (4 RCA unit tests) -> 4 passed
- run_w23_windows_lane_sweep.ps1 (~465s) -> exit 0; lane CLIs exit 1 (expected X3 non-ALLOW)
- ibm_bullets targeted re-run -> PRODUCT_QUALITY PASS
- proof_pool_c0_ssot_gap_audit.py (modular env) -> wrote audit JSON
```

---

## Track C — Executive summary synthesis RCA (remaining)

**Two-sentence root cause:** L2/Qwen produces proof-valid prose that passes X2 but fails unanimous X1D (≥ 4.0); graph-only anti-conflation repair is off under `product_fail_closed`, and synthesis regen can keep a weak `initial_llm` draft. X3 `X3_REVIEW_JUDGE_SOFT_FAIL` is correct product semantics, not infra failure.

**Relation to debugger RCA-6:** Same lane; W23 sweep now shows **X2 + lane_proof_ok PASS** and **X1D soft-fail** (matches Brown & Brown `exec_summary_20260522_*`). Earlier RCA-6 symptom (X2 claim-coverage / evidence-utilization FAIL) is the **hard gate** side of the same synthesis gap; Track C fixes should help both paths.

**Guardrails (unchanged):** No weaken X2/X3/judge thresholds/exit semantics; no default judge regen; no `agentic_core`; no target company in prose; preserve graph/ledger authority.

### Phase 0 — Baseline

| Step | Action |
|------|--------|
| C0.1 | Baseline runs: [exec_summary_20260522_230849](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_230849) (2/3 judges), [exec_summary_20260523_130346](artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes/executive_summary/real/exec_summary_20260523_130346) (modular; same X3) |
| C0.2 | Success: 3/3 judges ≥ 4.0 → `X3_ALLOW` |
| C0.3 | Keep `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=0` until C1–C2 stable |

### Phase 1 — Enforce synthesis (highest leverage)

| ID | Change | Files (expected) |
|----|--------|------------------|
| C1A | Allow `apply_graph_only_generation_quality_repair` on product path when `proof_source == augmented_skills_graph` (fail-closed safe) | [section_repair_policy.py](apps_rg/runtime/section_repair_policy.py), [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py), [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) |
| C1B | Regen authority: do not leave `initial_llm` authoritative when regen `accepted: false` / shape failures remain | [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) |
| C1C | Deterministic anti-conflation: always apply `governance_framework_to_basel_lineage` when `fact_governance_003` present; split platform vs Basel in display | [executive_summary_voice_repair.py](apps_rg/runtime/sections/executive_summary_voice_repair.py) |

### Phase 2 — Align X2 pre-checks with X1D (no threshold change)

| ID | Change |
|----|--------|
| C2A | Strengthen stacking: Led / Successfully / Also / Built / Delivered (fail at 3+ in 4–5 sentences) |
| C2B | Display-level causal merge gate when ledger row multi-base-fact + participial causation across governance vs platform |

### Phase 3 — Prompt / regen bullets (narrow)

- Keep I0 composition rules (complete S1, no cert dump, no opener chains, SVP technology-strategy voice).
- Regen repair user: one theme per sentence; Basel/CCAR only with `fact_governance_003`; weave `fact_exec_002` team scale.

### Phase 4 — Claude / SVP (only if still 2/3 after C1–C2)

- Shape from allowed facts only (platform + lineage + scale); optional graph slice expansion per [proof_pool_c0_ssot_gap_audit.json](artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json).

### Phase 5 — Verify

```text
python -m apps_rg --section executive_summary ...
```

Require 3× stability; modular sweep row `executive_summary` → `x3_outcome: X3_ALLOW`.

### Track C implementation receipt (2026-05-23)

**Receipt:** [track_c_exec_summary_remediation_receipt.md](artifacts/apps_rg/plans/track_c_exec_summary_remediation_receipt.md)

```text
STATUS: PARTIAL
COMMANDS_RUN:
- pytest Track C bundle (13 tests) -> 13 passed
- live executive_summary x3 -> NOT RUN (qwen_vllm + judges required)
```

C1A–C2B + C3 implemented; padding-loop infinite-spin fixed in graph-only builder.

---

## Unified priority order (what to do next)

1. **Track C5** — live 3× `executive_summary` proof → `X3_ALLOW` (operator; vLLM required).
2. **W0 Author-Gate** — allowlist SSOT A/B/C (original plan).
3. **W0 Author-Gate** — allowlist SSOT A/B/C (original plan).
4. **W1–W2** — FEC/pool convergence + digest receipts.
5. **Residual lane X3** — headline X2 word count; narrative parse/finalized-bullets; competencies/IBM/unify **judge** semantics (Track B fixed structure, not judges).
6. **W3** — full 7-lane proof sweep after above.

**Explicit non-goals:** `RELEASE_ELIGIBLE` claim; weakening gates; WSL product fixes.

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
