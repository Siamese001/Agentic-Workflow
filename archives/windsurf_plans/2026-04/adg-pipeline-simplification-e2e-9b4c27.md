# ADG Pipeline End-to-End Simplification Plan

**Plan ID:** `adg-pipeline-simplification-e2e-9b4c27`
**Scope:** `tools/generate/generate_full_adg.py` + its immediate fan-out (`tools/generate/**`, post-ADG gate chain).
**Mode:** Analysis + recommendations only — **NO CODE CHANGES in this plan**.
**Author:** Cascade
**Date:** 2026-04-24
**Status:** Complete (W1–W8 done 2026-04-24; W5/F-12 explicitly **won't-do**; the previously-deferred "post-P6b hang RCA" was diagnosed as **not a hang** — pipeline halts cleanly on P0 violations as designed; **W8 added `--continue-on-p0` / `ADG_CONTINUE_ON_P0=1` defer-exit path** to let authors iterate on post-P0 stages without first remediating every architectural P0 violation)
**ADG Snapshot cited:** latest under `artifacts/adg/` at plan time (no regen performed; this is an analysis plan).

---

## 0. Executive Summary

The ADG generator is **functionally complete and highly observable**, but it is **not 100% optimized**. Growth by accretion (~28 sequential phases, 10+ "plan `<slug>` W<n>` inline comments) has produced measurable redundancy in three axes:

| Axis | Redundancy signal | Dominant cost |
|---|---|---|
| **Compute** | Artifacts written twice (temp → prod); MV/infra-views recomputed; P6b projection built once + P7 graphdb queries reads it again; `ADGGraphWatchlistBuilder` instantiated twice (once in P5, once in E11 delta block). | Wall-clock seconds × every run. |
| **I/O** | ~15 JSON sidecar artifacts written per run (P4/P5/P6/P6b/P7 × 4/E7 snapshot/reports × 4/burndown/watchlists/graphsnap/plan md+json); zip archive re-reads and re-writes most of them. | Disk churn; git diff noise. |
| **Cognitive** | 28 sequential phases in one 1440-line module; 5 post-ADG CI gates invoked as subprocesses at the tail; 6 distinct "skip" ledger lines with identical shape; 4 near-identical tqdm-wrapped loops. | Review burden; refactor risk; onboarding time. |

**Headline finding:** the pipeline can be simplified to **~18 logical phases**, with an estimated **10-20% wall-clock reduction**, **~8 fewer sidecar artifacts per run** (post-fold), and a **~400-line reduction in `generate_full_adg.py`** — without losing a single gate, report, or invariant. Every recommendation below is *additive-by-removal*: it retires redundancy without weakening any constitutional gate.

---

## 1. Current Pipeline Inventory (observed)

Phases in `generate_full_adg.generate_full_adg()` + `main()`, in execution order:

| # | Phase | Module / function | Class | Blocking? | Notes |
|---|---|---|---|:---:|---|
| 1 | Pre-flight: MCP drift / WAL / file locks | `main()` → 3 helpers | Setup | yes | |
| 2 | Static scan (cached) | `ADGStaticScanner.scan()` | Core | yes | |
| 3 | Build canonical artifact | `build_artifact` | Core | yes | |
| 4 | Compute routing summary (P1/P2 seed) | `route_violations` | Core | yes | |
| 5 | **Write artifacts to TEMP** | `write_all_artifacts` | Core | yes | **DOUBLE WRITE — see F-1** |
| 6 | Tier-1 validity/integrity/consistency/P2 | `_check_*` | Gate (T1) | yes | Run on temp SQLite |
| 7 | **Write artifacts to PROD** (re-serialise) | `write_all_artifacts` again | Core | yes | **Same artifact, second pass** |
| 8 | Resolve + re-verify prod SQLite path | `_resolve_post_commit_sqlite` | Core | yes | |
| 9 | Phase-2 auto-disposition | `run_phase2_disposition_processing` | Enrich | soft | Fail-open |
| 10 | Infra wiring MVs | `_enrich_infra_views` | Enrich | yes | |
| 11 | Materialized views (A..E) | `_materialize_adg_views` | Enrich | yes | |
| 12 | P6 graph projection (networkx sqlite) | `build_graph_projection` | Proj | soft | ImportError-only |
| 13 | P6b graphdb projection (JSON + metadata) | `_build_graphdb_network_projection` | Proj | soft | Returns NX graph obj |
| 14 | P0 wave plan emit | `_emit_p0_remediation_wave_plan` | Plan | yes | |
| 15 | **Gate dispatcher subprocess** | `ops_scripts.ci.adg_gates.run` | Gate (T2) | yes (exit-tolerant) | 600s timeout |
| 16 | P0 two-pass runner | `_run_p0_two_pass_runner` | Gate (T2) | yes | |
| 17 | P0 / P1 ratchet / dead-imports | 3 gate fns | Gate (T2) | yes | |
| 18 | Structural conformance + agentic antipatterns | 2 gate fns | Gate (T2b) | yes | |
| 19 | P7 analyst reports × 4 | `_build_*_report` × 4 | Analyst | soft | tqdm loop |
| 20 | Witness-tier gates (A/B) | `_check_witness_tier_gates` | Gate (T2b) | yes | |
| 21 | P4 watchlist | `build_and_emit_watchlist` | Intel | soft | |
| 22 | P5 graph watchlist | `ADGGraphWatchlistBuilder.build_graph_watchlist` | Intel | soft | **First instantiation** |
| 23 | Repair orchestrator | `_run_p1_p2_auto_fix` | Repair | soft | |
| 24 | E6/E7 graph snapshot + diff | `build_snapshot`/`save_snapshot`/`diff_snapshots` | Analyze | yes | |
| 25 | E8 ownership registry | `OwnershipRegistry.from_scan_result` | Analyze | yes | Result discarded (!) |
| 26 | E9 confidence scoring + MemoryBridge persist | `score_edges`, bridge | Analyze | yes | |
| 27 | E5 impact prediction | `predict_impact` | Analyze | yes | |
| 28 | E11 graph-native SQL analytics | `ADGGraphWatchlistBuilder._compute_deltas` | Analyze | yes | **Second instantiation of same builder (!)** |
| 29 | Memory MCP persist | `_persist_adg_to_memory` | Side | soft | |
| 30 | Standardized reports (Wave 6) | `_generate_standardized_reports` | Report | yes | |
| 31 | Zip archive (always-on) | `_create_zip_archive` | Archive | yes | Re-reads ~10 artifacts |
| 32 | Archive old artifacts | `_archive_old_artifacts` | Archive | soft | |
| 33 | Closure validation evaluation | inline | Gate | yes | 3-way special-case branch |
| 34 | Defect table print | `_print_defect_table` | Report | no | |
| 35 | Redis ingest | `_auto_ingest_to_redis` | Side | soft | |
| 36 | Repo-state drift check | inline | Gate | yes | |
| 37 | Auto-commit artifacts | `_auto_commit_artifacts` | Side | soft | |
| 38 | Post-ADG gate chain × 5 subprocesses | `_run_post_adg_gate` × 5 | Gate (T3) | yes | wiring / config-ref / lifecycle / except-contract / test-coverage |

**Observed LOC:** `generate_full_adg.py` = 1440 lines. Function `generate_full_adg()` alone = ~665 lines (lines 488–1153).

---

## 2. Findings (F-1 … F-12)

Each finding is **evidence-backed**, **cost-classified**, and **paired with a remediation option**. Findings are ordered by estimated impact × confidence.

### F-1 — Double artifact write (temp + prod) is wasteful after Tier-1 becomes trustworthy

- **Evidence:** Lines 600–628. `write_all_artifacts` runs twice — once to `temp_dir`, again to `adg_artifacts_dir`. The second call re-serialises the *same* `ADGArtifact` object from memory; it does not re-derive anything.
- **Cost:** One full snapshot.json + one full ~38MB SQLite write per run (likely 2–6 s of I/O + sqlite finalise time).
- **Root rationale (valid):** protect prod from a corrupt artifact if a Tier-1 gate fails.
- **Simpler alternative:** write directly to `adg_artifacts_dir` with `.inprogress` suffix → run Tier-1 gates → `os.replace()` to final name (atomic rename on the same volume). Zero re-serialisation; same fail-safety.
- **Impact:** **HIGH** (wall-clock), **HIGH confidence** (pure I/O reduction, no semantic change).

### F-2 — `ADGGraphWatchlistBuilder` instantiated twice in the same run

- **Evidence:** Lines 811–820 (P5) *and* 952–956 (E11 delta). The second instantiation re-opens the same SQLite and re-initialises the builder only to call `_compute_deltas`.
- **Cost:** One extra SQLite connection open + builder constructor work. Minor wall-clock, but it signals architectural drift.
- **Simpler alternative:** in P5, keep the builder live long enough to also call `_compute_deltas`, then close. Or: extract deltas into a free function that takes `(items, sqlite_path)` and drop the re-instantiation.
- **Impact:** **MEDIUM** (mainly code-health), **HIGH confidence**.

### F-3 — E8 ownership registry is built then discarded

- **Evidence:** Line 850: `OwnershipRegistry.from_scan_result(result)` — return value not assigned. Lines 918–924 then call `_infer_ownership` per entity instead, effectively rebuilding ownership inline.
- **Cost:** Double work on ownership inference; `from_scan_result` becomes decorative.
- **Simpler alternative:** either (a) capture the registry and query it in the E8 print block, or (b) delete the unused `from_scan_result(result)` call entirely if the print-block path is canonical.
- **Impact:** **LOW** (wall-clock), **HIGH confidence** (pure dead code / redundant derivation).

### F-4 — Phase-2 auto-disposition uses legacy nested-try+broad-except pattern under a guardian exemption, but simpler contract is available

- **Evidence:** Lines 657–674. Two nested `try` blocks with guardian-tagged log-and-swallow. The real safety contract is "phase2 is enrichment, not a gate — continue on any failure."
- **Simpler alternative:** single try with `(ImportError, _phase2_sqlite3.Error, RuntimeError, OSError)` tuple, using the existing `_record_pipeline_skip()` helper (same as P4/P5/P6/P6b/P7 use). Eliminates a guardian-tagged antipattern instance and unifies the "non-blocking enrichment" error path.
- **Impact:** **LOW** wall-clock, **MEDIUM code-health**, **HIGH confidence**.

### F-5 — Closure-validation special-case branch is a fragile 3-way set membership check

- **Evidence:** Lines 1102–1124. Three `if`/`elif` branches enumerate specific failed-cap tuples (`["EDGE SEMANTIC PRECISION"]`, `["DETERMINISM (ARTIFACT LEVEL)"]`, set union of both). Adding a 3rd known-issue capability requires a 4-branch rewrite.
- **Simpler alternative:** data-driven — define `KNOWN_TOLERATED_CLOSURE_GAPS: set[str]` constant. If `failed_caps ⊆ KNOWN_TOLERATED_CLOSURE_GAPS`, warn + append; else `sys.exit(1)`. One branch, N capabilities.
- **Impact:** **LOW** runtime, **MEDIUM maintainability**, **HIGH confidence**.

### F-6 — Five post-ADG gates invoked as five distinct subprocesses (serial, ~3 min tail)

- **Evidence:** Lines 1327–1387. Each of `wiring / config-ref / lifecycle / except-contract / test-coverage` spawns its own `python <gate>.py` subprocess with its own interpreter warm-up, SQLite open, import cost.
- **Cost:** 5 × interpreter startup (~200 ms each on cold Python) + 5 × ADG SQLite open/close + ~5 × `ops_scripts.ci` package import. Observable in `[ADG] Running <label> gate` prints.
- **Simpler alternative (in order of escalation):**
    1. **Gate dispatcher absorption** — the existing `ops_scripts/ci/adg_gates/run` dispatcher already runs a fleet in-process (see line 740). Migrate the five post-ADG gates into the dispatcher entries. One subprocess replaces five; gate logic unchanged.
    2. **In-process orchestrator** — if dispatcher migration is too invasive, write a thin `post_adg_gate_chain.py` that imports all five gate modules and calls their `main()` inside one Python process.
- **Impact:** **HIGH** (wall-clock at the tail where the user is already waiting), **MEDIUM confidence** (depends on each gate's import safety inside a shared interpreter).

### F-7 — P7 analyst reports and intelligence watchlists share near-identical "build → try/except → record-skip" plumbing

- **Evidence:** P4 (line 799), P5 (line 811), P6 (705), P6b (720), P7 loop (789), all share the same pattern: call builder → catch a specific-tuple → `_record_pipeline_skip(...)`.
- **Simpler alternative:** drive all six through a single `_STAGES: tuple[PipelineStage, ...]` list of `(layer, name, callable, tolerated_exc)` and one loop. One source of truth for the non-blocking contract; trivially extensible; aligns with the `tqdm` progress-bar requirement (§16) since it becomes one progress-tracked loop instead of four tqdm loops + two bare blocks.
- **Impact:** **MEDIUM** code-health, **LOW** runtime, **HIGH confidence**.

### F-8 — Zip archive builds the file list via 4 ad-hoc list-append sites with time-window filtering

- **Evidence:** Lines 1021–1083. Artifact files, graphdb staged, P7 staged, standardized reports, burndown + watchlist globs (with 10-min mtime cutoff), P0 wave-plan markdown+json. Six separate `extend`/`append` sites.
- **Simpler alternative:** each phase that produces a zip-bound artifact returns the produced `Path`s; the main fn accumulates into one `list[Path]`. No mtime cutoff needed (all paths are known, not glob-discovered).
- **Impact:** **LOW** runtime, **MEDIUM** code-health, **HIGH confidence**. Also eliminates a subtle race: the `st_mtime >= _run_cutoff` filter can miss a watchlist file that a slow clock writes 10+ min later.

### F-9 — `_git_rev_parse` called 3 times for two distinct pieces of info

- **Evidence:** Lines 521, 528, 1133. Commit SHA + tree hash + end-tree hash.
- **Simpler alternative:** one `_capture_provenance()` helper that returns a dataclass `ProvenanceSnapshot(commit_sha, tree_hash, captured_at)`, called at start; a second `_check_repo_stability(initial)` at end. Cuts 3 subprocess spawns to 2.
- **Impact:** **LOW** runtime, **LOW** code-health, **HIGH confidence**.

### F-10 — Pipeline-skip ledger writes one file *per stage per run* but only 1 consumer (`check_pipeline_skips.py`)

- **Evidence:** `_record_pipeline_skip` (lines 432–464) appends to `adg_pipeline_skips_<ts>.jsonl`. Per-run file is fine, but there's no compaction or rollup into a single current-run summary.
- **Simpler alternative:** keep JSONL per run (auditable), but also emit a one-line summary at the end: `[ADG] Pipeline skips: <n> non-blocking skips recorded in <path>`. Makes the condition visible to any human reading the build log; today the skip lines are scattered among ~100 other print lines.
- **Impact:** **LOW** runtime, **MEDIUM** observability, **HIGH confidence**.

### F-11 — `ADG_ENABLE_DETERMINISM_PROBE` env-var parsing is inline and hostile to test

- **Evidence:** Lines 1013–1015. Manual `.strip().lower() not in ("0","false","no")` inline in the call site.
- **Simpler alternative:** factor `_env_flag(name: str, default: bool = True) -> bool` in `tools/generate/core/helpers.py` (M.6 module already exists). Reuse for `ADG_SKIP_REDIS` (line 1129) and `ADG_SKIP_GIT` (line 1136) which today each re-implement the same pattern. One parser, one test.
- **Impact:** **LOW** runtime, **MEDIUM** code-health, **HIGH confidence**.

### F-12 — Non-blocking `sys.path.insert` + `# guardian: allow-global-mutation` at module import time

- **Evidence:** Lines 52–55. Needed for dual `python tools/generate_full_adg.py` + `python -m tools.generate.generate_full_adg` invocation.
- **Simpler alternative:** the `tools/generate_full_adg.py` compat wrapper already does `sys.path.insert(...)`. If all production invocations go through the wrapper or through `python -m`, the module-level insert inside `tools/generate/generate_full_adg.py` becomes dead. Worth a one-sprint deprecation with a `SYS_PATH_FALLBACK_USED` marker, then remove.
- **Impact:** **LOW** runtime, **LOW** code-health, **LOW confidence** (may be invoked by unknown third-party scripts — needs a scan before removing).

---

## 3. Recommended Simplifications — Prioritised

### Wave Structure (analysis only — NO edits in this plan)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | W1.1, W1.2 | High-confidence I/O & compute reductions (F-1, F-2, F-3) | ~12000 | No change to gate outcomes; prod SQLite byte-identical | **DONE** 2026-04-24 | Double-write collapsed via `shutil.move`; duplicate `ADGGraphWatchlistBuilder` folded into single `with`; dead `OwnershipRegistry.from_scan_result` removed |
| **W2** | W2.1, W2.2 | Code-health unification (F-4, F-5, F-7, F-11) | ~15000 | Existing `_record_pipeline_skip` is the canonical non-blocking hook | **DONE (partial)** 2026-04-24 | F-4 phase-2 collapsed to `_record_pipeline_skip`; F-5 closure 3-way branch → data-driven `KNOWN_TOLERATED_CLOSURE_GAPS`; F-11 `_env_flag` helper in `tools/generate/core/helpers.py`; F-7 stage-loop unification deferred (see follow-ups) |
| **W3** | W3.1 | Post-ADG gate consolidation (F-6) | ~20000 | `ops_scripts/ci/adg_gates/run` dispatcher can host the five gates | **DONE (conservative variant)** 2026-04-24 | Parallel subprocess fan-out via `_run_post_adg_gates_parallel` + `ThreadPoolExecutor`; 5 serial subprocesses → concurrent; tail-latency sum(t) → max(t). Full dispatcher absorption deferred |
| **W4** | W4.1, W4.2 | Observability + zip (F-8, F-9, F-10) | ~8000 | Zip file list known deterministically per run | **DONE (F-8, F-10)** 2026-04-24 | Zip file list now references `watchlist_path`/`graph_watchlist_path` directly; mtime glob race eliminated. End-of-run skip summary emitted. F-9 provenance helper deferred (lowest ROI) |
| **W5** | W5.1 | Dead-path removal (F-12) | ~5000 | Scan of repo shows zero non-wrapper invocations | **DEFERRED** | Needs repo-wide scan for non-wrapper imports; low confidence of zero external consumers. Captured as follow-up. |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Collapse double-write (F-1) | `tools/generate/generate_full_adg.py`, `agentic_core/adg/artifact/ArtifactPaths.py` (review only) | Atomic rename on Windows; `.inprogress` suffix must not collide with zip/archive glob | 6000 | planned |
| W1.2 | De-duplicate builder + ownership (F-2, F-3) | `tools/generate/generate_full_adg.py`, `tools/generate/adg_graph_watchlist_builder.py` (signature only) | `_compute_deltas` is currently private (`_`-prefix) — promotion needs review | 6000 | planned |
| W2.1 | Unify non-blocking enrichment errors (F-4, F-7) | `tools/generate/generate_full_adg.py`, new `tools/generate/core/pipeline_stages.py` (proposed) | Must preserve every current `_record_pipeline_skip` call-site semantics | 9000 | planned |
| W2.2 | Data-drive closure + env-flag helpers (F-5, F-11) | `tools/generate/generate_full_adg.py`, `tools/generate/core/helpers.py` | KNOWN_TOLERATED_CLOSURE_GAPS needs explicit review before merge | 6000 | planned |
| W3.1 | Post-ADG gate chain → dispatcher entries (F-6) | `ops_scripts/ci/adg_gates/*`, `tools/generate/generate_full_adg.py` tail | Each gate must be re-entrant-safe inside a single interpreter | 20000 | planned |
| W4.1 | Deterministic zip file list (F-8) | `tools/generate/generate_full_adg.py` | Every producer must return its `Path` — small signature changes to P4/P5/burndown | 5000 | planned |
| W4.2 | Provenance + skip summary (F-9, F-10) | `tools/generate/generate_full_adg.py` | None significant | 3000 | planned |
| W5.1 | Retire dual-invocation `sys.path` hack (F-12) | `tools/generate/generate_full_adg.py`, `tools/generate_full_adg.py` | Need repo-wide scan for any script that imports by file path | 5000 | planned |

**Token estimate status:** UNRESOLVED. The current `tools/utils/planning/token_estimator.py` `ContextWindowEstimator` does not expose `estimate_file()` in the shape used above. Numbers are **rough line-count-based estimates** (~3× char/4). This is an **analysis-only** plan (no edits), so §plan-location classifies it as a warning, not a blocker. Re-estimation is required before any execution wave begins.

---

## 4. Non-Recommendations (things to leave alone)

For fairness, the following were considered and rejected as "already optimal" or "high-risk-for-low-reward":

- **Phase ordering** (enrichment before gates, P6/P6b before Tier-2): the current order is correct and carefully rationalised in inline comments (lines 676–704). Do not touch.
- **Fail-fast on SyntaxError / repo-state drift / locked files**: correct, early, cheap. Leave.
- **`write_split_planes=False` default**: explicit 100.75 MB savings; already optimal.
- **tqdm progress bars** on P6b stage, P7 queries, P7 stages: required by §16 (query-progress-bar rule). Leave.
- **Guardian-tagged allow-log-and-swallow in phase-2**: F-4 proposes style cleanup, not removal of the guardian itself. The fail-open policy is correct.
- **Three-tier artifact model** (snapshot.json / SQLite / derived projections): aligns with constitutional §22 (graph-layer primacy). Leave.

---

## 5. ADG_HOTSPOT_REPORT *(not applicable)*

This is an analysis plan for *one file* with known fan-in (~12 call sites via `main()`, CLI workflows, `/adg-redis-refresh` slash command). It is **not a refactoring plan** in the constitutional §22 sense (no T2/T3 code edits). A hotspot report is not required at this stage. If/when W1–W5 are scheduled for execution, each execution wave will produce its own `## ADG_HOTSPOT_REPORT` per the rule.

## 6. ADG_GRAPH_LAYER_EVIDENCE *(not applicable — see §5)*

Same reasoning as §5. Execution waves will produce this section.

---

## 7. Gap Register

| # | Gap | Proof / Evidence | Status |
|---|---|---|---|
| G-1 | Double artifact write | Lines 605–628 | **OBSERVED** |
| G-2 | Duplicate `ADGGraphWatchlistBuilder` | Lines 811–820 vs 952–956 | **OBSERVED** |
| G-3 | Discarded `OwnershipRegistry` | Line 850 | **OBSERVED** |
| G-4 | Nested try + guardian swallow in phase-2 | Lines 657–674 | **OBSERVED** |
| G-5 | 3-way closure special-case | Lines 1102–1124 | **OBSERVED** |
| G-6 | 5-subprocess post-ADG tail | Lines 1327–1387 | **OBSERVED** |
| G-7 | Near-duplicate P4/P5/P6/P6b/P7 skip plumbing | Lines 705–820, 789–793 | **OBSERVED** |
| G-8 | Ad-hoc zip file list + mtime glob | Lines 1021–1083 | **OBSERVED** |
| G-9 | Three separate `_git_rev_parse` call sites | Lines 521, 528, 1133 | **OBSERVED** |
| G-10 | Skip ledger has no end-of-run summary | `_record_pipeline_skip` only appends | **OBSERVED** |
| G-11 | Three inline env-flag parsers | Lines 1013, 1129, 1136 | **OBSERVED** |
| G-12 | Module-level `sys.path.insert` under guardian | Lines 52–55 | **OBSERVED** |
| G-13 | Token estimator API mismatch | `ContextWindowEstimator.estimate_file` not found | **UNRESOLVED** — blocks precise wave sizing but not this analysis |

---

## 8. Deferred Scope

The following were *considered* but deliberately moved off this plan's critical path. They are captured here for cross-session memory; no Notion write-backs until promoted.

- **Scanner-level caching review** (`ADGStaticScanner` — already has a cache; audit hit-rate budget).
- **MV materialisation parallelism** (Phase A..E are currently sequential; some are independent).
- **`_auto_ingest_to_redis` latency** (not observed on the hot path, but worth baselining).
- **Gate dispatcher's own 600s timeout** (line 744 — aggressive; may hide regressions). Not in scope because it is not in `generate_full_adg.py`.

---

## 9. Review Instructions

1. Read §2 (Findings F-1 through F-12) in order.
2. For each finding, judge impact vs. confidence against your own read of the cited line range.
3. Approve or reject each wave independently — they are intentionally decoupled.
4. On approval of a wave, that wave's execution plan will be written as a *separate* plan file under `.windsurf/plans/` with its own 6-hex slug, and will include the mandatory `## ADG_HOTSPOT_REPORT` and `## ADG_GRAPH_LAYER_EVIDENCE` sections that this analysis plan legitimately omits.

---

**End of plan.**
