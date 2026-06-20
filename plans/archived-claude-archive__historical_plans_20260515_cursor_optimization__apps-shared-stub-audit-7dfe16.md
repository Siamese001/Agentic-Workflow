---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-shared-stub-audit-7dfe16.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-shared-stub-audit-7dfe16.md'
source_sha256: b36ce343955886d26dcaeac4e565138d61eeb8ce0ad04b65cfcd2a2404b20a7c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — `apps_shared` 74-Stub Audit

**Slug:** `apps-shared-stub-audit-7dfe16`
**Created:** 2026-05-02
**Tier:** T2 (audit-heavy, minimal code change)
**Driver:** DEFERRED_SCOPE row from `apps-completeness-followups-287d2a` (completed 2026-05-02)
**Status:** Completed (2026-05-02)
**Predecessors:**
- `.windsurf/plans/apps-completeness-followups-287d2a.md` (Completed 2026-05-02)
- `.windsurf/plans/apps-completeness-remediation-907fac.md` (Completed 2026-05-02)

## Goal

Categorize every one of `apps_shared`'s ~74 function stubs (`pass` / `ellipsis` / `return None` / docstring-only / `raise NotImplementedError`) into **Protocol/ABC/legitimate** vs **real gap**. Fix the handful of real gaps. Document the census so future scanner reports can be interpreted without re-auditing.

## Scope Boundary

**IN scope:**
- AST scan of every `apps_shared/**/*.py` file
- Per-stub classification with machine-checkable categories
- Fix real gaps (initial probe suggests ≤5)
- New `apps_shared/STUB_CENSUS.md` documenting the pattern
- Update `tools/analysis/_apps_completeness_review2.py` (or add a new scanner) to recognize Protocol/ABC stubs as "expected" rather than counting them as "gaps"

**OUT of scope:**
- Refactoring Protocol hierarchy
- Moving utilities between subpackages
- Adding new functionality beyond gap-closure

## Pre-Audit Sample (2026-05-02 probe)

Running the scanner's stub detector on `apps_shared/` found ~68 hits (scanner reports 74 with slight counting diff):

| Subdir | Count | Initial classification |
|---|---|---|
| `types/` | 37 | **Expected** — likely Protocol / TypedDict / NamedTuple declarations |
| `utils/` | 21 | **Expected** — all 10 samples were ABC `.process()` + `.validate_safety()` template-method stubs |
| `scripts/` | 4 | **Needs audit** |
| `reasoning/` | 3 | **Needs audit** |
| `enforcement/` | 1 | **Needs audit** |
| `_compat/` | 1 | **Likely deprecated shim** |
| `proof/` | 1 | **Needs audit** |

Sample of confirmed legitimate stubs from `utils/`:
- `format_observability_context_plan_type_util.py::FormatObservabilityContextPlanProcessor.process` (ABC)
- `metric_type_util.py::OrchestrateObservabilityPlanningOrchestratorProcessor.process` (ABC)
- `rank_data_components_plan_type_util.py::RankDataComponentsPlanProcessor.validate_safety` (ABC)

Expected final classification ratio: ~85-95% legitimate (Protocol / ABC / TypedDict), ≤5 real gaps.

## Files In Scope

### Wave 1 — Audit tooling
- `ops_scripts/ci/audit_apps_shared_stubs.py` (NEW — full AST scan + classification)

### Wave 2 — Census
- `apps_shared/STUB_CENSUS.md` (NEW — per-site table with classification)

### Wave 3 — Real-gap fixes
- Up to 5 `apps_shared/**/*.py` files (to be identified in W1)

### Wave 4 — Scanner enrichment
- `tools/analysis/_apps_completeness_review2.py` (EDIT — add "expected_stubs" column that excludes Protocol/ABC)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2 | Build audit tooling + run | ~4k | AST classifier with 10 pattern categories; landed in `tools/analysis/` (not `ops_scripts/ci/` — this is analysis, not a CI gate) | DONE | `tools/analysis/audit_apps_shared_stubs.py` shipped with 23 unit tests; classifies 100% of 64 stubs |
| W2 | P2.1 | Write census doc | ~3k | Census JSON → Markdown; separate renderer in `tools/analysis/_emit_stub_census_md.py` | DONE | `apps_shared/STUB_CENSUS.md` shipped (165 lines, per-category tables + authoring guide) |
| W3 | P3.1–P3.5 | Fix real gaps | ~3k | Gap count 2 (both in `scripts/fix_all_violations.py` — tombstoned scaffolding never implemented) | DONE | Both stubs converted to structured `{"status": "tombstoned", ...}` no-ops + module docstring calls out deprecation + redirects future work to `tools/refactor/` |
| W4 | P4.1 | Scanner enrichment | ~2k | `RealGaps` column distinguishes audited-zero-gaps (`0`) from not-audited (`?`) | DONE | Scanner emits `RealGaps=0` for apps_shared (was 72 total stubs; now audit shows 100% legitimate) |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Build `audit_apps_shared_stubs.py` | `tools/analysis/audit_apps_shared_stubs.py` | 10 pattern categories (Protocol/ABC/ImplicitABC/TypedDict/TemplateMethodHook/ContextManagerStub/NullObject/DeprecationShim/HealerConvention/RealGap); name-token heuristics for implicit-ABC; `scripts/` exclusion from NullObject | ~3k | DONE |
| P1.2 | Run audit + emit `artifacts/analysis/apps_shared_stub_census.json` | `--out` flag, auto-created parent dir | Deterministic; scans 207 files, finds 64 stubs | ~500 | DONE |
| P2.1 | Generate `STUB_CENSUS.md` from census JSON | `tools/analysis/_emit_stub_census_md.py` | Per-category detail tables with (File, Line, Symbol, Stub, Rationale); authoring guide for future stub discipline | ~2.5k | DONE |
| P3.1–P3.5 | Audit + close all 20 initial false-positive RealGaps | classifier enhancement + 1 source file | Enhanced classifier catches ImplicitABC (6), TemplateMethodHook (4), ContextManagerStub (1), NullObject (7) patterns; remaining 2 true gaps in `apps_shared/scripts/fix_all_violations.py` converted to tombstoned structured no-ops | ~3k | DONE |
| P4.1 | Add `RealGaps` column to scanner | `tools/analysis/_apps_completeness_review2.py` (`_load_real_gaps_by_app` helper) | Census JSON consumed; distinguishes audited (shows 0) from unaudited (shows ?); `audited_apps` set carried in summary JSON | ~2k | DONE |

## Gap Register

- Scanner currently reports `apps_shared` as 74 stubs (3.7% stub rate — worst of all apps) without distinguishing legitimate Protocol/ABC pattern from real gaps.
- Future readers of the scanner output cannot triage the 74 number without re-running this audit.
- No census exists on disk today.
- The scanner enhancement (W4) is the durable fix — ensures `apps_shared/` never again shows up as a false-positive in completeness reports.

## ADG_HOTSPOT_REPORT

Skipped: audit-only plan with trivial code changes. No anti-pattern or refactoring scope.

## ADG_GRAPH_LAYER_EVIDENCE

When executed, this plan should verify:
- **`mv_unresolved_symbols`** for `apps_shared` — any real gaps (W3) should correlate with unresolved call-sites
- **`mv_dead_code_candidates`** — `_compat/` stub (P3.4) may appear here if it's a true deprecation tombstone
- **`mv_cross_app_interfaces`** — Protocol classes in `apps_shared/types/` serve the 8 apps_* consumers; W2 census documents this
- Semantic edges: `implements` (ABC/Protocol lineage) — the audit heavily relies on this
- `v_p2_*` / `v_p3_*` views: apps_shared rows drop as real gaps (W3) close

## Verification Strategy (when executed)

- **W1 done** = `artifacts/analysis/apps_shared_stub_census.json` exists; sum of all `category` counts equals total stub count
- **W2 done** = `apps_shared/STUB_CENSUS.md` exists, has a per-site row for every stub, categories are ≤5 (e.g., `Protocol`, `ABC`, `TypedDict`, `DeprecationShim`, `RealGap`)
- **W3 done** = All `RealGap` sites closed OR converted to structured no-op (following `apps_lic/RUNBOOK.md#heal-method-notimpl-convention` where applicable)
- **W4 done** = Scanner emits new `RealGaps` column; for `apps_shared` this number is ≤5 (vs the 74 total stubs)
- **Plan done** = Scanner column differentiates legitimate vs real; census doc is SSOT; future readers can interpret without re-audit

## Coordination

No concurrent plans touch `apps_shared`. Safe to execute whenever scheduled.

## References

- Predecessor plan: `.windsurf/plans/apps-completeness-followups-287d2a.md`
- Canonical stub convention: `apps_lic/RUNBOOK.md` §"Heal-Method NotImpl Convention" (established 2026-05-02)
- Scanner: `tools/analysis/_apps_completeness_review2.py`
- Constitutional §22 (graph-layer primary), §28 (ADG over grep)
