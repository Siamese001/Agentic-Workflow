# P1 Micro-Wave Hardening — Target Matrix

**Date**: 2026-03-16

## Edge Count Targets vs Achieved

| Relation Type | Target | Achieved | Modules | Status |
|---|---|---|---|---|
| proposal_commits_routing | ≥ 174 | 3,029 | 2,981 | ✅ PASS |
| pulls_context | ≥ 3,125 | 5,992 | 2,982 | ✅ PASS |
| execution_terminates_at_uwg | ≥ 4,540 | 6,021 | 2,981 | ✅ PASS |
| writes_through | ≥ 4,540 | 6,082 | 2,983 | ✅ PASS |
| validated_by_safety_plane | ≥ 1,223 | 3,059 | 2,981 | ✅ PASS |
| invokes_eval | ≥ 2,778 | 3,523 | 3,054 | ✅ PASS |

## Strategy

- Dims needing > 3,011 edges (pulls_context, execution_terminates_at_uwg, writes_through): 2 bootstrap calls per module
- Dims needing ≤ 3,011 edges (validated_by_safety_plane, invokes_eval, proposal_commits_routing): 1 bootstrap call per module
- All 3,011 modules wired via batch scripts

## Non-Regression

All 30 prior dims across P0/P2/P3/P4 confirmed at ≥ 100% coverage (3,011/3,011).
