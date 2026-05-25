---
plan_id: graph-skills-quality-enhancement-c4e8a1
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# Graph skills maximization — hardened execution charter (v3.1 pre-W0)

**Maximize** `augmented_skills_graph` across the full resume with **separated proof classes**, **canonical CLI-only runtime proof**, **authority invariants**, **phase gates**, and **honest closeout non-claims**. Mixed evidence must never upgrade status to PASS.

| Predecessor (COMPLETED) | This plan |
|-------------------------|-----------|
| [graph-skills-hardening-f3a8c1](graph-skills-hardening-f3a8c1.md) | Quality, utilization, coherence, CI — **not** a repeat of authority wiring |

**Evidence baseline:** [exec_summary_20260525_163633](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_163633/) · [master_skills_arsenal_ledger.json](apps_rg/fact_inventory/master_skills_arsenal_ledger.json)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W10
LAST_UPDATED: 2026-05-26
PLAN_COMPLETED: 2026-05-26
COMPLETION_NOTE: W0–W10 + hardening shipped; closeout PARTIAL (LIVE_X3 2/7); W10-AG unified C0.3 bind deferred per user-directed plan close
PLAN_HARDENING: applied-2026-05-26-v3.2-w10-ag-mandatory
PLAN_REVIEW: basically-safe-to-execute-2026-05-26
PLAN_CREATED: slug=graph-skills-quality-enhancement-c4e8a1 path=.cursor/plans/graph-skills-quality-enhancement-c4e8a1.md status=Completed
NOTION_PAGE_ID: 36b27693-f55c-81c0-bb50-d8df6df2b60e

---

AUTHORIZATION_DECISION: plan=graph-skills-quality-enhancement-c4e8a1 decision=ACCEPTED authorized_by=user decisive_reason="W10-AG mandatory post-W10: unified graph-skills bind to C0.3 spine traverse via apps_rg adapter and live route profiles"

## Wave plan (W0–W10, then mandatory W10-AG) — execution order

**Receipt per wave:** `docs/reports/apps_rg/graph_skills_quality_w<N>_receipt.json` (schema in § Wave command receipt).

**Canonical REAL_LLM CLI** (Brown fixtures pinned in § Brown fixture identity):

```bash
python -m apps_rg --section <lane> --provider qwen_vllm \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief <briefing.md per lane> \
```

Lanes: `headline`, `executive_summary`, `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`, `competencies`.

| Wave | Gate out | Primary proof | Status |
|------|----------|---------------|--------|
| W0 | — | DETERMINISTIC + inventory | **DONE** |
| W1 | G-W1 | CONTRACT + rationale artifact | **DONE** |
| W2 | G-W2 | CONTRACT (7 prompts) | **DONE** |
| W3 | G-W3 | DETERMINISTIC validator | **DONE** |
| W4 | G-W4 | CONTRACT negatives + rubric diff | **DONE** |
| W5 | G-W5 | CONTRACT + FEC equality | **DONE** |
| W6 | G-W6 | CONTRACT NEG-3 + hybrid receipt | **DONE** |
| W7 | G-W7 | CI_RATCHET | **DONE** |
| W8 | G-W8 | CONTRACT scorer + REAL_LLM utilization | **DONE** |
| W9 | G-W9 | docs | **DONE** |
| W10 | G-W10 | LIVE_X3 matrix only | **DONE** |
| W10-AG | G-W10-AG | C0.3 unified pipeline bind | **DEFERRED** (follow-on) |

**PLAN_COMPLETE (2026-05-26):** User-directed close. Waves W0–W10 + runtime hardening delivered. **W10-AG / D16** deferred to follow-on (unified C0.3 bind + Author-Gate). Closeout: [graph_skills_quality_enhancement_closeout.json](docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json) — `claims_release_eligible=false`, `live_x3_allow` 2/7 at close.

```
PLAN_COMPLETE: plan=graph-skills-quality-enhancement-c4e8a1 note="W0-W10+hardening on disk; Notion Completed; W10-AG deferred"
DEFERRED_SCOPE: plan=graph-skills-quality-enhancement-c4e8a1 wave=W10-AG gap="Unified C0.3 pipeline bind (c0_graph_adapter, route_profiles, D16 REAL_LLM)" impact="follow-on plan"
```

### W0 — Baseline ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w0_baseline.py
```

**Artifacts:** [graph_skills_quality_enhancement_w0_baseline.json](docs/reports/apps_rg/graph_skills_quality_enhancement_w0_baseline.json) · [graph_skills_quality_w0_receipt.json](docs/reports/apps_rg/graph_skills_quality_w0_receipt.json)

- Classify existing evidence (no LIVE_X3 claim from closeout alone).  
- Brown pins = on-disk SHA-256 at W0 run (JD/exec updated 2026-05-25).  
- `x3_disposition_normalize.py` + dry-run samples in baseline.  
- `lane_registry.py` briefing `.txt` vs on-disk `.md` discrepancy recorded.  

### W1 — JD subgraph ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w1.py
```

**Artifacts:** [graph_skills_quality_w1_jd_subgraph.json](docs/reports/apps_rg/graph_skills_quality_w1_jd_subgraph.json) · [graph_skills_quality_w1_receipt.json](docs/reports/apps_rg/graph_skills_quality_w1_receipt.json) · per-lane [graph_skills_quality_w1_rationale/](docs/reports/apps_rg/graph_skills_quality_w1_rationale/)

- `emit_graph_selection_rationale()` in [graph_selection_rationale.py](apps_rg/runtime/graph_selection_rationale.py) — fixture only until W10 CLI.  
- NEG-1 started: [test_graph_skills_authority_separation_w1.py](tests/unit/apps_rg/test_graph_skills_authority_separation_w1.py).  
- JD boost monotonic: [test_graph_skills_jd_subgraph_w1.py](tests/unit/apps_rg/test_graph_skills_jd_subgraph_w1.py).  

### W2 — Skill capsule ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w2.py
```

**Artifacts:** [graph_skills_quality_w2_skill_capsule.json](docs/reports/apps_rg/graph_skills_quality_w2_skill_capsule.json) · [graph_skills_quality_w2_receipt.json](docs/reports/apps_rg/graph_skills_quality_w2_receipt.json)

- [graph_skill_phrase_capsule.py](apps_rg/runtime/graph_skill_phrase_capsule.py) appends `SKILL_PHRASE_CAPSULE_NOT_EVIDENCE` via `finalize_section_compiled_with_proof_pool` + `augment_section_compiled_with_input_authority`.  
- NEG-6: [assert_capsule_phrases_not_proof_authority](apps_rg/runtime/validators/graph_skills_proof_common.py) + [test_graph_skills_authority_separation.py](tests/unit/apps_rg/test_graph_skills_authority_separation.py).  
- Seven-lane contract: [test_graph_skills_skill_capsule_w2.py](tests/unit/apps_rg/test_graph_skills_skill_capsule_w2.py).  

### W3 — Graph v2 ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w3.py
```

**Artifacts:** [graph_v2_migration_receipt.json](docs/reports/apps_rg/graph_v2_migration_receipt.json) · [graph_skills_quality_w3_graph_v2.json](docs/reports/apps_rg/graph_skills_quality_w3_graph_v2.json) · [graph_skills_quality_w3_receipt.json](docs/reports/apps_rg/graph_skills_quality_w3_receipt.json) · [graph_skills_graph_v2_rollback.md](docs/apps_rg/graph_skills_graph_v2_rollback.md)

- [graph_v2_quality_migration.py](apps_rg/fact_inventory/graph_v2_quality_migration.py) — controlled ACTIVE remediation; 0 orphans post-migration.  
- Stripped legacy `early_career` from four `ACTIVE_CONFIRMED` actuarial rows; derived `graph_hop_path` on all ACTIVE rows missing hops (106 remediated).  
- Backup: `artifacts/apps_rg/fact_inventory/backups/master_skills_arsenal_ledger_pre_graph_v2_w3_*.json`  
- SQLite rematerialized via `materialize_augmented_skills_graph_sqlite()`.  
- Tests: [test_graph_skills_graph_v2_w3.py](tests/unit/apps_rg/fact_inventory/test_graph_skills_graph_v2_w3.py).  

### W4 — Quality port ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w4.py
```

**Artifacts:** [graph_skills_x1d_rubric_port_diff.json](docs/reports/apps_rg/graph_skills_x1d_rubric_port_diff.json) · [graph_skills_quality_w4_quality_port.json](docs/reports/apps_rg/graph_skills_quality_w4_quality_port.json) · [graph_skills_quality_w4_receipt.json](docs/reports/apps_rg/graph_skills_quality_w4_receipt.json)

- [graph_skills_x1d_rubric_contract.py](apps_rg/runtime/judges/graph_skills_x1d_rubric_contract.py) — per-family rubric markers + baseline diff; `any_masking_relaxed=false`.  
- NEG-2..NEG-6 in [graph_skills_proof_common.py](apps_rg/runtime/validators/graph_skills_proof_common.py) + [test_graph_skills_authority_separation.py](tests/unit/apps_rg/test_graph_skills_authority_separation.py).  
- Baseline pin: [graph_skills_x1d_rubric_baseline_w4.json](apps_rg/runtime/judges/graph_skills_x1d_rubric_baseline_w4.json).  
- X2 subset: headline fixed-prefix + exec summary composition contracts.  

### W5 — Spine + FEC ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w5.py
```

**Artifacts:** [resume_spine_skill_bundle.json](docs/reports/apps_rg/resume_spine_skill_bundle.json) · [graph_skills_fec_set_equality_receipt.json](docs/reports/apps_rg/graph_skills_fec_set_equality_receipt.json) · [graph_skills_quality_w5_spine_fec.json](docs/reports/apps_rg/graph_skills_quality_w5_spine_fec.json) · [graph_skills_quality_w5_receipt.json](docs/reports/apps_rg/graph_skills_quality_w5_receipt.json)

- [resume_spine_skill_bundle.py](apps_rg/runtime/spine/resume_spine_skill_bundle.py) — `build_resume_spine_skill_bundle()` + dedupe matrix.  
- [graph_skills_fec_set_equality.py](apps_rg/runtime/spine/graph_skills_fec_set_equality.py) — D7 strict set equality on 6 lanes (excludes headline).  
- [proof_pool_c0_ssot_gap_audit.py](ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py) — `fec_only_ids` / `resolver_only_ids` / `d7_set_equal` fields.  
- Tests: [test_graph_skills_spine_fec_w5.py](tests/unit/apps_rg/test_graph_skills_spine_fec_w5.py).  

### W6 — Hybrid boost ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w6.py
```

**Artifacts:** [hybrid_graph_boost_receipt.json](docs/reports/apps_rg/hybrid_graph_boost_receipt.json) · [graph_skills_quality_w6_hybrid_boost.json](docs/reports/apps_rg/graph_skills_quality_w6_hybrid_boost.json) · [graph_skills_quality_w6_receipt.json](docs/reports/apps_rg/graph_skills_quality_w6_receipt.json)

- [graph_skills_hybrid_boost.py](apps_rg/runtime/graph_skills_hybrid_boost.py) — reorder-only via `apply_hybrid_informed_fact_plan_reorder`; rejected widen attempts with `reason_code=outside_resolver_pool`.  
- NEG-3: [assert_hybrid_fact_ids_in_resolver_pool](apps_rg/runtime/validators/graph_skills_proof_common.py) + tests.  
- Tests: [test_graph_skills_hybrid_boost_w6.py](tests/unit/apps_rg/test_graph_skills_hybrid_boost_w6.py).  

### W7 — CI ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w7.py
```

**Artifacts:** [graph_skills_quality_w7_ci_ratchet.json](docs/reports/apps_rg/graph_skills_quality_w7_ci_ratchet.json) · [graph_skills_agentic_core_boundary_w7.json](docs/reports/apps_rg/graph_skills_agentic_core_boundary_w7.json) · [graph_skills_quality_w7_receipt.json](docs/reports/apps_rg/graph_skills_quality_w7_receipt.json)

- Workflow: [.github/workflows/graph-skills-authority-ratchet.yml](.github/workflows/graph-skills-authority-ratchet.yml) — boundary guard + W1–W6 contract pytest.  
- Guard: [check_graph_skills_agentic_core_boundary.py](ops_scripts/ci/check_graph_skills_agentic_core_boundary.py).  
- D10/D13: local mirror **PARTIAL** until green GHA run (`ci_gha_executed`); nightly cron `17 9 * * *` on same workflow.  

### W8 — Utilization ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w8.py
```

**Artifacts:** [graph_skills_utilization_receipt.json](docs/reports/apps_rg/graph_skills_utilization_receipt.json) · [graph_skills_quality_w8_receipt.json](docs/reports/apps_rg/graph_skills_quality_w8_receipt.json)

- Scorer: [graph_skills_utilization_scorer.py](apps_rg/runtime/graph_skills_utilization_scorer.py) — D8 anti-gaming (phrase + fact_id, forbidden/suppressed, semantic variant map).  
- NEG-6: `validate_scorer_inputs_neg6` on scorer inputs.  
- Tests: [test_graph_skills_utilization_w8.py](tests/unit/apps_rg/test_graph_skills_utilization_w8.py).  
- **PARTIAL** on REAL_LLM until Brown exec + competencies live runs populate `real_llm_probe_paths` (CONTRACT lane fixtures PASS).  

### W9 — Operator guide ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w9.py
```

**Artifacts:** [graph_skills_quality_operator_guide.md](docs/apps_rg/graph_skills_quality_operator_guide.md) · [graph_skills_quality_w9_operator_guide.json](docs/reports/apps_rg/graph_skills_quality_w9_operator_guide.json) · [graph_skills_quality_w9_receipt.json](docs/reports/apps_rg/graph_skills_quality_w9_receipt.json)

- Canonical per-lane + whole-resume `python -m apps_rg` commands; Brown `.md` briefing SSOT; proof-class law; wave emitters W0–W9.  
- Tests: [test_graph_skills_operator_guide_w9.py](tests/unit/apps_rg/test_graph_skills_operator_guide_w9.py).  

### W10 — Closeout ✅ DONE

**Emit (re-run anytime):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w10.py
```

**Artifacts:** [graph_skills_quality_enhancement_closeout.json](docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json) · [graph_skills_quality_w10_receipt.json](docs/reports/apps_rg/graph_skills_quality_w10_receipt.json)

- Compiler: [graph_skills_quality_enhancement_closeout.py](apps_rg/fact_inventory/graph_skills_quality_enhancement_closeout.py) — `proof_classification_matrix` D1–D16, `d6_lane_matrix`, Brown digest pins, honest non-claims.  
- Tests: [test_graph_skills_closeout_w10.py](tests/unit/apps_rg/test_graph_skills_closeout_w10.py).  
- **Honest status:** closeout reflects live inventory (e.g. `live_x3_allow` count); **PARTIAL** at plan close (2/7 LIVE_X3).  
- Runtime hardening: [graph_skills_run_artifacts.py](apps_rg/runtime/graph_skills_run_artifacts.py) · [backfill_graph_skills_run_artifacts.py](ops_scripts/apps_rg/backfill_graph_skills_run_artifacts.py) · 62 contract tests.

### W10-AG — Unified C0.3 pipeline bind ⏸ DEFERRED (follow-on)

**Purpose:** Bind `augmented_skills_graph` to **core C0.3 GraphRAG** through apps_rg profiles and adapters — **one pipeline** (spine retrieve → `maybe_run_graph_rag` / `run_graph_traverse` → FEC → proof pool → L2). Retire parallel “static graph only” product path as SSOT.

**Entry gate:** **G-W10 PASS** (W10 closeout artifact on disk with honest status).

**Author-Gate (required — same wave, not optional):**

1. Emit packet via `.cursor/skills/author-gate-packet-builder/` — `architecture_choice`: **dynamic C0.3 GraphRAG traverse (unified)** vs **remain static graph + deferral SSOT**.  
2. `ask_user_question` with rendered `OPTIONS_JSON` (per [003-cursor-author-gate-hitl.mdc](.cursor/rules/003-cursor-author-gate-hitl.mdc)).  
3. Record `DECISION_CAPTURED:` + `author_gate_receipt_ref` in [graph_skills_quality_w10_ag_receipt.json](docs/reports/apps_rg/graph_skills_quality_w10_ag_receipt.json).  
4. **Default recommended option:** unified bind (apps_rg adapter + live `graph_traverse` + FEC-driven proof; no `graphrag_deferred_phase1` on product lanes).

**If unified option selected — implementation checklist (all required for W10-AG PASS):**

| # | Deliverable | Path / proof |
|---|-------------|--------------|
| 1 | apps_rg C0.3 graph adapter (missing today) | [apps_rg/integrations/c0_graph_adapter.py](apps_rg/integrations/c0_graph_adapter.py) + `apps_rg/integrations/__init__.py` — `get_graph_adapter()` over `augmented_skills_graph` |
| 2 | Live route `graph_traverse` block | [route_profiles.yaml](apps_rg/config/domain_contract/route_profiles.yaml): `graph_expansion_allowed: true`, `graph_adapter_ref: apps_rg.integrations.c0_graph_adapter`, `live_wiring_deferred: false`, `wiring_gate: LIVE` |
| 3 | Spine C0 retrieve uses graph expansion (not NA stamp) | [c0_binding.py](apps_rg/runtime/bindings/c0_binding.py) — `graph_expansion_refs` from traverse/FEC, not hardcoded `C0_GRAPH_LANE_NA_REF` when policy active |
| 4 | Proof pool consumes spine FEC graph refs | [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py) / section lanes — `c03_graphrag_bound` aligned to spine output; static-only shim demoted or gated |
| 5 | Retire deferral as product SSOT | Update [C0_graph_lane_deferral.md](apps_rg/config/domain_contract/C0_graph_lane_deferral.md) + [section_c0_retrieve.py](apps_rg/runtime/spine/section_c0_retrieve.py) receipts: `canonical_c0_3_graph_rag_claimed: true` on proof run |
| 6 | Contract proof | `tests/_apps_contract/test_w4n_app_graph_adapters.py` + `test_w3_c03_adapter_registry.py` resolve `apps_rg.integrations.c0_graph_adapter` |
| 7 | REAL_LLM proof (exec summary first, then 7/7) | `c0_graph_lane_receipt.json`: no `graphrag_deferred_phase1`; `c03_graphrag_bound_status: BOUND` from spine; artifact dir linked in receipt |

**Emit (after implementation):**

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w10_ag.py
```

**Artifacts:** [graph_skills_quality_w10_ag_receipt.json](docs/reports/apps_rg/graph_skills_quality_w10_ag_receipt.json) · [graph_skills_c03_unified_pipeline_bind.json](docs/reports/apps_rg/graph_skills_c03_unified_pipeline_bind.json)

**Closeout non-claims (W10-AG may flip only with proof):**

| Field | W10 (static path) | After W10-AG PASS (unified path) |
|-------|-------------------|----------------------------------|
| `claims_dynamic_graphrag_traverse` | must be **false** | may be **true** only if D16 + REAL_LLM receipts prove live traverse |
| `claims_agentic_core_changed` | must be **false** for W10-only commits | **true** only if W10-AG diff includes authorized `agentic_core/**` binding glue (generic only; no app-id branches in core) |

**D16 (W10-AG only):** Seven-lane (or exec-summary pilot + roll-forward) REAL_LLM runs show spine `graph_expansion_refs` ≠ `ref:graph:NOT_APPLICABLE:graphrag_deferred_phase1` and adapter resolution `RESOLVED`.

⛔ **W10-AG `status: PASS` forbidden** without Author-Gate `DECISION_CAPTURED`, adapter on disk, and at least one REAL_LLM lane receipt proving unified bind (exec_summary minimum).

### Phase gates (no downstream wave on red)

| Gate | Blocks | Requires green |
|------|--------|----------------|
| G-W1 | W2+ | `graph_selection_rationale` in fixture run; JD boost monotonic tests PASS |
| G-W2 | W3+ | Capsule in all 7 compiled prompts — contract tests PASS |
| G-W3 | W4+ | 0 ACTIVE orphan skills; graph v2 digest pinned; rollback doc |
| G-W4 | W5+ | X2 gates + negative authority tests PASS; rubric diff (no masking) |
| G-W5 | W6+ | `resume_spine_skill_bundle` manifest; D7 set equality 6/6 lanes |
| G-W6 | W7+ | `hybrid_graph_boost_receipt.json`; NEG-3 PASS |
| G-W7 | W8+ | CI ratchet green (`CI_RATCHET_PROOF`) |
| G-W8 | W9+ | Utilization scorer + anti-gaming tests PASS |
| G-W9 | W10 | Operator guide on disk |
| G-W10 | **W10-AG** | Per-lane REAL_LLM artifact inventory complete (W10 closeout JSON) |
| **G-W10-AG** | **plan complete** | Author-Gate captured + D16 unified-pipeline REAL_LLM proof |

Emit `PHASE_GATE: wave=Wn status=PASS|FAIL gate=G-Wn` in wave receipt (include `W10-AG`).

### Priority stack

| Tier | Waves |
|------|-------|
| P0 | W1, W2, W4, W7 |
| P1 | W3, W5, W6 |
| P2 | W8, W9, W10 |
| **P0 (terminal)** | **W10-AG** (blocks plan completion) |

### Closeout contract (W10)

File: `docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json`

- **`proof_classification_matrix`:** each D1–D15 with `dod_id`, `status`, `primary_proof_class`, `artifact_paths`, `command`, `exit_code`, `ci_unavailable`.  
- **D6 per-lane matrix:** `lane`, `x3_code_raw`, `x3_normalized`, `x3_pass`, `live_x3_allow_claimed`, `brown_jd_sha256`, `brown_briefing_sha256`, `x2_gate_summary`, artifact dir.  
- **`wave_receipt_paths[]`:** `graph_skills_quality_w0_receipt.json` … `w9_receipt.json`, **`graph_skills_quality_w10_ag_receipt.json`** (mandatory).  

| Non-claim | Field |
|-----------|--------|
| Release eligibility | `claims_release_eligible` |
| Production readiness | `claims_production_ready` |
| 7/7 live REAL_LLM X3 allow | `claims_live_x3_7_of_7` |
| CI ratchet on GHA | `claims_ci_ratchet_gha_executed` |
| Graph v2 migration complete | `claims_graph_v2_migration_complete` |
| CI ratchet active | `claims_ci_ratchet_active` |
| Nightly soak green | `claims_nightly_soak_green` |
| Dynamic GraphRAG traverse | `claims_dynamic_graphrag_traverse` (**false at W10**; may flip **true** only after **W10-AG PASS**) |
| agentic_core changed | `claims_agentic_core_changed` (**false for W0–W10 commits**; W10-AG may be **true** if unified bind required generic core glue) |
| C0.3 unified pipeline live | `claims_c03_unified_pipeline_bound` (**false until W10-AG PASS** — see D16) |

**Overall:** W10 PASS = all D1–D15 with correct primary class; **plan PASS** = W10 + **W10-AG** (D16 + Author-Gate receipt); PARTIAL = missing proof; FAIL = REAL_LLM X2/X3 fail; BLOCKED = env/gate.

---

## Proof classification contract (MUST — no mixed PASS)

Every DoD row and wave receipt MUST tag evidence with exactly one primary class (secondary classes allowed as supporting only).

| Class | ID | What counts | What does NOT count |
|-------|-----|-------------|---------------------|
| Contract / unit | `CONTRACT_TEST_PROOF` | `pytest` / `_apps_contract` against fixtures; resolver smoke without product CLI | Direct `resolve_section_proof_pool()` as **product** proof; dispatch-only scripts |
| Deterministic runtime | `DETERMINISTIC_RUNTIME_PROOF` | `python -m apps_rg` with `--dry-run` or fixture dev bypass **only** when plan wave explicitly allows; closeout validators; `run_full_closeout(skip_live=True)` | REAL_LLM claims; X3_ALLOW claims |
| Real LLM runtime | `REAL_LLM_RUNTIME_PROOF` | `python -m apps_rg --section <lane> --provider qwen_vllm` (or canonical full-resume CLI if productized) | Internal lane functions; smoke seams; helper-only runs |
| Live disposition | `LIVE_X3_ALLOW_PROOF` | Per-lane `x3_disposition.json` with `x3_code` raw + `x3_normalized=ALLOW_FINISH` from **REAL_LLM_RUNTIME_PROOF** only (see normalization map) | Label-only match without normalization; X2-only pass; dry-run; aggregate inference without per-lane artifacts |
| CI | `CI_RATCHET_PROOF` | Green workflow run URL + exit code for `graph-skills-authority-ratchet` / nightly soak | Local-only pytest without CI log |

**Status law**

- **PASS** on a DoD item: primary class satisfied + artifact path + command + exit code recorded in receipt.
- **PARTIAL**: some waves done; missing class, path, command, or exit code — list exact blocker.
- **FAIL**: command ran and failed.
- **BLOCKED**: missing provider, Chroma, permission, or phase gate predecessor red.

⛔ **W10 closeout `status: PASS` forbidden** unless `proof_classification_matrix` shows each D1–D15 row with valid primary class. **D6 may only use `LIVE_X3_ALLOW_PROOF`.**

---

## X3 disposition normalization (MUST — no label mismatch PASS/FAIL)

**apps_rg product SSOT** (not `agentic_core` L3 `ALLOW_FINISH` / `X3D_*`):

- Artifact field: `x3_disposition.json` → **`x3_code`** (string)
- Allow-family codes emitted by lane X3 modules include: `X3_ALLOW`, `X3_BLOCK`, `X3_REVIEW_*`, `X3_BLOCK_*`
- Closeout normalizer already treats `X3_ALLOW` and substring `ALLOW` as allow-family ([p2_graph_skills_accelerated_closeout.py](apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py) L418–431)

**Plan label `LIVE_X3_ALLOW_PROOF`** is a **proof class name only** — not a required raw enum string.

### Normalization map (W10 closeout + per-lane receipts)

Implement in `apps_rg/runtime/proof/x3_disposition_normalize.py` (W0 stub, W10 use):

| `x3_code` raw (examples) | `x3_normalized` | Counts toward D6 LIVE_X3? |
|--------------------------|-------------------|---------------------------|
| `X3_ALLOW` | `ALLOW_FINISH` | **yes** (requires `pass=true`, REAL_LLM, X2 policy met) |
| `X3_ALLOW_*` (if ever emitted) | `ALLOW_FINISH` | **yes** (same rules) |
| `X3_REVIEW_*`, `*SOFT_FAIL*` | `REVIEW` | no |
| `X3_BLOCK`, `X3_BLOCK_*`, `X3_DENY` | `BLOCK` | no |
| missing / empty | `UNKNOWN` | no (**blocking**) |
| `ALLOW_FINISH`, `X3D_ALLOW_FINISH` | `ALLOW_FINISH` | **only if** `x3_code` also present and maps — do not accept core-only labels without `x3_code` |

**W10 per-lane row MUST include:**

```json
{
  "x3_code_raw": "X3_ALLOW",
  "x3_normalized": "ALLOW_FINISH",
  "x3_pass": true,
  "live_x3_allow_claimed": true
}
```

⛔ Do not FAIL a lane solely because raw string ≠ `X3_ALLOW` when normalized = `ALLOW_FINISH`.  
⛔ Do not PASS when `x3_normalized=UNKNOWN` or `REVIEW` or `BLOCK`.

---

## Wave command receipt schema (MUST — every wave)

Every wave emits `docs/reports/apps_rg/graph_skills_quality_w<N>_receipt.json` containing:

| Field | Required |
|-------|----------|
| `wave_id` | e.g. `W1` |
| `proof_class` | primary class for wave |
| `command` | argv string (shell-safe list preferred) |
| `cwd` | repo root |
| `env_vars` | subset: `CHROMA_PERSIST_DIR`, `APPS_RG_*`, provider keys, JD paths if passed |
| `exit_code` | int |
| `artifact_paths` | repo-relative paths |
| `timestamp_utc` | ISO-8601 |
| `git_commit` | `git rev-parse HEAD` at run time |
| `phase_gate` | `G-Wn` + PASS/FAIL |
| `notes` | optional |

Closeout MUST aggregate wave receipts — no reconstruction from chat memory.

---

## Brown fixture identity (MUST — pinned in W0, echoed in W10)

**SSOT paths** (repo-relative). Do not use “latest Brown JD” prose.

| Fixture | Path | SHA-256 (pin in W0 baseline) |
|---------|------|------------------------------|
| JD | [brown_brown_svp_it_strategy_innovation_jd.txt](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt) | `3701dd5b1d6e0c92db394d6bf1879574e4ad638094d9b453f6d35e264e8e573f` (W0 pin) |
| Briefing (6 lanes) | [brown_brown_svp_it_strategy_innovation_briefing.md](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md) | `97b306a10498240fd676e9ce2d9d3fd00139d6f441d0401224e223456a95c78b` |
| Briefing (executive_summary) | [brown_brown_svp_it_strategy_innovation_briefing_exec.md](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md) | `74bd4674f23f17236abf3e5a3837e7fd422d6691e2f7e1dc234653f11a6da1f6` (W0 pin) |

**CLI targeting (canonical)** — mirror [lane_registry.py](apps_rg/runtime/rigor/lane_registry.py):

```text
--target-company "Brown & Brown"
--target-role "SVP IT Strategy & Innovation"
--jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt
--manual-brief <briefing.md per lane table above>
--provider qwen_vllm
```

W0 baseline JSON MUST copy this table. W10 closeout MUST assert **byte-identical** JD/briefing digests or FAIL D6.

**Note:** `lane_registry.py` references `briefing.txt` but on-disk SSOT is `.md` — W0 documents discrepancy; W9 operator guide uses `.md` paths above.

---

## Canonical CLI proof law (MUST)

All **product behavior** proof MUST use:

```bash
python -m apps_rg --section <lane> [canonical flags]
```

Allowed lanes: `headline`, `executive_summary`, `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`, `competencies`.

Whole-resume proof (if used) MUST use the **canonical full-resume CLI** documented in operator guide — not ad-hoc orchestration scripts.

**Forbidden as product proof**

- Calling `run_*_execution`, `wire_spine_c0_fec_for_section`, or resolver helpers directly to claim runtime PASS
- Fixture-only scripts without CLI invocation
- `--provider mock` (removed from CLI; tests must migrate)
- Isolated dispatch / smoke seams presented as lane proof

Helper and unit tests remain valid as **`CONTRACT_TEST_PROOF` only.**

---

## Authority separation invariant (MUST — W1, W2, W5, W6)

These rules are **constitutional** for this plan:

| Input | Role |
|-------|------|
| `augmented_skills_graph` | **evidence_authority** — skills, hops, allowed/forbidden phrases, graph-bound facts |
| `candidate_fact_ledger` / SRFS | **Claim text substrate only** — supplies `claim_text`; not skills SSOT |
| JD / briefing | **Targeting** — shape weights, reorder, gap notes; never new fact_ids |
| C0.2 hybrid | **Reorder** existing resolver-allowed graph facts only; **no pool widen** |
| Skill phrase capsule | **Lexical guidance** — wording constraints; **not** new evidence or fact_ids |
| `allowed_phrases` / `forbidden_phrases` | **Lexical constraints** — not proof authority |
| `broad_skills_ledger` | **DEPRECATED_REFERENCE_ONLY** — regression = FAIL |
| Base resume | **DEPRECATED_NON_AUTHORITY** — no story-claim fallback |

### Negative tests (required — CONTRACT_TEST_PROOF)

| Test ID | Assert |
|---------|--------|
| NEG-1 | JD-only skill cannot be admitted without graph `fact_id_links` |
| NEG-2 | Capsule-only phrase cannot satisfy X2 unsupported-claim without `allowed_fact_ids` |
| NEG-3 | Hybrid-suggested fact_id ∉ resolver pool → fail-closed + receipt entry |
| NEG-4 | `proof_source=broad_skills_ledger` or SRFS-as-proof → `GraphSkillsProofError` |
| NEG-5 | Base-resume story hydration cannot become selected_fact_plan authority |
| NEG-6 | `allowed_phrases` / capsule text cannot appear in `allowed_fact_ids`, claim_ledger `fact_id`, or `text_claim_coverage` as proof without graph fact link |

Implement in `tests/unit/apps_rg/test_graph_skills_authority_separation.py` + extend [graph_skills_proof_common.py](apps_rg/runtime/validators/graph_skills_proof_common.py).

### Capsule vs proof authority (W2 / W8 — MUST)

- Capsule lives only in **prompt guidance** fields (`compiled_prompt.txt` block `SKILL_PHRASE_CAPSULE_NOT_EVIDENCE`).
- Capsule MUST NOT populate: `proof_pool_metadata.allowed_fact_ids`, `selected_fact_plan`, `evidence_authority`, `native_c03` evidence_items authority, claim_ledger rows.
- **NEG-6** enforced in CONTRACT_TEST_PROOF + spot-check REAL_LLM `runtime_payload.json` / ledger dumps.

---

## agentic_core boundary (MUST — enforce)

- **W0–W10:** `touches_agentic_core: false` — **zero** `agentic_core/**` diffs in W0–W10 commits.
- **W10-AG (mandatory):** may touch `agentic_core/**` only for **generic** C0.3 bind glue (no `if app_id == "apps_rg"`); requires Author-Gate `DECISION_CAPTURED` + migration/boundary receipt if diff is non-trivial.
- No core route/gate/policy weakening to ease apps_rg PASS.
- **`run_graph_traverse` on product path** is **in scope for W10-AG** when Author-Gate selects unified bind (not a separate optional fork).
- Pre-wave gate (W7): `git diff --name-only` must not list `agentic_core/` **until W10-AG starts** (then W7 ratchet re-run or W10-AG-only commit scope).

---

## Graph maximization principles

1. Graph decides skills; ledger supplies claim text only.  
2. Every selected skill earns a verifiable hop.  
3. Prompts expose skill vocabulary via capsule (guidance, not evidence).  
4. JD shapes subgraph; hybrid never widens allowlist.  
5. One resume spine per run.  
6. Utilization measured with anti-gaming rules (D8).  
7. Judges may not mask weak graph grounding (W4).  

---

## Context (SCQA)

- **Situation** — P2 wired graph authority on seven sections; exec summary is quality reference.  
- **Complication** — Proof mixing, non-CLI seams, weak utilization metrics, FEC drift, judge-only PASS on 1/7 lanes.  
- **Question** — How to maximize graph skills **safely**?  
- **Answer** — W0–W10 with **phase gates**, **proof classes**, and **honest non-claims** at W10 closeout; then **mandatory W10-AG** to bind graph skills to **C0.3 unified pipeline** (Author-Gate + D16 proof).

---

## Scope

### In scope

`apps_rg`, `ops_scripts/apps_rg`, `tests/**`, `.github/workflows/**`, `docs/reports/apps_rg/**`, `docs/apps_rg/**` — per wave **W0–W10**.

**W10-AG (mandatory, in scope):** [apps_rg/integrations/c0_graph_adapter.py](apps_rg/integrations/c0_graph_adapter.py), live [route_profiles.yaml](apps_rg/config/domain_contract/route_profiles.yaml) `graph_traverse`, [c0_binding.py](apps_rg/runtime/bindings/c0_binding.py) spine graph refs, FEC/proof-pool alignment, deferral doc update, Author-Gate packet + receipt, D16 REAL_LLM proof. Generic `agentic_core/**` glue **only** when Author-Gate unified option is selected.

### Out of scope

- Gate/rubric weakening for convenience  
- Synthetic skills without candidate truth + section eligibility  
- Inventing graph metrics to pass bad output  
- **Skipping W10-AG** or marking plan **Completed** after W10 only  
- Permanent parallel static-only graph path as SSOT **after** W10-AG unified option is accepted

---

## Definition of Done (proof-class tagged)

| ID | Criterion | Primary proof class | Evidence |
|----|-----------|---------------------|----------|
| D1 | `graph_selection_rationale.json` per REAL_LLM lane run | `REAL_LLM_RUNTIME_PROOF` | Artifact path per lane |
| D2 | Skill capsule in all 7 `compiled_prompt.txt` | `CONTRACT_TEST_PROOF` + spot-check `REAL_LLM_RUNTIME_PROOF` | 7 contract tests + 7 CLI prompts |
| D3 | Graph-only repair + X2 locality all 7 sections | `CONTRACT_TEST_PROOF` + `REAL_LLM_RUNTIME_PROOF` | pytest + `x2_gate_outputs.json` per lane |
| D4 | Median hops ≥ 5 unify/ibm (resolver metadata) | `DETERMINISTIC_RUNTIME_PROOF` | closeout JSON |
| D5 | `resume_spine_skill_bundle.json` + dedupe | `CONTRACT_TEST_PROOF` (+ optional REAL_LLM per policy below) | unit test + manifest |
| D6 | **7/7** live allow (`x3_normalized=ALLOW_FINISH`) on **pinned Brown** | **`LIVE_X3_ALLOW_PROOF` only** | D6 checklist + x3 raw+normalized + fixture digests |
| D7 | FEC ≡ resolver pool **set equality** | `DETERMINISTIC_RUNTIME_PROOF` | audit JSON per lane |
| D8 | Utilization anti-gaming PASS | `REAL_LLM_RUNTIME_PROOF` | `graph_skills_utilization_receipt.json` |
| D9 | Zero ACTIVE orphan skills (v2) | `DETERMINISTIC_RUNTIME_PROOF` | validator + migration digest |
| D10 | CI ratchet green | `CI_RATCHET_PROOF` | workflow run URL — **BLOCKED/PARTIAL** if GHA unavailable locally |
| D11 | Forbidden phrase enforcement | `CONTRACT_TEST_PROOF` + one REAL_LLM lane | pytest + x2 |
| D12 | `native_c03_final_evidence.json` all 7 REAL_LLM | `REAL_LLM_RUNTIME_PROOF` | inventory |
| D13 | Nightly soak green | `CI_RATCHET_PROOF` | GHA nightly — **BLOCKED/PARTIAL** if GHA unavailable locally |
| D14 | Operator guide | `DETERMINISTIC_RUNTIME_PROOF` | doc path |
| D15 | Graph v2 digest + v1 rollback | `DETERMINISTIC_RUNTIME_PROOF` | migration receipt |
| D16 | C0.3 unified pipeline bound (spine graph ≠ deferred NA) | `REAL_LLM_RUNTIME_PROOF` + `CONTRACT_TEST_PROOF` | W10-AG receipt + `c0_graph_lane_receipt.json` per lane (exec_summary pilot OK to start) |

### D5 — Whole-run dependency (MUST)

**Primary proof:** `CONTRACT_TEST_PROOF` for `build_resume_spine_skill_bundle()` + dedupe matrix.

**REAL_LLM evidence for D5 (pick one — no ad-hoc orchestrator):**

1. **Preferred:** seven per-section canonical CLI runs (same pinned Brown fixtures) each writing `resume_spine_skill_bundle.json` copy or `whole_run_graph_manifest.json` fragment — class `REAL_LLM_RUNTIME_PROOF` per lane, spine logic still `CONTRACT_TEST_PROOF`.
2. **Optional:** single canonical `python -m apps_rg` whole-run (no `--section`) **only if** W9 operator guide documents it as productized entry — class `REAL_LLM_RUNTIME_PROOF` with `full_resume_<id>/` artifact tree.

⛔ **Forbidden for D5 PASS:** custom Python scripts that call resolvers/lanes directly without `python -m apps_rg`.

### D6 artifact checklist (all seven lanes — REAL_LLM only)

Each lane under `artifacts/apps_rg/runtime_proofs/<lane>/real/<run_id>/` via **canonical CLI** with **pinned Brown digests** (see table above):

| Artifact | Required |
|----------|----------|
| `native_c03_final_evidence.json` | yes |
| `graph_selection_rationale.json` | yes |
| `section_input_usage_ledger.json` | yes (`augmented_skills_graph` = SKILLS_COMPETENCY_AUTHORITY) |
| `compiled_prompt.txt` | yes (skill capsule block present — guidance only) |
| `l2_output.json` | yes |
| `x2_gate_outputs.json` | yes — see **X2 gate policy** below |
| `x3_disposition.json` | yes — `x3_code` raw + **normalized** allow |
| `provider_request.json` + `provider_response.json` | yes |
| `x1d_llm_judge_outputs.json` (or lane equivalent) | yes when judges enabled |
| `brown_fixture_digests.json` | yes (W10 emitter — copy pinned hashes) |

**Environment:** `--provider qwen_vllm`, pinned Brown paths/digests, `CHROMA_PERSIST_DIR` set where C0.2 mandatory.

### X2 gate policy (D6 — precise)

From `x2_gate_outputs.json`:

- **PASS lane:** every gate either `pass: true` **OR** documented NA per gate row:
  - `pass: false` with `failure_reason` containing `not_applicable` / `skipped` **and**
  - `gate_id`, `gate_type`, `observed_value`, `threshold`, `policy_ref` (e.g. `apps_rg/runtime/validators/<lane>_x2.py#L725`)
  - `na_allowed: true` in closeout matrix for that `(lane, gate_id)`
- **FAIL lane:** any gate with `pass: false` without allowed NA
- **BLOCKING:** gate missing, malformed, or verdict `UNKNOWN` without NA policy

⛔ “All gates PASS” in prose is insufficient — closeout must list NA gates explicitly or prove zero failed_gates.

---

## D7 — FEC set equality (exact)

Per lane receipt MUST show:

- `fec_only_ids`: **[]** (0 FEC-only fact IDs)
- `resolver_only_ids`: **[]** (0 required resolver IDs missing from FEC)
- `fec_ids` == `resolver_ids` (set equality)
- Every exclusion has `reason_code`
- Any mismatch → lane **FAIL** for product proof (not PARTIAL)

Script: `ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py` — extend to emit equality proof.

---

## D8 — Utilization anti-gaming (MUST)

Phrase overlap alone is **insufficient**. PASS requires per lane:

1. Selected `allowed_phrase` appears in output **OR** normalized semantic variant (configured synonym map, not LLM-judged).  
2. Output sentence maps to **allowed `fact_id`** (claim_ledger / text_claim_coverage).  
3. No `forbidden_phrase` hit.  
4. No unsupported skill phrase (phrase not in selected skill row set).  
5. Denominator excludes `suppressed_skill_ids` with non-empty `reason_code`.

Emit `graph_skills_utilization_receipt.json` (schema — W8):

```json
{
  "selected_skill_ids": [],
  "allowed_phrases": [],
  "used_phrases": [],
  "semantic_variants_matched": [],
  "cited_fact_ids": [],
  "unused_skill_ids": [],
  "suppressed_skill_ids": [{ "skill_id": "", "reason_code": "" }],
  "forbidden_phrase_violations": [],
  "unsupported_skill_phrase_violations": [],
  "utilization_score": 0.0,
  "pass": false
}
```

**CONTRACT_TEST_PROOF** for scorer logic; **REAL_LLM_RUNTIME_PROOF** for Brown exec + competencies minimum.

---

## Appendix: W4 — No judge masking (MUST)

X1D rubric ports **must not** lower:

- factual support thresholds  
- graph phrase grounding requirements  
- citation / metric locality  
- bans on cross-fact causal merge  
- bans on credential/tool inventory dumps  
- bans on JD keyword stuffing without facts  

**Deliverable:** `docs/reports/apps_rg/graph_skills_x1d_rubric_port_diff.json` — before/after per lane family.

**Required non-claim string in receipt:**

> Rubric port did not relax groundedness, specificity, or citation thresholds.

Judge improvements may **add** requirements only, or keep equal stringency with clearer graph hooks.

---

## Appendix: W3 — Controlled graph v2 migration (MUST — no inventory sprawl)

Every **new or edited ACTIVE** skill row MUST document:

| Field | Required |
|-------|----------|
| `skill_id` | yes |
| `allowed_sections` | yes (subset of GENERATED_LANES) |
| `fact_id_links` | yes (non-empty) |
| `link_class` | `primary` or `secondary` per fact |
| `graph_hop_path` | yes (≥1 hop for ACTIVE) |
| `source_ledger_ref` | candidate fact id or migration note |
| `forbidden_phrases` | when applicable |
| Migration row in | `graph_v2_migration_receipt.json` |

**Forbidden**

- ACTIVE row with empty `fact_id_links`  
- Synthetic skill without candidate truth + section eligibility  
- Bulk auto-generated skills without human-review queue (use `PENDING_REVIEW` activation status)  

**Deliverables:** digest pin, sqlite rematerialize, **rollback path to v1** (D15).

---

## Appendix: W3 skill row template (reference)

```yaml
skill_id: skill_example
allowed_sections: [executive_summary, headline]
fact_id_links: [fact_engineering_platform_001]
link_class_by_fact:
  fact_engineering_platform_001: primary
graph_hop_path: [TRACK_GENAI_AGENTIC, pillar_agentic_ai_platforms, skill_example, fact_engineering_platform_001]
source_ledger_ref: fact_engineering_platform_001
forbidden_phrases: []
activation_status: ACTIVE_CONFIRMED
```

---

## Key references

| Doc | Use |
|-----|-----|
| [graph_skills_proof_common.py](apps_rg/runtime/validators/graph_skills_proof_common.py) | Fail-closed pool validator |
| [executive_summary_generation_quality_root_cause.md](docs/reports/apps_rg/executive_summary_generation_quality_root_cause.md) | Semantic failure modes |
| [proof_pool_c0_ssot_gap_review_plan.md](docs/reports/apps_rg/proof_pool_c0_ssot_gap_review_plan.md) | FEC sync |
| [graph-skills-hardening-f3a8c1](graph-skills-hardening-f3a8c1.md) | Authority predecessor |

---

## Notion

```bash
python tools/notion/plan_notion_sync_graph_skills_quality_enhancement_patch.py
```
