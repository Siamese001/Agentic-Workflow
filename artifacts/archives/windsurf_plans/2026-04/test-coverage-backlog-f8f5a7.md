# Test Coverage Backlog — Post Wave-C Remaining Scope

**Status**: Ready (backlog) — Last updated 2026-04-22
**Source of truth**: `artifacts/test_gaps/risk_weighted_04222026_1359.md`
**Method**: ADG fan-in × layer multiplier (constitutional §22, adg-canonical-invariants §6)

Documents the residual test-coverage gap across the repo **after** Waves A/B/C landed 825 behavioral tests (commits `506cf0e5f9` → `1af5f73d58`). Top-30 of the risk-weighted report is fully closed. This plan covers the tail.

---

## Wave Structure

### Priority revision 2026-04-22 (F5)

**Original scheme**: ADG fan-in × layer multiplier (L0/L5 ×2.0 first).

**Revised scheme**: Coverage-starvation × reachability. The post-F4 report
(`risk_weighted_04222026_1734.md`) shows:
- **L1 — 4.61% covered** (7/152) — most starved
- **L_OPS — 4.77% covered** (21/440) — biggest absolute gap
- **L5 — 12.28% covered** (48/391) — big but less starved
- **L0 — 42.70% covered** (38/89) — best-covered layer already

Strict layer-multiplier ranking under-weights starvation. Revised ordering
keeps L0/L5 ×2.0 for the **highest fan-in** rows but promotes L1/L_OPS
microwaves into D-tier when fan-in ≥ 3 regardless of multiplier. This
maximizes movement of the headline coverage % while still prioritizing
blast-radius.

| Wave | Phase IDs | Focus | Modules in scope | Est. Tokens | Assumptions | Status |
|---|---|---|---|---|---|---|
| Wave D0 | D0.1 | BLOCKER — fix gap-report Symbol-import detection | 1 script (`report_risk_weighted_test_gaps.py`) | 4000 🟢 | — | **Done** (commit `0da037a484`) |
| Wave D1 | D1.1–D1.3 | L0 + L5 tail (×2.0 multiplier), next 30 rows after top-30 | ~60 untested, fan-in ≥ 2 | 30000 🟢 | D0 done | Ready |
| Wave D1b | D1b.1 | **NEW (F5)** — L1 + L_OPS starvation microwaves, fan-in ≥ 3 | ~25 high-fan-in in L1/L_OPS | 12000 🟢 | After D0; promoted from E2 | Ready |
| Wave D2 | D2.1–D2.2 | L3 + L4 tail (×1.75) | ~50 untested, fan-in ≥ 2 | 22000 🟢 | After D1 | Ready |
| Wave D3 | D3.1 | L1 + L2 tail (×1.0) | ~40 untested, fan-in ≥ 2 | 16000 🟢 | After D2 | Ready |
| Wave D4 | D4.1 | L_RUNTIME + L_SHARED + L_PG + L_INFRA hotspots | ~30 high-fan-in | 12000 🟢 | After D3 | Ready |
| Wave D5 | D5.1 | L6 observability tail (×0.75) | ~20 targeted | 8000 🟢 | After D4 | Ready |
| Wave E1 | E1.1–E1.4 | apps_* coverage (see test-coverage-improvement-a1b2c3.md) | 78 files across apps_eval/exec/research/rfp | 56000 🟡 | Supersedes the older plan | Ready |
| Wave E2 | E2.1 | L_TOOLS + L_OPS + L_SL hotspots | 25 scripts with ≥3 callers | 10000 🟢 | After E1 | Ready |
| Descope | — | L_UNKNOWN (96% untested — likely dead code) | 80 modules | 0 | ADG triage first; delete candidates | Descoped |

**Grand total** (if fully executed): ~154,000 tokens. Most waves are independently shippable; no hard dependency chain across waves.

---

## Layer Gap Snapshot (from risk_weighted_04222026_1359.md)

| Layer | Modules | Untested | % | Layer ×mult | Priority |
|---|---:|---:|---:|:---:|:---:|
| L5 | 391 | 362 | 92.58% | 2.0 | **D1** |
| L0 | 89 | 64 | 71.91% | 2.0 | **D1** |
| L3 | 168 | 130 | 77.38% | 1.75 | **D2** |
| L4 | 142 | 129 | 90.85% | 1.75 | **D2** |
| L1 | 152 | 144 | 94.74% | 1.0 | **D3** |
| L2 | 195 | 163 | 83.59% | 1.0 | **D3** |
| L_RUNTIME | 66 | 55 | 83.33% | 1.0 | **D4** |
| L_SHARED | 322 | 279 | 86.65% | 1.0 | **D4** |
| L_PG | 125 | 102 | 81.60% | 1.0 | **D4** |
| L_INFRA | 17 | 12 | 70.59% | 1.0 | **D4** |
| L6 | 92 | 65 | 70.65% | 0.75 | **D5** |
| L_APP | 796 | 670 | 84.17% | 1.0 | **E1** |
| L_TOOLS | 625 | 539 | 86.24% | 1.0 | **E2** |
| L_OPS | 436 | 416 | 95.41% | 1.0 | **E2** |
| L_SL | 241 | 224 | 92.95% | 1.0 | **E2** |
| L_UNKNOWN | 83 | 80 | 96.39% | 1.0 | **Descope** |

Total: **3434 untested modules** across 3940 scored. Wave D1–D5 targets ~200 highest-impact nodes (fan-in-weighted). Waves E* cover the long tail.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|:---:|
| D1.1 | L5 reasoning tail (rows 31–60 of gap report) | ~30 L5 files, fan-in 2–3 | Large agent files, mock-heavy | 12000 | Ready |
| D1.2 | L5 enforcement gates | ~15 L5 enforcement files | Gate fixtures | 8000 | Ready |
| D1.3 | L0 routing tail | ~15 L0 files | Routing-contract fixtures | 10000 | Ready |
| D2.1 | L3 orchestration hotspots | ~25 L3 files | Orchestrator chain mocking | 12000 | Ready |
| D2.2 | L4 state/memory hotspots | ~20 L4 files | Store fixtures | 10000 | Ready |
| D3.1 | L1 cognition + L2 execution | ~40 files | Execution mode coverage | 16000 | Ready |
| D4.1 | Cross-cutting runtime/shared/pg/infra | ~30 files | Adapter mocking | 12000 | Ready |
| D5.1 | L6 observability | ~20 files | OTEL span fixtures | 8000 | Ready |
| E1.1 | apps_eval (21 files) | services/reasoning/outputs | See test-coverage-improvement-a1b2c3 | 15000 | Ready |
| E1.2 | apps_exec (18 files) | services/reasoning/outputs | See test-coverage-improvement-a1b2c3 | 13000 | Ready |
| E1.3 | apps_research (20 files) | services/reasoning/outputs | See test-coverage-improvement-a1b2c3 | 14000 | Ready |
| E1.4 | apps_rfp (19 files) | services/reasoning/outputs | See test-coverage-improvement-a1b2c3 | 14000 | Ready |
| E2.1 | L_TOOLS + L_OPS + L_SL hotspots | 25 scripts, fan-in ≥ 3 | Script testing patterns | 10000 | Ready |

---

## Gap Register

**GAP-1: ADG snapshot regenerated 2026-04-22 12:18 — RESOLVED**
New canonical snapshot `adg_indexed_04222026_1218.sqlite` (248 MB, 126s generation). Redis hot cache HOT. ADG MCP reloaded. All 4 CI gates (G1-G4) PASS. P0/P1/P2 ratchets stable at 0/0. Layer gap improvements: L0 71.91%→58.43% (-13.48pp), L4 90.85%→78.17% (-12.68pp), L5 92.58%→86.70% (-5.88pp). 49 modules dropped off untested list.

**GAP-2: Gap-report script has Symbol-import detection defect — NEW BLOCKER (Wave D0)**
Verified 2026-04-22 via ADG MCP: `ops_scripts/verification/report_risk_weighted_test_gaps.py` counts fan-in on Module→Module edges only. Test imports of form `from pkg.subpkg import module as alias` resolve to Symbol nodes (e.g., `ADG::Symbol::...` id 15116) rather than Module nodes (id 57), so those tests are invisible to the gap-report heuristic. Effect: safety_reasoning_seam, safety_validators_seam, safety_enforcement_seam (all tested in commits `1ffb383f87` and `8c28b16753`) still list as untested at rows 1-3 of the new gap report. Fix: extend fan-in query to UNION Module-targeted and Symbol-targeted edges where the Symbol's resolved_path matches a Module's resolved_path. Expect another 30-60 modules to drop off untested list after fix. BLOCKS Wave D1+ scope accuracy.

**GAP-3: MRO fix in FileClassificationAgent (commit `7531ee74d9`)**
Wave C1 fixed a real import-time bug (`BASE_CLASSES = (AtomicExecutionMixin, SovereignBaseAgent)` → `(SovereignBaseAgent,)`). Monitor downstream agents for similar patterns where an explicit mixin duplicates an existing base.

**GAP-4: apps_* plan (`test-coverage-improvement-a1b2c3.md`) predates this backlog**
Wave E1 absorbs its scope. Do not run the old plan standalone — it lacks the gap-report prioritization.

**GAP-5: L_UNKNOWN descope**
83 modules with 96% gap rate. Likely dead code from `archives/` drift. Triage first (`adg_edge_fanin` + `git log --name-only`) — delete candidates rather than test.

**GAP-6: Stashed pre-existing UTC→ET autofixer diffs — PARKED (2026-04-22 F3)**
`stash@{0}: On main: pre-existing-autofixer-diffs-2026-04-22-preWaveC-close` contains ~30 production files where an earlier autofixer substituted UTC timestamps with America/New_York local time. User stashed pre-Wave-C to avoid shipping semantic regressions. Disposition: **keep parked** pending a dedicated review wave. NOT dropped, NOT applied. To review later: `git stash show -p stash@{0}` then decide file-by-file. Do not discard without explicit user decision — contains legitimate work mixed with regressions.

---

## Acceptance

For each wave D1–E2: per-wave microwave commits with behavioral tests (constitutional §1, no skips, no xfail without strict=True). Each microwave ≤ ~50 tests, scoped to one file family, ends in `git add + commit + push`. Pattern matches Waves A/B/C.

## Execution Notes

- **ADG regenerated 2026-04-22 12:18** — snapshot `adg_indexed_04222026_1218.sqlite`. Redis HOT. MCP reloaded.
- **Do NOT start Wave D1 before Wave D0 lands.** The gap-report script has a detection defect (see GAP-2) — starting D1 with the current output will waste effort on already-covered seam modules.
- **Author-Gate triggers**: any module hitting the 4 deadly antipattern edges (broad_exception_catch, log_and_swallow, silent_exception_swallow, return_none_swallow) — apply anti-pattern-author-gate rule.
- **MRO audits**: while writing agent tests, grep for `BASE_CLASSES = (...)` patterns that duplicate mixins already in `SovereignBaseAgent.__mro__`. Fix upstream, don't work around.
- **Backlog is non-blocking.** Waves D–E are independently shippable; no hard sequence beyond "regenerate ADG first."
