---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\wave1-p1-remediation-revision-0f0783.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\wave1-p1-remediation-revision-0f0783.md'
source_sha256: ed5f4fd6577f2bc249bd7d5cc8a093d34ca71e731cf71540c4195956d3245cdd
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 1 P1 Remediation Revision

This revision converts Wave 1 from file-level remediation to site-level remediation, prioritizes swallow-behavior fixes over exception-type cosmetics, and tightens expected net reduction targets to conservative, evidence-backed ranges.

## Objective
- Execute a first real P1 remediation wave against authoritative snapshot `04192026_0728`.
- Maximize trustworthy net reduction with low operational risk.
- Keep scope bounded to a safe, validation-friendly tranche.

## Authoritative Truth
- Snapshot: `artifacts/adg/adg_indexed_04192026_0728.sqlite`
- P1 net: `505`
- P1 kind net:
  - `log_and_swallow=238`
  - `return_none_swallow=141`
  - `silent_exception_swallow=74`
  - `broad_exception_catch=52`

## Policy Revisions (Required)
1. Mode granularity: assign remediation mode per site/cluster, not per file.
2. Kind-first behavior policy:
   - `log_and_swallow` -> default `re-raise` or `explicit guardian with specific justification`
   - `return_none_swallow` -> default `typed non-fatal handling` or `re-raise`
   - `silent_exception_swallow` -> default `re-raise` unless explicitly justified
   - `broad_exception_catch` -> default `narrow catch`
3. Exemption policy:
   - Skip already-guardianed sites unless a concrete correctness defect requires change.

## Revised Wave 1 Scope (7 Files, Bounded)

### Keep
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- `agentic_core/L5_safety/reasoning/location_validator.py`
- `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py`
- `agentic_core/mixins/tracing_mixin.py`
- `agentic_core/utils/workflow_engines/drift_monitor.py`
- `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py`

### Swap for cleaner first-wave burndown proof
- Remove: `agentic_core/mixins/meta_learning_client_mixin.py`
- Add: `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py`

Rationale: preserve bounded size while favoring simpler, high-net, behavior-centric sites for cleaner first-wave proof and lower ambiguity.

## Site-Level Remediation Matrix

### Cluster 1: `log_and_swallow` dominant (primary net driver)
- Candidate files: `FileClassificationAgent.py`, `location_validator.py`, `EmbeddingSovereignAgent.py`, `tracing_mixin.py`, `drift_monitor.py`, `SystemArchitectAgent.py`
- Primary mode: `re-raise`
- Allowed alternate: `explicit guardian with specific justification` (only where intentional fire-and-forget semantics are required)

### Cluster 2: `return_none_swallow` dominant
- Candidate files: `FileClassificationAgent.py`, `SystemArchitectAgent.py`, `L5SafetyExerciserAgent.py`
- Primary mode: `typed non-fatal handling`
- Allowed alternate: `re-raise` when upstream contract can absorb failure safely

### Cluster 3: incidental `broad_exception_catch`
- Candidate files: `SystemArchitectAgent.py` (and any incidental same-file P1 broad sites)
- Primary mode: `narrow catch`

## Conservative Net Reduction Targets
- Hard scope max: `38` net (sum of in-scope file-level net exposure ceiling)
- Credible validated target: `18-28` net
- Stretch target: `30+` only if no scope expansion and site-level fixes validate cleanly

## Validation Gates (Post-Implementation)
1. Targeted tests for edited modules and adjacent enforcement paths.
2. Canonical regeneration: `python tools/generate/generate_full_adg.py` exits `0`.
3. Snapshot convergence:
   - `adg_status.timestamp` matches latest generated snapshot
   - `adg_health` healthy for sqlite + redis
   - `adg_runtime_info.snapshot_id` matches snapshot truth
4. Burndown provenance:
   - `sqlite_source_name` equals latest snapshot
   - `source_mismatch_with_latest=false`
5. Burndown effect:
   - P1 net reduction within target band
   - zero P0 regression

## Stop / Rollback Conditions
- Stop if P0 rises, snapshot drift reappears, or runtime behavior regresses.
- Roll back unstable site clusters first (not entire wave) when failures are localized.
- Defer scanner-sensitive or gateway-sensitive adjacent edits to later wave unless direct correctness risk is proven.

## Execution Readiness
- This plan is planning-only and awaits explicit approval before remediation edits.
