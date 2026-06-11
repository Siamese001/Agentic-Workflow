---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\p1_target_matrix.md'
original_relative_path: 'p1_target_matrix.md'
source_sha256: 469f38f192832b3a8f044b4436d9010be9e46d8ac75bba96eecd5edee6e48cf1
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-15'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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

