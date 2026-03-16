# P2 Runtime Baseline

**Date**: 2026-03-15
**ADG Before Wiring**: `adg_indexed_03152026_2210.sqlite`

## Baseline Counts (Pre-Wiring)

| Relation Type | Edges | Modules | Coverage |
|---|---:|---:|---:|
| `calls` (denominator) | 44,691 | 3,011 | — |
| `authorize_and_execute` | ~19 | 19 | 0.63% |
| `validates_capability` | 0 | 0 | 0.00% |
| `routes_to_capability` | 0 | 0 | 0.00% |
| `writes_via_uwg` | 0 | 0 | 0.00% |
| `blocks_direct_write` | 0 | 0 | 0.00% |
| `records_tool_invocation` | 0 | 0 | 0.00% |
| `captures_execution_output` | 0 | 0 | 0.00% |

## Related Pre-Existing Relations

| Relation Type | Edges | Modules | Notes |
|---|---:|---:|---|
| `execution_terminates_at_uwg` | 61 | 16 | L5 validation proof |
| `issues_capability_token` | 6 | 4 | Existing capability edge |
| `validates_agent_capability` | 48 | 47 | P1 edge |
| `writes_through` | 105 | 17 | Pre-existing write edge |
| `enters_sandbox` | 39 | 15 | Sandbox entry |

## Gap Analysis

- **3,011** modules in `modules_with_calls` denominator
- **19** modules had natural `authorize_and_execute` pickup from existing code
- **2,992** modules missing all 7 P2 dimensions
- **19** modules missing 6 P2 dimensions (had `authorize_and_execute` only)
