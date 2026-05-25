# ADR-081: ADG CI unified enforcement planes

**Status**: Accepted (2026-05-23)  
**Related**: ADR-079 (three-bucket opt-in), [ADG_Audit_Pipeline.md](../../guides/ADG_Audit_Pipeline.md), plan `adg-ci-unified-migration-a7f3b2`

## Context

ADG CI grew across four orchestrators:

1. **Plane 1 — Generator** (`tools/generate/_required_gates.py`, 15 gates)
2. **Plane 2 — Snapshot manifest** (`ops_scripts/ci/adg_gate_manifest.yaml`, 20 gates)
3. **Plane 3 — Deep graph dispatcher** (`ops_scripts.ci.adg_gates.run`, ~25 dispatched gates)
4. **Plane 4 — Satellite** (AUDIT_1–6, M1–M12, plan gates, JSONL deltas)

High-value checks existed but fragmentation allowed silent skips (non-blocking dispatcher, manifest absent from GHA, `check_adg_certified` re-running six scripts).

## Decision

### Four enforcement planes

| Plane | SSOT | Blocks certification |
|-------|------|----------------------|
| 1 Generator | `_required_gates.py` + invocation manifest | Yes |
| 2 Snapshot | `adg_gate_manifest.yaml` + `run_adg_three_graph_tests.py` | Yes (`--strict`) |
| 3 Dispatcher | `unified_registry.py` + `adg_gates.run` | Yes when `ADG_CERTIFICATION_MODE=1` |
| 4 Satellite | Contract / GHA adjunct | Selective |

### Single rollup artifact

`artifacts/adg/adg_enforcement_report_<ts>.json` aggregates plane 1–3 outcomes. `check_adg_certified.py` reads this report by default (`--rollup`) instead of re-invoking sub-gates.

### Dedup rules

- One **blocking owner** per bug class in certification mode.
- `static.mv_count_floor` / `static.pview_count_floor` removed; thresholds live on `static.snapshot_has_mvs`.
- M10/M11/M12 default to **sunset** (warn-only stub); plane 1 owns antipattern/dead-import/layer violations.
- AUDIT_5 (`check_env_var_in_config_layer`) removed from GHA; `config-ref` is the owner.

### CI entrypoints

| Mode | Command |
|------|---------|
| Certification | `python tools/adg/run_full_adg_audit.py --mode certification` |
| PR quick (no regen) | `run_adg_three_graph_tests.py --suite quick --strict --snapshot <path>` |
| Changed subset | `run_adg_three_graph_tests.py --suite changed --strict` |

## Consequences

- Certification fails on dispatcher BLOCK regressions.
- Faster PR signal via quick/changed manifest suites.
- Operators triage one `adg_enforcement_report_*.json` file.
