---
plan_id: apps-rg-golden-state-section-generation-a4f9e1
plan_type: architecture
authored_at: 2026-05-12
last_updated: 2026-05-12T11:15:00
status: In Progress
dod_exempt: false
parent_plan: apps-rg-exit-gate-fix-g24-hardening-d7c4b1
---

# apps_rg Golden State — Section-Level Generation + Spine Decoupling

Design plan for migrating `apps_rg` from single-pass whole-resume generation to section-level generation, scoring, and merging — and for moving all apps_rg dispatch and layer bindings out of `agentic_core` so it becomes a generic spine.

> ⛔ **This plan is In Progress for controlled migration waves. Golden State section-generation runtime implementation still requires explicit wave approval. No gate weakening, threshold tuning, or unapproved runtime feature work is allowed.**

> **ADDENDUM (2026-05-12):** Tiered section-priority model added to prevent over-engineering low-signal resume sections. Not all sections receive bespoke rubrics.
>
> **Governance Anchor:** This plan operates under [agentic-core-static-apps-customization-governance-a1b2c3](../plans/agentic-core-static-apps-customization-governance-a1b2c3.md). All migrations must use U0 runtime_customization_package pattern; no app-specific code in `agentic_core` except approved temporary shims with migration receipts.

---

## Context (SCQA)

**Situation:** `apps_rg` currently generates a resume in a single LLM call and scores the entire output at once. All dispatch and layer bindings live in `agentic_core`, making it app-specific code in the generic spine.

**Complication:** This single-pass architecture cannot independently optimize different resume sections (header, executive summary, experience bullets, competencies). Whole-resume scoring conflates good and weak sections. Meanwhile, `agentic_core` carries app-specific shims (dispatch, U0, C0, PA, L1, L2, Exit bindings) that belong in `apps_rg`.

**Question:** How do we migrate to section-level generation/scoring while simultaneously removing all apps_rg-specific code from `agentic_core`?

**Answer:** Define the target architecture first (this plan), then execute in waves. No code changes until design is approved.

---

## Rebaseline Summary (2026-05-12)

This plan has been rebaselined forward to reflect design decisions made after W2C-HARDEN and before W2E/W3 implementation.

### Completed Migration Work (W1 through W2D)

| Wave | Status | Evidence |
|------|--------|----------|
| W1 | ✅ DONE | Architecture audit — 14 files classified |
| W1B | ✅ DONE | Blocker disposition — hardened migration order |
| W2A | ✅ DONE | U0/L1 bindings migrated to `apps_rg/runtime/bindings/` |
| W2B | ✅ DONE | L0 binding migrated; route behavior preserved |
| W2C | ✅ DONE | C0 binding migrated; behavior preserved |
| W2C-HARDEN | ✅ DONE | Evidence reconciliation — W2B import gap resolved; L0 repair classified B |
| W2D | ✅ DONE | PA binding migrated; prompt assembly behavior preserved |

### W2C-HARDEN Evidence Reconciliation Summary

- **Issue discovered:** W2B import verification was shallow — `RouteFamily`, `CacheEligibility`, `HitlPosture` types not available at claimed import path
- **Resolution:** Types defined locally in `apps_rg/runtime/bindings/l0_binding.py` (architecturally correct — app-owned semantic interpretations)
- **Classification:** B — New App-Owned Compatibility Type Definition (not behavior change)
- **Route constants verified:** All values identical after repair
- **Dispatch import failure:** Known pre-existing W2F/W3 blocker (not W2C regression)

### Remaining Migration Work

| Wave | Scope | Blockers |
|------|-------|----------|
| W2E | L2 binding migration | ✅ SCOPE_COMPLETE / 🚧 GLOBAL_GOV3_BLOCKED — W2E changes baselined (GOV-3-BASELINE-007, GOV-3-BASELINE-008) but global GOV-3 still has 4 ERRORs from pre-existing W2F Exit binding + data files. See evidence: golden_state_w2e_l2_migration_evidence.md |
| W2F | Exit binding migration | Circular import risk (deferred last per W1B) |
| W2G | Create app-owned dispatch | Fresh creation (no source to migrate) |

### New Design Additions (This Rebaseline)

| Component | Purpose | Target Wave |
|-----------|---------|-------------|
| **SectionBenchmarkSet** | Per-section positive/negative examples, quality thresholds | W3A |
| **SectionSeedSet** | Deterministic seed management for generation, retry, replay | W3A |
| **AggregateResumeScorer** | Whole-resume X1B/X1D scoring after section merge | W5B |
| **AggregateBenchmarkSet** | Full-resume coherence benchmarks | W5B |
| **SectionArtifact** | Per-section output with provenance, scores, writeback candidates | W4 |
| **SectionWritebackCandidate** | Inert cache/index candidate until Exit/UWG | W5C |
| **AggregateWritebackCandidate** | Full-resume cache/index candidate until Exit/UWG | W5C |
| **SectionCompletedEvalRecord** | L6 shadow learning record per section | W7 |
| **AggregateCompletedEvalRecord** | L6 shadow learning record for full resume | W7 |
| **No Direct Writeback Rule** | All writeback candidates inert until Exit/UWG/L4 | W3A |

### Architecture Principles Reinforced

1. **Section-level pass does not imply aggregate pass** — whole-resume review mandatory after merge
2. **Aggregate pass does not erase section failures** — section attribution preserved
3. **G22 factual_grounding = 0.950** — applies to every claim-bearing section AND aggregate output
4. **G24/G28 remain whole-run invariants** — run at aggregate time, not per-section
5. **No writeback bypasses Exit/UWG/L4** — all candidates inert until proper gating
6. **L6 learning is future-run only** — no current-run rescue; proposals route through gauntlet/UWG

---

## Agentic Core Boundary Rule

`agentic_core` is the generic spine. `apps_rg` is the app overlay. `apps_rg`-specific behavior must not be implemented inside `agentic_core`.

**`apps_rg` customization enters only through:**
1. App-owned U0 `runtime_customization_package`
2. `apps_rg/runtime/bindings/` (app-owned layer bindings)
3. App-owned profiles: SectionSpec, scorer profiles, benchmark sets, seed sets, prompt profiles, writeback policies, L6 profiles
4. Generic `agentic_core` contracts consumed by the spine

**`agentic_core` may own:**
- Generic U0 validation machinery
- Generic L1/L0/C0/PA/L2/Exit/UWG/L4/L6 engines
- Generic contract schemas
- Generic gate enforcement
- Generic audit/replay/receipt mechanics
- Generic provider/gateway execution

**`agentic_core` must not own:**
- `apps_rg` route defaults
- Resume section definitions
- `apps_rg` prompt profiles
- `apps_rg` scorer/rubric profiles
- `apps_rg` benchmark/seed sets
- `apps_rg` writeback policies
- `apps_rg` L6 proposal policies
- Resume merge behavior
- `apps_rg` validation rules except approved temporary shims with migration receipts

---

## U0 App Package Rule

Every `apps_*` runtime enters through U0 `runtime_customization_package`.

**U0 may:**
- Pass app config and route hints
- Provide app-owned profiles and bindings

**U0 may not:**
- Set final route authority
- Bypass L0, C0, PA, L2, Exit, UWG, or L4
- Authorize writeback

---

## Core Change Prohibition

`agentic_core` changes are allowed **only** for approved temporary shims with migration receipts.

**Forbidden:**
- No new `apps_rg` semantics may be added to `agentic_core`
- No new `apps_rg` imports may be added to generic core
- No new `apps_rg` route constants may be added to generic core
- No new `apps_rg` scorer logic may be added to generic core

**Required procedure for any generic core change:**
Any required generic core change must stop at `CORE_BOUNDARY_REVIEW_REQUIRED` and move to a separate generic-core plan with its own approval.

**Evidence wording requirement:**
Every wave evidence artifact must include the statement: *"No new agentic_core behavior added; only approved temporary shim changes occurred."*

---

## Hard Constraints (Non-Negotiable)

| Constraint | Rule |
|---|---|
| No gate weakening | G21/G22/G24/G26/G28 thresholds and logic must not change |
| No threshold tuning | G22 `factual_grounding` stays at 0.950; no per-section relaxation without explicit approval |
| No new `agentic_core` behavior | All new logic goes in `apps_rg`; core is a generic spine only |
| No section-generation implementation without wave approval | Migration waves may proceed as explicitly scoped; Golden State section runtime requires separate wave approval |
| No dispatch leakage | `apps_rg_dispatch.py` and all `apps_rg_*_binding.py` files must migrate to `apps_rg/` |
| No equal-weight bespoke rubrics | P0 sections get bespoke X1B/X1D; P1/P2 use shared or basic scoring |
| Preserve section attribution | All scoring failures identify the specific section, even for P2 basic checks |

---

## Original As-Built Baseline (Pre-W2)

```
apps_rg/__main__.py
  → agentic_core/runtime/entry/apps_rg_dispatch.py   [expected legacy entry path; source absent during W1B, only .pyc remnant observed]
      → U0: agentic_core/runtime/entry/u0_apps_rg_binding.py
      → L1: agentic_core/L1_cognition/apps_rg_l1_binding.py
      → L0: agentic_core/L0_routing/apps_rg_l0_binding.py
      → C0: agentic_core/runtime/c0/apps_rg_c0_binding.py
      → PA: agentic_core/prompt_governance/apps_rg_pa_binding.py
      → L2: agentic_core/L2_execution/apps_rg_l2_binding.py  [single LLM call for entire resume]
      → Exit: agentic_core/runtime/exit/apps_rg_exit_binding.py
```

**Generation unit:** One LLM call → one `master_resume_v2.16` JSON blob.

**Scoring unit:** Entire output scored at once.

---

## Current Rebaselined State After W2D

### Migration Status (As of 2026-05-12)

- **U0 binding:** Migrated to `apps_rg/runtime/bindings/u0_binding.py` — temporary shim remains in `agentic_core`
- **L1 binding:** Migrated to `apps_rg/runtime/bindings/l1_binding.py` — temporary shim remains in `agentic_core`
- **L0 binding:** Migrated to `apps_rg/runtime/bindings/l0_binding.py` — temporary shim remains in `agentic_core`
- **C0 binding:** Migrated to `apps_rg/runtime/bindings/c0_binding.py` — temporary shim remains in `agentic_core`
- **PA binding:** Migrated to `apps_rg/runtime/bindings/pa_binding.py` — temporary shim remains in `agentic_core`
- **L2 binding:** **MIGRATED** — moved to `apps_rg/runtime/bindings/l2_binding.py`; shim remains in `agentic_core/L2_execution/apps_rg_l2_binding.py`
- **Exit binding:** **PENDING** — still in `agentic_core/runtime/exit/apps_rg_exit_binding.py`
- **apps_rg_dispatch.py:** **DOES NOT EXIST** as source in `agentic_core` (only .pyc) — must be created fresh in `apps_rg/runtime/dispatch/`

### Current Architecture (Post-W2E, Pre-W2F)

```
apps_rg/__main__.py
  → current legacy entry path expects agentic_core.runtime.entry.apps_rg_dispatch [MISSING SOURCE / known deferred W2G blocker]
      → U0: apps_rg/runtime/bindings/u0_binding.py   [MIGRATED — shim in agentic_core]
      → L1: apps_rg/runtime/bindings/l1_binding.py   [MIGRATED — shim in agentic_core]
      → L0: apps_rg/runtime/bindings/l0_binding.py   [MIGRATED — shim in agentic_core]
      → C0: apps_rg/runtime/bindings/c0_binding.py   [MIGRATED — shim in agentic_core]
      → PA: apps_rg/runtime/bindings/pa_binding.py   [MIGRATED — shim in agentic_core]
      → L2: apps_rg/runtime/bindings/l2_binding.py   [MIGRATED — shim in agentic_core; evidence: artifacts/apps_rg/golden_state_w2e_l2_migration_evidence.md]
      → Exit: agentic_core/runtime/exit/apps_rg_exit_binding.py   [PENDING W2F]
```

**W2E Status:** 🚧 BLOCKED_VERIFICATION — L2 binding migrated to `apps_rg/runtime/bindings/l2_binding.py` (781 lines), LEGACY_SHIM in place at `agentic_core/L2_execution/apps_rg_l2_binding.py` (27 lines). Import verification blocked by pre-existing circular import chain (missing `agentic_core.L4_state.utils`). Static analysis PASS (no forbidden patterns). G22 factual_grounding = 0.950 preserved.

**Section generation:** **NOT YET IMPLEMENTED** — single-pass whole-resume generation still active

**Hard Constraints Preserved:**
- G22 factual_grounding = 0.950 (unchanged)
- All gate thresholds unchanged (G21/G22/G24/G26/G28)
- Legacy route labels not canonicalized (R3_MANAGED_DRAFT, R5_SEMANTIC_REFRESH remain)

---

## Target Golden State

### Section-Level Generation + Scoring

```
apps_rg/__main__.py
  → apps_rg/runtime/dispatch/apps_rg_dispatch.py     [MOVED OUT of agentic_core]
      → apps_rg/runtime/bindings/u0_binding.py       [MOVED OUT]
      → apps_rg/runtime/bindings/l1_binding.py       [MOVED OUT]
      → apps_rg/runtime/bindings/l0_binding.py       [MOVED OUT]
      → apps_rg/runtime/bindings/c0_binding.py       [MOVED OUT]
      → apps_rg/runtime/section_planner.py           [NEW: decompose run → section specs]
      → per-section PA + L2 loop:
          for section in [header, executive_summary, experience_bullets, competencies, ...]:
              PA: apps_rg/runtime/bindings/pa_binding.py (section-scoped prompt)
              L2: generic agentic_core L2 (LLM call) — one per section
              Section scorer: apps_rg/runtime/scoring/section_scorer.py [NEW]
      → apps_rg/runtime/bindings/merge_binding.py    [NEW: merge section outputs]
      → Exit: apps_rg/runtime/bindings/exit_binding.py [MOVED OUT]
```

**Generation unit:** One LLM call per section. Sections are independent; failures in one section don't force full regeneration.

**Scoring unit (target):**
- **Section-level X1B/X1D scorer** evaluates each section independently before merge using tiered priority model (P0/P1/P2)
- **X1B scoring**: Did the section complete its assigned task, format, and instruction requirements? (task compliance)
- **X1D scoring**: Is the section actually good, grounded, specific, faithful, credible, and useful? (quality/value)
- `factual_grounding` applied per-section → precise identification of which section fails G22
- `header_block` validation applied per-section → G21 section-aware (not whole-resume repair)
- Whole-resume G24/G28 still run at merge time (these are whole-run invariants)

---

## Current vs Target Comparison

| Dimension | Current (Single-Pass) | Target (Section-Level) |
|---|---|---|
| **LLM calls** | 1 per run | N per run (one per section) |
| **Generation unit** | Entire resume JSON | Individual section |
| **X1B/X1D scoring** | Whole output | Per section, before merge |
| **G22 failure** | Whole run fails; no section attribution | Section fails; others can succeed |
| **G21 header repair** | Deterministic fallback on whole output | Per-section generation; repair not needed |
| **Dispatch location** | `agentic_core/runtime/entry/apps_rg_dispatch.py` | `apps_rg/runtime/dispatch/apps_rg_dispatch.py` |
| **Binding location** | `agentic_core/*/apps_rg_*_binding.py` (7 files) | `apps_rg/runtime/bindings/*.py` (7 files) |
| **`agentic_core` usage** | Contains app-specific dispatch + bindings | Generic spine only — no apps_rg code |
| **Section merging** | N/A (single output) | `merge_binding.py` assembles final JSON |
| **Retry granularity** | Full resume retry | Tiered retry: P0 (section-level retry), P1 (conditional retry), P2 (schema/factual only) |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | P1 | Architecture audit — map every apps_rg-specific file in `agentic_core`, classify as MIGRATE/KEEP | ~600 | ADG has current snapshot | ✅ DONE | All 14 files classified; 8 bindings + 4 contracts + 2 integration; W2 blockers identified |
| W1B | P1-B | Blocker disposition — hardened migration order, circular import mitigation | ~400 | W1 complete | ✅ DONE | W2 order hardened; Exit deferred last; dispatch dispositioned as CREATE |
| W2A | P2 | Create runtime structure + migrate U0/L1 bindings | ~800 | No behavior change; existing tests pass | ✅ DONE | U0/L1 in apps_rg; shims in agentic_core; all imports work |
| W2B | P3 | Migrate L0 binding | ~400 | U0/L1 complete | ✅ DONE | L0 binding migrated; route behavior preserved |
| W2C | P4 | Migrate C0 binding | ~400 | L0 complete | ✅ DONE | C0 binding migrated; behavior preserved; shim in place |
| W2C-HARDEN | P4-H | Evidence hardening: reconcile W2B import evidence; classify L0 repair; verify route constants | ~200 | W2C complete | ✅ DONE | W2B/W2C inconsistency explained; L0 repair classified B (app-owned types); all constants verified |
| W2D | P5 | Migrate PA binding | ~400 | W2C-HARDEN complete | ✅ DONE | PA binding migrated; behavior preserved; shim in place |
| W2E | P6 | Migrate L2 binding | ~400 | PA complete | � BLOCKED_VERIFICATION | L2 migrated to apps_rg; shim in place; evidence: artifacts/apps_rg/golden_state_w2e_l2_migration_evidence.md |
| W2F | P7 | Migrate Exit binding (deferred last per W1B) | ~400 | L2 complete | 🔲 TODO | Exit binding migrated; circular import resolved; no scoring redesign |
| W2G | P8 | Create app-owned dispatch | ~600 | Exit complete | 🔲 TODO | Fresh dispatch creation (not migrate per W1B); preserve live entry behavior; `python -m apps_rg` uses app-owned path |
| W3A | P9 | Design hardening before section implementation | ~1,200 | Dispatch created | 🔲 TODO | SectionSpec final schema; SectionBenchmarkSet; SectionSeedSet; AggregateResumeScorer; AggregateBenchmarkSet; SectionArtifact; SectionWritebackCandidate; AggregateWritebackCandidate; SectionCompletedEvalRecord; AggregateCompletedEvalRecord; No direct writeback rule |
| W3B | P10 | Section planner implementation | ~1,200 | W3A design hardened | 🔲 TODO | `apps_rg/runtime/section_planner.py`; deterministic ordering; P0/P1/P2 assignment; P1 promotion logic; benchmark_set_id and seed_set_id assignment; scorer_profile_id assignment; retry policy construction |
| W4 | P11 | Section-level PA + L2 loop | ~2,000 | Qwen vLLM running | 🔲 TODO | One section-scoped PA packet per section; one bounded L2 call per section; no full-resume retry when one section fails; emit SectionArtifact per section |
| W5 | P12 | Section-level scorer | ~1,500 | Section artifacts from W4 | 🔲 TODO | `apps_rg/runtime/scoring/section_scorer.py`; section X1B/X1D/G21/G22 scoring; section failure attribution; P0/P1/P2 retry behavior; no G22 threshold drift |
| W5B | P13 | Aggregate resume scorer after merge | ~800 | Section scoring complete | 🔲 TODO | Aggregate X1B/X1D scoring; merge consistency; repetition/contradiction checks; ATS balance; narrative coherence; seniority and role-fit check; full-resume benchmark comparison |
| W5C | P14 | Section and aggregate writeback candidate emission and inertness proof | ~600 | Aggregate scoring defined | 🔲 TODO | Emit semantic cache candidate per section; emit vector/index candidate per section; emit aggregate resume cache/index candidate; prove all candidates remain inert; prove no direct L4 write from section scorer, merge, L2, PA, C0, or L6 |
| W6 | P15 | Gate verification and baseline comparison | ~600 | W5C complete | 🔲 TODO | G21/G22/G24/G28 unchanged; G22 remains 0.950; section-level gate receipts visible; aggregate receipts visible; no bypass of Exit/UWG/L4 |
| W7 | P16 | L6 shadow learning proof and future-run proposal path | ~800 | W6 complete | 🔲 TODO | SectionCompletedEvalRecord coverage per section; AggregateCompletedEvalRecord coverage per aggregate; ProposalPacket inertness until FutureRunPromotionRequest; no-current-run-rescue proof; no-direct-write proof; FutureRunPromotionRequest/UWG/L4 path verified; G22 unchanged at 0.950 |

**Wave Clarifications:**
- **W5C:** Schema design belongs to W3A. W5C proves emitted candidates remain inert and do not bypass Exit/UWG/L4.
- **W7:** Schema design belongs to W3A. W7 verifies section and aggregate completed-run evals are produced after runtime boundary and proposals go through gauntlet/UWG/L4.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Architecture audit | ADG + 14 files catalogued (8 bindings, 4 contracts, 2 integration) | Classified as MIGRATE/KEEP_GENERIC/LEGACY_SHIM; identified 5 W2 blockers | ~600 | ✅ DONE |
| W1B.P1-B | Blocker disposition — hardened migration order | Migration order + circular import mitigation + dispatch disposition | W1B: hardened W2 order; Exit deferred last; dispatch = CREATE not migrate | ~400 | ✅ DONE |
| W2A.P2 | Create `apps_rg/runtime/` directory structure + migrate U0/L1 bindings | `apps_rg/runtime/bindings/` + U0/L1 binding migration + shims | U0→L1 first migration; backward-compat shims; no behavior change | ~800 | ✅ DONE |
| W2B.P3 | Migrate L0 binding | `apps_rg/runtime/bindings/l0_binding.py` + shim | L0 migration after U0/L1; route behavior preserved | ~400 | ✅ DONE |
| W2C.P4 | Migrate C0 binding | `apps_rg/runtime/bindings/c0_binding.py` + shim | C0 migration after L0 | ~400 | ✅ DONE |
| W2C-HARDEN.P4-H | Evidence hardening — reconcile W2B import gap | W2B import verification was shallow; W2C discovered missing `RouteFamily`/`CacheEligibility`/`HitlPosture` types | Type definitions added to apps_rg L0 binding; classified as B (app-owned compatibility types) | ~200 | ✅ DONE |
| W2D.P5 | Migrate PA binding | `apps_rg/runtime/bindings/pa_binding.py` + shim | PA migration after C0+HARDEN; prompt assembly behavior preserved | ~400 | ✅ DONE |
| W2E.P6 | Migrate L2 binding | `apps_rg/runtime/bindings/l2_binding.py` + shim | L2 migration after PA; no section generation | ~400 | � BLOCKED_VERIFICATION |
| W2E.P6a | Core boundary verification checkpoint | `check_agentic_core_addition.py` + static analysis | Import chain BLOCKED (pre-existing); static analysis PASS (no forbidden patterns); shim purity verified; evidence artifact created | ~200 | � BLOCKED_VERIFICATION |
| W2F.P7 | Migrate Exit binding (deferred last) | `apps_rg/runtime/bindings/exit_binding.py` + shim | Exit migration LAST per W1B; circular import resolved; no scoring redesign | ~400 | 🔲 TODO |
| W2G.P8 | Create app-owned dispatch | `apps_rg/runtime/dispatch/apps_rg_dispatch.py` | Fresh creation (not migrate per W1B); preserve live entry behavior | ~600 | 🔲 TODO |
| W3A.P9 | Design hardening before section implementation | SectionSpec, SectionBenchmarkSet, SectionSeedSet, AggregateResumeScorer, AggregateBenchmarkSet, SectionArtifact, writeback candidates, L6 records | All schema design before implementation; no direct writeback rule | ~1,200 | 🔲 TODO |
| W3B.P10 | Section planner implementation | `apps_rg/runtime/section_planner.py` | Deterministic ordering; P0/P1/P2 assignment; P1 promotion logic; benchmark/seed/scorer assignment | ~1,200 | 🔲 TODO |
| W4.P11 | Section-level PA + L2 loop | Per-section PA packet; bounded L2 call per section; SectionArtifact emission | No full-resume retry when one section fails | ~2,000 | 🔲 TODO |
| W5.P12 | Section-level scorer | `apps_rg/runtime/scoring/section_scorer.py` | Section X1B/X1D/G21/G22 scoring; failure attribution; P0/P1/P2 retry; G22 = 0.950 | ~1,500 | 🔲 TODO |
| W5B.P13 | Aggregate resume scorer after merge | Aggregate X1B/X1D; merge consistency; repetition/contradiction; ATS balance; narrative coherence; seniority/role-fit | Full-resume benchmark comparison | ~800 | 🔲 TODO |
| W5C.P14 | Section and aggregate writeback candidate emission and inertness proof | Emit SectionWritebackCandidate; emit AggregateWritebackCandidate; prove inertness | Schema design is W3A; W5C proves emission + inertness + no bypass | ~600 | 🔲 TODO |
| W6.P15 | Gate verification and baseline comparison | All gate files, test suite | G21/G22/G24/G28 unchanged; G22 = 0.950; section + aggregate receipts | ~600 | 🔲 TODO |
| W7.P16 | L6 shadow learning proof and future-run proposal path | SectionCompletedEvalRecord; AggregateCompletedEvalRecord; ProposalPacket; FutureRunPromotionRequest; anti-bypass proofs | Schema design is W3A; W7 proves runtime eval production + future-run proposal path; concrete proof artifacts for each anti-bypass rule | ~800 | 🔲 TODO |

---

## Definition of Done

| ID | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Zero apps_rg-specific files remain in `agentic_core` (no `apps_rg_*_binding.py`, no `apps_rg_dispatch.py`) | `rg -l "apps_rg" agentic_core/` returns only generic imports | 🔲 TODO |
| DoD-2 | `python -m apps_rg [canonical args]` exits 0 with `exit_status=success` after all bindings moved | Live smoke run | 🔲 TODO |
| DoD-3 | Section-level generation: live run produces per-section artifacts (`section_header.json`, `section_exec_summary.json`, etc.) | Artifact inspection | 🔲 TODO |
| DoD-4 | G22 `factual_grounding` threshold unchanged at 0.950; per-section scores visible in gate receipt | `07_gate_mesh_result.json` inspection | 🔲 TODO |
| DoD-5 | G21/G22/G24/G28 pass rate at or above `rg-run-c68e95637652` baseline | Baseline comparison report | 🔲 TODO |
| DoD-6 | `pytest tests/_apps_contract/ -x` — all tests pass; zero new failures | pytest output | 🔲 TODO |
| DoD-7 | `python -m apps_rg --dry-run [canonical args]` exits 0 (APPS-DRYRUN gate) | CI gate green | 🔲 TODO |
| DoD-8 | Section benchmark and seed records emitted or referenced in section artifacts | SectionArtifact inspection | 🔲 TODO |
| DoD-9 | Aggregate X1B/X1D scorer receipts exist after merge | Aggregate scoring output inspection | 🔲 TODO |
| DoD-10 | Section and aggregate writeback candidates present but inert before Exit/UWG | Candidate state inspection; no premature L4 writes | 🔲 TODO |
| DoD-11 | RuntimeExhaustBundle includes section and aggregate artifacts for L6 | Bundle artifact inspection | 🔲 TODO |
| DoD-12 | L6 records section and aggregate completed evals without current-run mutation | L6 eval record inspection | 🔲 TODO |
| DoD-13 | No direct writes to semantic cache/vector DB from section loop, scorer, merge, or L6 | Write path audit | 🔲 TODO |
| DoD-14 | MergedResumeArtifact exists and references all SectionArtifacts | MergedResumeArtifact schema inspection; section_artifact_refs non-empty | 🔲 TODO |
| DoD-15 | Aggregate scorer receipts attach to MergedResumeArtifact | aggregate_x1b_result_ref and aggregate_x1d_result_ref present | 🔲 TODO |
| DoD-16 | Seed support status is recorded for each section generation | SectionSeedSet.seed_support_status present in artifacts | 🔲 TODO |
| DoD-17 | Benchmark thresholds are recorded separately from runtime gate thresholds | minimum_score_thresholds in SectionBenchmarkSet; no override of G22=0.950 | 🔲 TODO |
| DoD-18 | W5C proves no writeback candidate mutates L4 before Exit/UWG | W5C verification artifacts; inert_until_exit_uwg assertions | 🔲 TODO |
| DoD-19 | W7 proves L6 proposals are future-run only | W7 verification artifacts; no current-run rescue paths | 🔲 TODO |
| DoD-20 | Core boundary audit passes with no apps_rg-specific additions in agentic_core | `check_agentic_core_addition.py` output shows zero ERROR; all bindings are generic engines consuming app-owned profiles | 🔲 TODO |

### Verification-vs-Deferral

| Item | Verified | Deferred |
|---|---|---|
| G22 threshold lowering | ❌ | **Permanently deferred** — do not lower below 0.950 |
| Section retry on G22 fail | ❌ | Deferred to W5 or later sub-plan |
| Multi-candidate ensemble | ❌ | Deferred — not in scope |
| Section-level G26 no_fabrication | ❌ | Deferred — whole-run only for now |
| Shim removal from `agentic_core` | ❌ | Deferred to wave after W2 (shims in W2 are temporary) |

---

## W2C-HARDEN — Evidence Reconciliation

### W2B Import Evidence Reconciliation

**The Issue:** W2B evidence claimed "All import paths verified" but W2C discovered that `RouteFamily`, `CacheEligibility`, and `HitlPosture` could not be imported from `agentic_core.L0_routing.contracts.route_contract`.

**Root Cause:** W2B import verification was **shallow** — it tested:
```bash
python -c "from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg"
```

This succeeded because Python's deferred execution doesn't validate type hints at import time. The W2B evidence incorrectly assumed these types existed at the claimed import path, but `agentic_core.L0_routing.route_contract` only exports `L0Router`, `RouteContract`, and `L1PlanContract` — not apps_rg-specific Enums.

**Resolution:** W2C discovered the issue when importing C0 binding triggered deep type resolution. The fix was to define these types locally in `apps_rg/runtime/bindings/l0_binding.py` — which is architecturally correct as they are apps_rg-specific semantic interpretations.

### L0 Repair Classification

**Classification: B — New App-Owned Compatibility Type Definition**

**Why NOT behavior change (C) or unsafe (D):**
- Underlying string VALUES unchanged: `R3_MANAGED_DRAFT`, `EXACT_MATCH_CANDIDATE`, `ADVISORY`, etc.
- Route constants verified identical after repair:
  - `APPS_RG_ROUTE_FAMILY.value == "R3_MANAGED_DRAFT"` ✅
  - `APPS_RG_ROUTE_ID == "R3A_RESUME_GENERATION"` ✅
  - `APPS_RG_CACHE_ELIGIBILITY.value == "EXACT_MATCH_CANDIDATE"` ✅
  - `APPS_RG_HITL_POSTURE.value == "ADVISORY"` ✅
  - `APPS_RG_FALLBACK_ROUTE_ID == "R5_SEMANTIC_REFRESH"` ✅

**Why app-owned is correct:**
These types represent apps_rg's interpretation of route policy, not generic L0 infrastructure. They were always apps_rg-specific strings; adding Enum wrappers in apps_rg improves type safety without changing behavior.

### Test Status Classification

**Dispatch Import Failure:** `ModuleNotFoundError: No module named 'agentic_core.runtime.entry.apps_rg_dispatch'`

**Classification:** Known pre-existing W2F/W3 blocker — NOT a W2C regression.

- `apps_rg_dispatch` is scheduled for creation in W3 (not migration)
- Per W1B hardened order: dispatch is created fresh after all bindings migrate
- All binding shims (U0, L1, L0, C0) work correctly without dispatch existing
- This failure does NOT block W2D (PA migration)

**Evidence:** `artifacts/apps_rg/golden_state_w2c_hardening_evidence.md`

---

## Gap Register

| ID | Description | Severity | Wave | Status |
|---|---|---|---|---|
| GAP-GS-1 | `apps_rg_dispatch.py` does NOT exist in `agentic_core` (only .pyc) — must be created in `apps_rg/runtime/dispatch/` | High | W2 | ✅ RESOLVED — W1B disposition: CREATE (not migrate) |
| GAP-GS-2 | Remaining apps_rg-specific binding implementation in `agentic_core` is limited to Exit only; temporary shims remain for migrated bindings | High | W2 | � W2E BLOCKED_VERIFICATION; W2F pending; U0/L1/L0/C0/PA/L2 resolved or shimmed |
| GAP-GS-2a | Exit binding circular import risk (imports from `apps_rg_exit_evidence_builder`) | High | W2 | ✅ MITIGATED — W1B: defer Exit migration until last |
| GAP-GS-2b | Prerequisite gate imports from `apps_rg.prerequisites.briefing_validator` | Medium | W2 | ✅ ACCEPTED — Keep as LEGACY_SHIM in agentic_core |
| GAP-GS-3 | Single LLM call produces entire resume — no section-level failure attribution | Medium | W4 | 🔲 Open |
| GAP-GS-4 | G22 `factual_grounding` scorer operates on whole output — can't identify which section causes failure | Medium | W5 | 🔲 Open |
| GAP-GS-5 | No section-level X1B/X1D scorer — only whole-resume scoring exists | Medium | W5 | 🔲 Open |
| GAP-GS-6 | No tiered section priority — risk of over-engineering low-signal sections | Medium | W3 | 🔲 Open |
| GAP-GS-7 | SectionBenchmarkSet / SectionSeedSet | Medium | W3A | ✅ DESIGN DEFINED — implementation pending W3A/W3B |
| GAP-GS-8 | No aggregate whole-resume scorer after merge | Medium | W5B | 🔲 Open |
| GAP-GS-9 | SectionArtifact writeback candidate | Medium | W5C | ✅ DESIGN DEFINED — emission proof pending W5C |
| GAP-GS-10 | Aggregate writeback candidate | Medium | W5C | ✅ DESIGN DEFINED — emission proof pending W5C |
| GAP-GS-11 | Section-level L6 completed eval record | Medium | W7 | ✅ DESIGN DEFINED — proof pending W7 |
| GAP-GS-12 | Aggregate L6 completed eval record | Medium | W7 | ✅ DESIGN DEFINED — proof pending W7 |
| GAP-GS-13 | Aggregate benchmark set for full-resume coherence | Medium | W5B | ✅ DESIGN DEFINED — implementation/proof pending W5B |
| GAP-GS-14 | Legacy apps_rg route labels are non-canonical relative to spine route-family names; defer route canonicalization | Low | Deferred | 🔲 Deferred — separate route canonicalization plan |

---

## Relationship to Backlog

The 10 backlog items in `artifacts/apps_rg/next_apps_rg_golden_state_backlog.md` map to this plan as follows:

| Backlog Item | Plan Wave |
|---|---|
| GS-01: Move `apps_rg_dispatch.py` to `apps_rg/runtime/dispatch/` | W2 |
| GS-02: Move 7 `apps_rg_*_binding.py` to `apps_rg/runtime/bindings/` | W2 |
| GS-03: Remove `agentic_core` shims after binding migration | Post-W2 sub-plan |
| GS-04: Section planner schema | W3 |
| GS-05: N-section PA prompt scoping | W4 |
| GS-06: N-section L2 loop | W4 |
| GS-07: Section merge contract | W4 |
| GS-08: Section-level X1B/X1D scorer | W5 |
| GS-09: Per-section G22 attribution | W5 |
| GS-10: Gate verification baseline comparison | W6 |
| GS-11: SectionBenchmarkSet + SectionSeedSet | W3A |
| GS-12: Aggregate resume scorer | W5B |
| GS-13: Aggregate benchmark set | W5B |
| GS-14: SectionArtifact writeback candidates | W5C |
| GS-15: Aggregate writeback candidates | W5C |
| GS-16: Section-level L6 completed eval record | W7 |
| GS-17: Aggregate-level L6 completed eval record | W7 |
| GS-18: Route canonicalization follow-up plan | Deferred |

---

## Non-Goals (Explicit Fence)

The following are **explicitly forbidden** in this plan and must not be implemented:

- ❌ Lowering G22 `factual_grounding` threshold below 0.950
- ❌ Weakening G21, G24, G26, G28 gates in any way
- ❌ Adding new runtime features to `agentic_core`
- ❌ Implementing section retry without explicit wave approval
- ❌ Multi-candidate ensemble generation
- ❌ Unscoped code changes outside the active approved wave
- ❌ Starting Wave 2 before this plan is transitioned to `In Progress` by the user
- ❌ Equal-weight bespoke rubric for every resume section — P2 sections use basic checks only

---

## Architecture Classification

| Component | Location (Current) | Location (Target) | Classification | Status |
|---|---|---|---|---|
| `u0_binding.py` | `agentic_core/runtime/entry/u0_apps_rg_binding.py` (shim) | `apps_rg/runtime/bindings/u0_binding.py` | `MIGRATED` | ✅ Migrated; shim remains in `agentic_core` |
| `l1_binding.py` | `agentic_core/L1_cognition/apps_rg_l1_binding.py` (shim) | `apps_rg/runtime/bindings/l1_binding.py` | `MIGRATED` | ✅ Migrated; shim remains in `agentic_core` |
| `l0_binding.py` | `agentic_core/L0_routing/apps_rg_l0_binding.py` (shim) | `apps_rg/runtime/bindings/l0_binding.py` | `MIGRATED` | ✅ Migrated; shim remains in `agentic_core` |
| `c0_binding.py` | `agentic_core/runtime/c0/apps_rg_c0_binding.py` (shim) | `apps_rg/runtime/bindings/c0_binding.py` | `MIGRATED` | ✅ Migrated; shim remains in `agentic_core` |
| `pa_binding.py` | `agentic_core/prompt_governance/apps_rg_pa_binding.py` (shim) | `apps_rg/runtime/bindings/pa_binding.py` | `MIGRATED` | ✅ Migrated; shim remains in `agentic_core` |
| `l2_binding.py` | `agentic_core/L2_execution/apps_rg_l2_binding.py` | `apps_rg/runtime/bindings/l2_binding.py` | `PENDING` | 🔲 Pending W2E |
| `exit_binding.py` | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | `apps_rg/runtime/bindings/exit_binding.py` | `PENDING` | 🔲 Pending W2F (deferred last per W1B) |
| `apps_rg_dispatch.py` | **Does not exist** (only .pyc in agentic_core) | `apps_rg/runtime/dispatch/apps_rg_dispatch.py` | **CREATE** (not migrate) | 🔲 Pending W2G — no source to migrate |
| `section_planner.py` | (new) | `apps_rg/runtime/` | `NEW — app-owned` |
| `section_scorer.py` | (new) | `apps_rg/runtime/scoring/` | `NEW — app-owned` |
| Generic L2 executor | `agentic_core/L2_execution/` | stays | `GENERIC_INFRASTRUCTURE` |
| G21/G22/G24/G26/G28 gates | `agentic_core/` | stays | `GENERIC_INFRASTRUCTURE — DO NOT MOVE` |

---

## W1B Blocker Disposition Summary

**Status:** ✅ COMPLETE — W2 readiness assessed, blockers dispositioned, migration order hardened

### Blockers Resolved

| Blocker | Disposition | W2 Impact |
|---------|-------------|-----------|
| BLK-W2-1: Dispatch missing source | ✅ **ACCEPTED** | Create `apps_rg/runtime/dispatch/apps_rg_dispatch.py` fresh (not migrate) |
| BLK-W2-2: Exit evidence circular risk | ✅ **MITIGATED** | Defer Exit migration until **last** (after L2); use hardened order |
| BLK-W2-3: Prerequisite gate import | ✅ **ACCEPTED** | Keep gate in `agentic_core` as LEGACY_SHIM; approved L0 coupling point |
| BLK-W2-4: Core→app imports | ✅ **REFINED** | Only 3 actual imports (not 19); classified and dispositioned |
| BLK-W2-5: Integrated pipeline ownership | ✅ **DECIDED** | Pipeline stays in `agentic_core` (generic spine); apps_rg owns dispatch only |

### Core→App Import Classification (3 files, not 19)

| File | Import | Classification |
|------|--------|----------------|
| `L0_routing/apps_rg_l0_binding.py` | `from apps_rg.activation_policy import ...` | LEGACY_SHIM_ALLOWED_TEMPORARILY — becomes internal after move |
| `L0_routing/gates/apps_rg_prerequisite_gate.py` | `from apps_rg.prerequisites.briefing_validator import ...` | CORE_BOUNDARY_VIOLATION — keep in core temporarily |
| `runtime/exit/apps_rg_exit_binding.py` | `from apps_rg.exit.apps_rg_exit_evidence_builder import ...` | CONTRACT_ONLY_ALLOWED — Exit must import evidence builders |

### Hardened W2 Migration Order

```
Step 1:  U0 binding (least dependencies)
Step 2:  L1 binding (consumes U0 output)
Step 3:  L0 binding (consumes L1 output; imports activation_policy → internal after move)
Step 4:  C0 binding (consumes L0 output)
Step 5:  PA binding (consumes C0 output)
Step 6:  L2 binding (consumes PA output)
Step 7:  Exit binding (consumes L2 output; **DEFERRED LAST** due to evidence_builder imports)
Step 8:  CREATE dispatch (apps_rg/runtime/dispatch/apps_rg_dispatch.py) — orchestrates all 7 bindings
```

### W2 Readiness Verdict

**✅ SAFE TO START** with hardened migration order. Exit deferred last resolves circular import risk.

**Artifact:** `artifacts/apps_rg/golden_state_w1b_blocker_disposition.md`

---

## Tiered Section-Priority Model (Design Addendum)

To prevent over-engineering low-signal resume sections, the Golden State architecture adopts a three-tier priority model for section-level scoring.

### Tier Definitions

| Tier | Sections | X1B/X1D Treatment | Retry Policy |
|------|----------|-------------------|--------------|
| **P0** | headline, executive_summary, unify_narrative, competencies_ats, IBM | Bespoke section-specific X1B and X1D scorer profiles | Section-level retry/regeneration on X1B or X1D failure |
| **P1** | InsurTech, EY | Shared "experience-section" X1B/X1D rubric by default; promoted to bespoke when target role activates domain | Retry only when promoted OR on factual/schema failure |
| **P2** | Early Career, Education, low-signal certifications/background | Basic checks only (existence, structure, compactness, factuality) | No retry for subjective quality; repair only schema/factual failures |

### P1 Promotion Conditions

P1 sections promote to bespoke scoring when the target role matches one of these domains:
- `insurance` (exact match)
- `InsurTech` (exact match, case-insensitive)
- `financial services AI`
- `regulated transformation`
- `model governance`
- `advisory / consulting transformation`
- `risk / compliance / controls`

Promotion is determined at planning time (W3 section planner) by inspecting `target_role_profile.industry` and `target_role_profile.domain_keywords`.

### SectionSpec Schema (Updated)

```python
@dataclass(frozen=True)
class SectionSpec:
    section_id: str                          # canonical ID
    priority_tier: Literal["P0", "P1", "P2"]  # tier assignment
    prompt_profile_id: str                   # PA profile for section-scoped prompt
    scorer_profile_id: str                   # X1B/X1D rubric reference
    benchmark_set_id: str                    # SectionBenchmarkSet reference
    seed_set_id: str                         # SectionSeedSet reference
    section_output_schema_ref: str           # schema URI for section validation
    retry_policy: RetryPolicy                # tiered retry configuration
    
    # P1 only: conditions that trigger bespoke promotion
    promotion_conditions: Optional[List[str]] = None  # e.g., ["industry=insurance", "domain=InsurTech"]
    
    # X1B vs X1D clarification
    x1b_checklist: List[str] = field(default_factory=list)  # task completion requirements
    x1d_quality_dims: Optional[List[str]] = None  # None for P2 (basic only)
    
    # Writeback and shadow learning
    writeback_policy: Optional[WritebackPolicy] = None  # inert candidate emission rules
    shadow_learning_profile_id: Optional[str] = None  # L6 eval profile for this section
```

> **Implementation note:** `RetryPolicy` is constructed by the section planner using `build_retry_policy(priority_tier)`, not inside the `SectionSpec` field default. This avoids the circular reference issue where `priority_tier` is referenced before the instance is fully constructed.

### X1B vs X1D Clarification

| Dimension | X1B (Task Compliance) | X1D (Quality/Value) |
|-----------|----------------------|---------------------|
| **Question** | Did the section complete its assigned task, format, and instruction requirements? | Is the section actually good, grounded, specific, faithful, credible, and useful? |
| **Checks** | - Required fields present<br>- Format constraints met<br>- Instruction adherence<br>- Structural validity | - Factual grounding (G22)<br>- Specificity (concrete vs vague)<br>- Faithfulness to source resume<br>- Credibility of claims<br>- Utility for interview conversion |
| **Failure mode** | Section incomplete or malformed | Section present but weak, generic, or unconvincing |
| **Retry** | P0/P1: regenerate; P2: repair | P0: regenerate; P1: regenerate if promoted; P2: no retry |

### P2 Basic Checks (No Bespoke Rubric)

P2 sections receive these checks only:
1. **Section existence**: Required section is present
2. **Accurate structure**: Role/company/date fields correctly formatted
3. **Compact length**: Within token/line budget
4. **No unsupported claims**: All claims traceable to source resume
5. **No narrative drift**: Section doesn't contradict current AI/platform positioning
6. **No distraction**: Section doesn't dilute high-signal content

### Scorer Profile Mapping

| Section | Default Profile | Promoted Profile | Notes |
|---------|-----------------|------------------|-------|
| headline | `rg_headline_x1bd` | — | P0 bespoke |
| executive_summary | `rg_exec_summary_x1bd` | — | P0 bespoke |
| unify_narrative | `rg_narrative_x1bd` | — | P0 bespoke |
| competencies_ats | `rg_competencies_x1bd` | — | P0 bespoke |
| IBM | `rg_ibm_x1bd` | — | P0 bespoke |
| InsurTech | `shared_experience_x1bd` | `rg_insurtech_x1bd` | P1 conditional |
| EY | `shared_experience_x1bd` | `rg_ey_x1bd` | P1 conditional |
| Early Career | `basic_compactness` | — | P2 basic only |
| Education | `basic_compactness` | — | P2 basic only |
| certifications_low_signal | `basic_compactness` | — | P2 basic only |

---

## Section Benchmark and Seed Model

To enable reproducible, measurable section quality, every section generation must reference deterministic benchmarks and seeds.

### SectionBenchmarkSet Schema

```python
@dataclass(frozen=True)
class SectionBenchmarkSet:
    benchmark_set_id: str                          # canonical ID, e.g., "rg_headline_benchmark_v1"
    section_id: str                                  # target section
    priority_tier: Literal["P0", "P1", "P2"]        # tier alignment
    positive_examples: List[BenchmarkExample]        # high-quality section exemplars
    negative_examples: List[BenchmarkExample]        # common failure modes
    target_role_family: str                          # e.g., "AI_executive", "platform_engineering"
    benchmark_source_refs: List[str]                 # human-labeled holdout references
    expected_quality_dimensions: List[str]             # X1D dimensions expected
    minimum_score_thresholds: Dict[str, float]        # per-dimension floors
    calibration_refs: List[str]                       # judge calibration anchors
    version: str                                      # semantic version
    owner: str                                        # team/app accountable
```

### SectionSeedSet Schema

```python
@dataclass(frozen=True)
class SectionSeedSet:
    seed_set_id: str                                 # canonical ID
    section_id: str                                  # target section
    generation_attempt_seed: int                       # LLM generation RNG seed
    prompt_variant_seed: int                           # prompt A/B variant selection
    evidence_selection_seed: int                       # C0 evidence subsampling (if needed)
    judge_order_seed: int                              # X1B/X1D judge evaluation order
    retry_seed: int                                    # retry/regeneration branching
    benchmark_sample_seed: int                         # benchmark example selection
    replay_seed: int                                   # deterministic replay for debugging
    seed_support_status: Literal["SUPPORTED", "PARTIAL", "UNSUPPORTED"]  # provider seeding capability
```

### Seed Determinism Limits

**`generation_attempt_seed` is used only when provider/runtime supports deterministic seeding.**

When unsupported:
- `seed_support_status` must be recorded as `PARTIAL` or `UNSUPPORTED`
- Replay relies on `prompt_hash`, model/provider digest, inputs, and attempt metadata
- Deterministic reproduction is best-effort, not guaranteed
- SectionArtifact still captures full provenance for traceability

### Design Rules

- **P0 sections** require richer benchmark coverage (positive/negative examples, multiple quality dimensions, calibration anchors).
- **P1 sections** use shared benchmark sets unless promoted by target_role_profile.
- **P2 sections** use compactness/factuality benchmark only (minimal examples, basic thresholds).
- **No benchmark or seed change** may be silently promoted into runtime behavior without L6 gauntlet/UWG approval.

### Benchmark Thresholds Clarification

**Benchmark thresholds are scorer-profile thresholds only. They do not override runtime gate thresholds.**

- `minimum_score_thresholds` in SectionBenchmarkSet are for rubric calibration and judge agreement tracking.
- **G22 factual_grounding remains 0.950** — this is a hard runtime gate threshold, not a benchmark threshold.
- No benchmark-defined threshold may weaken, override, or bypass runtime gate enforcement.

---

## Section-Specific Benchmark Mapping

### P0 Sections (Bespoke Benchmarks)

| Section | Benchmark Set | Notes |
|---------|----------------|-------|
| headline | `rg_headline_benchmark_v1` | Leadership signal, concision, hook strength |
| executive_summary | `rg_exec_summary_benchmark_v1` | Narrative arc, evidence density, positioning clarity |
| unify_narrative | `rg_unify_narrative_benchmark_v1` | Cross-role coherence, platform/AI thread |
| competencies_ats | `rg_competencies_ats_benchmark_v1` | Skill-market match, keyword authenticity |
| IBM | `rg_ibm_impact_benchmark_v1` | Enterprise transformation quantification |

### P1 Sections (Shared Default, Promoted When Target Role Activates)

| Section | Default Benchmark | Promoted Benchmark | Promotion Triggers |
|---------|-------------------|-------------------|-------------------|
| InsurTech | `shared_experience_benchmark_v1` | `rg_insurtech_benchmark_v1` | `industry=insurance`, `domain=InsurTech`, `regulated transformation` |
| EY | `shared_experience_benchmark_v1` | `rg_ey_advisory_benchmark_v1` | `advisory/consulting transformation`, `risk/compliance/controls` |

### P2 Sections (Compactness/Factuality Only)

| Section | Benchmark Set | Notes |
|---------|----------------|-------|
| Early Career | `basic_compactness_factuality_benchmark_v1` | Structure, dates, no unsupported claims |
| Education | `basic_compactness_factuality_benchmark_v1` | Degree accuracy, institution formatting |
| Certifications/Background (low-signal) | `basic_compactness_factuality_benchmark_v1` | Existence, relevance, no dilution |

---

## Aggregate Resume Review After Merge

**Hard Rule:** Every final assembled resume must be reviewed as a whole after section aggregation.

Section-level pass does NOT imply aggregate pass. Aggregate pass does NOT erase section failures.

### Aggregate Scorer Profiles

#### rg_resume_aggregate_x1b (Task Compliance)

- All required sections present (per target role profile)
- Final schema valid (master_resume_v2.16)
- Target role instructions followed
- Section order correct (per section_planner spec)
- No missing P0 section
- No merge artifacts (duplicate fields, malformed JSON)
- Length within configured profile limits
- Formatting consistency (fonts, bullets, spacing)
- No unsupported inserted section types

#### rg_resume_aggregate_x1d (Quality/Value)

- Full narrative coherence across sections
- Seniority signal consistent throughout
- AI/platform leadership signal prominent
- Evidence-backed specificity (concrete > vague)
- No repetition across sections (same achievement claimed twice)
- No contradiction across roles (titles/companies/dates)
- Strongest achievements foregrounded (top-loading)
- Low-signal sections do not dilute positioning
- ATS coverage without keyword stuffing
- Interview-conversion strength (compelling, credible, memorable)

### Supporting Aggregate Profiles

| Profile | Purpose |
|---------|---------|
| `rg_resume_merge_consistency` | Cross-section field consistency |
| `rg_resume_ats_balance` | Keyword coverage vs. readability |
| `rg_resume_repetition_contradiction` | Detect same claim in multiple sections; detect date/title conflicts |
| `rg_resume_narrative_coherence` | Story arc integrity from header through experience |

### AggregateBenchmarkSet Schema

```python
@dataclass(frozen=True)
class AggregateBenchmarkSet:
    benchmark_set_id: str                              # canonical ID
    target_role_family: str                            # e.g., "AI_executive"
    positive_full_resume_examples: List[ResumeExample]   # strong complete resumes
    negative_full_resume_examples: List[ResumeExample]   # weak/problematic complete resumes
    section_overfit_examples: List[ResumeExample]     # strong sections, weak whole
    keyword_stuffed_examples: List[ResumeExample]     # ATS-heavy, human-hostile
    generic_summary_examples: List[ResumeExample]     # bland, unmemorable
    strong_sections_weak_whole_examples: List[ResumeExample]  # excellent bullets, no arc
    human_score_refs: List[str]                        # human evaluator references
    version: str
```

---

## SectionArtifact and Writeback Candidate Model

### SectionArtifact Schema

```python
@dataclass(frozen=True)
class SectionArtifact:
    section_id: str                                    # canonical section ID
    priority_tier: Literal["P0", "P1", "P2"]          # assigned tier
    section_payload_ref: str                           # pointer to generated content
    section_payload_digest: str                        # cryptographic hash
    prompt_profile_id: str                             # PA profile used
    prompt_hash: str                                   # PA compilation hash
    evidence_refs: List[str]                           # C0 evidence consumed
    scorer_profile_id: str                           # X1B/X1D rubric applied
    benchmark_set_id: str                            # benchmark set referenced
    seed_set_id: str                                 # seeds used
    x1b_result_ref: Optional[str]                   # X1B evaluation receipt
    x1d_result_ref: Optional[str]                   # X1D evaluation receipt
    g21_result_ref: Optional[str]                   # G21 schema validation receipt
    g22_result_ref: Optional[str]                   # G22 factual_grounding receipt
    retry_count: int                                  # number of regeneration attempts
    terminal_class: Literal["PASS", "FAIL", "UNKNOWN"]  # final disposition
    decisive_reason: str                              # why this classification
    semantic_cache_candidate_ref: Optional[str]      # inert cache candidate pointer
    vector_index_candidate_ref: Optional[str]        # inert vector index candidate pointer
```

### SectionWritebackCandidate Schema

```python
@dataclass(frozen=True)
class SectionWritebackCandidate:
    candidate_id: str                                  # canonical candidate ID
    section_id: str                                    # source section
    target_role_profile_hash: str                      # role that triggered generation
    section_payload_digest: str                        # content hash
    prompt_hash: str                                   # prompt hash
    evidence_refs: List[str]                         # evidence used
    scorer_profile_id: str                           # rubric applied
    benchmark_set_id: str                            # benchmarks used
    seed_set_id: str                                 # seeds used
    quality_score: float                               # composite X1B/X1D score
    factual_grounding_score: float                     # G22 score
    reuse_eligibility: Literal["eligible", "conditional", "ineligible"]
    embedding_text: str                                # text for vector embedding
    embedding_metadata: Dict[str, Any]               # namespace, tags, version
    cache_key_material: Dict[str, Any]               # fields for cache keying
    vector_namespace: str                              # target vector collection
    write_scope: Literal["section_only", "section_plus_context"]
    inert_until_exit_uwg: bool = True                 # HARD RULE: no direct write
```

### AggregateWritebackCandidate Schema

```python
@dataclass(frozen=True)
class AggregateWritebackCandidate:
    candidate_id: str                                  # canonical candidate ID
    final_resume_id: str                             # aggregate resume reference
    target_role_profile_hash: str                      # role that triggered generation
    section_artifact_refs: List[str]                   # all section artifacts included
    aggregate_x1b_result_ref: str                      # aggregate X1B receipt
    aggregate_x1d_result_ref: str                    # aggregate X1D receipt
    g24_result_ref: str                              # G24 per-input hash receipt
    g28_result_ref: str                              # G28 audit-ref coverage receipt
    full_resume_digest: str                          # cryptographic hash of final JSON
    semantic_cache_candidate_ref: Optional[str]      # inert cache candidate pointer
    vector_index_candidate_ref: Optional[str]        # inert vector index candidate pointer
    reuse_eligibility: Literal["eligible", "conditional", "ineligible"]
    inert_until_exit_uwg: bool = True                 # HARD RULE: no direct write
```

### Hard Rule: No Direct Writeback

**No SectionArtifact, SectionWritebackCandidate, AggregateWritebackCandidate, scorer, merge step, PA, C0, L2, or L6 component may write directly to semantic cache, vector DB, or L4.**

**Correct Write Path:**

```
SectionArtifact / AggregateArtifact
  → Exit validation
  → CommitRequest candidate
  → UWG (Universal Write Gate)
  → L4 semantic cache / vector surfaces
```

---

## MergedResumeArtifact

**Hard Rule:** SectionArtifact pass does NOT authorize final output. MergedResumeArtifact must pass aggregate review and Exit before user release or writeback.

### MergedResumeArtifact Schema

```python
@dataclass(frozen=True)
class MergedResumeArtifact:
    final_resume_id: str                               # canonical aggregate resume ID
    target_role_profile_hash: str                        # role that triggered generation
    section_artifact_refs: List[str]                     # all SectionArtifacts included in merge
    merge_profile_id: str                              # merge configuration used
    merged_payload_ref: str                              # pointer to final assembled resume
    merged_payload_digest: str                         # cryptographic hash of final JSON
    aggregate_x1b_result_ref: str                        # aggregate X1B evaluation receipt
    aggregate_x1d_result_ref: str                      # aggregate X1D evaluation receipt
    g21_result_ref: str                                # G21 schema validation receipt
    g22_result_ref: str                                # G22 factual_grounding receipt (0.950 threshold)
    g24_result_ref: str                                # G24 per-input hash receipt
    g28_result_ref: str                                # G28 audit-ref coverage receipt
    aggregate_writeback_candidate_ref: Optional[str]   # inert aggregate writeback candidate
    terminal_class: Literal["PASS", "FAIL", "UNKNOWN"]  # final disposition
    decisive_reason: str                               # why this classification
    inert_until_exit_uwg: bool = True                  # HARD RULE: no direct write
```

**Explanation:**
- Section-level pass does not imply aggregate pass.
- Aggregate pass does not erase section failures (attribution preserved).
- Final output requires explicit Exit validation before release.

---

## L6 Shadow Learning for Section and Aggregate Resume

L6 evaluates completed runs only. No current-run rescue. All proposed learning routes through gauntlet/UWG/L4.

### SectionCompletedEvalRecord Schema

```python
@dataclass(frozen=True)
class SectionCompletedEvalRecord:
    section_id: str                                    # section evaluated
    priority_tier: Literal["P0", "P1", "P2"]          # assigned tier
    prompt_profile_id: str                           # PA profile used
    scorer_profile_id: str                           # rubric applied
    benchmark_set_id: str                            # benchmarks referenced
    seed_set_id: str                                 # seeds used
    x1b_result: Dict[str, Any]                       # full X1B evaluation
    x1d_result: Dict[str, Any]                       # full X1D evaluation
    g21_result: Dict[str, Any]                       # schema validation result
    g22_result: Dict[str, Any]                       # factual_grounding result
    retry_count: int                                  # regeneration attempts
    failure_reason: Optional[str]                      # if terminal_class=FAIL
    judge_disagreement: Optional[str]                # if judge variance detected
    human_override_if_any: Optional[str]            # HITL intervention record
    final_section_used_in_merge: bool                # was this the section that made it?
    suggested_future_prompt_change_ref: Optional[str]   # proposal only
    suggested_future_rubric_change_ref: Optional[str]       # proposal only
    suggested_future_benchmark_change_ref: Optional[str]    # proposal only
    suggested_future_evidence_change_ref: Optional[str]     # proposal only
```

### AggregateCompletedEvalRecord Schema

```python
@dataclass(frozen=True)
class AggregateCompletedEvalRecord:
    final_resume_id: str                             # aggregate resume evaluated
    target_role_profile_hash: str                      # role that triggered generation
    section_artifact_refs: List[str]                   # all sections in final merge
    merge_profile_id: str                            # merge configuration used
    aggregate_x1b_result: Dict[str, Any]           # full aggregate X1B evaluation
    aggregate_x1d_result: Dict[str, Any]             # full aggregate X1D evaluation
    g24_result: Dict[str, Any]                       # per-input hash receipt
    g28_result: Dict[str, Any]                       # audit-ref coverage receipt
    repetition_score: float                            # cross-section claim overlap
    contradiction_score: float                       # detected conflict severity
    ats_balance_score: float                         # keyword density vs. readability
    narrative_coherence_score: float                 # story arc strength
    interview_conversion_score: float                # compelling/memorable signal
    human_feedback_if_available: Optional[str]       # post-hoc human evaluation
    future_run_proposal_refs: List[str]              # proposed improvements (inert)
```

### Hard L6 Rule

```
RuntimeExhaustBundle (current-run complete)
  → L6 completed-run evaluation
  → ProposalPacket (prompt/rubric/benchmark/evidence change suggestions)
  → gauntlet/regression proof
  → FutureRunPromotionRequest
  → UWG
  → L4 (if approved)
```

**L6 CANNOT:**
- Patch current-run prompts
- Modify current-run rubrics
- Update cache/vector DB/memory/policy/registry directly
- Rescue a failing current run

**L6 CAN:**
- Record completed-run evaluation
- Suggest future-run improvements
- Route proposals through proper gating (gauntlet → UWG → L4)

---

## Design Invariants

These invariants govern all Golden State implementation:

| Invariant | Enforcement |
|-----------|-------------|
| **INV-1** | Section-level pass does not imply aggregate pass. |
| **INV-2** | Aggregate pass does not erase section failures. |
| **INV-3** | G22 factual_grounding = 0.950 applies to every claim-bearing section AND aggregate output where claims are merged or transformed. |
| **INV-4** | G24/G28 remain whole-run invariants — run at aggregate time, not per-section. |
| **INV-5** | P0 sections get bespoke rubrics and richer benchmarks. |
| **INV-6** | P1 sections promoted only by target_role_profile conditions (not by scorer discretion). |
| **INV-7** | P2 sections never receive subjective-quality retry by default. |
| **INV-8** | Every section failure must retain section_id attribution in all receipts. |
| **INV-9** | Every aggregate failure must retain section_artifact_refs in all receipts. |
| **INV-10** | No writeback bypasses Exit/UWG/L4 — all candidates inert until proper gating. |
| **INV-11** | L6 learning is future-run only — no current-run rescue. |
| **INV-12** | No direct writes to semantic cache/vector DB from section loop, scorer, merge, L2, PA, C0, or L6. |
| **INV-13** | L6 produces SectionCompletedEvalRecord for every SectionArtifact consumed. |
| **INV-14** | L6 produces AggregateCompletedEvalRecord for every MergedResumeArtifact consumed. |
| **INV-15** | ProposalPackets are inert until promoted through gauntlet → UWG → L4. |
| **INV-16** | All accepted learning changes route through FutureRunPromotionRequest/UWG/L4. |
| **INV-17** | G22 threshold 0.950 is never modified by L6 proposals. |

---

## Acceptance Criteria

The hardened design satisfies these acceptance criteria:

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-1 | P0 sections have bespoke X1B/X1D scorer profiles | Review SectionSpec.scorer_profile_id for P0 sections |
| AC-2 | InsurTech and EY use shared `shared_experience_x1bd` profile unless activated by target_role_profile | Unit test: promotion_conditions matching logic |
| AC-3 | Early Career uses `basic_compactness` checks only — no bespoke X1B/X1D | Review SectionSpec for P2 sections |
| AC-4 | G22 `factual_grounding` threshold remains at 0.950 for all claim-bearing sections | Hard constraint verification; no threshold drift |
| AC-5 | No new `agentic_core` behavior added — all scoring logic lives in `apps_rg/runtime/scoring/` | ADG query: `apps_rg` nodes only; no new `agentic_core` edges |
| AC-6 | Plan remains design-only — no runtime code changes | File diff inspection; only markdown modified |
| AC-7 | Tests can verify tier assignment deterministically | SectionSpec includes deterministic promotion logic; testable without LLM |
| AC-8 | Section-level attribution preserved for all failures — scorer identifies specific section ID | SectionSpec.section_id threaded through all scorer receipts |
| AC-9 | Retry policy by tier is explicit and enforceable | RetryPolicy dataclass with boolean flags; built by planner, not field default |
| AC-10 | Non-goal documented: "No equal-weight bespoke rubric for every resume section" | Explicit non-goal in plan §Non-Goals |
| AC-11 | No X1D-only scorer naming remains in design | All references updated to X1B/X1D or section_scorer.py |
| AC-12 | Section-level retry for P0 (not whole-resume retry) | P0 retry policy specifies section-level regeneration only |
| AC-13 | SectionBenchmarkSet exists in design | Schema defined in §Section Benchmark and Seed Model |
| AC-14 | SectionSeedSet exists in design | Schema defined in §Section Benchmark and Seed Model |
| AC-15 | AggregateResumeScorer profiles are defined | rg_resume_aggregate_x1b and rg_resume_aggregate_x1d profiles in §Aggregate Resume Review After Merge |
| AC-16 | AggregateBenchmarkSet is defined | Schema defined in §Aggregate Resume Review After Merge |
| AC-17 | SectionArtifact includes benchmark_set_id and seed_set_id | Schema inspection |
| AC-18 | Section writeback candidates are inert until Exit/UWG | inert_until_exit_uwg = True in SectionWritebackCandidate schema |
| AC-19 | Aggregate writeback candidates are inert until Exit/UWG | inert_until_exit_uwg = True in AggregateWritebackCandidate schema |
| AC-20 | SectionCompletedEvalRecord is defined for L6 | Schema defined in §L6 Shadow Learning |
| AC-21 | AggregateCompletedEvalRecord is defined for L6 | Schema defined in §L6 Shadow Learning |
| AC-22 | Whole-resume aggregate scoring is mandatory after merge | Explicit rule in §Aggregate Resume Review After Merge |
| AC-23 | Section-level pass does not imply aggregate pass | Design Invariant INV-1 |
| AC-24 | L6 cannot patch current-run prompts/rubrics/cache/vector/memory/policy/registry directly | Hard L6 Rule in §L6 Shadow Learning |
| AC-25 | Current Rebaselined State After W2D is documented | Section exists in plan with migration status for each binding |
| AC-26 | MergedResumeArtifact schema exists | Schema defined in §MergedResumeArtifact |
| AC-27 | Benchmark thresholds cannot override G22 or runtime gate thresholds | Benchmark Thresholds Clarification rule in §Section Benchmark and Seed Model |
| AC-28 | Seed support status is recorded when deterministic provider seeding is not available | `seed_support_status` field in SectionSeedSet schema |
| AC-29 | W5C proves inert writeback candidate emission, not schema-only design | Wave Structure clarification note and W5C title |
| AC-30 | W7 proves L6 future-run proposal path, not current-run rescue | Wave Structure clarification note and W7 title |
| AC-31 | SectionCompletedEvalRecord is produced for every SectionArtifact | W7 detailed proof; SectionCompletedEvalRecord inventory |
| AC-32 | AggregateCompletedEvalRecord is produced for every MergedResumeArtifact | W7 detailed proof; AggregateCompletedEvalRecord inventory |
| AC-33 | ProposalPackets are inert until FutureRunPromotionRequest | W7 detailed proof; inertness verification |
| AC-34 | L6 runs only after RuntimeExhaustBundle/current-run boundary | W7 detailed proof; boundary verification |
| AC-35 | No L6 direct writes to semantic cache, vector DB, memory, policy, registry, or L4 | W7 detailed proof; no-direct-write assertion |
| AC-36 | No L6 current-run rescue, retry, prompt patch, rubric patch, or merge patch | W7 detailed proof; no-current-run-rescue assertion |
| AC-37 | G22 factual_grounding remains 0.950 through all L6 proposals | W7 detailed proof; G22 threshold unchanged assertion |
| AC-38 | All accepted learning changes route through UWG → L4 | W7 detailed proof; FutureRunPromotionRequest/UWG/L4 refs |
| AC-39 | Benchmark thresholds remain separate from runtime gate thresholds | W7 detailed proof; threshold-confusion failure classification |

---

## W7 Detailed Proof Plan — L6 Shadow Learning and Future-Run Proposal Path

### W7 Objective

W7 proves that completed apps_rg runs produce section-level and aggregate-level L6 shadow learning records after the current-run boundary, and that any learning output remains future-run-only until promoted through gauntlet, UWG, and L4.

### W7 Non-Negotiable Boundary

- L6 consumes RuntimeExhaustBundle only after Exit completes the current run.
- L6 may evaluate section artifacts and aggregate artifacts.
- L6 may produce completed evaluation records.
- L6 may produce inert ProposalPackets.
- L6 may not mutate current-run output.
- L6 may not trigger retries.
- L6 may not modify section prompts, scorer profiles, benchmark sets, seed sets, merge rules, cache, vector DB, memory, policy, or registry directly.
- L6 may not write L4 directly.
- All accepted changes require FutureRunPromotionRequest → UWG → L4.

### W7 Inputs

| Input | Required fields | Purpose |
|---|---|---|
| RuntimeExhaustBundle | run_id, request_id, trace_root, exit_disposition_ref, section_artifact_refs, merged_resume_artifact_ref | Completed-run boundary input |
| SectionArtifact[] | section_id, priority_tier, prompt_profile_id, scorer_profile_id, benchmark_set_id, seed_set_id, x1b_result_ref, x1d_result_ref, g21_result_ref, g22_result_ref, retry_count | Per-section learning evidence |
| MergedResumeArtifact | final_resume_id, section_artifact_refs, aggregate_x1b_result_ref, aggregate_x1d_result_ref, g21/g22/g24/g28 refs | Aggregate resume learning evidence |
| Human feedback, if available | reviewer, feedback type, affected sections, aggregate comments | Optional calibration evidence |
| Benchmark/Judge metadata | benchmark_set_id, seed_set_id, scorer_profile_id, judge refs | Drift and calibration evidence |

### W7 Section-Level Shadow Learning

| Section tier | Sections | W7 evaluates | Example learning signal |
|---|---|---|---|
| P0 | headline, executive_summary, unify_narrative, competencies_ats, IBM | prompt fit, rubric sensitivity, benchmark fit, judge disagreement, retry cause, factual grounding, interview signal | P0 prompt too generic, scorer missed vague content, IBM proof should be foregrounded |
| P1 | InsurTech, EY | promotion rule accuracy, compression vs. expansion, target-role relevance, factual grounding | EY should promote only for advisory/transformation roles |
| P2 | Early Career, Education, low-signal certs/background | compactness, factual accuracy, non-distraction, omission/compression suitability | Early Career should compress further for AI platform roles |

### W7 SectionCompletedEvalRecord Production

W7 must produce one SectionCompletedEvalRecord for every SectionArtifact included in the RuntimeExhaustBundle.

Required record content:
- section_id
- priority_tier
- prompt_profile_id
- scorer_profile_id
- benchmark_set_id
- seed_set_id
- x1b_result
- x1d_result
- g21_result
- g22_result
- retry_count
- terminal_class
- decisive_reason
- failure_reason
- judge_disagreement
- human_override_if_any
- final_section_used_in_merge
- suggested_future_prompt_change_ref
- suggested_future_rubric_change_ref
- suggested_future_benchmark_change_ref
- suggested_future_evidence_change_ref

### W7 Aggregate-Level Shadow Learning

| Aggregate signal | W7 evaluates | Example learning signal |
|---|---|---|
| aggregate_x1b_result | Did final resume satisfy deliverable, schema, section order, target instructions? | Merge created malformed or missing section |
| aggregate_x1d_result | Is the whole resume coherent, senior, credible, and compelling? | Strong sections but weak overall story |
| repetition_score | Cross-section duplicate claims | IBM claim repeated in summary and experience |
| contradiction_score | Role/date/title/company conflicts | Section claims conflict across roles |
| ats_balance_score | Keyword coverage vs. readability | Competencies overfit ATS keywords |
| narrative_coherence_score | Story arc from headline through experience | Resume feels fragmented |
| interview_conversion_score | Likelihood of earning a conversation | Strong facts but weak executive positioning |
| human_feedback_if_available | Post-hoc calibration | Human preferred lower-key InsurTech section |

### W7 AggregateCompletedEvalRecord Production

W7 must produce exactly one AggregateCompletedEvalRecord for each MergedResumeArtifact.

Required record content:
- final_resume_id
- target_role_profile_hash
- section_artifact_refs
- merge_profile_id
- aggregate_x1b_result
- aggregate_x1d_result
- g21_result
- g22_result
- g24_result
- g28_result
- repetition_score
- contradiction_score
- ats_balance_score
- narrative_coherence_score
- interview_conversion_score
- human_feedback_if_available
- future_run_proposal_refs

### W7 ProposalPacket Types

| Proposal type | Trigger | Example |
|---|---|---|
| PROMPT_CHANGE | section prompt repeatedly produces generic or weak output | tighten executive summary prompt |
| RUBRIC_CHANGE | scorer misses obvious weakness or over-penalizes good section | penalize generic headline phrasing harder |
| BENCHMARK_CHANGE | benchmark set lacks relevant positive/negative examples | add keyword-stuffed resume negatives |
| EVIDENCE_CHANGE | section lacks strong support for claim-bearing content | improve IBM evidence selectors |
| MERGE_RULE_CHANGE | aggregate coherence/repetition failures | suppress repeated platform-governance phrase |
| PROMOTION_RULE_CHANGE | P1 section promotion too broad or too narrow | promote EY only for advisory/control roles |
| CACHE_INDEX_POLICY_CHANGE | reuse eligibility too permissive or too strict | require target_role_profile_hash match for section cache reuse |
| JUDGE_PROFILE_CHANGE | judge disagreement or drift detected | recalibrate headline judge against human labels |

### W7 Future-Run Promotion Path

```
RuntimeExhaustBundle
  → SectionCompletedEvalRecord[]
  → AggregateCompletedEvalRecord
  → ProposalPacket[]
  → replay/regression/safety gauntlet
  → FutureRunPromotionRequest
  → UWG
  → L4
  → active only at future run_start
```

No ProposalPacket is active by default.
No proposal can affect the completed run that produced it.
No proposal can affect the next run until UWG admits it and L4 stores the approved promoted object.

### W7 Anti-Bypass Proofs

Required proofs:
- proof L6 ran only after RuntimeExhaustBundle/current-run boundary
- proof every SectionArtifact has one SectionCompletedEvalRecord
- proof every MergedResumeArtifact has one AggregateCompletedEvalRecord
- proof proposals are inert before FutureRunPromotionRequest
- proof no L6 component wrote to cache/vector DB/L4 directly
- proof no L6 output modified current-run response
- proof no L6 output triggered live retry/regeneration
- proof all accepted learning changes route through UWG/L4
- proof G22 remains 0.950 and is not modified by L6 proposals
- proof benchmark thresholds remain separate from runtime gate thresholds

### W7 Failure Classifications

| Failure | Classification | Required result |
|---|---|---|
| Missing section eval record | W7_FAIL_SECTION_EVAL_MISSING | Block W7 proof |
| Missing aggregate eval record | W7_FAIL_AGGREGATE_EVAL_MISSING | Block W7 proof |
| L6 ran before runtime boundary | W7_FAIL_BOUNDARY_BREACH | Hard fail |
| Proposal mutates current run | W7_FAIL_CURRENT_RUN_RESCUE | Hard fail |
| Direct cache/vector/L4 write detected | W7_FAIL_DIRECT_WRITE_BYPASS | Hard fail |
| Proposal missing gauntlet refs | W7_FAIL_PROMOTION_UNSAFE | Block promotion |
| G22 threshold changed | W7_FAIL_THRESHOLD_DRIFT | Hard fail |
| Benchmark threshold used as gate threshold | W7_FAIL_THRESHOLD_CONFUSION | Hard fail |
| apps_rg code detected in agentic_core after migration | FAIL_CORE_BOUNDARY | Hard fail — must migrate to apps_rg/runtime/ using U0 pattern |
| New apps_rg import added to agentic_core | FAIL_CORE_IMPORT | Hard fail — revert and migrate to apps_rg/runtime/ |
| SectionSpec resolved from agentic_core instead of apps_rg | FAIL_SECTIONSPEC_SOURCE | Hard fail — SectionSpec must be app-owned |
| apps_rg scorer profile loaded from agentic_core | FAIL_SCORER_PROFILE_SOURCE | Hard fail — profiles must be app-owned |
| U0 package attempting to set final route authority | FAIL_U0_AUTHORITY | Hard fail — U0 may hint, not decide |
| U0 package attempting to authorize writeback | FAIL_U0_WRITEBACK | Hard fail — U0 may not bypass Exit/UWG/L4 |

### W7 Evidence Artifact

Expected artifact:
`artifacts/apps_rg/golden_state_w7_l6_shadow_learning_proof.md`

Required contents:
- run_id / request_id / trace_root
- RuntimeExhaustBundle ref
- SectionArtifact inventory
- SectionCompletedEvalRecord inventory
- MergedResumeArtifact ref
- AggregateCompletedEvalRecord ref
- ProposalPacket inventory
- FutureRunPromotionRequest refs if any
- UWG/L4 refs if any accepted
- anti-bypass proof table
- failure classification table
- no-current-run-rescue assertion
- no-direct-write assertion
- G22 threshold unchanged assertion

### W7 Acceptance Criteria

- W7-AC-1: every SectionArtifact has exactly one SectionCompletedEvalRecord
- W7-AC-2: every MergedResumeArtifact has exactly one AggregateCompletedEvalRecord
- W7-AC-3: L6 consumes only RuntimeExhaustBundle after current-run boundary
- W7-AC-4: L6 proposals are inert until FutureRunPromotionRequest/UWG/L4
- W7-AC-5: no L6 direct writes to semantic cache, vector DB, memory, policy, registry, or L4
- W7-AC-6: no L6 current-run rescue, retry, prompt patch, rubric patch, or merge patch
- W7-AC-7: proposal types are classified and traceable to section or aggregate evidence
- W7-AC-8: judge disagreement and benchmark drift are recorded where applicable
- W7-AC-9: G22 remains 0.950
- W7-AC-10: benchmark thresholds are not treated as runtime gate thresholds

---

## Final Plan Freeze Rule

This plan is frozen after the W7 detailed proof section is added.

Allowed future edits:
- evidence updates from completed waves
- status updates from TODO to DONE after successful execution
- correction of factual mistakes discovered during implementation
- blocker disposition updates with evidence

Disallowed future edits without a new rebaseline:
- new runtime stages
- new scorer families
- new writeback paths
- new cache/vector write paths
- new L6 current-run behavior
- new agentic_core app-specific behavior
- G22 threshold change
- route-label canonicalization

---

## Implementation Readiness Gate

Before W3B/W4 section-generation runtime implementation begins, the following must be true:

| Gate | Requirement |
|---|---|
| IRG-1 | W2E L2 binding migration complete |
| IRG-2 | W2F Exit binding migration complete |
| IRG-3 | W2G app-owned dispatch created and python -m apps_rg uses app-owned dispatch |
| IRG-4 | W3A schemas finalized for SectionSpec, SectionArtifact, MergedResumeArtifact, writeback candidates, and L6 records |
| IRG-5 | G22 factual_grounding remains 0.950 |
| IRG-6 | No apps_rg implementation logic remains in agentic_core except approved temporary shims |
| IRG-7 | Dispatch missing-source blocker resolved |
| IRG-8 | Exit circular import risk resolved |
| IRG-9 | Section and aggregate writeback candidates are defined as inert |
| IRG-10 | L6 future-run-only proposal path is defined and anti-bypass proofs are specified |
| IRG-11 | Core boundary audit passes — `python ops_scripts/ci/check_agentic_core_addition.py --app apps_rg` shows zero ERROR (no leakage) |
| IRG-12 | No new `apps_rg` imports or semantics exist in `agentic_core` beyond approved temporary shims |
| IRG-13 | Required generic core changes are blocked pending separate generic-core review — `CORE_BOUNDARY_REVIEW_REQUIRED` disposition recorded |

If any IRG gate fails, section-generation implementation must not begin.

---

## Receipt Inventory

Every wave must produce a named evidence artifact.

| Wave | Required evidence artifact |
|---|---|
| W2E | artifacts/apps_rg/golden_state_w2e_l2_migration_evidence.md |
| W2F | artifacts/apps_rg/golden_state_w2f_exit_migration_evidence.md |
| W2G | artifacts/apps_rg/golden_state_w2g_dispatch_creation_evidence.md |
| W3A | artifacts/apps_rg/golden_state_w3a_schema_design_evidence.md |
| W3B | artifacts/apps_rg/golden_state_w3b_section_planner_evidence.md |
| W4 | artifacts/apps_rg/golden_state_w4_section_runtime_evidence.md |
| W5 | artifacts/apps_rg/golden_state_w5_section_scorer_evidence.md |
| W5B | artifacts/apps_rg/golden_state_w5b_aggregate_scorer_evidence.md |
| W5C | artifacts/apps_rg/golden_state_w5c_writeback_inertness_evidence.md |
| W6 | artifacts/apps_rg/golden_state_w6_gate_verification_evidence.md |
| W7 | artifacts/apps_rg/golden_state_w7_l6_shadow_learning_proof.md |

Each evidence artifact must include:
- files changed
- commands run
- import verification
- test output
- skipped commands with reason
- gate/threshold unchanged assertion
- G22 remains 0.950 assertion
- no direct writeback assertion where applicable
- core boundary audit result (no apps_rg leakage in agentic_core)
- **CORE_BOUNDARY_PASS** or **CORE_BOUNDARY_FAIL**
- command output from: `python ops_scripts/ci/check_agentic_core_addition.py --app apps_rg`
- statement: *"No new agentic_core behavior added; only approved temporary shim changes occurred."*
- W-next readiness recommendation

---

## Section-to-Aggregate Traceability Matrix

Every generated section must be traceable from SectionSpec to SectionArtifact to MergedResumeArtifact to L6.

Required chain:

```
SectionSpec
  → section-scoped PA packet
  → L2 section output
  → SectionArtifact
  → section X1B/X1D/G21/G22 receipts
  → MergedResumeArtifact.section_artifact_refs
  → aggregate X1B/X1D/G21/G22/G24/G28 receipts
  → ExitDispositionReceipt
  → RuntimeExhaustBundle
  → SectionCompletedEvalRecord
  → AggregateCompletedEvalRecord
  → ProposalPacket, if any
  → FutureRunPromotionRequest, if promoted
  → UWG/L4, if admitted
```

Hard rule:
A section may not be reused, cached, indexed, learned from, or merged unless its section_id and artifact digest are preserved through this chain.

---

## Required Negative Controls

Add these negative controls to W6/W7 proof expectations:

| Negative control | Expected result |
|---|---|
| SectionArtifact without section_id | Fail |
| SectionArtifact without g22_result_ref for claim-bearing content | Fail |
| MergedResumeArtifact missing SectionArtifact refs | Fail |
| Aggregate pass tries to erase section failure | Fail |
| Section writeback candidate writes directly to cache/vector DB | Fail |
| Aggregate writeback candidate writes directly to cache/vector DB | Fail |
| L6 ProposalPacket mutates current run | Fail |
| L6 writes directly to L4 | Fail |
| Benchmark threshold used as G22 threshold | Fail |
| G22 factual_grounding changed below 0.950 | Fail |
| Runtime proceeds with missing aggregate scorer receipt | Fail |
| Exit releases final resume without MergedResumeArtifact | Fail |

---

## Final Non-Expansion Rule

After this patch, do not add new design surfaces to this plan.

Any new concern must become either:
1. a blocker disposition inside the current wave, or
2. a separate follow-up plan after Golden State migration reaches W7 proof.
