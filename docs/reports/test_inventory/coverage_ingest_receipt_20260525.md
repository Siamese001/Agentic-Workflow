# Coverage ingest + hotspot report — receipt

**Snapshot**: [adg_indexed_05242026_2005.sqlite](../../artifacts/adg/adg_indexed_05242026_2005.sqlite)  
**Report**: [hotspot_coverage_priority.md](../../artifacts/test_inventory/hotspot_coverage_priority.md)

## STATUS: PASS (ingest + MV + report)

| Step | Command | Result |
|------|---------|--------|
| Coverage data | Existing `.coverage` (1788 files from prior `coverage run`) | present |
| Ingest | `python tools/adg/ingest_coverage_py.py --adg artifacts/adg/adg_indexed_05242026_2005.sqlite` | exit 0, **1788 rows** |
| Phase F MV | `materialize_phase_f(2005)` | **4291** rows in `mv_hotspot_coverage_risk` |
| Report | `python tools/analysis/hotspot_coverage_report.py --adg …2005.sqlite` | exit 0 |

## Before → after

| Metric | Pre-ingest | Post-ingest |
|--------|------------|---------------|
| Measured nodes | 0 | **1786** |
| P1_URGENT | 1644 | **1530** |
| P2_GAP | 0 | **56** |
| P3_OK | 0 | **58** |
| Avg measured coverage | — | **11.2%** |

## NOTES

- Ingest used existing `.coverage`; for fresher bands re-run `coverage run` over a broader `tests/agentic_core` slice before ingest.
- Full ADG regen (`generate_full_adg.py`) also ingests coverage automatically on success.
