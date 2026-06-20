---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-repo-brief-c0-runtime-wiring-f4a8b2.md'
original_relative_path: '_archive\\2026-05\\apps-repo-brief-c0-runtime-wiring-f4a8b2.md'
source_sha256: 6eddcacb8030d84bce72a35acae6cc5ba3a5211ab8ebae664ce7b9362a0913e2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_repo_brief — C0 Runtime Wiring

> **Status:** Completed · **Tier:** T2 · **Slug:** `apps-repo-brief-c0-runtime-wiring-f4a8b2`
> **Parent:** `deferred-scope-ds2-ds3-ds7-c9e4f1` (DS-2)
> **Est. tokens:** ~10k

---

## 1. Problem Statement

`apps_repo_brief/c0/repo_brief_c0_adapter.py` defines `C0_RETRIEVAL_LANES` and builds `C0RequestSpec` but no runtime invocation of `run_c0` is wired into the spine handoff or governed run path.

Concretely:
- `spine_handoff.run_repo_brief_via_spine()` delegates directly to `GovernedExecRun.run()` — it does not invoke C0 retrieval.
- `GovernedExecRun.run()` delegates back to `run_repo_brief_via_spine()` — circular stub delegate.
- The `RepoBriefFinalEvidenceContract` schema (`repo_brief_final_contract.py`) exists but is never populated from a real C0 invocation; `fec_producer.py` returns a stub FEC with `grounded=False`.
- `governed_exec_run.py` never threads a C0 result into the exit pipeline.

---

## 2. Target State

After this plan:
1. `run_repo_brief_via_spine()` builds a `C0RequestSpec` via `RepoBriefC0Adapter` and calls `run_c0()` when `c0_required=True`.
2. The C0 result populates a `RepoBriefFinalEvidenceContract` (stub-safe: if C0 returns no sources, `grounded=False` with `evidence_status=MISSING`).
3. `GovernedExecRun.run()` accepts the FEC result and passes it into the exit pipeline (fail-soft).
4. `fec_producer.py` `produce_fec()` reads from the FEC when available, returning `grounded=True` + populated `retrieval_sources`.
5. 8 governance tests cover the wiring seam.

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1.1–P1.3 | C0 invocation seam in spine_handoff | ~4k | ✅ DONE |
| W2 | P2.1–P2.2 | GovernedExecRun FEC threading + fec_producer grounding | ~3k | ✅ DONE |
| W3 | P3.1 | Governance tests (8 cases) | ~3k | ✅ DONE |

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | `run_c0` import seam in spine_handoff | `apps_repo_brief/integrations/spine_handoff.py` | `run_c0` lives in `agentic_core.L0_routing.c0_retrieval` — must import without circular dep | ~1k | ✅ |
| P1.2 | `RepoBriefC0Adapter` call in `run_repo_brief_via_spine` | `apps_repo_brief/integrations/spine_handoff.py` | Must be fail-soft: if C0 unavailable, continue with `grounded=False` | ~2k | ✅ |
| P1.3 | `C0RequestSpec` → `RepoBriefFinalEvidenceContract` mapping | `apps_repo_brief/integrations/spine_handoff.py` | Schema mismatch between core `FinalEvidenceContract` and `RepoBriefFinalEvidenceContract` | ~1k | ✅ |
| P2.1 | `GovernedExecRun.run()` accepts FEC | `apps_repo_brief/integrations/governed_exec_run.py` | Must not break existing tests | ~1k | ✅ |
| P2.2 | `fec_producer.produce_fec()` reads FEC | `apps_repo_brief/cert/fec_producer.py` | Must remain backward-compat when no C0 result passed | ~2k | ✅ |
| P3.1 | 8 governance tests | `tests/_apps_contract/test_apps_repo_brief_c0_wiring.py` | Must test stub-safe path (no real C0), grounded path, FEC threading | ~3k | ✅ |

---

## 5. Files In Scope

- `apps_repo_brief/integrations/spine_handoff.py` — add C0 call seam
- `apps_repo_brief/integrations/governed_exec_run.py` — thread FEC into exit path
- `apps_repo_brief/cert/fec_producer.py` — read C0 sources when available
- `tests/_apps_contract/test_apps_repo_brief_c0_wiring.py` — new test file

---

## 6. Non-Goals

- No real C0 invocation against a live vector store (stub-safe only)
- No changes to `agentic_core` C0 engine logic
- No changes to `RepoBriefFinalEvidenceContract` schema (already defined in `repo_brief_final_contract.py`)
- No DS-3 L3 adapter work (separate plan `apps-repo-brief-l3-workflow-<6hex>`)

---

## 7. Acceptance Criteria

1. `run_repo_brief_via_spine()` calls `RepoBriefC0Adapter.build_c0_request()` when request has `c0_required=True`.
2. FEC is returned from `run_repo_brief_via_spine()` and threaded through `GovernedExecRun.run()`.
3. `produce_fec({})` returns `grounded=False` (no sources → template_only, backward-compat).
4. `produce_fec({"c0_result": <fec>})` returns `grounded=True` when FEC has sources.
5. All 8 governance tests pass.
6. All existing `test_apps_repo_brief_fec_producer.py` tests still pass.

---

## 8. Gap Register

| Gap | Risk | Mitigation |
|-----|------|-----------|
| `run_c0` interface may differ from `C0RequestSpec` shape | Medium | Import fail-soft; stub if unavailable |
| Circular import: `spine_handoff` ↔ `governed_exec_run` | Low | Already uses `TYPE_CHECKING` guard; extend pattern |
| FEC schema mismatch (core vs repo_brief types) | Medium | Map at call site; never mutate core types |

**PLAN_CREATED:** `.windsurf/plans/apps-repo-brief-c0-runtime-wiring-f4a8b2.md`
