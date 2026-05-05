# apps_repo_brief — L3 Managed Workflow Adapter

> **Status:** Not Started · **Tier:** T2 · **Slug:** `apps-repo-brief-l3-workflow-e2c7d9`
> **Parent:** `deferred-scope-ds2-ds3-ds7-c9e4f1` (DS-3)
> **Prerequisite:** `apps-repo-brief-c0-runtime-wiring-f4a8b2` (DS-2 must complete first)
> **Est. tokens:** ~15k

---

## 1. Problem Statement

`apps_repo_brief` uses a direct orchestration path (`GovernedExecRun` → `spine_handoff`). The canonical spine pattern for R3/R3R4 routes (`apps_underwriting_ai`, via `underwriting_l3_workflow_adapter.py`) uses an explicit L3 managed workflow adapter that:

1. **Expands** the workflow into stage contracts with dependency edges (L3's role — expand, not execute).
2. **Declares** L2 receipt types (E1–E3) for each stage.
3. **Injects** HITL posture based on C0 evidence state.
4. Gives the static-evidence scanner a direct L3-layer proof that the app walks the governed stage graph.

`apps_repo_brief` has no equivalent. Its stages (C0 retrieval → prompt assembly → exit) are implicit in `GovernedAppRunner`, not declared as explicit evidence.

---

## 2. Target State

After this plan:
1. `apps_repo_brief/integrations/repo_brief_l3_workflow_adapter.py` exists — declares a 3-stage workflow (C0 retrieval, prompt assembly, exit validation) with dependency edges and HITL posture injection.
2. `apps_repo_brief/integrations/repo_brief_l2_step_adapters.py` exists — declares E1–E3 L2 receipt types for the 3 stages.
3. `spine_handoff.run_repo_brief_via_spine()` calls `expand()` on the L3 adapter before delegating to `GovernedExecRun`.
4. 10 governance tests verify the expands-not-executes invariant and HITL posture rules.

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1.1–P1.2 | L3 workflow adapter + L2 step adapters | ~6k | Not Started |
| W2 | P2.1 | Wire `expand()` call into `run_repo_brief_via_spine` | ~3k | Not Started |
| W3 | P3.1 | Governance tests (10 cases) | ~4k | Not Started |
| W4 | P4.1 | Static DAG proof annotation in `spine_manifest.yaml` | ~2k | Not Started |

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | `repo_brief_l3_workflow_adapter.py` | `apps_repo_brief/integrations/` (new file) | Pattern from `underwriting_l3_workflow_adapter.py`; 3 stages not 5 | ~3k | ⬜ |
| P1.2 | `repo_brief_l2_step_adapters.py` | `apps_repo_brief/integrations/` (new file) | E1 = C0 retrieval bound, E2 = PA evidence validated, E3 = exit sealed | ~3k | ⬜ |
| P2.1 | Wire `expand()` in `run_repo_brief_via_spine` | `apps_repo_brief/integrations/spine_handoff.py` | Must remain fail-soft; expand result is metadata only, does not change pipeline execution | ~3k | ⬜ |
| P3.1 | 10 governance tests | `tests/_apps_contract/test_apps_repo_brief_l3_adapter.py` | Must test: expand returns `WorkflowExpansion`, expands-not-executes, HITL posture inject, stage ordering | ~4k | ⬜ |
| P4.1 | `spine_manifest.yaml` static DAG row | `apps_repo_brief/spine_manifest.yaml` | Add `l3_workflow_adapter` field pointing to new adapter module | ~2k | ⬜ |

---

## 5. Files In Scope

- `apps_repo_brief/integrations/repo_brief_l3_workflow_adapter.py` — new file
- `apps_repo_brief/integrations/repo_brief_l2_step_adapters.py` — new file
- `apps_repo_brief/integrations/spine_handoff.py` — add `expand()` call
- `apps_repo_brief/spine_manifest.yaml` — add l3_workflow_adapter reference
- `tests/_apps_contract/test_apps_repo_brief_l3_adapter.py` — new test file

---

## 6. 3-Stage Workflow Design

```
Stage 1 — C0 Retrieval Bound        → L2.E1.repo_brief_c0_context_bound
Stage 2 — Prompt Assembly Validated → L2.E2.repo_brief_evidence_validated
Stage 3 — Exit Sealed               → L2.E3.repo_brief_artifact_sealed
```

**HITL triggers (mirrors underwriting pattern):**
- `c0_state=FAIL` + no sources → `HITL_REQUIRED`
- `contradiction_flags` present → `HITL_ADVISORY`
- `evidence_status=MISSING` → `HITL_REQUIRED`
- otherwise → `HITL_NONE`

---

## 7. Non-Goals

- No execution of stages (L3 expands only — L2 executes)
- No changes to `agentic_core` L3 orchestration engine
- No new route families
- No DS-2 re-work (this plan depends on DS-2 being complete)

---

## 8. Acceptance Criteria

1. `repo_brief_l3_workflow_adapter.expand(run_context)` returns a `WorkflowExpansion` with `l3_expanded=True`, `stage_count=3`.
2. Stage dependency order is 1→2→3 (no skips, no parallelism).
3. `expand()` never mutates `run_context`.
4. HITL posture injection follows the 4-rule table in §6.
5. `repo_brief_l2_step_adapters.py` exports `L2_RECEIPT_E1`, `L2_RECEIPT_E2`, `L2_RECEIPT_E3` string constants.
6. `spine_handoff.run_repo_brief_via_spine()` calls `expand()` fail-soft (exception → log + continue).
7. All 10 governance tests pass. All prior tests pass (no regressions).

---

## 9. Gap Register

| Gap | Risk | Mitigation |
|-----|------|-----------|
| `spine_manifest.yaml` may not have a `l3_workflow_adapter` schema field | Low | Check existing schema; add if missing |
| Underwriting adapter imports 5-stage-specific types not present in repo_brief | Low | Define repo_brief-specific receipt constants locally |

**PLAN_CREATED:** `.windsurf/plans/apps-repo-brief-l3-workflow-e2c7d9.md`
