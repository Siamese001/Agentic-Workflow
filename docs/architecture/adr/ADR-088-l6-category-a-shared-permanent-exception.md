# ADR-088: L6 Category A `_shared` Types — Permanent Exception

**Status:** Accepted  
**Date:** 2026-05-25  
**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.claude/plans/l6-reorg-deferred-followup-f3a9c2.md) W3 (closeout)  
**Spike:** [l6_category_a_shared_spike_20260525.md](../../reports/cursor/l6_category_a_shared_spike_20260525.md)

## Context

Category A modules (`determinism_types`, `path_constants`, `human_decision_artifact_types`, `mutation_prohibition`) are imported by L6 surfaces for typed contracts but live in L0/L3 with `record_execution_trace` at import time.

## Decision

1. **No `_shared` physical extraction in this plan** — instrumentation coupling requires a dedicated `l6-shared-types-split-*` plan (2–3 day estimate).
2. **Document** all Category A edges under `types_and_path_constants` in [architectural_exceptions.yaml](../../config/architectural_exceptions.yaml).
3. **Scaffold** [agentic_core/_shared/types/README.md](../../agentic_core/_shared/types/README.md) as the target layout for a future split (pure types vs layer bootstrap).

## Consequences

- W3 closes with **permanent_exception_documented** (not BLOCKED).
- Burndown via extraction is out of scope until lifecycle bootstrap is split.
