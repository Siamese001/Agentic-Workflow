# L6 Import Blast-Radius Baseline

**Date:** 2026-05-25  
**Plan:** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Wave:** W0.1 (baseline — pre-architecture decision)

---

## Summary

| Metric | Value |
|--------|------:|
| Python files with `system_learning` imports | **329** |
| Import line matches (approx) | **732** |
| `system_learning/chapters/` exists | **false** |
| L6-TAG untagged modules (advisory gate) | **292** |
| L6-OBS findings (advisory gate) | **2** |

---

## Gate outputs (W0.1)

### L6 layer tag (`check_l6_layer_tag_consistency.py`)

- **Exit code:** 0 (advisory — not fail-closed)
- **Snapshot:** `adg_indexed_05252026_0610.sqlite` (from gate stderr)
- **Finding:** 292 modules under `system_learning/` not tagged `layer=L6`
- **Report:** [l6_layer_tag_violations.json](../../../artifacts/windsurf/l6_layer_tag_violations.json)

### L6 observer law (`check_l6_observer_law.py`)

- **Exit code:** 0 (advisory)
- **Findings:** 2
  - `system_learning/ports/meta_outcome_bus_hook.py:89` → `healing_tier_dispatcher`
  - `system_learning/ports/outcome_write_back_hook.py:91` → `healing_tier_dispatcher`
- **Report:** [l6_observer_law_violations.json](../../../artifacts/windsurf/l6_observer_law_violations.json)

---

## Top import hotspots (by line count)

| Lines | File |
|------:|------|
| 40 | `system_learning/pipelines/meta_learning_pipeline.py` |
| 24 | `system_learning/pipelines/pipeline_factory.py` |
| 18 | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py` |
| 14 | `tests/integration/system_learning/runtime_adg/test_tier2_tier3_e2e.py` |
| 12 | `tests/unit/system_learning/test_v6_invariants.py` |
| 11 | `system_learning/engines/semantic_index_registry.py` |
| 10 | `system_learning/engines/__init__.py` |
| 8 | `system_learning/engines/meta_learning_bus.py` |
| 8 | `system_learning/engines/semantic_memory_registry.py` |
| 8 | `tests/unit/system_learning/engines/test_v7_invariants_regression.py` |

**Cross-tree consumers (sample):** `agentic_core/L6_observability/otel_runtime_ingest.py`, `agentic_core/interfaces/meta_control.py`, `agentic_core/seams/workflow_learning_bridge.py`, multiple `agentic_core/mixins/*`.

---

## PATH_RENAME blast-radius note

If `PATH_RENAME_CANONICAL` is selected at W0.2, W5.0 must regenerate this report immediately before `git mv`. Baseline above is **pre-rename** only.

---

## Command evidence

```text
python ops_scripts/ci/check_l6_layer_tag_consistency.py  → exit 0 (292 untagged)
python ops_scripts/ci/check_l6_observer_law.py           → exit 0 (2 findings)
python import scan (repo-wide *.py)                      → 329 files, 732 lines
```
