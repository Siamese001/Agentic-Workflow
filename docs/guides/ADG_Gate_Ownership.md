# ADG gate ownership (bug-class SSOT)

Plan: [adg-ci-unified-migration-a7f3b2.md](../../.codex/plans/adg-ci-unified-migration-a7f3b2.md) · ADR: [ADR-081](../architecture/adr/ADR-081-adg-ci-unified-enforcement-planes.md)

| Bug class | Blocking owner (cert) | Plane | Also reports (advisory) |
|-----------|----------------------|-------|-------------------------|
| Layer / import gravity | `p0_violations` | 1 | `1_critical_path_integrity`, M12 (sunset) |
| Write bypass / UWG | `3_write_sovereignty`, `static.authority_boundary_breaches` | 2+3 | M3 (sunset) |
| Dead / orphan code | `dead_production_imports`, `A3` | 1+3 | M11 (sunset) |
| Anti-patterns | `p1_ratchet`, `p2_ratchet`, `agentic_antipatterns` | 1 | M10 (sunset) |
| Runtime proof lies | `runtime.proof_view_well_formed`, `runtime.trace_topology`, `cross_bucket.impossible_states` | 2 | 3B1 (contract, same script) |
| Registry / MCP drift | `mcp_config_drift`, `registry.graph_integrity` | 1+2 | `J1`, `G2` |
| Wiring / seams | `wiring`, `check_expected_wiring` | 1+3 | `E1`, `9_executor_theater` |
| Config / env undeclared | `config-ref` | 1 | ~~AUDIT_5~~ (removed) |
| Exception holes | `except-contract` | 1 | — |
| Test debt | `test-coverage`, `check_test_harness_coverage` | 1+4 | — |
| Supply chain / stale | `provenance.snapshot_signed`, `adg_stale_guard` | 2+4 | 3B4 |
| Cross-bucket gaps | `cross_bucket.gap_thresholds`, Stage-2 gap report | 2 | 3B3 |
| Plan discipline | `check_graph_layer_evidence` | 4 | — |

**Rollup:** `check_adg_certified.py --rollup` reads `adg_enforcement_report_*.json`; do not add parallel blocking scripts without updating this table.
