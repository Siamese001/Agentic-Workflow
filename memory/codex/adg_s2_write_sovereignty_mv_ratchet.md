# ADG S2 Write-Sovereignty MV Ratchet

## ProceduralPattern:ADGS2WriteSovereigntyMVRatchetInvariant

- INVARIANT: S2 UWG-bypass ratchet counts must use `mv_write_sovereignty_paths` as the canonical write-sovereignty inventory when the MV exists, not raw `writes_to` edges.
- scope: `ops_scripts/ci/check_uwg_bypass_ratchet.py`, ADG snapshots with `mv_write_sovereignty_paths`, S2/UWG bypass burndown reports.
- enforcement: `S2_uwg_bypass_ratchet` plus `tools/reports/gate_signal_catalog.py` copy that describes S2 as an overlay on write-sovereignty edges.
- diagnostic: pin the released snapshot with `$env:ADG_SNAPSHOT='<snapshot>'; python ops_scripts\ci\check_uwg_bypass_ratchet.py; Remove-Item Env:\ADG_SNAPSHOT`.
- canonical_pattern: prefer `mv_write_sovereignty_paths WHERE is_uwg_routed = 0`, preserving raw-edge fallback only for old snapshots without the MV.
- guard: do not shrink S2 by broad source instrumentation or by excluding layers ad hoc; durable-write exclusions, `ops_scripts/%`, nested scripts/tests, `_wg.*` routing, ArchivalGatekeeper, and scanner false positives belong in the MV producer.
- discovered: 2026-07-05, validated: 2026-07-05 against `adg_indexed_07042026_2305.sqlite`.
