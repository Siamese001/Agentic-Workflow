# P1 Target Matrix

- Timestamp: `03152026_2125`
- Route baseline (`N`): `0`

## Computed Targets

| Metric | Formula | Target |
|---|---|---:|
| orchestration_target | `routes * 0.90` | 0 |
| plan_dispatch_target | `routes * 0.95` | 0 |
| capability_validation | `routes * 1.00` | 0 |
| registry_validation | `routes * 1.00` | 0 |
| evaluation_target | `routes * 0.80` | 0 |
| guardrail_target | `routes * 0.80` | 0 |
| trace_target | `routes * 0.90` | 0 |
| policy_read_target | `routes * 0.95` | 0 |

## Interpretation

- The canonical formula produces zero targets because `routes_to_agent=0` in the current ADG baseline.
- This is a metric degeneracy, not proof of complete orchestration coverage.
- To achieve the user-stated objective, the planning/orchestration layer must first emit `routes_to_agent` and the rest of the required governance edge family so that coverage can be measured meaningfully.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

