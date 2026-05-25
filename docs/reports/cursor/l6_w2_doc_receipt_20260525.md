# L6 W2 — Documentation & Marker Completion (provisional)

**Plan:** [l6-repo-reorganization-mental-model-c4e8f2](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Date:** 2026-05-25  
**Architecture path:** `PATH_RENAME_CANONICAL`  
**doc_canonical_root_claim:** `pre_rename_temporary_only`

> **Not final canonical-root proof for PATH_RENAME_CANONICAL.** Active code root remains `system_learning/` until W5.1; final path statements for `agentic_core/L6_system_learning/` belong in **W5.3** only.

---

## W2 deliverables

### 1. Doctrinal doc folder rename (G7)

| Before | After |
|--------|-------|
| `docs/reference/06_L6_Shadow_Evaluation_System_Learning/` | `docs/reference/06_L6_Observability_and_System_Learning/` |

Command: `git mv docs/reference/06_L6_Shadow_Evaluation_System_Learning docs/reference/06_L6_Observability_and_System_Learning`

Cross-link sweep: **65** active files updated (excludes `_archive/` and `*.bak`).

### 2. Chapter markers on 8 markerless packages (G3)

| Package | `__l6_chapter__` | New `__init__.py` |
|---------|------------------|-------------------|
| `adg` | 06.1 | [adg/__init__.py](../../system_learning/adg/__init__.py) |
| `telemetry` | 06.1 | [telemetry/__init__.py](../../system_learning/telemetry/__init__.py) |
| `policy` | 06.2 | [policy/__init__.py](../../system_learning/policy/__init__.py) |
| `ml_integration` | 06.5 | [ml_integration/__init__.py](../../system_learning/ml_integration/__init__.py) |
| `monitoring` | 06.8 | [monitoring/__init__.py](../../system_learning/monitoring/__init__.py) |
| `state` | 06.7 | [state/__init__.py](../../system_learning/state/__init__.py) |
| `runtime` | (cross-cutting) | [runtime/__init__.py](../../system_learning/runtime/__init__.py) |
| `config` | (cross-cutting) | [config/__init__.py](../../system_learning/config/__init__.py) |

### 3. Files tagged `PRE_RENAME_TEMPORARY`

| File | Reason |
|------|--------|
| [system_learning/LAYER.md](../../system_learning/LAYER.md) | Describes pre-W5 active root; defers final canonical path to W5.3 |

### 4. Intentionally unchanged (PATH_RENAME constraint)

- [L6_mental_model.md](../../docs/reference/_notes/L6_mental_model.md) — doc folder path updated; **no** claim that `agentic_core/L6_system_learning/` is the final install path before W5.3.
- `engines/__init__.py` — retains `__l6_chapter__ = ""` (cross-chapter bucket; W3/doc-map deferred).

---

## Verification

```text
pytest tests/unit/system_learning/test_l6_layer_markers.py -o addopts=  -> 36 passed, exit 0
```

Prior W1 gates remain valid on pre-rename tree (see [l6_w1_gate_receipt_20260525.json](l6_w1_gate_receipt_20260525.json)).

---

## Path binding summary

| Field | Value |
|-------|-------|
| `architecture_path` | `PATH_RENAME_CANONICAL` |
| `doc_canonical_root_claim` | `pre_rename_temporary_only` |
| `canonical_active_root_at_time_of_w2` | `system_learning/` (pre-move) |
| `planned_final_active_root` | `agentic_core/L6_system_learning/` (W5.1) |
| `proof_phase` | `pre_rename` |

---

## Next wave

**W4** — Passive surface drift (`L6_observability/promotion/`). **W3 skipped** per W0.2 path lock. **W5** requires Author-Gate + W5 preflight after W4 (optional) or directly if scope allows.
