---
plan_id: l2-rationalization-waves-c8e4f1
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# L2 + apps_rg rationalization (12 waves)

Rationalize agentic_core L2 validators/executors/healers and apps_rg section runtime: inventory SSOT, model env boundaries, same-authority healing, quarantine non-product paths, gated archive. **Evidence reports:** `docs/reports/agent_inventory/`.

> **plan_id:** `l2-rationalization-waves-c8e4f1` → markers use `plan=l2-rationalization-waves-c8e4f1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W11_CLOSED
LAST_COMPLETED_WAVE: W11_CLOSEOUT
LAST_UPDATED: 2026-05-19
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-24
PARENT_SPINE_PLAN: apps-rg-spine-only-unification-d8f4a2

---

## Context (SCQA)

- **Situation** — Early-learning L2.2/L2.3/L2.4 components, shared spine model envs, and apps_rg section runtime coexist; inventory and ownership docs exist under `docs/reports/agent_inventory/`.
- **Complication** — Label drift (L2.x vs E2/E3/E4), model env bleed risk, stub signal-quality paths, and non-product smoke/demo entries can be mistaken for live proof.
- **Question** — How do we safely rationalize L2 spine vs apps_rg product paths without breaking canonical section generation or Exit/UWG boundaries?
- **Answer** — Twelve bounded waves: document ownership (W0–W1), guard env boundaries (W2–W4), enforce healing and boundaries (W5–W10), gated archive only after fan-in zero (W11).

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Inventory SSOT + ADG | ✅ DONE | orchestration 8 pass | docs/reports/agent_inventory |
| W1 | L2.2/2.3/2.4 ↔ E1–E5 docs | ✅ DONE | orchestration 8 pass | 3 ownership docs + assessment |
| W2 | Generation model env guards | ✅ DONE | [w2_w5_boundary_and_healing.md](../../docs/reports/agent_inventory/w2_w5_boundary_and_healing.md) | 35 boundary tests pass |
| W3 | Judge env isolation | ✅ DONE | same | APPS_RG primary; GOOGLE_AI_PRO_MODEL limited fallback |
| W4 | Signal-quality SSOT / quarantine | ✅ DONE | same | QUARANTINE stubs; core SSOT unchanged |
| W5 | Same-authority healing audit | ✅ DONE | same | repair_decision + routing_gates tests |
| W6 | Retire apps_rg_l2_binding | ✅ DONE | [w6_w9_quarantine_and_e2_boundary.md](../../docs/reports/agent_inventory/w6_w9_quarantine_and_e2_boundary.md) | RETIRE_CANDIDATE; tests/CI still import shim |
| W7 | Quarantine non-product paths | ✅ DONE | same | Registry + contract tests |
| W8 | Dispatch vs section consolidation | ✅ DONE | same | Canonical hygiene static proof |
| W9 | L2 E2 consolidation | ✅ DONE | same | KEEP_CORE pipeline; orchestrator QUARANTINE |
| W10 | Exit/UWG/L4/L6 no-bypass tests | ✅ DONE | [w10_exit_uwg_l4_l6_no_bypass.md](../../docs/reports/agent_inventory/w10_exit_uwg_l4_l6_no_bypass.md) | 24 boundary tests pass |
| W11 | Gated archive/delete | ✅ CLOSED | [w11_closeout_and_next_plan_handoff.md](../../docs/reports/agent_inventory/w11_closeout_and_next_plan_handoff.md) | Shim archived only; DELETE_READY=0; successor: apps-rg-legacy-dependency-burndown |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Regenerate inventory JSON | ✅ DONE |
| W1.1 | l2_ownership_model.md | ✅ DONE |
| W1.2 | apps_rg + env boundary docs | ✅ DONE |
| W2.1 | Generation env contract tests | 🔲 TODO |
| W3.1 | Judge profile + receipt audit | 🔲 TODO |

---

## Wave summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Freeze inventory SSOT | ~50K | ADG snapshot 05172026_0651 | ✅ DONE | compileall 0; JSON refreshed |
| W1 | W1.1–W1.2 | E-phase ownership docs | ~80K | No runtime edits | ✅ DONE | 3 boundary docs + orchestration tests pass |
| W2 | W2.1 | apps_rg generation env guards | ~120K | W1 docs accepted | ✅ DONE | [w2_w5_boundary_and_healing.md](../../docs/reports/agent_inventory/w2_w5_boundary_and_healing.md) |
| W3 | W3.1 | APPS_RG_* judge isolation | ~100K | W2 green | ✅ DONE | same |
| W4 | W4.1 | Signal stub decision | ~90K | Independent of W2 | ✅ DONE | QUARANTINE stubs |
| W5 | W5.1 | Healing same-authority tests | ~150K | W1 mapping stable | ✅ DONE | same |
| W6 | W6.1 | Retire l2_binding shim | ~80K | W2–W3 green | ✅ DONE | [w6_w9_quarantine_and_e2_boundary.md](../../docs/reports/agent_inventory/w6_w9_quarantine_and_e2_boundary.md) |
| W7 | W7.1 | proof_eligible manifest | ~70K | W0 inventory | ✅ DONE | same |
| W8 | W8.1 | Section SSOT per lane | ~200K | W7 green | ✅ DONE | same |
| W9 | W9.1 | Single E2 entry doc | ~120K | W5 green | ✅ DONE | same |
| W10 | W10.1 | Boundary contract tests | ~100K | W5 green | ✅ DONE | [w10_exit_uwg_l4_l6_no_bypass.md](../../docs/reports/agent_inventory/w10_exit_uwg_l4_l6_no_bypass.md) |
| W11 | W11.1 | Archive after quarantine | ~60K | W6–W10 green | ✅ CLOSED | Shim archived; no further archive; see burndown plan |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Inventory refresh | docs/reports/agent_inventory/* | Stale grep counts | 50K | ✅ DONE |
| W1.1 | L2 ownership model | l2_ownership_model.md | L2.x vs E2 drift | 40K | ✅ DONE |
| W1.2 | apps_rg + env boundaries | apps_rg_canonical_runtime_boundary.md, env_ownership_boundary.md | Product vs stub proof | 40K | ✅ DONE |
| W2.1 | Generation guards | apps_rg/runtime/providers, tests/_apps_contract | GOOGLE_AI_* bleed | 120K | 🔲 TODO |
| W3.1 | Judge isolation | apps_rg/runtime/judges/* | Fallback to spine vars | 100K | 🔲 TODO |
| W4.1 | Signal SSOT | apps_shared stubs, signal_quality_config | Fake quality scores | 90K | 🔲 TODO |
| W5.1 | Healing audit | L2_execution/healers/* | Over-healing authority gaps | 150K | 🔲 TODO |
| W6.1 | Shim retirement | apps_rg_l2_binding.py | Test import paths | 80K | 🔲 TODO |
| W7.1 | Quarantine manifest | dry_run, Rg*, deprecated dispatch | False PASS claims | 70K | 🔲 TODO |
| W8.1 | Lane consolidation | dispatch/* vs sections/* | Receipt drift | 200K | 🔲 TODO |
| W9.1 | E2 consolidation | enforcement/, validation_orchestrator | Duplicate gates | 120K | 🔲 TODO |
| W10.1 | Boundary tests | tests/_apps_contract, UWG | Durable write bypass | 100K | ✅ DONE |
| W11.1 | Gated archive | archives/, migration receipt | Premature delete | 60K | 🔲 TODO |

---

## Out Of Scope

- Live full `python -m apps_rg` proof runs (unless explicitly scoped per wave)
- Weakening X2/X3 gates or judge rubrics
- Deletion or deprecation markers before W11 gates
- Generic agentic_core feature work unrelated to rationalization

---

## Wave 0 — Inventory SSOT

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Acceptance:** Assessment JSON + compileall 0. See [l2_rationalization_repo_assessment.json](../docs/reports/agent_inventory/l2_rationalization_repo_assessment.json).

---

## Wave 1 — Ownership documentation

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Artifacts:**
- [l2_ownership_model.md](../docs/reports/agent_inventory/l2_ownership_model.md)
- [apps_rg_canonical_runtime_boundary.md](../docs/reports/agent_inventory/apps_rg_canonical_runtime_boundary.md)
- [env_ownership_boundary.md](../docs/reports/agent_inventory/env_ownership_boundary.md)

**Acceptance:** Zero runtime behavior change; `pytest tests/unit/agentic_core/L2_execution/orchestration/ -q` → 8 passed.

---

## Wave 2 — Generation model env guards

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases:**
- **W2.1** — Contract tests: section lanes must not use OPENAI_MODEL/GOOGLE_AI_* for generation | ~120K | PHASE_STATUS: TODO

**Acceptance:**
- New contract test in `tests/_apps_contract/`
- `pytest tests/unit/apps_rg/test_section_judge_policy.py -q` still green

**Combine with W3** per wave plan.

---

## Wave 3 — Judge env isolation

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Acceptance:** APPS_RG_*_JUDGE_MODEL_* sole source when set; receipts show `resolved_model_source`.

---

## Waves 4–11 (summary)

Detail in [l2_rationalization_full_wave_plan.md](../docs/reports/agent_inventory/l2_rationalization_full_wave_plan.md).

| Wave | One-line objective |
|------|-------------------|
| W4 | Signal-quality SSOT wire or quarantine apps_shared stubs |
| W5 | Same-authority healing negative tests |
| W6 | Retire `agentic_core/L2_execution/apps_rg_l2_binding.py` |
| W7 | proof_eligible manifest; quarantine dry_run/Rg*/stub |
| W8 | Single SSOT runner per section lane |
| W9 | Document single E2 entry; dedupe enforcement |
| W10 | Exit/UWG/L4/L6 no-bypass contract tests |
| W11 | Archive only after fan-in zero + 30d quarantine |

---

## Gap Register

**GAP-1: validation_orchestrator vs l2_phase_pipeline E2**
- Duplicate validation surfaces — defer to W9 NEEDS_DECISION

**GAP-2: apps_shared signal stubs**
- subatomic_hop_util / engine_type_types — defer to W4 Author-Gate

**GAP-3: legacy_full_resume rollback**
- Keep vs sunset — NEEDS_DECISION before W7 manifest

---

## Definition of Done

DoD-1: All 12 waves complete with PASS receipts per wave acceptance
- Evidence: Wave table all ✅ DONE; inventory JSON `waves_completed`
- Status: TODO

DoD-2: apps_rg canonical path documented and guarded
- Evidence: `proof_eligible` manifest + contract tests; [apps_rg_canonical_runtime_boundary.md](../docs/reports/agent_inventory/apps_rg_canonical_runtime_boundary.md)
- Status: TODO

DoD-3: Model env boundaries enforced by tests
- Evidence: W2/W3 pytest green; no generation path imports GEMINI_FLASH_MODEL_ID
- Status: TODO

DoD-4: Same-authority healing runtime-proven
- Evidence: W5 negative tests + OTel spans
- Status: TODO

DoD-5: No premature deletion
- Evidence: W11 migration receipt; ADG fan-in=0 for retired paths
- Status: TODO

DoD-6: Inventory regen smoke
- Evidence: `python docs/reports/agent_inventory/_generate_l2_inventory.py` exit 0
- Status: DONE (W0)

---

## Marker Quick Reference

```
WAVE_START: plan=l2-rationalization-waves-c8e4f1 wave=<N>
WAVE_COMPLETE: plan=l2-rationalization-waves-c8e4f1 wave=<N> note="+N tests, N files, scope=<summary>"
```

Completed (emit retroactively if hooks missed):
```
WAVE_COMPLETE: plan=l2-rationalization-waves-c8e4f1 wave=0 note="+0 tests, 8 files, scope=inventory"
WAVE_COMPLETE: plan=l2-rationalization-waves-c8e4f1 wave=1 note="+8 tests, 5 files, scope=ownership-docs"
```

---

## W11 receipt (2026-05-19)

- **SHIM-ARCHIVE:** [w11_shim_archive_receipt.md](../docs/reports/agent_inventory/w11_shim_archive_receipt.md) — archived 20260519
- **SHIM-ARCHIVE-PREP:** [w11_shim_archive_prep_receipt.md](../docs/reports/agent_inventory/w11_shim_archive_prep_receipt.md)
- **M2.2+M3+M4 prep:** [w11_remaining_candidates_prep_receipt.md](../docs/reports/agent_inventory/w11_remaining_candidates_prep_receipt.md)
- **M3A+M4A:** [w11_m3_m4_facade_dispatch_migration.md](../docs/reports/agent_inventory/w11_m3_m4_facade_dispatch_migration.md) — facade canonical export; PA helpers → sections
- **M3B+M4B+M4C+M4D:** [w11_fast_blocker_burn_m3b_m4d.md](../docs/reports/agent_inventory/w11_fast_blocker_burn_m3b_m4d.md)
- **M4C-FIX + closeout:** [w11_m4c_competencies_contract_fix.md](../docs/reports/agent_inventory/w11_m4c_competencies_contract_fix.md), [w11_closeout_and_next_plan_handoff.md](../docs/reports/agent_inventory/w11_closeout_and_next_plan_handoff.md)
- **DELETE_READY:** 0 — **W11 closed**; do not expand archive under this plan
- **Successor:** [apps-rg-legacy-dependency-burndown-b7e4a2.md](apps-rg-legacy-dependency-burndown-b7e4a2.md)
- **Matrix:** [w11_candidate_fanin_matrix.json](../docs/reports/agent_inventory/w11_candidate_fanin_matrix.json) (snapshot `05192026_0920`)
- **M2.2:** `validation_orchestrator` → `ARCHIVE_CANDIDATE_AFTER_30D` (ADG 0; CI baselines blocker)
- **M3:** `Rg*` → `QUARANTINE_30D` (no product import; facades/tests block archive)
- **M4:** dispatch PA → `QUARANTINE_30D`; `dry_run/` → `QUARANTINE_30D`; `orchestrate_full_resume` → `KEEP_TEST_SUPPORT_ONLY`

---

## ADG_GRAPH_LAYER_EVIDENCE

Rationalization scope is driven by latest `artifacts/adg/adg_indexed_*.sqlite` graph-layer primitives (constitutional §22):

| Primitive | Use in this plan |
|-----------|------------------|
| `mv_hotspot_centrality` | Rank L2/L5 fan-in hotspots (W0 inventory, W11 gate) |
| `mv_blast_radius` | Blast-radius for validator/executor moves |
| `mv_chokepoints` | Identify orchestration chokepoints before archive |
| `flows_to` / `reads_from` / `writes_to` | Execution vs read vs durable-write surfaces |
| `v_p0_high_fanin` | P0 seam selection for spine rationalization |

Evidence reports under `docs/reports/agent_inventory/` were produced with ADG MCP (`adg_edge_fanin`, `adg_nodes_by_file`) — not grep-for-deps.

## ADG_HOTSPOT_REPORT

| Rank | Symbol / path | Archetype | ADG Surface | Notes |
|------|---------------|-----------|-------------|-------|
| 1 | `agentic_core/L2_execution/reasoning/execution_gateway.py` | ORCHESTRATOR | Execution Surface | Primary L2 dispatch hub |
| 2 | `agentic_core/L2_execution/reasoning/validation_orchestrator.py` | ORCHESTRATOR | Execution Surface | W11 fan-in gate |
| 3 | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | CENTRAL_DEPENDENCY | State Surface | Parent plan cross-ref; ratchet tracked separately |
| 4 | `apps_rg/runtime/section_runtime/*` | STATE_NODE | Write Surface | Product path — apps-owned, not core leakage |

---

## Related reports (filesystem SSOT for evidence)

| Report | Path |
|--------|------|
| W11 gated archive/delete | [w11_gated_archive_delete_plan.md](../docs/reports/agent_inventory/w11_gated_archive_delete_plan.md) |
| Repo assessment | [l2_rationalization_repo_assessment.md](../docs/reports/agent_inventory/l2_rationalization_repo_assessment.md) |
| Wave plan (detail) | [l2_rationalization_full_wave_plan.md](../docs/reports/agent_inventory/l2_rationalization_full_wave_plan.md) |
| Model env | [model_env_ownership_plan.md](../docs/reports/agent_inventory/model_env_ownership_plan.md) |
| Quarantine | [deprecation_quarantine_plan.md](../docs/reports/agent_inventory/deprecation_quarantine_plan.md) |
| Canonical proof | [canonical_path_proof_plan.md](../docs/reports/agent_inventory/canonical_path_proof_plan.md) |
