# SC-1 Closure Validation — 2026-04-24

## Verdict: ✅ CLOSED

All 7 SC-1-related P-views return **0 rows** in the fresh ADG snapshot
`adg_indexed_04242026_1027.sqlite` (generated post-fix commit `afac09e137`).

## Evidence

| P-view | Before fix | After fix | Delta |
|---|---:|---:|---:|
| `v_p0_write_bypass_uwg` | 3 | **0** | -3 |
| `v_p0_l6_mutation` | 0 | 0 | 0 |
| `v_p0_apps_direct_infra` | 0 | 0 | 0 |
| `v_p0_l1_direct_infra` | 0 | 0 | 0 |
| `v_p1_mis_layered_infra` | 0 | 0 | 0 |
| `v_p0_l0_raw_execution` | 0 | 0 | 0 |
| `v_p0_provider_bypass` | 0 | 0 | 0 |
| **Total SC-1 P0+P1** | **3** | **0** | **-3** |

## Provenance

- **Snapshot**: `artifacts/adg/adg_indexed_04242026_1027.sqlite`
- **Fix commit**: `afac09e137` (W7.1-P1 — ensure_dir migration)
- **Before-state snapshot**: `adg_indexed_04242026_0713.sqlite` (prior to fix)
- **Validation query**: 7 P-view row counts via direct SQLite read

## Scope Closed

W7.1 (SC-1 Structural Block Remediation) is fully closed:

- W7.1-P0 ✅ DONE — classifier + triage report (commit `c096c68439`)
- W7.1-P1 ✅ DONE — 3 UWG-bypass sites fixed (commit `afac09e137`)
- W7.1-P2 ✅ OBSOLETE — no boundary-bypass sites remained
- W7.1-P3 ✅ OBSOLETE — no exemptions needed
- W7.1-P4 ✅ DONE — this validation report

**Total effort**: ~3.5h actual vs 30–45h estimated in original ADR-051.

## Next Steps

ADR-051 may be transitioned from **Accepted (with Amendment)** → **Resolved**
in a future session. The companion plan `sc1-structural-block-closure-f9e3b1`
can be archived. No further execution is required.

---

_Generated 2026-04-24 per W7.1-P4 validation requirement._
