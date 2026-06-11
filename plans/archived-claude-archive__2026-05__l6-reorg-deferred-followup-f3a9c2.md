---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\l6-reorg-deferred-followup-f3a9c2.md'
original_relative_path: '_archive\\2026-05\\l6-reorg-deferred-followup-f3a9c2.md'
source_sha256: 1fe917fdd177129c577d92119b6ff5197898c6a9fbf3889c5412d3af3f95fe94
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: l6-reorg-deferred-followup-f3a9c2
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: l6-repo-reorganization-mental-model-c4e8f2
parent_plan_status: Completed
---

# L6 Reorg — Deferred Scope Follow-Up

Execute deferred work captured during [l6-repo-reorganization-mental-model-c4e8f2](l6-repo-reorganization-mental-model-c4e8f2.md) (W0–W6 **Completed** 2026-05-25). Parent plan delivered `PATH_RENAME_CANONICAL`, fail-closed L6-TAG/L6-OBS, and documented gravity burndown (ADR-085). This plan owns **everything explicitly deferred** — passive-surface moves, L_OPS gravity targets, eval consolidation, and optional `_shared` extraction.

> **plan_id discipline**: `plan=l6-reorg-deferred-followup-f3a9c2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: M3
LAST_UPDATED: 2026-05-25
M3_RECEIPT: docs/reports/cursor/l6_adr086_m3_closeout_20260525.json
PARENT_PLAN: l6-repo-reorganization-mental-model-c4e8f2
PARENT_E2E_RECEIPT: docs/reports/cursor/l6_plan_e2e_closeout_20260525.json
DEFERRED_REGISTER: docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.md

---

## Context (SCQA)

- **Situation** — Parent L6 reorg is closed: canonical active root `agentic_core/L6_system_learning/`, passive `agentic_core/L6_observability/`, E2E 21/21 PASS, Notion Plans row **Completed**.
- **Complication** — W4 (passive drift) and W6 (gravity) intentionally deferred invasive moves and consolidation; ADR-085 documents **86** L6→lower import edges (`documented_over_threshold`). Eval overlap (24 vs 12 modules) and `promotion/` placement remain unresolved.
- **Question** — How do we burn down deferred L6 layout/gravity debt without reopening the parent plan or violating single-root / observer-law invariants?
- **Answer** — **Inventory-first (W0), then three optional burndown tracks** (passive relocations, L_OPS gravity moves, engines/eval ADR) — each wave Author-Gate gated; no stacked shims.

---

## Parent Plan Receipts (read-only authority)

| Wave | Receipt |
|------|---------|
| W0.2 | [l6_w0_architecture_decision_20260525.md](docs/reports/cursor/l6_w0_architecture_decision_20260525.md) |
| W5 + W1.5 | [l6_w5_post_rename_cert_20260525.json](docs/reports/cursor/l6_w5_post_rename_cert_20260525.json) |
| W6 | [l6_w6_gravity_receipt_20260525.json](docs/reports/cursor/l6_w6_gravity_receipt_20260525.json) |
| E2E closeout | [l6_plan_e2e_closeout_20260525.json](docs/reports/cursor/l6_plan_e2e_closeout_20260525.json) |
| Passive map | [l6_w4_passive_drift_20260525.md](docs/reports/cursor/l6_w4_passive_drift_20260525.md) |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Deferred register + ADG reconcile | ✅ DONE | reconcile script | [l6_followup_w0_receipt_20260525.md](docs/reports/cursor/l6_followup_w0_receipt_20260525.md) |
| W1 | Passive surface D1–D3 (optional moves) | ✅ DONE | — | ADR-087; promotion + runtime_trace |
| W2 | L_OPS gravity moves (eval utils) | ✅ DONE | arch gate | ops_scripts/reports canonical; 43 pairs documented |
| W3 | `_shared` Category A extraction spike | ✅ DONE | — | [l6_category_a_shared_spike_20260525.md](docs/reports/cursor/l6_category_a_shared_spike_20260525.md) |
| W4 | Engines map + eval consolidation ADR | ✅ DONE | — | engines/README.md; ADR-086 |
| M3 | ADR-086 B→`shadow_eval/legacy_parallel` + 90-day shims | ✅ DONE | 506+ pytest | [l6_adr086_m3_closeout_20260525.json](docs/reports/cursor/l6_adr086_m3_closeout_20260525.json) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Publish deferred scope register | ✅ DONE |
| W0.2 | Reconcile gravity inventory vs YAML | ✅ DONE |
| W1.1 | D1 `promotion/` relocation ADR + move | ✅ DONE |
| W1.2 | D3 OTEL root nest under `runtime_trace/` | ✅ DONE |
| W1.3 | D2 eval consolidation scoping ADR only | ✅ DONE |
| W2.1 | Move `async_eval_packet` / `governed_handoff` / `desk_d_governed_board` | ✅ DONE |
| W2.2 | ADG inventory refresh + YAML reconcile | ✅ DONE |
| W3.1 | Instrumentation decoupling spike (Category A) | ✅ DONE |
| W4.1 | `engines/` chapter map README under canonical tree | ✅ DONE |
| M3.1 | Relocate B eval cluster to `shadow_eval/legacy_parallel/` | ✅ DONE |

---

## Out Of Scope

- Reopening parent plan W3 chapter namespace wrappers (forbidden on `PATH_RENAME_CANONICAL`).
- Root `system_learning/` shim or dual canonical roots.
- Weakening L6-TAG / L6-OBS gates.
- `apps_rg` section content work (unless import paths break during moves).

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Register + inventory reconcile | ~4k | Parent receipts on disk | Not Started | Register published; inventory matches ADR-085 |
| W1 | W1.1–W1.3 | Passive drift deferred D1–D3 | ~12k | Author-Gate per physical move | Not Started | ADR per move OR explicit DEFERRED_SCOPE with P-Band |
| W2 | W2.1–W2.2 | L_OPS gravity burndown | ~10k | Fan-in preflight per file | Not Started | ≥9 edges removed OR updated exceptions + ADG proof |
| W3 | W3.1 | Category A `_shared` spike | ~8k | May BLOCK on instrumentation | Not Started | Spike report: feasible path or permanent exception |
| W4 | W4.1 | Engines / eval doctrine | ~6k | Doc-first for D2 | Not Started | `engines/README.md` + eval consolidation ADR draft |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|------------|--------|
| W0.1 | Deferred register | `docs/reports/cursor/l6_reorg_deferred_scope_register_*.md` | SSOT for chat + parent deferrals | ~2k | Not Started |
| W0.2 | Inventory reconcile | `l6_w6_gravity_edge_inventory_*.json`, `architectural_exceptions.yaml` | Drift between ADG and YAML | ~2k | Not Started |
| W1.1 | D1 promotion/ move | `L6_observability/promotion/`, importers | Active-adjacent 06.7 semantics | ~4k | Not Started |
| W1.2 | D3 OTEL nest | root OTEL modules → `runtime_trace/` | 8+ fan-in on ingest | ~4k | Not Started |
| W1.3 | D2 eval scope ADR | `utils/evaluation/*`, `shadow_eval/` | 24-module blast radius | ~4k | Not Started |
| W2.1 | L_OPS moves | 3 eval utility files | Eval pipeline coupling | ~6k | Not Started |
| W2.2 | ADG proof | `tools/generate/generate_full_adg.py` | Long runtime (~13+ min) | ~4k | Not Started |
| W3.1 | Category A spike | `determinism_types`, `path_constants`, etc. | Lifecycle instrumentation | ~8k | Not Started |
| W4.1 | Engines chapter map | `L6_system_learning/engines/README.md` | Flat engines bucket G4 | ~6k | Not Started |

---

## Gap Register (deferred from parent)

| ID | Source | Gap | Evidence | Target wave |
|----|--------|-----|----------|-------------|
| DS-1 | W4 D1 | `L6_observability/promotion/` not in mental model | [l6_w4_passive_drift_20260525.md](docs/reports/cursor/l6_w4_passive_drift_20260525.md) §4 | W1.1 |
| DS-2 | W4 D2 | Eval overlap: `shadow_eval/` (12) vs `utils/evaluation/` (24) | W4 §3 | W1.3 + W4.1 |
| DS-3 | W4 D3 | Root OTEL modules outside `runtime_trace/` | W4 §4 | W1.2 |
| DS-4 | W6 / ADR-085 | L_OPS move: `async_eval_packet`, `governed_handoff`, `desk_d_governed_board` | [l6_w6_gravity_receipt_20260525.md](docs/reports/cursor/l6_w6_gravity_receipt_20260525.md) | W2.1 |
| DS-5 | W6 / ADR-085 | Category A → `_shared/types/` blocked on instrumentation | ADR-085 §Context | W3.1 |
| DS-6 | Gap matrix G4 | Flat `engines/` cross-chapter bucket | [l6_reorg_gap_matrix_20260525.md](docs/reports/cursor/l6_reorg_gap_matrix_20260525.md) | W4.1 |
| DS-7 | 7c4e2a remainder | Gravity CI read of `architectural_exceptions.yaml` | Partial 7c4e2a W3/W4 | W2.2 (optional gate) |
| DS-8 | Parent | ADG regen post-marker fixes (`span_contracts`, `snapshot/`) | E2E closeout | W2.2 |

---

## Wave 0 — Deferred Register & Inventory

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Deliverables:**
- [l6_reorg_deferred_scope_register_20260525.md](docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.md) (SSOT)
- Reconcile row counts: inventory JSON ↔ YAML ↔ ADR-085

**Acceptance:**
```bash
python -c "import json; from pathlib import Path; r=json.loads(Path('docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.json').read_text()); assert r['deferred_items']"
```

---

## Wave 1 — Passive Surface (W4 Deferred)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Author-Gate:** `refactor_scope` per physical move (D1, D3). D2 is **ADR-only** in W1 — no file moves.

| Phase | Action | Preconditions |
|-------|--------|---------------|
| W1.1 | Relocate `promotion/` under active 06.7 path in `L6_system_learning/` | ADG fan-in + apps_lic importer proof |
| W1.2 | Nest OTEL root modules under `runtime_trace/` | Fan-in on `otel_runtime_ingest` |
| W1.3 | Publish eval consolidation ADR (no moves) | Overlap map from W4 |

---

## Wave 2 — Gravity Burndown (W6 Deferred)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Targets (ADR-085):**
- `agentic_core/L6_observability/utils/evaluation/async_eval_packet.py`
- `agentic_core/L6_observability/utils/evaluation/governed_handoff.py`
- `agentic_core/L6_observability/utils/engines/desk_d_governed_board.py`

**Success:** L6→L0..L5 distinct import edges **≤24** OR updated `architectural_exceptions.yaml` + ADR amendment with receipt.

```bash
python tools/_oneoff/l6_w6_gravity_inventory.py
python tools/_oneoff/l6_e2e_closeout_verify.py
```

---

## Wave 3 — Category A `_shared` Spike

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Blocked in 7c4e2a W1.P2:** `determinism_types`, `path_constants`, `human_decision_artifact_types`, `mutation_prohibition` are instrumented envelopes.

**Outcome:** Spike report only — `feasible` | `permanent_exception` | `requires_lifecycle_split`.

---

## Wave 4 — Engines & Eval Doctrine

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: E

**Deliverables:**
- `agentic_core/L6_system_learning/engines/README.md` — chapter map (06.3 / 06.6 / 06.7 / 06.8)
- ADR draft for D2 eval consolidation (implementation deferred until ADR accepted)

---

## Definition of Done

DoD-0: Deferred register published and linked from parent plan
- Evidence: [l6_reorg_deferred_scope_register_20260525.md](docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.md)
- Status: TODO

DoD-1: W0 inventory reconcile (JSON ↔ YAML ↔ ADR-085)
- Evidence: W0 receipt with row counts
- Status: TODO

DoD-2: Each executed move wave has Author-Gate + ADG fan-in proof
- Evidence: `DECISION_CAPTURED` + move receipt per wave
- Status: TODO

DoD-3: Gravity burndown measurable (≤24 edges OR documented amendment)
- Evidence: post-wave `l6_w6_gravity_inventory_*.json` + gate pass
- Status: TODO

DoD-4: L6 governance suite green after any code moves
- Evidence: `python tools/_oneoff/l6_e2e_closeout_verify.py` → PASS
- Status: TODO

DoD-5: Category A spike report filed (even if BLOCKED)
- Evidence: `docs/reports/cursor/l6_category_a_shared_spike_*.md`
- Status: TODO

---

## Verification vs Deferral

| Item | Execute in this plan | Defer further |
|------|---------------------|---------------|
| D1 promotion/ move | W1.1 (if ADR approves) | — |
| D2 eval file consolidation | ADR only W1.3; moves → new plan after ADR | Full merge |
| D3 OTEL nest | W1.2 | — |
| L_OPS eval utils | W2.1 | — |
| Category A `_shared` | W3 spike only | Extraction until instrumentation split |
| engines/ physical split | W4 README only | Directory restructure → post-ADR plan |

---

## References

- Parent (Completed): [l6-repo-reorganization-mental-model-c4e8f2.md](l6-repo-reorganization-mental-model-c4e8f2.md)
- ADR-085: [ADR-085-l6-observability-dependency-hygiene.md](docs/architecture/adr/ADR-085-l6-observability-dependency-hygiene.md)
- Gravity child: [l6-gravity-hybrid-7c4e2a.md](_archive/2026-05/l6-gravity-hybrid-7c4e2a.md)
- Exceptions SSOT: [architectural_exceptions.yaml](config/architectural_exceptions.yaml)
