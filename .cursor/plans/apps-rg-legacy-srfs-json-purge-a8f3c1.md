# apps_rg legacy SRFS JSON + broad-ledger purge

**Status:** Completed (2026-05-22)  
**Slug:** `apps-rg-legacy-srfs-json-purge-a8f3c1`  
**User lock:** Never use SRFS JSON in prod — **delete** file-envelope model, not defer.  
**Closeout receipt:** [apps_rg_legacy_srfs_json_purge_closeout_receipt.md](../../docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_closeout_receipt.md)  
**Complements:** [apps-rg-x2-dead-gates-burndown-c4e8f2.md](apps-rg-x2-dead-gates-burndown-c4e8f2.md) (W1–W4 ✅), [SIMPLIFICATION_REDESIGN.md](../../docs/reports/apps_rg/SIMPLIFICATION_REDESIGN.md)

## What we are deleting vs renaming

| Delete entirely | Rename / keep (graph path) |
|-----------------|----------------------------|
| `selected_role_fact_set_active.json` materialization | `select_candidate_facts_for_role()` → `project_graph_for_target()` |
| `load_selected_role_fact_set(path)` runtime loaders | In-memory `SectionProofPool.selected_fact_plan` |
| `artifact_path_resolved` / `srfs_integration` envelope | `selection_scope` receipt fields only |
| `build_srfs_integration_envelope`, JSON write helpers | `graph_only_proof_pool_metadata` |
| `exec_summary_srfs_*` repair/binding/integration | `input_authority_prompt_block` |
| `broad_skills_ledger` as proof / `APPS_RG_BROAD_SKILLS_LEDGER_PATH` authority | Candidate fact **ledger** as graph substrate (not “broad skills JSON”) |
| `srfs_receipt_aggregator`, SRFS audit judge | `product_evidence_authority_receipt` only |

## Waves

| Wave | Scope | Status | Receipt |
|------|-------|--------|---------|
| D1 | Delete zero-caller modules: `executive_summary_srfs_binding`, `exec_summary_srfs_integration`, `exec_summary_srfs_judge_safe`; disable JSON capsule loader; drop judge_safe prefilter | ✅ DONE | [d1_receipt](../../docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_d1_receipt.md) |
| D2 | Remove `load_selected_role_fact_set`, `build_srfs_integration_envelope`, SRFS X2 check fns; strip `srfs_integration` from lanes | ✅ DONE | [d2_receipt](../../docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_d2_receipt.md) |
| D3 | Delete `srfs_receipt_aggregator`, SRFS audit tests; metadata field purge (`srfs_present`, `broad_skills_ledger_*`) | ✅ DONE | [d3_receipt](../../docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_d3_receipt.md) |
| D4 | Fact inventory: drop `write_selected_role_fact_set_artifacts` from hot path; fold `exec_summary_srfs_arsenal` into graph projection module | ✅ DONE | [d4_receipt](../../docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_d4_receipt.md) |
| D5 | Prompt/judge vocabulary purge; remove JSON file envelope from PA/capsule/token-budget required paths | ✅ DONE | [d5_receipt](../../docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_d5_receipt.md) |

### D1 — Orphan SRFS JSON runtime modules

- Deleted: `executive_summary_srfs_binding`, `exec_summary_srfs_integration`, `exec_summary_srfs_judge_safe` + judge_safe unit tests.
- Disabled: `try_judge_safe_prefilter` no-op; `load_srfs_and_build_capsule_from_path` fail-closed.

### D2 — Lane / X2 / judge envelope removal

- `load_selected_role_fact_set`, `build_srfs_integration_envelope`, `resolve_srfs_section_proof_bundle` → `RuntimeError` on product path.
- Judge packet always GRAPH_ONLY; lanes no longer thread `srfs_integration`.

### D3 — Aggregator + metadata purge

- Deleted: `srfs_receipt_aggregator`, `srfs_audit_advisory_judge`, `test_apps_rg_srfs_aggregator`.
- Reporting: `product_authority_reporting_fields` only; legacy SRFS-active branch removed.

### D4 — Fact inventory graph migration

- Deleted: `exec_summary_srfs_arsenal.py` (merged into `exec_summary_graph_projection_w4b.py`).
- Hot path: no JSON write unless `APPS_RG_OFFLINE_SRFS_JSON_WRITE=1` (offline `select_role_facts.py` only).

### D5 — Prompt/judge vocabulary purge

- PA: `GRAPH_PROOF_POOL_APPENDIX`; product hard rules on any `selected_fact_plan.facts`; no `srfs_integration` gate.
- Capsule: `proof_pool_metadata` + plan only; `graph_proof_pool_used=True`, `selected_role_fact_set_used=False`.
- Token budget: `graph_product_pool_active()`; no `artifact_path_resolved` detection.
- Judge render: “graph proof pool” labels (GRAPH_ONLY rubric SSOT from D2).

## Proof (each wave)

- Narrow pytest for touched lanes (recorded per wave receipt).
- Optional live (documented BLOCKED when `APPS_RG_L2_PROVIDER_MODE=stub_only`):

```text
python -m apps_rg --section executive_summary --provider qwen_vllm --allow-non-allow-exit-zero
python ops_scripts/apps_rg/run_live_section_authority_proof.py
```

## Deferred scope — closed

| Item | Resolution |
|------|------------|
| PA/capsule `srfs_integration` reads | **Closed D5** — graph metadata + plan; legacy dict ignored on capsule path |
| `format_srfs_role_adaptive_appendix` / JSON artifact line | **Closed D5** — `format_graph_proof_pool_appendix`; no file path in prompts |
| `srfs_receipt_aggregator`, inventory JSON on hot path | **Closed D3/D4** |
| `exec_summary_srfs_arsenal` | **Closed D4** — folded into w4b projection |
| Live qwen_vllm + `run_live_section_authority_proof` | **Operational follow-on** — BLOCKED in stub_only workspace; not a plan wave gate |
| Legacy `SRFS_*` marker strings in prompts | **Retained** for grep continuity; semantics are graph-only |

## Non-negotiable (held)

- Do not weaken X2 gates on graph path
- Do not edit `agentic_core`

## Notion

- Sync script: [plan_notion_sync_apps_rg_legacy_srfs_json_purge.py](../../tools/notion/plan_notion_sync_apps_rg_legacy_srfs_json_purge.py)
- Plans DB status: **Completed**
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
