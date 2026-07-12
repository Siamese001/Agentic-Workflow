# ADG Cleanup Queue and P2 Ratchet Trace

- **Generated:** 2026-07-12T02:27:23+00:00
- **Report status:** present
- **Dead-code source:** `artifacts/adg/dead_code_zone_control_report_latest.json`
- **Published sqlite:** `artifacts/adg/adg_indexed_07112026_2208.sqlite`
- **P2 ratchet:** `artifacts/adg/p2_ratchet.json`
- **Failed-run manifest:** `artifacts/adg/adg_gate_invocation_manifest_07112026_2208.json`

### BCG Cleanup Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Business read:** ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics.
- **Deletion status:** DELETION_CANDIDATES
- **Source report status:** PASS
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_07112026_2208.sqlite (snapshot 07112026_2208)
  - Dead code candidates: 935
  - Dead imports: 935
  - Unresolved imports: 466
  - First-party low-confidence ratio: 1.49%
  - Inferred-symbol ratio: 10.12%
  - Cleanup candidates surfaced: 0
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 19 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 2 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 14 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 3 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 13 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 4 | Triage unresolved imports | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 466 unresolved imports; lead hotspot ADG::Module::tests/integration/retrieval_layers/test_bge_embedding_e2e.py (9). | Trace the top unresolved scope before deleting anything else. |
| 5 | Reduce low-confidence noise | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.49% and inferred-symbol ratio = 10.12%. | Lower the noise floor, then rerun the scan. |
| 6 | Deprecate low-value ADG signals | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 0 MV candidates and 0 unused artifacts surfaced by the report. | Deprecate only after higher-confidence cleanup is complete. |

Next step: Deprecate first, then delete after the evidence stays clean.

## Cleanup Queue

The dead-code report found no confirmed deletions, so this queue prioritizes signal cleanup and unresolved-import noise reduction.

### Live unresolved-import queue

| Priority | Move | Why it matters | Evidence | Next step |
|---:|---|---|---|---|
| 1 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 9 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 2 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 9 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 3 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 8 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 4 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 8 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 5 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 8 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 6 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 7 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 7 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 7 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 8 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 7 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |
| 9 | Triage unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 6 unresolved import(s) on this surface. | Trace the live imports, then rerun the scan. |

### Archived or obsolete surfaces

| Priority | Move | Why it matters | Evidence | Next step |
|---:|---|---|---|---|
| 10 | Defer archived unresolved imports | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 7 unresolved import(s) on this surface. | Leave archived noise deferred unless it affects live paths. |

## P2 Ratchet Trace

This section explains the current MEDIUM hygiene count, the ceiling in `p2_ratchet.json`, and why the latest run is still blocked.

### BCG P2 Ratchet Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Business read:** The published snapshot is at or below the P2 ceiling, so this blocker is cleared.
- **P2 ratchet status:** WITHIN_CEILING
- **Technical evidence:**
  - Published sqlite snapshot: artifacts/adg/adg_indexed_07112026_2208.sqlite
  - P2 ceiling: 34
  - Current MEDIUM hygiene count: 34
  - Delta vs ceiling: +0
  - Baseline snapshot: adg_indexed_07112026_2208.sqlite
  - Latest failed run: 2026-07-12T02:27:23Z (failed)
- **Priority rule:** Fix the largest live runtime hygiene hotspots first, then remove star imports, then re-baseline only if the debt is intentional.

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Reduce MEDIUM hygiene debt | This is a live surface where removing hygiene debt improves trust in the next run. | 4 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 2 | Reduce MEDIUM hygiene debt | This is a live surface where removing hygiene debt improves trust in the next run. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 3 | Reduce MEDIUM hygiene debt | This is a live surface where removing hygiene debt improves trust in the next run. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 4 | Reduce MEDIUM hygiene debt | This is a live surface where removing hygiene debt improves trust in the next run. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 5 | Re-run ADG and keep the ceiling honest | Do not change the ceiling until the underlying hygiene debt is actually reduced or explicitly accepted. | Current count=34; ceiling=34; delta=0. | Re-baseline only after the evidence changes are intentional and approved. |

Next step: Burn down the top runtime hotspots, then rerun ADG and confirm the count stays under the ceiling.

### Trace Summary

- **Current MEDIUM hygiene count:** 34
- **Ceiling:** 34
- **Delta:** +0
- **Baseline snapshot:** adg_indexed_07112026_2208.sqlite
- **Published snapshot:** artifacts/adg/adg_indexed_07112026_2208.sqlite
- **Latest failed run:** 2026-07-12T02:27:23Z (failed)

### Evidence Buckets

| Evidence | Count | Interpretation |
|---|---:|---|
| OSError | 13 | Filesystem / IO error handling needs to be narrowed. |
| Exception | 6 | Broad exception catch or swallow on a live hygiene path. |
| ValueError | 5 | Parsing or validation guard should be tightened. |
| FACT_VECTOR_RUNTIME_EXCEPTIONS | 3 | Hygiene debt on the current published snapshot. |
| TypeError | 2 | Hygiene debt on the current published snapshot. |
| getattr | 2 | Hygiene debt on the current published snapshot. |
| ImportError | 2 | Import fallback logic should be explicit and local. |
| NotADirectoryError | 1 | Hygiene debt on the current published snapshot. |

### File Hotspots

| Priority | Move | Why it matters | Evidence | Next step |
|---:|---|---|---|---|
| 1 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 4 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 2 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 3 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 4 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 5 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 6 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 2 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 7 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |
| 8 | Reduce MEDIUM hygiene debt | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | Burn down the highest-count files, then rerun ADG. |

### What This Means

- There are no confirmed dead-code deletions in the latest dead-code report, so deletion stays deferred.
- The published snapshot still carries MEDIUM hygiene debt against the P2 ceiling, so the ratchet remains open.
- Reduce the live runtime hotspots first, then rerun ADG and confirm the ceiling stays honest.
