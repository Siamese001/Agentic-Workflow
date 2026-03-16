# P0 Runtime Baseline — 2026-03-15T19:45

**ADG Source:** `adg_indexed_03152026_1925.sqlite`
**Total modules with `calls` edges:** 3,010
**Total modules with any edges:** 6,273

## Edge Counts

| Relation Type | Edge Count | Distinct Modules |
|---|---:|---:|
| calls | 30,198 | 3,010 |
| records_execution_trace | 3,497 | 1,803 |
| applies_guardrail | 1,308 | 1,180 |
| reads_policy_state | 3,077 | 1,335 |
| reads_runtime_state | 534 | 241 |
| snapshots_state | 1,172 | 1,163 |
| observes_runtime_state | 26 | 20 |
| invokes_eval | 542 | 201 |
| emits_replay_key | 272 | 76 |
| emits_determinism_digest | 145 | 76 |
| signs_execution_trace | 1,298 | 1,161 |

## Module Coverage (% of 3,010 calling modules)

| Metric | Modules | Coverage |
|---|---:|---:|
| records_execution_trace | 1,803 | 59.9% |
| applies_guardrail | 1,180 | 39.2% |
| reads_policy_state | 1,335 | 44.4% |
| reads_runtime_state | 241 | 8.0% |
| snapshots_state | 1,163 | 38.6% |
| observes_runtime_state | 20 | 0.7% |
| state_authority (union) | 1,333 | 44.3% |
| invokes_eval | 201 | 6.7% |
| emits_replay_key | 76 | 2.5% |
| emits_determinism_digest | 76 | 2.5% |
| signs_execution_trace | 1,161 | 38.6% |
