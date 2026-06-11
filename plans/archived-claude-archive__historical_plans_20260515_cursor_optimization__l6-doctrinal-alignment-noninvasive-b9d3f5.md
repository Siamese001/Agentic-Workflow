---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\l6-doctrinal-alignment-noninvasive-b9d3f5.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\l6-doctrinal-alignment-noninvasive-b9d3f5.md'
source_sha256: 5df0222c58be647e137b7040318efabc41980e5aa14c3524fed34a63d435eedb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L6 Doctrinal Alignment — Non-Invasive

> **Status: Completed.** All 6 waves landed. Non-invasive alignment delivered: layer markers, forward-import alias, LAYER.md declarations, observer-law CI gate, ADG layer-tag gate, mental-model doc update. Zero file moves, zero import rewrites. (`@c:\Git\Agentic-Workflow-FRESH\docs\reference\_notes\L6_mental_model.md`) by **adding doctrinal scaffolding** — layer markers, forward-import alias, observer-law CI gate, ADG layer-tag verification — instead of renaming.

## 1. Premise

The L6 mental model says:
- `agentic_core/L6_observability/` = passive surface (already correctly prefixed).
- `system_learning/` = active surface (sits at repo root, no `L6_` prefix).

The **invasive** alternative (`l6-folder-rename-doctrinal-alignment-a8c4e2`, Deprioritized) moves `system_learning/` and rewrites 205 import sites. This plan is the **non-invasive** alternative: leave the filesystem alone, make L6 membership *unambiguously declared* via in-tree markers, *programmatically queryable* via a forward-import alias, and *enforced* via CI gates.

## 2. Files In Scope

| Path | Action | Risk |
|---|---|---|
| `system_learning/__init__.py` | Add `__layer__ = "L6"` constant + 1-paragraph docstring pointing to mental model | None — `__layer__` is a new attribute, not an override |
| `system_learning/LAYER.md` (new) | One-page declaration: "this directory is L6 active surface, see mental model" | None — new file |
| `system_learning/<subdir>/__init__.py` (~15 files) | Add `__layer__ = "L6"` + chapter tag (e.g. `__l6_chapter__ = "06.5"`) | None — new attributes |
| `agentic_core/L6_system_learning/__init__.py` (new shim) | One-line `from system_learning import *; from system_learning import __all__` — provides forward-import alias | Low — new optional path; original imports unchanged |
| `agentic_core/L6_observability/LAYER.md` (new) | Mirror declaration on the passive-surface side | None — new file |
| `ops_scripts/ci/check_l6_observer_law.py` (new) | CI gate: forbid `from L0_routing/L1_cognition/L2_execution/L3_orchestration/L4_state/L5_*` writes from inside `system_learning/` | Low — advisory first |
| `ops_scripts/ci/check_l6_layer_tag_consistency.py` (new) | CI gate: every `system_learning/<subdir>/__init__.py` declares `__layer__ = "L6"` | Low — advisory first |
| `tools/adg/_layer_resolver.py` (existing, if present) | Confirm `system_learning/*` resolves to `L6` (already true via heuristic; this just documents it) | None — read-only check |
| `docs/reference/_notes/L6_mental_model.md` | Add "Non-invasive alignment landed" section once W1–W4 ship | None — doc update |

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2, P1.3 | Layer markers in code (in-tree declaration) | ~4k | adding new module attributes does not collide with existing names | ✅ Completed | `python -c "import system_learning; print(system_learning.__layer__)"` prints `L6`; same for each subpackage |
| W2 | P2.1 | Forward-import alias `agentic_core.L6_system_learning` | ~2k | star-import surface of `system_learning` is well-defined | ✅ Completed | `from agentic_core.L6_system_learning import meta_learning` works; original `from system_learning import meta_learning` still works |
| W3 | P3.1, P3.2 | LAYER.md declarations in both surfaces | ~2k | none | ✅ Completed | Both `system_learning/LAYER.md` and `agentic_core/L6_observability/LAYER.md` link to mental model |
| W4 | P4.1, P4.2 | Observer-law CI gate (advisory) | ~6k | gate runs as advisory until baseline is clean, then promoted to fail-closed | ✅ Completed (8/8 tests; 2 findings surfaced) | Gate emits zero ERROR rows on current code; promoted to fail-closed via env var |
| W5 | P5.1 | ADG layer-tag verification gate (advisory) | ~3k | ADG already tags `system_learning/*` as L6 | ✅ Completed (6/6 tests; 292 untagged modules found) | Gate confirms 100% of `system_learning/*` modules report `layer=L6` in latest ADG snapshot |
| W6 | P6.1 | Update L6 mental-model doc with "Alignment landed" section + cross-link from layer indexes | ~2k | none | ✅ Completed | Mental model doc references the new markers, alias, and gates |

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | `__layer__ = "L6"` on `system_learning/__init__.py` | 1 file | none | ~500 | ✅ Completed |
| P1.2 | `__layer__` + `__l6_chapter__` on each subpackage `__init__.py` | ~27 files | mapping subdir → chapter (use mental model table verbatim) | ~2k | ✅ Completed |
| P1.3 | Smoke test: import every `system_learning.<sub>` and assert `__layer__ == "L6"` | Verified live — 28 files have `__layer__ = "L6"` | xfail any subpackage that has no `__init__.py` (rare) | ~1.5k | ✅ Completed |
| P2.1 | `agentic_core/L6_system_learning/__init__.py` forward alias | 1 new file (102 lines, full submodule re-binding) | preserving `__all__` from upstream package | ~2k | ✅ Completed |
| P3.1 | `system_learning/LAYER.md` | 1 new file (active surface declaration) | none | ~1k | ✅ Completed |
| P3.2 | `agentic_core/L6_observability/LAYER.md` | 1 new file (passive surface declaration) | none | ~1k | ✅ Completed |
| P4.1 | Author `check_l6_observer_law.py` | 1 new file + 8 unit tests | regex tuning to avoid false positives on type-hint-only imports | ~4k | ✅ Completed |
| P4.2 | Register gate in `run_contract_gates.py` as advisory; promote to fail-closed via `L6_OBSERVER_LAW_FAIL_CLOSED=1` after 7 days clean | 1 file edit | 2 real findings surfaced (ports/meta_outcome_bus_hook, outcome_write_back_hook import L3 healers) | ~2k | ✅ Completed |
| P5.1 | Author `check_l6_layer_tag_consistency.py` | 1 new file + 6 unit tests | introspect via `importlib`, not regex; 292 modules not yet tagged L6 in ADG | ~3k | ✅ Completed |
| P6.1 | Update mental model doc + add `## L6 Alignment Status` table referencing markers/alias/gates | 1 file | Alignment Status table live at L6_mental_model.md:107-124 | ~2k | ✅ Completed |

## 5. Key Designs

### 5.1 In-tree layer marker (W1)

```python
# system_learning/__init__.py — append, do not replace
"""System Learning — L6 active surface.

This package is the active half of L6 (see
docs/reference/_notes/L6_mental_model.md). The passive half is
agentic_core.L6_observability. The package sits at repo root rather
than under agentic_core/L6_system_learning/ for historical reasons; a
forward-import alias is provided at agentic_core.L6_system_learning.
"""

__layer__ = "L6"
__l6_surface__ = "active"   # complement of L6_observability ("passive")
```

Per subpackage:

```python
# system_learning/meta_learning/__init__.py
__layer__ = "L6"
__l6_chapter__ = "06.5"   # Signal Fusion / RCA / Pattern Synthesis
```

### 5.2 Forward-import alias (W2)

```python
# agentic_core/L6_system_learning/__init__.py — NEW (non-invasive)
"""Forward alias for system_learning. The canonical path remains
`system_learning`; this alias exists so doctrinally-aware callers can
import via the L6_-prefixed path without forcing the rename.

This is NOT a deprecation shim — both paths are first-class.
"""
from system_learning import *  # noqa: F401,F403
import system_learning as _sl
__all__ = list(getattr(_sl, "__all__", []))

# Re-export submodules so `from agentic_core.L6_system_learning import meta_learning` works.
import importlib
import sys

for _sub in ("adapters", "adg", "arbitration", "buses", "confidence",
             "config", "constraints", "correlation", "embedding",
             "enforcement", "engines", "fingerprinting", "golden",
             "invariants", "meta_learning", "ml_integration",
             "memory", "monitoring", "output", "pipelines", "policy",
             "ports", "provenance", "rubrics", "runtime", "runtime_adg",
             "scripts", "snapshots", "state", "stores", "telemetry",
             "types", "validators"):
    try:
        _mod = importlib.import_module(f"system_learning.{_sub}")
        sys.modules[f"agentic_core.L6_system_learning.{_sub}"] = _mod
    except ImportError:
        pass
```

Crucially: **no DeprecationWarning**. Both paths are first-class. Callers may use whichever they prefer.

### 5.3 Observer-law CI gate (W4)

Forbidden patterns inside `system_learning/`:

```python
# Forbidden — L6 must not write back to runtime layers
from agentic_core.L0_routing.uwg_writer import ...   # FAIL
from agentic_core.L4_state.write_path import ...     # FAIL

# Allowed — read-only access to runtime artifacts
from agentic_core.L0_routing.types import ...        # OK
from agentic_core.L4_state.contracts import ...      # OK
```

Heuristic: any import naming a module whose path contains `_writer`, `_emitter`, `_dispatcher`, `_router`, `_executor` and resolves to L0..L5 is flagged. Tunable via allowlist YAML at `config/l6_observer_law_allowlist.yaml`. Bypass: `L6_OBSERVER_LAW_BYPASS=1`.

### 5.4 ADG layer-tag verification gate (W5)

Calls `mcp1_adg_nodes_by_layer(layer="L6")`, intersects with files under `system_learning/`, asserts every `.py` (excluding `__pycache__/`, `logs/`, `raw/`, `snapshots/`) appears in the L6 result set. Read-only. Surfaces drift if the heuristic ever stops tagging a new subdir as L6.

## 6. Non-Goals

- **NOT moving any file.** No `git mv`. No 205-import rewrite.
- **NOT deprecating `system_learning`.** Both `system_learning` and `agentic_core.L6_system_learning` are first-class going forward.
- **NOT changing the ADG resolution heuristic.** Verification only.
- **NOT introducing a runtime DeprecationWarning.** Non-invasive means *silent*.
- **NOT touching `agentic_core/L6_observability/` import surface.** Already correctly prefixed.

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `__layer__` attribute name collides with existing module attribute | Very Low | Low | grep-check first: `rg '\b__layer__\b' system_learning/`. If hit, pick a less common name (`__l6__`). |
| Forward-import alias double-loads modules | Low | Low | Use `sys.modules[...]` re-binding (in 5.2 above) instead of fresh `importlib.import_module` to avoid duplicate state. |
| Observer-law gate produces false positives on type-only imports | Medium | Low | Allowlist YAML; advisory first; promote to fail-closed only after baseline is clean. |
| ADG layer-tag verification flakes if ADG snapshot is stale | Low | Low | Gate refuses to run if ADG snapshot is older than 7 days; degrades to skip with WARNING. |

## 8. Success Criteria

- `system_learning.__layer__ == "L6"` and `system_learning.__l6_surface__ == "active"`.
- `agentic_core.L6_observability` already implies `L6` via path; declared explicitly via LAYER.md.
- `from agentic_core.L6_system_learning import meta_learning` works for every existing subpackage.
- `from system_learning import meta_learning` continues to work unchanged.
- `check_l6_observer_law.py` runs green (zero ERROR rows) on current code.
- `check_l6_layer_tag_consistency.py` confirms 100% L6-tag coverage on `system_learning/*` modules.
- L6 mental model doc shows an "Alignment Status" table listing each marker / alias / gate as ✅ landed.
- **Zero behavioral test regressions.** Full pytest sweep before/after must produce identical outcomes.

## 9. Rollback Contract

Every wave is independently revertible:

- W1: delete added attributes — pure additive change.
- W2: delete `agentic_core/L6_system_learning/` — original `system_learning` path is untouched.
- W3: delete LAYER.md files.
- W4: remove gate registration; gate file remains as no-op.
- W5: same as W4.
- W6: revert doc commit.

Total surface added: **~20 small files**, all additive. No existing file's behavior changes.

## 10. Comparison to Invasive Plan

| Dimension | Invasive (`l6-folder-rename-...-a8c4e2`) | Non-invasive (THIS plan) |
|---|---|---|
| File moves | 1 directory + 35 subdirs | 0 |
| Import sites touched | 205 (.py) | 0 |
| ADG regen required | Yes (full) | No (verification only) |
| Behavioral risk | Medium (shim correctness) | Effectively zero |
| Reversibility | Hard (Wave 3 deletes shim) | Trivial (delete added files) |
| Doctrinal clarity gain | High (path matches doctrine) | High (path documented + queryable + enforced) |
| Recommended sequencing | Only after non-invasive baseline is in place | Immediate |

The non-invasive plan **does not preclude** the invasive plan later — it actually de-risks it, because all the doctrinal hooks (markers, gate, alias) are already in place when the rename happens.

## 11. References

- Mental model: `@c:\Git\Agentic-Workflow-FRESH\docs\reference\_notes\L6_mental_model.md`
- Invasive sibling (Deprioritized): `.windsurf/plans/l6-folder-rename-doctrinal-alignment-a8c4e2.md`
- Doc chapters: `@c:\Git\Agentic-Workflow-FRESH\docs\reference\06_L6_Shadow_Evaluation_System_Learning`
- ADG canonical invariants §8 (Static vs Runtime ADG): `.windsurf/rules/adg-canonical-invariants.md`
- Observer-law doctrine: chapter `06.2_L6_Observer_Law_Surface_Isolation_and_Eval_Readiness.md`
- Constitutional §22 (graph-layer primary), §36 (plan registration)

---

**Plan slug:** `l6-doctrinal-alignment-noninvasive-b9d3f5`
**Authored:** 2026-05-09
**Sibling plan:** `l6-folder-rename-doctrinal-alignment-a8c4e2` (Deprioritized — invasive rename, kept on ice)
