# P1 Micro-Wave Hardening — Baseline Report

**Date**: 2026-03-16
**ADG (pre-wiring)**: `adg_indexed_03152026_2246.sqlite` — 508,629 edges, 6,293 modules
**Denominator**: 3,011 modules with `calls` edges

## Baseline Edge Counts

| Relation Type | Edges | Modules | Target | Gap | % of Target |
|---|---|---|---|---|---|
| proposal_commits_routing | 48 | 31 | 174 | 126 | 27.59% |
| pulls_context | 32 | 6 | 3,125 | 3,093 | 1.02% |
| execution_terminates_at_uwg | 61 | 16 | 4,540 | 4,479 | 1.34% |
| writes_through | 105 | 37 | 4,540 | 4,435 | 2.31% |
| validated_by_safety_plane | 78 | 49 | 1,223 | 1,145 | 6.38% |
| invokes_eval | 542 | 129 | 2,778 | 2,236 | 19.51% |

## Key Findings

- All 6 frozensets already exist in `schema.py`
- 2 emitters already exist: `_emit_validated_by_safety_plane`, `_emit_writes_through`
- 4 emitters missing: `_emit_pulls_context`, `_emit_execution_terminates_at_uwg`, `_emit_invokes_eval`, `_emit_proposal_commits_routing`
- Existing scanner visitors already emit all 6 relation types from domain-specific symbols
