# Plan — `apps_shared` 74-Stub Audit

**Slug:** `apps-shared-stub-audit-7dfe16`
**Created:** 2026-05-02
**Tier:** T2 (audit-heavy, minimal code change)
**Driver:** DEFERRED_SCOPE row from `apps-completeness-followups-287d2a` (completed 2026-05-02)
**Status:** Live (plan only — NOT executed this session per Author-Gate 2026-05-02-T19:19)
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
| W1 | P1.1, P1.2 | Build audit tooling + run | ~4k | AST scan identifies `Protocol` base class and `ABC`/`ABCMeta` lineage | TODO | `ops_scripts/ci/audit_apps_shared_stubs.py` emits JSON census with 100% of stubs classified |
| W2 | P2.1 | Write census doc | ~3k | Census JSON → Markdown table; stable section structure | TODO | `apps_shared/STUB_CENSUS.md` exists with per-site row + category + rationale |
| W3 | P3.1–P3.5 | Fix real gaps | ~3k | Real gaps are ≤5; each is a single-function fix | TODO | All identified real gaps closed OR explicitly documented as `pattern=intentional-stub` |
| W4 | P4.1 | Scanner enrichment | ~2k | New column: `RealGaps` = total stubs − expected_stubs | TODO | Scanner output distinguishes Protocol/ABC stubs from real gaps |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Build `audit_apps_shared_stubs.py` | 1 new file | AST class-lineage analysis; Protocol base detection; ABC lineage detection (works when `ABC` in bases OR `ABCMeta` as metaclass OR `@abstractmethod` on method) | ~3k | TODO |
| P1.2 | Run audit + emit `artifacts/analysis/apps_shared_stub_census.json` | 1 command | None — deterministic | ~500 | TODO |
| P2.1 | Generate `STUB_CENSUS.md` from census JSON | 1 new file | Markdown formatting; keep table sortable | ~2.5k | TODO |
| P3.1 | Audit `scripts/` stubs (4 sites) | ≤4 files | Tracing ABC lineage for command-runner base classes | ~1k | TODO |
| P3.2 | Audit `reasoning/` stubs (3 sites) | ≤3 files | Check if these match the healer-stub pattern from `apps_lic` | ~1k | TODO |
| P3.3 | Audit `enforcement/` stub (1 site) | 1 file | Likely strategy-pattern ABC | ~500 | TODO |
| P3.4 | Audit `_compat/` stub (1 site) | 1 file | Likely deprecation shim — may be removable | ~500 | TODO |
| P3.5 | Audit `proof/` stub (1 site) | 1 file | Unknown | ~500 | TODO |
| P4.1 | Add `RealGaps` column to scanner | 1 edit | Preserve backward compat with existing callers | ~2k | TODO |

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
