---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-env-kill-switch-cleanup-f8e2a3.md'
original_relative_path: '_archive\\2026-05\\apps-rg-env-kill-switch-cleanup-f8e2a3.md'
source_sha256: 119720ddaea9d8cce07e71f76034f1fb322783b2a622dc9705e5137ba83cd1c2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-env-kill-switch-cleanup-f8e2a3
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: apps-rg-runtime-substitute-burndown-c4e8f1
---

# apps_rg Env Kill-Switch Cleanup (C0 Retrieval Authority)

Remove transitional env vars that weld **optional legacy spine merge** to **required product hybrid retrieval**, fix misleading receipts, and document the operator surface so release proof does not depend on debug levers.

> **plan_id discipline**: `apps-rg-env-kill-switch-cleanup-f8e2a3` · marker `plan=apps-rg-env-kill-switch-cleanup-f8e2a3`  
> **Parent**: [apps-rg-runtime-substitute-burndown-c4e8f1.md](apps-rg-runtime-substitute-burndown-c4e8f1.md) (W4.3 hybrid landed; this plan closes the env/receipt debt)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Complete
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-22
REVIEW_STATUS: APPROVED_WITH_HARDENINGS
CLOSEOUT_RECEIPT: docs/reports/apps_rg/apps_rg_env_kill_switch_cleanup_closeout_receipt.md
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF,IMPLEMENTATION_RECEIPT,LIVE_RUNTIME_PROOF
PROOF_CLASSIFICATION_NOT_CLAIMED: RELEASE_ELIGIBLE_PROOF
W4_ARTIFACT_DIR: artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522

---

## Context (SCQA)

- **Situation** — W4.3 wired `perform_product_hybrid_retrieval` in [`evidence_room.py`](../apps_rg/runtime/c0/evidence_room.py) keyed on `section_retrieval_profile.yaml` + `product_fail_closed_runtime()`. Product section runs default to ledger/graph authority (`c0_authority_mode=ledger_graph_primary`). **Closeout 2026-05-22:** W0–W4 complete; BM25 seeded; live hybrid receipts in `env_kill_switch_w4_validate_20260522`.
- **Complication** — Ownership-split left `APPS_RG_SPINE_CHROMA_ENRICH` as the only obvious “Chroma on” switch. Operators and receipts conflate it with hybrid read. Fallback receipt reason `spine_chroma_enrich_disabled` appears when **product hybrid did not run**, not when spine enrich is off. Inverted naming: `APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH=1` means bridge **on**. `APPS_RG_C0_EVIDENCE_ROOM=0` silently drops the entire C0 room including hybrid.
- **Question** — How do we make product retrieval authority **profile-driven and fail-closed** with **no transitional env** on the shipping path?
- **Answer** — Delete spine-enrich env/alias; decouple Chroma write policy from enrich; fix receipt vocabulary; rename or remove inverted kill switches; SSOT operator doc — keep dev/test envs explicit and forbidden on release proof.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Inventory lock + review gate | ~8K | User approves plan | ✅ DONE | Approved with hardenings |
| W1 | W1.1–W1.3 | Delete `APPS_RG_SPINE_CHROMA_ENRICH` + `merge_canonical_c0` | ~25K | No product caller needs spine merge | ✅ DONE | 64 pytest pass (scoped) |
| W2 | W2.1–W2.2 | Receipt + lifecycle decouple | ~18K | W4.3 hybrid stays in evidence room | ✅ DONE | Positive truth fields SSOT |
| W3 | W3.1–W3.2 | FEC mandatory + forbidden env fail-closed | ~15K | Remove kill switch on product | ✅ DONE | [apps_rg_runtime_proof.md](../docs/cursor/apps_rg_runtime_proof.md) updated |
| W4 | W4.1 | Live proof + closeout receipt | ~20K | BM25 + Brown & Brown exec-summary | ✅ DONE | [env_kill_switch_w4_validate_20260522](../artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522/) |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Review gate | plan, Notion | Scope sign-off | ~8K | ✅ DONE |
| W1.1 | Remove env resolver | `c0_section_authority.py`, `c05_fec_packet.py` | Spine merge only behind explicit API param (dev) or delete branch | ~10K | ✅ DONE |
| W1.2 | Evidence room write policy | `evidence_room.py`, `c0_section_authority.py` | `section_chroma_write_in_c02` must not key off enrich | ~8K | ✅ DONE |
| W1.3 | Contract + doc purge | `test_apps_rg_c0_ownership_split.py`, reports, `apps_rg_runtime_proof.md` | References to SPINE_CHROMA_ENRICH | ~7K | ✅ DONE |
| W2.1 | Receipt vocabulary | `c02_chroma_lifecycle.py`, `c05_fec_packet.py` | Misleading `spine_chroma_enrich_disabled` | ~10K | ✅ DONE |
| W2.2 | Hybrid required assertions | `c02_product_hybrid_retrieval.py`, product tests | Fail-closed when profile requires hybrid | ~8K | ✅ DONE |
| W3.1 | FEC bridge kill switch | `section_fec_bridge.py`, `executive_summary_pa.py` | Inverted default; product must not use raw proof_pool | ~8K | ✅ DONE |
| W3.2 | Operator SSOT table | `docs/cursor/apps_rg_runtime_proof.md` | Tier 1–5 env audit from review | ~7K | ✅ DONE |
| W4.1 | Live runtime proof | CLI exec-summary, artifacts | BM25 seeded; hybrid receipts captured | ~20K | ✅ DONE |

---

## Env Audit — Delete / Fix / Keep (review baseline)

### Tier 1 — Delete or replace (product path)

| Env / alias | Action | Replacement |
|-------------|--------|-------------|
| `APPS_RG_SPINE_CHROMA_ENRICH` | **Delete** | `section_retrieval_profile.yaml` + `perform_product_hybrid_retrieval` |
| `merge_canonical_c0` (param/receipt) | **Delete** | Same as above |
| `APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH` | **Forbidden on product** (`=0` raises); harness bypass only | `product_fec_bridge_mandatory()` |
| Receipt `spine_chroma_enrich_disabled` | **Replace** | `product_hybrid_not_run` / `product_hybrid_failed` / lane-specific |

### Tier 2 — Never on release proof (document only)

| Env | Risk |
|-----|------|
| `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` | Disables entire fail-closed stack |
| `APPS_RG_C0_EVIDENCE_ROOM=0` | **Runtime error on product** (not doc-only) |
| `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1` | Same-run write; not product PASS |
| `APPS_RG_L2_FORCE_STUB` / `APPS_RG_L2_PROVIDER_MODE=stub_only` | Non-live L2 |

### Tier 3 — Keep (legitimate)

`CHROMA_PERSIST_DIR`, `EMBEDDING_*`, `APPS_RG_EMBEDDING_MODEL_PATH`, `VLLM_BASE_URL`, index maintenance pair (`APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH` + `APPS_RG_INDEX_MAINTENANCE_ENTRYPOINT`) for **pre-run only**.

---

## Target architecture (post-cleanup)

```text
python -m apps_rg --section <lane>
  → bootstrap_apps_rg_embedding_env (CHROMA + BGE path)
  → wire_section_fec_bridge_for_lane
       → run_section_c0_evidence_room (default ON, no env)
            → C0.2 ledger/graph atoms [authority]
            → perform_product_hybrid_retrieval [profile, fail-closed]
            → build_c05_final_evidence_contract [no spine env]
  → section PA consumes FEC bridge only
```

**Explicit non-goals:** Re-enable default `c0_retrieve_apps_rg` full-spine merge on product paths. Optional additive spine hits only if a future **non-env** dev API is justified.

---

## Out Of Scope

- BM25 sparse index seeding (stays on parent substitute burndown live-proof blocker)
- `agentic_core` C0 builder changes
- Broad deletion of all `APPS_RG_*` test harness envs
- Notion backlog row creation (optional follow-up)

---

## Wave 0 — Review gate

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: REVIEW

**Phases**:
- **W0.1** — User reviews plan on disk + Notion; approves W1 start | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Plan file at `.cursor/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md`
- Notion Plans row exists with `Status=Not Started` (or `In Progress` after approval)

---

## Wave 1 — Delete spine-enrich env

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: A

**Authorization**: REQUIRED — deletion strategy + receipt field removal (`merge_canonical_c0`, ownership-split tests).

**Phases**:
- **W1.1** — Remove `resolve_spine_chroma_enrich` env branch; delete or gate `c0_retrieve_apps_rg` enrich block in `c05_fec_packet.py` | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — `section_chroma_write_in_c02()` uses `product_section_skip_lane_upsert()` only | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Update `test_apps_rg_c0_ownership_split.py`, purge docs mentioning operator workaround `APPS_RG_SPINE_CHROMA_ENRICH=1` | ~7K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `rg APPS_RG_SPINE_CHROMA_ENRICH` → zero product-path reads
- `pytest tests/_apps_contract/test_apps_rg_c0_ownership_split.py -q` pass

---

## Wave 2 — Receipt vocabulary + hybrid truth

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — `build_c02_chroma_query_receipt`: distinct reasons for hybrid skip vs spine (no shared “disabled” string) | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Assert `product_hybrid` + `attempted` on product fail-closed lanes in unit tests | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Product exec-summary artifact `c02_vector_query.json` uses `product_hybrid_bounded_section_retrieval` or explicit failure reason when hybrid required

---

## Wave 3 — Foot-gun env hardening + operator doc

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: REQUIRED — `APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH` rename vs remove (script blast radius).

**Phases**:
- **W3.1** — Product path: FEC bridge mandatory; env opt-out only under `APPS_RG_TEST_HARNESS` | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Extend [apps_rg_runtime_proof.md](../docs/cursor/apps_rg_runtime_proof.md) with Tier 1–5 table + forbidden set for release proof | ~7K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Setting `APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH=0` cannot occur on default `python -m apps_rg` product run without explicit test harness

---

## Wave 4 — Live proof (depends on parent BM25)

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Brown & Brown `executive_summary` strict product run; capture `c02_vector_query`, `c05` receipt, `c0_evidence_room_receipt` | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Commands** (from [apps_rg_runtime_proof.md](../docs/cursor/apps_rg_runtime_proof.md)):

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m apps_rg --section executive_summary ^
  --target-company "Brown & Brown" ^
  --target-role "SVP IT Strategy & Innovation" ^
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt ^
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md ^
  --artifact-dir artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522
```

**Acceptance** (met — see [closeout receipt](../docs/reports/apps_rg/apps_rg_env_kill_switch_cleanup_closeout_receipt.md)):
- `product_fail_closed=true`, `c0_authority_mode=ledger_graph_primary`
- `product_hybrid_required=true`, `product_hybrid_attempted=true`, `bm25_available=true`
- Lanes `dense`/`sparse`/`metadata` = `completed`; `c0_retrieval_mode=ledger_plus_hybrid_retrieval`
- **No** `spine_chroma_enrich_disabled` in run bundle
- Run exit 1 / `X3_BLOCK` on product quality — **out of scope** for this plan; not `RELEASE_ELIGIBLE`

---

## Gap Register

**GAP-1: Parent plan BM25 blocker** — **RESOLVED 2026-05-22**
- `data/cache/sparse/fact_vectors.db` seeded; W4 live run hybrid receipts PASS.

**GAP-2: Optional spine enrichment branch**
- If any stress tool still needs additive non-proof hits, keep **explicit function param** (default false), not env.
- Impact: W1.1 Author-Gate if delete vs dev-only param.

**GAP-3: Historical artifacts**
- Old runs show `spine_chroma_enrich_disabled` in `c02_vector_query.json`; do not reinterpret as current code truth.

---

## Definition of Done

| DoD | Outcome | Evidence | Status |
|-----|---------|----------|--------|
| DoD-1 | `APPS_RG_SPINE_CHROMA_ENRICH` removed from runtime | Contract tests + no reads in `apps_rg/` | DONE |
| DoD-2 | Product hybrid driven by profile only | 64 pytest pass (scoped bundle) | DONE |
| DoD-3 | Receipts truthful | `test_apps_rg_env_kill_switch_cleanup.py` | DONE |
| DoD-4 | Operator doc updated | [apps_rg_runtime_proof.md](../docs/cursor/apps_rg_runtime_proof.md) forbidden env table | DONE |
| DoD-5 | Live proof | [env_kill_switch_w4_validate_20260522/c02_vector_query.json](../artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522/c02_vector_query.json) | DONE |

### Verification vs Deferral

| Item | In charter | Deferred |
|------|------------|----------|
| Delete spine enrich env | Yes | No |
| Fix receipts | Yes | No |
| FEC kill-switch rename | Yes | No |
| BM25 index seed | No | Parent plan |
| Full integrated résumé | No | Parent plan |

---

## Locked review decisions (2026-05-22)

1. **FEC:** Remove product kill switch — no rename. `product_fec_bridge_mandatory()`; bypass only with `APPS_RG_TEST_HARNESS=1`.
2. **C0 room:** `APPS_RG_C0_EVIDENCE_ROOM=0` → `ProductRuntimeEnvForbiddenError` on product lanes.
3. **Receipts:** Positive truth fields required (`retrieval_profile_ref`, `product_hybrid_*`, `dense_attempted`, `sparse_attempted`, `bm25_available`, `failure_reason`, `proof_classification`). Never emit `spine_chroma_enrich_disabled`.
4. **Proof:** W1–W3 = CONTRACT_TEST_PROOF; W4 = LIVE_RUNTIME_PROOF on C0 hybrid. RELEASE_ELIGIBLE not claimed.

---

## Marker Quick Reference

```
PLAN_CREATED: slug=apps-rg-env-kill-switch-cleanup-f8e2a3 path=.cursor/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md status=Not Started
WAVE_COMPLETE: plan=apps-rg-env-kill-switch-cleanup-f8e2a3 wave=4 note="W4 live hybrid PASS; 64 pytest; closeout receipt"
PLAN_COMPLETE: plan=apps-rg-env-kill-switch-cleanup-f8e2a3 note="W0-W4 complete; LIVE_RUNTIME_PROOF; not RELEASE_ELIGIBLE"
```
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
