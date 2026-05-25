# L6 W6 Wave Receipt — Cross-Layer Gravity (Documented Burndown)

**Date:** 2026-05-25  
**Plan:** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Child plan:** [l6-gravity-hybrid-7c4e2a.md](../../.cursor/plans/_archive/2026-05/l6-gravity-hybrid-7c4e2a.md)  
**Status:** PASS (documented_over_threshold)

---

## Summary

W6 closes the optional gravity wave by **documenting** residual L6→L0..L5 ADG import edges after W5 canonical root stabilization. Edge count (**86** distinct ADG records; **43** deduplicated source→target pairs) exceeds the ≤24 burndown target; acceptance path per plan is full documentation.

| Metric | Value |
|--------|------:|
| ADG snapshot | `artifacts/adg/adg_indexed_05252026_0751.sqlite` |
| Distinct import edges | 86 |
| Deduplicated YAML entries | 43 |
| L6 source files | 37 |
| Burndown threshold | 24 |
| Outcome | **documented_over_threshold** |

---

## Deliverables

| Artifact | Purpose |
|----------|---------|
| [l6_w6_gravity_edge_inventory_20260525.json](l6_w6_gravity_edge_inventory_20260525.json) | Machine-readable ADG edge inventory |
| [architectural_exceptions.yaml](../../../config/architectural_exceptions.yaml) | SSOT for accepted L6 downstream imports |
| [ADR-085-l6-observability-dependency-hygiene.md](../../architecture/adr/ADR-085-l6-observability-dependency-hygiene.md) | Decision record + category rationale |

---

## Prior burndown (child plan 2026-05-01)

- `integrity_report_generator_util.py` → `ops_scripts/reports/` (eliminated top single-file offender)
- `agentic_core/_shared/` namespace created; Category A type extraction **deferred** (instrumented envelopes)

---

## Governance (post-W5)

```text
L6_LAYER_TAG_FAIL_CLOSED=1 → exit 0 (300/300 L6)
L6_OBSERVER_LAW_FAIL_CLOSED=1 → exit 0 (0 findings)
pytest L6 suite → exit 0
```

**Cert JSON:** [l6_w6_gravity_receipt_20260525.json](l6_w6_gravity_receipt_20260525.json)

---

## Deferred (follow-on)

- Physical move of `L6_observability/utils/evaluation/{async_eval_packet,governed_handoff}.py` and `desk_d_governed_board.py` to L_OPS (requires per-file Author-Gate + fan-in proof)
- Category A extraction to `_shared/types/` when instrumentation can be decoupled
