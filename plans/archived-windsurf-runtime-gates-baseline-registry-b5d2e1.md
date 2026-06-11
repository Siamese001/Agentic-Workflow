---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-gates-baseline-registry-b5d2e1.md'
original_relative_path: 'runtime-gates-baseline-registry-b5d2e1.md'
source_sha256: b5fa8050192e6d9767b72eace2058545632ac73ce3b95551130a084041b24769
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Gates — G25 Baseline Registry

Status: In Progress
Owner: Cascade
Plan ID: runtime-gates-baseline-registry-b5d2e1

## Goal

Provide a persistent task-class baseline store for G25 RuntimeAnomalyGate with rolling-window EMA updates.

## Wave Structure

| Wave | Phase IDs | Focus | Est Tokens | Status |
|---|---|---|---|---|
| W1 | 1.1 | BaselineRegistry class (in-memory + JSON persistence) | 3000 | Done |
| W2 | 2.1 | Tests | 2000 | Done |
| W3 | 3.1 | Commit | 1000 | Done |

## Phase-Level Summary

| Phase | Title | Scope | Pain | Est | Status |
|---|---|---|---|---|---|
| 1.1 | BaselineRegistry | runtime_gates/baseline_registry.py | EMA semantics, atomic writes | 3000 | Done |
| 2.1 | Tests | tests/.../test_baseline_registry.py | persistence + EMA | 2000 | Done |
| 3.1 | Commit | git | none | 1000 | Done |

## Out of Scope

- Persistent storage backend (SQLite/Redis) — JSON file is enough for v1.
- Cross-tenant baseline isolation (single-tenant scope first).
