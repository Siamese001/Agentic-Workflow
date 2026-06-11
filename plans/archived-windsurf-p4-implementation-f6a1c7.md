---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p4-implementation-f6a1c7.md'
original_relative_path: 'p4-implementation-f6a1c7.md'
source_sha256: abdb620aabe100a857b746efc24a29b8af35678b24b9e79717c496c5a9a77a9b
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P4 Implementation — Out-of-Scope Items

> Parent: consolidated-deferred-scope-may7-e6f1b5
> Scope: Implement all 8 P4 backlog items

## Wave Structure

| Wave | Item | Scope | Est. Tokens |
|------|------|-------|-------------|
| W1 | ADR authoring (item 6) | 3 ADRs: D2 default, spine envelope pattern, sub-stage telemetry | ~8K |
| W2 | C0 grounding retrieval strategy (item 3) | C0 retrieval strategy doc + code | ~12K |
| W3 | X1-X3 routing logic (item 1) + L5 guardrails (item 2) | Gate logic + safety rules | ~15K |
| W4 | apps_research internals (item 7) + apps_lic path (item 8) | Internal refactoring | ~15K |
| W5 | L6 exhaust schema (item 5) + BGE-M3 model (item 4) | Schema + model config | ~10K |

## Implementation Order

Items 6 (ADRs) first — they document decisions that inform items 1-5, 7-8.
Items 3 (C0) next — affects all apps.
Items 1-2 (gates) next — routing/safety logic.
Items 7-8 (apps internals) next — depends on ADR decisions.
Items 4-5 (model/schema) last — lowest urgency.
