# Hotspot report archive — 2026-05

Superseded by fresh generation on **2026-05-25** against snapshot `adg_indexed_05242026_2005.sqlite` (today's ADG gate / burndown SSOT).

## Current SSOT (do not archive)

| Report | Path |
|--------|------|
| Test gap (basename) | [test_hotspot_gaps_05252026.md](../../test_hotspot_gaps_05252026.md) |
| Hotspot × coverage MV | [hotspot_coverage_priority.md](../../../../artifacts/test_inventory/hotspot_coverage_priority.md) |
| App hotspot slices | `docs/reports/adg/apps_*_hotspots_20260525T040757Z.md` |
| ADG CI burndown | [adg_burndown_report.md](../../adg/adg_burndown_report.md) |

## Archived in this folder

- `test_hotspot_gaps_04252026.md` — April 25 snapshot `0843`
- `hotspot_coverage_priority.md`, `hotspot_coverage_priority_05232026.md`, `hotspot_coverage_priority_2005.md` — prior inventory copies
- `apps_*_hotspots_20260429T*.md`, `apps_*_hotspots_20260510T*.md` — May 10 / Apr 29 app scans

## Regenerate

```powershell
$env:ADG_SNAPSHOT='artifacts/adg/adg_indexed_05242026_2005.sqlite'
python tools/analysis/test_hotspot_gaps_report.py
python tools/analysis/hotspot_coverage_report.py
python tools/adg/scan_apps_hotspots.py
```
