---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\l6-alignment-deferred-scope-c5e8a7.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\l6-alignment-deferred-scope-c5e8a7.md'
source_sha256: 5d01fb91382884827006976195dee6b99e2c211c6042e6fdde3ff58cf79bb344
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L6 Alignment — Deferred Scope

> **Status: In Progress.** Execution plan converting deferred items from the parent plan `l6-doctrinal-alignment-noninvasive-b9d3f5` (Completed) and the parked invasive sibling `l6-folder-rename-doctrinal-alignment-a8c4e2` (Deprioritized) into actionable waves.

## 1. Origin

The non-invasive alignment plan landed all six waves successfully but each gate surfaced real findings that exceed the plan's non-invasive scope. Rather than blur the boundary, the parent plan was marked Completed with these items captured here.

## 2. Deferred Items

### D1. Observer-law violations in `system_learning/ports/`

**Surfaced by:** `ops_scripts/ci/check_l6_observer_law.py` (gate L6-OBS).

**Findings:**
- `system_learning/ports/meta_outcome_bus_hook.py:89` — imports `agentic_core.L3_orchestration.healers.healing_tier_dispatcher`
- `system_learning/ports/outcome_write_back_hook.py:91` — same import

**Question:** Are these legitimate (the UWG promotion path from chapter 06.7 does cross back into runtime, by design) or genuine observer-law breaches that need refactoring?

**Resolution paths:**
1. **Refactor.** Replace the dispatcher import with a read-only contract or a queued-event adapter that doesn't directly invoke the dispatcher. Preserves observer-law strictly.
2. **Allowlist.** If these are legitimate UWG-promotion-path crossings, add a `config/l6_observer_law_allowlist.yaml` with explicit reasons + ADR cross-reference, and update the gate to honor it.
3. **Doctrinal exception.** Document chapter 06.7 as the legitimate promotion-path exception in `06.2_L6_Observer_Law_Surface_Isolation_and_Eval_Readiness.md` and amend the gate's pattern to ignore promotion-gate code paths.

**Estimated effort:** 1–2 days (option 1) / 0.5 day (options 2 or 3).

**Promotion gate:** Once resolved, flip `L6_OBSERVER_LAW_FAIL_CLOSED=1` to enforce.

### D2. ADG layer-resolution heuristic does not tag `system_learning/*` as L6

**Surfaced by:** `ops_scripts/ci/check_l6_layer_tag_consistency.py` (gate L6-TAG).

**Findings:** 292 modules under `system_learning/` not tagged `layer=L6` in the latest ADG snapshot (`adg_indexed_05052026_0722.sqlite`). The earlier claim in this plan's authoring session that "ADG already tags `system_learning/*` as L6" was incorrect — verified empirically via SQLite read.

**Root cause hypothesis:** ADG layer-resolution likely uses a path-prefix heuristic that matches `agentic_core/L<N>_<name>/` and falls back to a default layer for everything else. `system_learning/` at repo root never hits the L6 prefix.

**Resolution paths:**
1. **Update ADG heuristic.** Add `system_learning/` (and the new `agentic_core/L6_system_learning/` alias) to the L6-resolution rules. File: probably `tools/adg/_layer_resolver.py` or similar (TBD via grep).
2. **Tag via in-tree marker.** If the ADG ingester is willing, have it read `__layer__` from `__init__.py` files at indexing time and override the path heuristic. This is the most architecturally principled fix because it makes in-tree markers (W1) the source of truth.
3. **Accept and document.** If neither is feasible, document the gap and live with `L6-TAG` as advisory-only.

**Recommended:** Option 2 — `__layer__` becomes SSOT.

**Estimated effort:** 2–3 days (option 2) / 1 day (option 1) / 0 days (option 3, but lowest value).

**Promotion gate:** Once resolved, regenerate the ADG (`python tools/generate_full_adg.py`) and flip `L6_LAYER_TAG_FAIL_CLOSED=1`.

### D3. Documentation alignment artifacts (low priority)

- The merged folder `docs/reference/06_L6_Shadow_Evaluation_System_Learning/` should be renamed to `06_L6_Observability_and_System_Learning/` to reflect that it now holds both the exhaust-schema doc and the shadow-eval/system-learning chapters.
- 06_Shadow_Evaluation_System_Learning.md (the index) does not yet reference LAYER.md or the alignment-status section in the mental model.

**Estimated effort:** 1–2 hours.

### D4. Invasive rename (parked)

The full move `system_learning/` → `agentic_core/L6_system_learning/` is tracked in plan `l6-folder-rename-doctrinal-alignment-a8c4e2` (Deprioritized). The non-invasive alignment that landed (parent plan `b9d3f5`) is the prerequisite — all the markers/alias/gates are now in place to de-risk the eventual rename. **Do not promote to In Progress until D1 + D2 are resolved**, otherwise the gates would be moving targets during the rename.

**Estimated effort:** 4–5 days for the full rename + grace period (per that plan).

### D5. CI gate test layout SSOT compliance

The two new test files (`tests/unit/ops_scripts/ci/test_check_l6_*.py`) match other CI-gate tests' layout but were created without explicit verification against the SSOT folder routing rules. Audit pass should confirm they're in the canonical location and that the gates themselves register properly via `run_contract_gates.py`.

**Estimated effort:** 30 minutes (audit only).

## 3. Wave Structure

| Wave | Item | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | D2 | Update ADG layer-resolver to honor `__layer__` markers | ~10k | ADG ingester allows per-file override; indexer perf acceptable | Not Started | L6-TAG gate reports 100% coverage; promoted to fail-closed |
| W2 | D1 | Resolve `system_learning/ports/` observer-law findings | ~6k | Chapter 06.7 promotion-path exception documented or refactor is non-breaking | Not Started | L6-OBS gate reports zero findings; promoted to fail-closed |
| W3 | D3 | Doc folder rename + index updates | ~3k | No downstream links outside `docs/reference/` | Not Started | All cross-links resolve; index references LAYER.md + alignment status |
| W4 | D5 | CI gate test layout audit | ~1k | Gates already registered via `run_contract_gates.py` | Not Started | Tests in canonical location; gates registered correctly |
| W5 | D4 | (Optional) Promote invasive rename `a8c4e2` to In Progress | ~30k+ | W1 + W2 complete; gates fail-closed | Blocked on W1 + W2 | All 4 waves of `a8c4e2` ship; shim removal CI gate live |

## 4. Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | ADG layer-resolver investigation | Find which file owns the L<N> path-prefix heuristic | path-discovery via grep — single afternoon | ~2k | Not Started |
| P1.2 | Add `__layer__` honor logic to resolver | Read each `__init__.py` at index time; override path inference when present | thread-safety + perf in the indexer | ~6k | Not Started |
| P1.3 | Regen ADG + verify gate green | `python tools/generate_full_adg.py`; rerun L6-TAG; expect 0 missing | none | ~2k | Not Started |
| P2.1 | Diagnose `*_hook.py` dispatcher imports | Read both files; trace what they actually call on the dispatcher | may need ADR review re. promotion path | ~2k | Not Started |
| P2.2 | Refactor or allowlist | Apply chosen path (refactor / allowlist YAML / doctrinal exception) | breaking changes if refactor — paced rollout | ~4k | Not Started |
| P3.1 | Rename `06_L6_Shadow_Evaluation_System_Learning/` → `06_L6_Observability_and_System_Learning/` | `git mv` + update doc cross-links | none | ~1k | Not Started |
| P3.2 | Update doc index + LAYER.md cross-references | 1 markdown edit | none | ~1k | Not Started |
| P3.3 | Drop alignment status from mental model into chapter index | dedupe authoring | none | ~1k | Not Started |
| P4.1 | Audit CI gate test layout | confirm SSOT folder routing | none | ~1k | Not Started |
| P5.1 | (Optional) Promote a8c4e2 | flip Notion status; execute that plan's W1 | many — see a8c4e2 | ~30k | Blocked |

## 5. Non-Goals

- Resolving `agentic_core/L2_execution/providers` `DeprecationWarning` (unrelated; surfaced in test runs but pre-existing).
- Closing chapter 06.X gaps in the doctrinal docs (different scope).
- Adding new L6 features (this is alignment, not feature work).

## 6. References

- Parent (Completed): `.windsurf/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md`
- Sibling (Deprioritized): `.windsurf/plans/l6-folder-rename-doctrinal-alignment-a8c4e2.md`
- Mental model: `@c:\Git\Agentic-Workflow-FRESH\docs\reference\_notes\L6_mental_model.md`
- L6-OBS gate report: `artifacts/windsurf/l6_observer_law_violations.json`
- L6-TAG gate report: `artifacts/windsurf/l6_layer_tag_violations.json`

---

**Plan slug:** `l6-alignment-deferred-scope-c5e8a7`
**Authored:** 2026-05-09
**Promoted:** 2026-05-09
**Implementation status:** **In Progress.** Execute W1 → W2 → W3 → W4 in sequence. W5 gated on W1 + W2 completion.
