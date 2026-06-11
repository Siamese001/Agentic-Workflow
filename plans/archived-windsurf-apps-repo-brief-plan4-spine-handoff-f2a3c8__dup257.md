---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-repo-brief-plan4-spine-handoff-f2a3c8__dup257.md'
original_relative_path: 'apps-repo-brief-plan4-spine-handoff-f2a3c8__dup257.md'
source_sha256: 9eda6e9dd2be32f15e8d048b5f82e99b6148438e11c9e87b59ad3b480e0b0eb3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_repo_brief Plan 4 — Spine Handoff + Full Coverage

> **Status:** Completed · **Tier:** T2 · **Slug:** `apps-repo-brief-plan4-spine-handoff-f2a3c8`
> **Parent:** `apps-repo-brief-plan3-deferred-scope-b9e4c1` (Completed 2026-05-05)
> **Purpose:** Complete the `PARTIAL_SPINE → FULL_SPINE` gap left after Plan 3 acceptance. The single concrete gap is `spine_handoff.py` — the cross-layer handoff contract connecting `apps_repo_brief` to the canonical agentic_core spine at 100% scanner coverage. No implementation in this document.

---

## 1. Context

Plan 3 deferred scope (`apps-repo-brief-plan3-deferred-scope-b9e4c1`) completed on 2026-05-05 with a **YES** verdict on all 15 §20.2 acceptance gates. The one acknowledged gap noted in the final acceptance report (§9 Remaining Gaps) is:

> `spine_handoff.py` was not built in W1–W5 (deliberate non-goal of Plan 3). Spine scanner reports `PARTIAL_SPINE` (5.3% coverage). This is the expected state — `spine_handoff.py` is a future wave item, not a Plan 3 acceptance requirement.

The spine scanner (`tools/analysis/apps_spine_coverage.py --app=apps_repo_brief`) declared 8 contracts in `apps_repo_brief/spine_manifest.yaml` but found 0 runtime imports, yielding `PARTIAL_SPINE` at 5.3% coverage. Full spine alignment requires the handoff contract module so the scanner can trace imports from the manifest entries to actual runtime code.

---

## 2. Deferred Scope Items

### F1 — `spine_handoff.py` implementation

**Source:** Plan 3 D1.1 spine scanner output; W2 scaffold stub note
**What:** `apps_repo_brief/spine_handoff.py` is referenced in `apps_repo_brief/spine_manifest.yaml` as the cross-layer handoff entry point but was never built. Without it, the spine scanner cannot resolve the 8 declared contracts to runtime import paths and reports `PARTIAL_SPINE`.
**Gap:** Spine coverage 5.3% (0/8 contracts resolvable at runtime). Full spine requires all 8 manifest contracts to trace to importable modules.
**Scope:**
- Create `apps_repo_brief/spine_handoff.py` implementing the canonical handoff shape
- Wire the 8 spine manifest contracts to concrete runtime imports
- Re-run spine scanner to confirm `FULL_SPINE` (100% coverage)
- Add 1–2 tests confirming the handoff module is importable and declares expected contracts
**Blocking:** N/A — Plan 3 acceptance already at YES. This is a quality/completeness item.
**Estimated tokens:** ~10k

### F2 — ADG edge validation post-`spine_handoff.py`

**Source:** Plan 3 §24 ADG Hotspot Report; Plan 3 D1.2 blast-radius
**What:** After `spine_handoff.py` is built, re-run the ADG snapshot to confirm:
  - `apps_repo_brief/spine_handoff.py` node appears in ADG with correct layer assignment
  - No new L4 write edges introduced
  - Blast radius of `spine_handoff.py` is bounded (expected: direct callers only, no cascade)
**Gap:** ADG snapshot `05052026_0623` predates `spine_handoff.py`; post-build snapshot needed.
**Scope:** `adg_reload` + `adg_nodes_by_file` + `adg_blast_radius` for the new module
**Blocking:** N/A — quality evidence only.
**Estimated tokens:** ~3k

### F3 — Spine scanner CI gate for `apps_repo_brief`

**Source:** Plan 3 §21 "Commands to Run"
**What:** Add `apps_repo_brief` to the CI spine coverage gate so a regression from `FULL_SPINE` → `PARTIAL_SPINE` fails CI. Currently the gate only runs on `apps_research` and `apps_lic`.
**Gap:** No automated guard prevents future scope drift from re-introducing `PARTIAL_SPINE`.
**Scope:** Update `ops_scripts/ci/check_app_spine_coverage.py` (or equivalent) to include `apps_repo_brief` with `min_coverage_pct=100`.
**Blocking:** N/A — CI hygiene only.
**Estimated tokens:** ~3k

---

## 3. Wave Structure

| Wave | Scope | Est. Tokens | Status |
|------|-------|-------------|--------|
| F1 | `spine_handoff.py` implementation + tests | ~10k | ✅ DONE |
| F2 | ADG re-snapshot + edge validation | ~3k | ✅ DONE |
| F3 | CI spine gate update for `apps_repo_brief` | ~3k | ✅ DONE |

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| F1.1 | Implement `spine_handoff.py` | `apps_repo_brief/spine_handoff.py` (new) | Must match canonical handoff shape | 7k | ✅ DONE |
| F1.2 | Wire manifest contracts | `apps_repo_brief/spine_manifest.yaml` | 8 contracts must resolve | 2k | ✅ DONE |
| F1.3 | Spine scanner verification | `tools/analysis/apps_spine_coverage.py` | Scanner must report FULL_SPINE | 1k | ✅ DONE |
| F2.1 | ADG re-snapshot | `artifacts/adg/` | Requires ADG regeneration | 2k | ✅ DONE |
| F2.2 | Blast-radius capture for `spine_handoff.py` | `adg_sqlite` MCP | ADG snapshot must be fresh | 1k | ✅ DONE |
| F3.1 | CI spine gate update | `ops_scripts/ci/check_apps_spine_delegation.py` | Remove apps_repo_brief from allowlist | 3k | ✅ DONE |

---

## 5. Non-Goals

- No re-implementation of Plan 3 work (all 15 §20.2 gates already YES).
- No changes to `cert_projection_adapter.py`, `fec_producer.py`, or C0 layer.
- No new C0 retrieval lanes or depth profiles.
- No HITL or L4 state table changes.
- No broad refactors beyond `spine_handoff.py` + CI gate.

---

## 6. Success Criteria

- `tools/analysis/apps_spine_coverage.py --app=apps_repo_brief` → **FULL_SPINE** (100% coverage, all 8 contracts resolvable)
- ADG snapshot includes `spine_handoff.py` node with correct layer; blast radius bounded
- CI spine gate includes `apps_repo_brief` and passes at 100%
- 0 regressions on the 87 governance tests from Plan 3 D2+D3+W5

---

## 7. Dependencies

| Item | Dependency | Notes |
|------|-----------|-------|
| F1.1 | `apps_repo_brief/spine_manifest.yaml` (exists) | Must read all 8 contract entries |
| F1.1 | Canonical handoff shape from `apps_research/spine_handoff.py` or `apps_lic/` | Pattern source for implementation |
| F2.1 | `tools/generate_full_adg.py` | Must be run post-F1.1 |
| F3.1 | `ops_scripts/ci/check_app_spine_coverage.py` (exists or must be created) | SSOT: `ops_scripts/ci/` per §31 |

---

## 8. AI Summary

- **Target:** `apps_repo_brief` — close `PARTIAL_SPINE → FULL_SPINE` gap from Plan 3
- **Root cause:** `spine_handoff.py` was a W2 scaffold stub, never built in W1–W5
- **New files:** `apps_repo_brief/spine_handoff.py`; 1–2 tests
- **Edits:** `apps_repo_brief/spine_manifest.yaml` (wire contracts); `ops_scripts/ci/check_app_spine_coverage.py` (add apps_repo_brief)
- **Pattern source:** `apps_research/spine_handoff.py`, `apps_repo_brief/spine_manifest.yaml`
- **Non-goals:** No Plan 3 re-work; no new FEC/C0/PA changes
- **Success:** FULL_SPINE verdict + CI gate green + 0 regressions

**PLAN_CREATED:** `.windsurf/plans/apps-repo-brief-plan4-spine-handoff-f2a3c8.md`
