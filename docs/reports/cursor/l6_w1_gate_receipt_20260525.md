# L6 W1 governance gate receipt (provisional)

**Plan:** [l6-repo-reorganization-mental-model-c4e8f2](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Architecture path:** `PATH_RENAME_CANONICAL` (locked W0.2)  
**Proof phase:** `pre_rename` — **not** final canonical certification (see W1.5 after W5.3).

## Gate results

| Gate | Mode | Exit | Evidence |
|------|------|------|----------|
| L6-TAG | `L6_LAYER_TAG_FAIL_CLOSED=1` | 0 | 292/292 modules under `system_learning/` tagged `L6` in [adg_indexed_05252026_0634.sqlite](../../artifacts/adg/adg_indexed_05252026_0634.sqlite) |
| L6-OBS | `L6_OBSERVER_LAW_FAIL_CLOSED=1` | 0 | 0 findings; TYPE_CHECKING imports excluded |

## Path binding (W1 invariant)

| Field | Value |
|-------|-------|
| `canonical_active_root_at_time_of_gate` | `system_learning/` |
| `alias_root_role` | `agentic_core.L6_system_learning` — re-export alias |
| `root_shim_role` | `none` |
| `adg_scan_root` | `system_learning/` |
| `observer_law_scan_root` | `system_learning/` |
| `proof_authority` | `provisional_pre_rename` |

## Commands

```text
python tools/generate/generate_full_adg.py  -> exit 0
L6_LAYER_TAG_FAIL_CLOSED=1 python ops_scripts/ci/check_l6_layer_tag_consistency.py  -> exit 0
L6_OBSERVER_LAW_FAIL_CLOSED=1 python ops_scripts/ci/check_l6_observer_law.py  -> exit 0
pytest tests/unit/ops_scripts/ci/test_check_l6_*.py -o addopts=  -> 15 passed
```

## Machine-readable manifest

[l6_w1_gate_receipt_20260525.json](l6_w1_gate_receipt_20260525.json)
