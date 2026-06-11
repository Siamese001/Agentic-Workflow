---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\deferred-scope-ds2-ds3-ds7-c9e4f1.md'
original_relative_path: 'deferred-scope-ds2-ds3-ds7-c9e4f1.md'
source_sha256: caff9347bb406fe5edd70906dfdd3d3cc3ba52c6624884bdeebe6b18165a0fbd
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deferred Scope — DS-2, DS-3, DS-7 Backlog

> **Status:** Not Started · **Tier:** T2 · **Slug:** `deferred-scope-ds2-ds3-ds7-c9e4f1`
> **Parent:** `apps-repo-brief-closeout-impl-b3e7a2` (Completed 2026-05-05)
> **Purpose:** Capture remaining deferred scope items from the apps-repo-brief closeout implementation plan that were not implemented. **No implementation in this document.**

---

## 1. Context

The `apps-repo-brief-closeout-impl-b3e7a2` plan completed all high/medium priority waves (DS-4, DS-5, DS-6, DS-1). The following lower-priority items remain unimplemented and are tracked here for future planning.

| Completed | Deferred (this plan) |
|-----------|---------------------|
| DS-4 ✅ — underwriting plan status sync | DS-2 — `apps_repo_brief` real C0 retrieval |
| DS-5 ✅ — P0 ADG violations (resolved in ADG 0722) | DS-3 — `apps_repo_brief` L3 managed workflow adapter |
| DS-6 ✅ — underwriting spine allowlist burned down | DS-7 — `apps_eval` phase 2 (AE-1/2/3/4/5/6) |
| DS-1 ✅ — `apps_repo_brief` FEC producer live + tests | |

---

## 2. Deferred Scope Registry

### DS-2 — `apps_repo_brief` Real C0 Retrieval Lane Integration

**Source:** `apps-repo-brief-deferred-scope-closeout-a7d2f1` DS-2
**Priority:** P4
**Description:** `apps_repo_brief/c0/repo_brief_c0_adapter.py` defines `C0_RETRIEVAL_LANES` and builds `C0RequestSpec` but no runtime invocation of `run_c0` is wired into the spine handoff or governed run path. The `spine_handoff.py` `run_repo_brief_via_spine` is a stub delegate only — it does not invoke C0 retrieval.
**Scope:**
- Wire `run_repo_brief_via_spine` to invoke C0 retrieval via `run_c0` when `c0_required=True`
- Populate `FinalEvidenceContract` from C0 output
- Update `governed_exec_run.py` to thread C0 result into exit pipeline
**Blocking:** No
**Recommended plan slug:** `apps-repo-brief-c0-runtime-wiring-<6hex>`
**Est. tokens:** ~10k

---

### DS-3 — `apps_repo_brief` L3 Managed Workflow Adapter

**Source:** `apps-repo-brief-deferred-scope-closeout-a7d2f1` DS-3
**Priority:** P4
**Description:** `apps_repo_brief` currently uses a direct orchestration path. The canonical spine pattern (`apps_underwriting_ai`, `apps_rfp`) uses an L3 managed workflow adapter (`underwriting_l3_workflow_adapter.py`) that expands into E-stage receipts via L2 step adapters. `apps_repo_brief` has no equivalent.
**Scope:**
- Create `apps_repo_brief/integrations/repo_brief_l3_workflow_adapter.py` (expands 3 stages: C0 retrieval, prompt assembly, exit)
- Create `apps_repo_brief/integrations/repo_brief_l2_step_adapters.py` (E1–E3 receipts)
- Governance tests for L3 expands-not-executes invariant
**Blocking:** No (DS-2 is a natural prerequisite)
**Recommended plan slug:** `apps-repo-brief-l3-workflow-<6hex>`
**Est. tokens:** ~15k

---

### DS-7 — `apps_eval` Harness Phase 2 (6 open items)

**Source:** `apps-eval-harness-parity-f8d4a2`, `apps-eval-harness-deferred-e4a1b7`, `apps-eval-harness-closeout-b7c9d2`
**Priority:** P3–P4
**Description:** 6 items explicitly deferred from the eval harness work. All advisory — no CI gate is currently failing because of these.

| ID | Item | Priority |
|----|------|----------|
| AE-1 | W5.P1 holdout vs dev eval-set separation | P3 |
| AE-2 | W5.P2 production-log mining with PII redaction | P3 |
| AE-3 | Real LLM-judge scoring logic (4 stubs: `executive_positioning`, `response_likelihood`, `brand_voice`, `win_theme_alignment`) — Spearman ≥ 0.80 calibration required | P3 |
| AE-4 | W5.P4 SSOT consolidation of legacy policy/threshold YAMLs | P4 |
| AE-5 | Per-app rubric migrations to new grader types (`tool_calls`, `state_check`, `transcript`) | P4 |
| AE-6 | 70 taxonomy_class annotation backlog (INFO-level gate findings, advisory only) | P4 |

**Blocking:** None — all advisory gate WARNs. AE-3 stubs are `IS_STUB=True`; `NO_UNIMPL_JUDGES` gate is green.
**Recommended plan slug:** `apps-eval-harness-phase2-<6hex>`
**Est. tokens:** ~40k (AE-1/2/3 alone; AE-4/5/6 additional)

---

## 3. Priority Matrix

| ID | Item | Priority | Blocking | Notes |
|----|------|----------|----------|-------|
| DS-7 (AE-1/2/3) | `apps_eval` real judges + holdout | P3 | No | Requires Spearman calibration |
| DS-2 | `apps_repo_brief` C0 runtime wiring | P4 | No | Prerequisite for DS-3 |
| DS-3 | `apps_repo_brief` L3 workflow adapter | P4 | No | Requires DS-2 first |
| DS-7 (AE-4/5/6) | SSOT consolidation + rubric migration | P4 | No | Advisory only |

---

## 4. Wave Structure (planning only — no implementation here)

| Wave | Scope | Est. Tokens | Status |
|------|-------|-------------|--------|
| N/A | This is a planning-only document | — | Not Started |

---

## 5. Non-Goals

- No implementation of any DS item in this document
- No changes to the completed closeout work (DS-1/DS-4/DS-5/DS-6)
- No new canonical route families
- DS-8 (`apps_exec`/`apps_research` exit hook) was confirmed done for `apps_research`; `apps_exec` is archived — not tracked here

---

## 6. AI Summary

- Target: deferred scope backlog for 3 remaining items post-closeout (DS-2, DS-3, DS-7)
- DS-2 and DS-3 are sequential `apps_repo_brief` depth completions (~25k tokens combined)
- DS-7 is a large standalone `apps_eval` phase 2 effort (~40k+ tokens)
- No items are currently blocking CI or app functionality
- All items are advisory/enhancement grade
- Success: all 3 DS items tracked with recommended slugs and token estimates

**PLAN_CREATED:** `.windsurf/plans/deferred-scope-ds2-ds3-ds7-c9e4f1.md`
