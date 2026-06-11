---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\deferred-scope-post-plan4-closeout-a7d2f1.md'
original_relative_path: 'deferred-scope-post-plan4-closeout-a7d2f1.md'
source_sha256: 3920045e75887c10125b7a7e236f5362a5ccfa3c4d0fef71944fbde902f3fe62
recovered_status: LOST_RECOVERED
last_commit: 'eaba307040c'
last_commit_date: '2026-05-05 08:20:41 -0400'
created_date: '2026-05-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deferred Scope — Post-Plan 4 Closeout

> **Status:** Not Started · **Tier:** T2 · **Slug:** `deferred-scope-post-plan4-closeout-a7d2f1`
> **Parent:** `apps-repo-brief-plan4-spine-handoff-f2a3c8` (Completed 2026-05-05)
> **Purpose:** Capture all deferred scope items surfaced during or adjacent to the apps_repo_brief Plan 4 closeout. **No implementation in this document.** Each item has a source plan, priority, and recommended next-plan assignment.

---

## 1. Context

Plan 4 (`apps-repo-brief-plan4-spine-handoff-f2a3c8`) completed 2026-05-05. During execution the following items were explicitly deferred (non-goals) or surfaced as adjacent work needing tracking:

1. `apps_repo_brief` C0 and FEC producer wiring (not built in Plan 3 or Plan 4)
2. `apps_underwriting_ai` spine hardening plan status sync (all waves completed, plan doc stale)
3. 7 pre-existing P0 ADG layer violations blocking full ADG hard-pass
4. `apps_eval` deferred scope items (6 open from parent plans `apps-eval-harness-parity-f8d4a2` and `apps-eval-harness-deferred-e4a1b7`)
5. `apps_underwriting_ai` allowlist expiry (expires 2026-05-31; burndown scheduled but not started)

---

## 2. Deferred Scope Registry

### DS-1 — `apps_repo_brief` C0 FEC Producer Wiring

**Source:** Plan 3 non-goals; Plan 4 non-goals
**Priority:** P3
**Description:** `apps_repo_brief/cert/fec_producer.py` currently produces a stub FEC (retired W4 P4.5). No C0 retrieval sources are wired to `grounded=True`. The `cert_projection_adapter.py` provides a read-only projection but does not mint a live FEC. The canonical pattern exists in `apps_qna`, `apps_research`, `apps_rfp`, `apps_underwriting_ai` (each ~6k tokens following `apps-qna-c0-fec-producer-wiring-d4f1e8` pattern).
**Scope:**
- Wire `apps_repo_brief/cert/fec_producer.py` to produce a live FEC with `grounded=True` when C0 evidence is present
- Add `apps_repo_brief/__main__.py` cert hook adoption (call `maybe_invoke_exit_eval`)
- 7 tests mirroring `test_apps_qna_fec_producer.py` pattern
**Blocking:** No — Plan 4 acceptance already at YES
**Recommended plan slug:** `apps-repo-brief-c0-fec-producer-<6hex>`
**Est. tokens:** ~6k

---

### DS-2 — `apps_repo_brief` Real C0 Retrieval Lane Integration

**Source:** Plan 3 D1 deferred scope DS-4; Plan 4 non-goals
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

**Source:** Plan 3 non-goals; Plan 4 non-goals
**Priority:** P4
**Description:** `apps_repo_brief` currently uses a direct orchestration path. The canonical spine pattern (`apps_underwriting_ai`, `apps_rfp`) uses an L3 managed workflow adapter (`underwriting_l3_workflow_adapter.py`) that expands into E-stage receipts via L2 step adapters. `apps_repo_brief` has no equivalent.
**Scope:**
- Create `apps_repo_brief/integrations/repo_brief_l3_workflow_adapter.py` (expands 3 stages: C0 retrieval, prompt assembly, exit)
- Create `apps_repo_brief/integrations/repo_brief_l2_step_adapters.py` (E1–E3 receipts)
- Governance tests for L3 expands-not-executes invariant
**Blocking:** No
**Recommended plan slug:** `apps-repo-brief-l3-workflow-<6hex>`
**Est. tokens:** ~15k

---

### DS-4 — `apps_underwriting_ai` Spine Hardening Plan Status Sync

**Source:** `apps-underwriting-ai-spine-hardening-d7f3b2` (plan doc stale; all waves completed in commit `af226d3bc0`)
**Priority:** P1 (admin only — no code change)
**Description:** The plan file `.windsurf/plans/apps-underwriting-ai-spine-hardening-d7f3b2.md` still shows all waves as `⬜ Not Started`. All waves (P0/P1/P1.5/W1–W6) are complete and committed. The Notion page `35727693-f55c-8130-860b-c4230416ab18` is still `In Progress`. Requires:
- Update plan file wave table to all `✅ DONE`
- Patch Notion page to `Completed`
- Update AI Summary with actual outcomes
**Blocking:** No — Notion staleness only
**Recommended action:** Inline fixup, no new plan required
**Est. tokens:** ~1k

---

### DS-5 — 7 Pre-existing P0 ADG Layer Violations

**Source:** ADG generation output, F2 session
**Priority:** P2
**Description:** `tools/generate_full_adg.py` exits 1 on 7 unapproved P0 layer violations. These block the ADG hard-pass gate but are pre-existing (predates Plan 4). Files:
- `agentic_core/L0_routing/gates/apps_rg_prerequisite_gate.py:17`
- `agentic_core/runtime/l2_recipe_resolver.py:38`
- `apps_eval/integrations/llm_client.py:11`
- `apps_lic/integrations/llm_client.py:11`
- `apps_research/integrations/llm_client.py:11`
- `apps_rg/integrations/llm_client.py:11`
- `apps_underwriting_ai/integrations/llm_client.py:11`

All 5 `llm_client.py` violations are the same import pattern. `agentic_core/runtime/l2_recipe_resolver.py` and `apps_rg_prerequisite_gate.py` are one-offs. Remediation wave plan: `artifacts/adg/issues/p0_remediation_wave_plan_05052026_0709.md`.
**Blocking:** Blocks full ADG CI hard-pass. Does not block app functionality.
**Recommended plan slug:** `adg-p0-layer-violations-remediation-<6hex>`
**Est. tokens:** ~8k

---

### DS-6 — `apps_underwriting_ai` Spine Delegation Allowlist Expiry

**Source:** `config/apps_spine_delegation_allowlist.yaml` — expires 2026-05-31
**Priority:** P2
**Description:** `apps_underwriting_ai` remains on the spine delegation allowlist (0 spine imports into `agentic_core`). The allowlist entry expires `2026-05-31` — after that date the strict-mode gate exits 1. Burndown was scheduled in plan `adg-three-bucket-unified-c4f8e2` W5 P5.4 but not completed.
**Scope:** Wire `apps_underwriting_ai` imports into `agentic_core` spine via `spine_handoff.py` (same pattern as `apps_repo_brief` F1). Update allowlist.
**Blocking:** Becomes a CI blocker after 2026-05-31
**Recommended plan slug:** `apps-underwriting-ai-spine-delegation-<6hex>`
**Est. tokens:** ~6k (same shape as Plan 4 F1)

---

### DS-7 — `apps_eval` Deferred Scope (6 open items from parent plans)

**Source:** `apps-eval-harness-parity-f8d4a2`, `apps-eval-harness-deferred-e4a1b7`, `apps-eval-harness-closeout-b7c9d2`
**Priority:** P3–P4
**Description:** 6 items explicitly deferred from the eval harness work:

| ID | Item | Priority |
|----|------|----------|
| AE-1 | W5.P1 holdout vs dev eval-set separation | P3 |
| AE-2 | W5.P2 production-log mining with PII redaction | P3 |
| AE-3 | Real LLM-judge scoring logic (4 stubs: `executive_positioning`, `response_likelihood`, `brand_voice`, `win_theme_alignment`) — Spearman ≥ 0.80 calibration required | P3 |
| AE-4 | W5.P4 SSOT consolidation of legacy policy/threshold YAMLs | P4 |
| AE-5 | Per-app rubric migrations to new grader types (`tool_calls`, `state_check`, `transcript`) | P4 |
| AE-6 | 70 taxonomy_class annotation backlog (INFO-level gate findings, advisory only) | P4 |

**Blocking:** None currently — all advisory gate WARNs. AE-3 stubs are `IS_STUB=True`; `NO_UNIMPL_JUDGES` gate is green.
**Recommended plan slug:** `apps-eval-harness-phase2-<6hex>`
**Est. tokens:** ~40k (AE-1/2/3 alone; AE-4/5/6 additional)

---

### DS-8 — `apps_exec` and `apps_research` Exit Hook Adoption

**Source:** `apps-qna-c0-fec-producer-wiring-d4f1e8` session memory
**Priority:** P3
**Description:** `apps_exec` and `apps_research` have FEC producers registered but have NOT adopted `maybe_invoke_exit_eval` in `__main__.py`. Their FEC is computed but never flows into the Exit pipeline. `apps_qna`, `apps_rfp`, `apps_underwriting_ai` are adopted.
**Scope:** 2-file change per app (`__main__.py` + cert hook); 3 tests each following `test_w2p6_cert_hook_e2e.py` pattern.
**Blocking:** No — eval harness gate is advisory
**Recommended plan slug:** `apps-exec-research-exit-hook-adoption-<6hex>`
**Est. tokens:** ~5k

---

## 3. Priority Matrix

| ID | Item | Priority | Blocking | Expires |
|----|------|----------|----------|---------|
| DS-4 | Underwriting plan status sync | P1 | No | N/A |
| DS-5 | 7 P0 ADG layer violations | P2 | CI ADG gate | None |
| DS-6 | Underwriting spine allowlist expiry | P2 | CI after 2026-05-31 | 2026-05-31 |
| DS-1 | `apps_repo_brief` FEC producer | P3 | No | None |
| DS-7 | `apps_eval` phase 2 (AE-1/2/3) | P3 | No | None |
| DS-8 | `apps_exec`/`apps_research` exit hook | P3 | No | None |
| DS-2 | `apps_repo_brief` C0 runtime wiring | P4 | No | None |
| DS-3 | `apps_repo_brief` L3 workflow adapter | P4 | No | None |
| DS-7 | `apps_eval` phase 2 (AE-4/5/6) | P4 | No | None |

---

## 4. Wave Structure (planning only — no implementation here)

| Wave | Scope | Est. Tokens | Status |
|------|-------|-------------|--------|
| N/A | This is a planning-only document | — | Not Started |

---

## 5. Non-Goals

- No implementation of any DS item in this document
- No changes to committed Plan 4 work
- No changes to `agentic_core` routing logic
- No new canonical route families

---

## 6. AI Summary

- Target: deferred scope registry post-Plan 4 closeout
- 8 deferred items across 5 source plans
- Highest priority: DS-4 (admin), DS-5 (P0 ADG blocker), DS-6 (expiry 2026-05-31)
- Pattern source: plans `apps-repo-brief-plan4-spine-handoff-f2a3c8`, `apps-eval-harness-deferred-e4a1b7`
- Non-goals: no implementation — capture and triage only
- Success: all 8 DS items tracked, owners assigned, expiry dates noted

**PLAN_CREATED:** `.windsurf/plans/deferred-scope-post-plan4-closeout-a7d2f1.md`
