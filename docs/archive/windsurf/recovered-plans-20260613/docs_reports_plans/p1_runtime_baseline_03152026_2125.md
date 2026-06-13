# P1 Runtime Baseline

- Timestamp: `03152026_2125`
- ADG SQLite: `artifacts/adg/adg_indexed_03152026_2125.sqlite`
- Method: canonical SQLite query pack against the freshly regenerated ADG artifact

## DEPENDENCY_GRAPH

- Modules scanned: `6291`
- Total edges: `322261`
- Graph planes:
  - `G1_imports=80795`
  - `G3_implements=2272`
  - `G4_calls=44519`
  - `GT_covers=9101`
  - `GV_violates=740`
  - `GG_governance=1324`
- Blast radius: pending first micro-wave selection

## Baseline Query Pack

| Relation Type | Count |
|---|---:|
| `routes_to_agent` | 0 |
| `orchestrates_workflow` | 0 |
| `dispatches_execution_plan` | 0 |
| `validates_agent_capability` | 0 |
| `checks_agent_registry` | 0 |
| `invokes_eval` | 542 |
| `applies_guardrail` | 3132 |
| `records_execution_trace` | 6556 |
| `reads_policy_state` | 4770 |

## Findings

- The upstream orchestration governance edge family is absent in the current baseline: `routes_to_agent`, `orchestrates_workflow`, `dispatches_execution_plan`, `validates_agent_capability`, and `checks_agent_registry` are all `0`.
- Downstream governance/trace evidence already exists: `invokes_eval`, `applies_guardrail`, `records_execution_trace`, and `reads_policy_state` are populated.
- The provided deficit SQL required schema translation for this repository because the `edges` table uses `src_id` and `dst_id` rather than `caller` and `callee` columns.
- A zero `routes_to_agent` count makes the numeric target matrix degenerate to zero, but this does not satisfy the stated orchestration-coverage objective; it indicates missing route-edge emission rather than completed governance coverage.

## Evidence

[Provide evidence supporting the findings]

---

