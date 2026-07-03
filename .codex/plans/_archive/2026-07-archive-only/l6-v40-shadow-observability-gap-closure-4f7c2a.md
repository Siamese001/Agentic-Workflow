---
plan_id: l6-v40-shadow-observability-gap-closure-4f7c2a
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/l6_v40_core_addition_author_gate_receipt.json"
dod_exempt: false
---

# L6 v40 Shadow Observability Gap Closure

Close the L6 shadow observability gaps against v40 for `agentic_core`, `apps_rg`, and `apps_eval` while preserving current-run artifact immutability, UWG-only durable writes, and future-run-only learning activation.

> **plan_id discipline:** `plan_id` = filename stem `l6-v40-shadow-observability-gap-closure-4f7c2a`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Complete
CURRENT_WAVE: W6
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-06-13

PLAN_CREATED: slug=l6-v40-shadow-observability-gap-closure-4f7c2a path=.codex/plans/l6-v40-shadow-observability-gap-closure-4f7c2a.md status=In Progress

---

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|---|---|---|
| W0 | Branch isolation, plan registration, evidence pull | Complete |
| W1 | Core v40 adapter, L5/Exit readiness, G28/G29 contracts and spans | Complete |
| W2 | Span artifact export and synthetic proof update | Complete |
| W3 | apps_rg v40 runner, env flag wiring, handoff/learning refs | Complete |
| W4 | apps_eval bridge, driver output integration, README boundary | Complete |
| W5 | Legacy writeback proposer quarantine | Complete |
| W6 | Unit/E2E tests and acceptance commands | Complete |

### Scope Controls

| Control | Decision |
|---|---|
| Current-run artifact mutation | Forbidden |
| L6 current-run X3 emission or mutation | Forbidden |
| Direct L4 write from L6 | Forbidden |
| UNKNOWN treated as PASS | Forbidden |
| Durable write path | UWG only |
| Learned-change activation | Future-run only |
| Public app behavior | Preserve; add observability artifacts and tests |

---

## Context (SCQA)

- **Situation** - Existing L6 shadow evaluation has core 6A/observer/6B/6C pipeline functions and in-memory spans. `apps_rg` has post-Exit RuntimeExhaust handoff artifacts, and `apps_eval` emits scorecard/proof ingredients.
- **Complication** - v40 requires a canonical runtime/app exhaust adapter, durable G28/G29 receipts, span artifact exports, app bridge/runners, and a stricter writeback boundary. The current ingest path substitutes `MISSING_CERT_REF_SENTINEL` for absent L5 refs, which must not manufacture readiness.
- **Question** - How do we close the v40 observability gaps without letting L6 mutate current-run state or bypass UWG?
- **Answer** - Add a canonical v40 adapter and receipts at the L6 observation boundary, run app bridges only after Exit/runtime exhaust, export evidence artifacts, and quarantine legacy promotion creation unless completed eval, RCA, and gauntlet evidence is present.

---

## Wave 0 - Setup and Evidence

**Goal:** isolate implementation from unrelated workspace changes and confirm current surfaces.

**Tasks**
- Create clean worktree on `codex/l6-v40-shadow-observability-gap-closure`.
- Register this plan in Notion Plans.
- Use memory, GitKraken, ADG fallback, and exact file reads for evidence.

**DoD**
- Clean worktree available.
- Plan file exists and is registered.
- No implementation files edited before approval.

## Wave 1 - Core L6 v40 Adapter and Gates

**Goal:** create a canonical v40 raw exhaust adapter and harden readiness.

**Tasks**
- Add `agentic_core/L6_observability/shadow_eval/adapters/runtime_exhaust_v40.py`.
- Map core runtime bundles and generic section artifacts into `run_6a`-consumable raw exhaust; keep apps-specific file maps in `apps_rg`.
- Add explicit G28/G29 receipt shape and ensure UNKNOWN never passes.
- Require trace root, Exit disposition, policy hash, replay key, route contract, L5 certification, lineage/normalized records, and sealed artifacts for G28 PASS.
- Ensure missing/sentinel L5 prevents `READY_FOR_6B`; missing Exit remains `NON_EVALUABLE_PACKET`.

**DoD**
- Adapter validation rejects missing Exit and missing/sentinel L5 readiness.
- Readiness receipts expose G28/G29 refs or sidecar refs without breaking existing callers.

## Wave 2 - Span Export and Proof

**Goal:** make L6 span coverage durable.

**Tasks**
- Add `span_export.py` for serializing recorder spans, building export bundles, and writing JSON/JSONL span artifacts.
- Insert `l6.g28.audit_completeness` and `l6.g29.learning_firewall` after observer spans and before readiness.
- Update synthetic proof to export span artifacts.

**DoD**
- Coverage receipt asserts canonical order, no feedback edge, required attrs, G28/G29 status, and no write/mutation attempts.

## Wave 3 - apps_rg v40 Runner and Receipts

**Goal:** run v40 L6 observability after Exit on section lanes.

**Tasks**
- Add `apps_rg/runtime/spine/l6_shadow_eval_runner.py`.
- Wire optional execution through `APPS_RG_L6_V40_SHADOW_EVAL=1` at the post-Exit/runtime-exhaust boundary.
- When the env flag is enabled, write v40 exhaust/readiness/observer/G28/G29/span receipts.
- Keep 6B/6C outside the section-lane opt-in runner; readiness artifacts prove whether downstream eval is permitted.
- Add v40 refs to L6 handoff, learning, and section runtime exhaust receipts.

**DoD**
- Runner never modifies X2, X3, Exit, X1D, ledger, or L2 artifacts.
- Default behavior remains off unless the env flag is set.

## Wave 4 - apps_eval Bridge

**Goal:** let apps_eval emit and consume v40 L6 proof artifacts without owning release authority.

**Tasks**
- Add `apps_eval/l6_shadow_bridge.py`.
- Emit a bridge for CLI completed eval records, and add driver bridge artifacts for scenario matrix, app scorecards, trace/replay/gate coverage, and ADG delta summary.
- Run 6A, observer, readiness, G28/G29, and span export for completed eval records.
- Update proof and validator drivers plus README.

**DoD**
- apps_eval emits the requested v40 L6 artifacts and states it is a proof harness, not release or write authority.

## Wave 5 - Legacy Writeback Quarantine

**Goal:** prevent normal-mode promotion requests from raw RuntimeExhaustBundle plus learning signals alone.

**Tasks**
- Mark `L6WritebackProposer` as legacy or default-off.
- Require completed eval, RCA, and audit manifest proof refs for any promotion request in normal mode, or return `[]` unless an explicit legacy flag is enabled.
- Extend tests for inert/UWG-only behavior.

**DoD**
- No normal-mode promotion request can be created without completed eval, RCA, and audit manifest evidence refs.

## Wave 6 - Tests and Verification

**Goal:** prove the requested acceptance criteria.

**Tasks**
- Add requested unit tests under `tests/l6_observability`, `tests/apps_rg`, and `tests/apps_eval`.
- Add `tests/e2e/test_l6_v40_apps_rg_apps_eval.py`.
- Add companion E2E proof script for real apps_rg/apps_eval bridge code.
- Run requested proof, pytest slices, apps_eval deterministic run, and no-agents CI check.

**DoD**
- Targeted proof/test commands pass or any failures are reported with exact blockers.
