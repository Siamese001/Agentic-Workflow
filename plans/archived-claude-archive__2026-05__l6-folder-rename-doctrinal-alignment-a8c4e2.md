---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\l6-folder-rename-doctrinal-alignment-a8c4e2.md'
original_relative_path: '_archive\\2026-05\\l6-folder-rename-doctrinal-alignment-a8c4e2.md'
source_sha256: bc29ad310d6785eacdb1e9baed9cc0f16a8d80d7d9fee658b4866cf9b89f5317
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L6 Folder Rename — Doctrinal Alignment of Code Layout to Layer Doctrine

> **Status: Deprioritized (deferred).** Scope-defining plan only — DO NOT IMPLEMENT until explicitly promoted to In Progress. Captures the rename strategy, blast radius, shim/grace-period mechanics, and rollback contract for aligning physical code layout with the L6 doctrinal model (Observability + System Learning are one layer, two surfaces).

## 1. Background

Per the doctrine in `@c:\Git\Agentic-Workflow-FRESH\docs\reference\06_L6_Shadow_Evaluation_System_Learning` (chapters 06.1–06.9), L6 is **one layer with two surfaces**:

```
L6 (one layer)
├── Observability         → passive: capture exhaust          → agentic_core/L6_observability/
└── System Learning       → active: learn from exhaust        → system_learning/   ← NO L6_ PREFIX
    ├── Shadow Evaluation     (06.2, 06.3 — observe-only eval)
    ├── Meta-Learning         (system_learning/meta_learning/ — 06.5 fusion, 06.6 proposals)
    └── Promotion Loop        (06.7 gauntlet → UWG → L4)
```

The code layout violates the layer-prefix convention: `system_learning/` is a top-level package without the `L6_` prefix, despite being doctrinally part of L6. ADG already tags 100+ `system_learning/` modules as `layer=L6` (via layer-resolution heuristics), so the rename is cosmetic at the ADG level but doctrinally correct at the filesystem/import level.

## 2. Files In Scope (target rename)

| Current path | Target path | Reason |
|---|---|---|
| `system_learning/` | `agentic_core/L6_system_learning/` | Apply L6_ prefix; collocate with `L6_observability/` under `agentic_core/`. |
| `tests/unit/system_learning/` | `tests/unit/L6_system_learning/` | Mirror code-tree rename. |
| `tests/integration/system_learning/` (if any) | `tests/integration/L6_system_learning/` | Mirror code-tree rename. |

`agentic_core/L6_observability/` stays as-is (already correctly prefixed).

## 3. Blast Radius (measured 2026-05-09)

- **205 Python files** contain `from system_learning` or `import system_learning`.
- **413 import-line matches** total.
- Top hot-spots: `system_learning/pipelines/meta_learning_pipeline.py` (24), `system_learning/engines/semantic_index_registry.py` (11), `system_learning/engines/meta_learning_bus.py` (8), `system_learning/types/__init__.py` (6).
- Cross-tree consumers: `agentic_core/L6_observability/`, `tools/debug/`, `tools/runtime_cert/`, `tests/unit/system_learning/`.
- ADG impact: 100+ nodes change `resolved_path`. ADG must be regenerated post-rename.

## 4. Strategy — Minimal-Disruption Shim + Grace Period

Reject in-place mass rewrite. Adopt the **shim-and-deprecate** pattern that's been successful for prior layer reorgs:

### Wave 1 — Move + shim (atomic single PR)

1. `git mv system_learning agentic_core/L6_system_learning` (preserves history).
2. Create top-level shim at `system_learning/__init__.py`:
   ```python
   """Compatibility shim — import from agentic_core.L6_system_learning instead.

   This module re-exports agentic_core.L6_system_learning.* for backward
   compatibility. Will be removed after the grace period (target: 2026-Q3).
   """
   import warnings
   from agentic_core.L6_system_learning import *  # noqa: F401,F403
   from agentic_core.L6_system_learning import __all__  # noqa: F401

   warnings.warn(
       "Importing from `system_learning` is deprecated; use "
       "`agentic_core.L6_system_learning` instead. The shim will be removed "
       "after the grace period.",
       DeprecationWarning,
       stacklevel=2,
   )
   ```
3. Create per-submodule shims for each existing top-level subpackage (`adapters/`, `arbitration/`, `buses/`, `confidence/`, `correlation/`, `embedding/`, `enforcement/`, `engines/`, `meta_learning/`, `pipelines/`, `runtime_adg/`, `runtime_hitl_consumer.py`, `types/`, `validators/`, etc.) that re-export from the new path. Generate via script — do NOT hand-write 30+ shim files.
4. Update `pyproject.toml` package list to include `agentic_core.L6_system_learning` (and keep `system_learning` as a shim package for one release).
5. Regenerate ADG: `python tools/generate_full_adg.py`.
6. Run full test suite: `pytest tests/unit/L6_system_learning tests/_apps_contract` — expected: zero regressions because shim preserves import surface.
7. Deprecation warnings will surface in test runs but are non-fatal.

### Wave 2 — Migrate first-party importers (paced)

Migrate import sites from `system_learning` → `agentic_core.L6_system_learning` in batches grouped by ownership domain:

- Batch 2.1: `agentic_core/L6_observability/` consumers (~5 files).
- Batch 2.2: `tools/debug/`, `tools/runtime_cert/` (~10 files).
- Batch 2.3: `system_learning/` internal cross-imports (~150 files — these become `agentic_core/L6_system_learning/` internal imports).
- Batch 2.4: `tests/unit/system_learning/` → `tests/unit/L6_system_learning/` and update test imports.
- Each batch: `ruff --fix` import sorting + targeted test sweep. Single PR per batch.

### Wave 3 — Shim removal (after grace period)

After 2026-Q3 (or 30 days post-Wave-2 completion, whichever later):

1. Confirm zero `from system_learning` / `import system_learning` matches via `rg`.
2. CI gate: add `check_no_system_learning_top_level_imports.py` that fails when matches found outside the shim itself.
3. Delete `system_learning/` shim directory.
4. Final ADG regen.

## 5. Doc Folder Rename (parallel, lower risk)

After Wave 1 lands, rename `docs/reference/06_L6_Shadow_Evaluation_System_Learning/` → `docs/reference/06_L6_Observability_and_System_Learning/` to reflect the merged scope (already merged into one folder 2026-05-09 per request from this plan's authoring session).

Update internal markdown links via `rg -l '06_L6_Shadow_Evaluation_System_Learning' docs/` then sed-batch.

## 6. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1 git mv, P1.2 shim authoring, P1.3 ADG regen | Move + shim — atomic landing of new path with full back-compat | ~12k | shim covers full public surface; deprecation warning is non-fatal | Not Started | All existing tests pass with shim active; ADG regenerates cleanly; deprecation warnings logged. |
| W2 | P2.1–P2.4 batched migration | Migrate import sites in 4 ownership-grouped batches | ~25k | each batch is ≤50 files; one PR per batch | Not Started | Zero behavioral regressions per batch; per-batch test sweep green. |
| W3 | P3.1 audit, P3.2 CI gate, P3.3 shim removal | Remove shim and lock with CI gate | ~6k | grace period elapsed; zero remaining `system_learning` imports | Not Started | `system_learning/` directory deleted; CI gate active; final ADG regen clean. |
| W4 | P4.1 doc folder rename, P4.2 link updates | Doc-tree alignment | ~3k | only markdown link updates required | Not Started | All `docs/reference/` cross-links resolve; folder name reflects merged scope. |

## 7. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | git mv system_learning | 1 directory move (preserves git history) | git history preservation across rename — verify with `git log --follow` | ~1k | Not Started |
| P1.2 | Shim authoring | 1 top-level + ~15 submodule shims (script-generated) | covering `__all__` correctly for star-import call sites | ~5k | Not Started |
| P1.3 | ADG regenerate | 1 invocation, full reindex | ~100 nodes change resolved_path; downstream MV/P-view recomputation | ~3k | Not Started |
| P1.4 | pyproject.toml + setup.cfg updates | 1–2 files | ensure both packages declared during grace period | ~1k | Not Started |
| P1.5 | Smoke test | full pytest sweep | flaky tests unrelated to rename — keep noise floor low | ~2k | Not Started |
| P2.1 | Migrate L6_observability consumers | ~5 files | none expected | ~3k | Not Started |
| P2.2 | Migrate tools/ consumers | ~10 files | runtime_cert evidence path strings may embed `system_learning` literal | ~4k | Not Started |
| P2.3 | Migrate L6_system_learning internal imports | ~150 files | high file count, but mechanical sed-style edit | ~10k | Not Started |
| P2.4 | Migrate tests | ~40 files | test directory rename + import updates | ~6k | Not Started |
| P3.1 | Final import audit | full repo grep | hidden dynamic imports via `importlib.import_module("system_learning.X")` | ~2k | Not Started |
| P3.2 | CI gate authoring | 1 new file + tests | bypass env var convention | ~3k | Not Started |
| P3.3 | Shim removal | delete shim dir | irreversible — gate behind explicit user approval | ~1k | Not Started |
| P4.1 | Rename docs folder | 1 directory rename | none | ~1k | Not Started |
| P4.2 | Update doc cross-links | ~10 markdown files | link-rot risk in archived plans referencing old folder | ~2k | Not Started |

## 8. Non-Goals

- **NOT renaming `agentic_core/L6_observability/`.** Already correctly prefixed.
- **NOT changing the ADG layer-resolution heuristic.** Rename should be cosmetic at the ADG level.
- **NOT consolidating L6_observability and L6_system_learning into a single package.** They remain distinct surfaces of the same layer.
- **NOT migrating Notion / artifact references** to old paths — those are point-in-time records, not live import paths.

## 9. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Star-import surface drift between shim and target | Medium | Medium | Script-generate shims by introspecting target `__all__`; include shim-completeness test. |
| Dynamic imports via `importlib.import_module` miss the rename | Low | High | grep for `import_module.*system_learning` in P3.1; pattern is rare. |
| ADG regen fails post-rename | Low | High | Pre-flight: run `python tools/generate_full_adg.py --dry-run` (if supported) on a branch before merging W1. |
| Grace period rushed; shim removed before all consumers migrated | Medium | High | Hard gate W3.P3.3 behind a CI check that confirms zero non-shim imports. |
| Breaking import order in tests due to deprecation-warning side effects | Low | Low | Filter `DeprecationWarning` in `pytest.ini` for `system_learning` module during grace period. |

## 10. Success Criteria

- All 205 import sites migrated to `agentic_core.L6_system_learning`.
- `system_learning/` shim directory removed.
- CI gate `check_no_system_learning_top_level_imports.py` active and green.
- ADG layer column for affected nodes still reads `L6` (no regression).
- Doc folder renamed; cross-links resolve.
- Zero behavioral test regressions across all four waves.

## 11. Rollback Contract

- W1: `git revert` of the move commit restores `system_learning/` at top level. Shims removed atomically with the revert.
- W2: per-batch revert is safe because shim still active.
- W3: shim deletion is the only irreversible step. Gate behind: (a) explicit user approval, (b) 30-day clean-import window, (c) successful CI gate run for 7 consecutive days.
- W4: doc folder rename is trivially reversible via `git mv` reverse.

## 12. References

- `@c:\Git\Agentic-Workflow-FRESH\docs\reference\06_L6_Observability_and_System_Learning` (folder pending W4 rename; currently `06_L6_Shadow_Evaluation_System_Learning/`)
- ADG canonical invariants: `.cursor/rules/adg-canonical-invariants.md`
- Constitutional §5 (ADG before T2/T3), §22 (graph-layer primary driver), §36 (plan registration)
- Apps folder taxonomy precedent (ADR-082) — same shim+grace-period pattern.

---

**Plan slug:** `l6-folder-rename-doctrinal-alignment-a8c4e2`
**Authored:** 2026-05-09
**Authored from:** session merging `06_L6_Observability/` into `06_L6_Shadow_Evaluation_System_Learning/`.
**Implementation status:** **Deprioritized — DO NOT IMPLEMENT** until explicitly promoted.
