---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\rca_agents_outside_reasoning.md'
original_relative_path: 'rca_agents_outside_reasoning.md'
source_sha256: 3e531eae154df2666c78dcc9a532020d3342700a8b6e75a28a8d25eb2cb95e91
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Agents Outside reasoning/ Folders (L0–L6)

**Date**: 2026-02-11
**Commit before**: `2835b2641`
**Branch**: `agentic-core-v5.3`

## Summary

Full AST scan of `agentic_core/L0–L6` for files containing classes inheriting
`SovereignBaseAgent` that are NOT in `reasoning/` folders.

**Result**: 2 true violations found and fixed. 4 false positives triaged and excluded.

## Root Cause

The FCA `validate_layer_alignment()` **already detects** both violations via the
`AGENT_OUTSIDE_REASONING` check (line 1596–1627). The root cause is that the
detection was never acted on — the agents were flagged but never relocated.

Both agents were in `L0_maintenance/scripts/`, which is a valid location for
scripts but NOT for agents. The scripts purity gate (line 1547) did not block
them because neither filename matched the forbidden patterns (PascalCase or
`test_*` prefix) — they used snake_case filenames.

## Scan Methodology

1. Glob `agentic_core/L*/**/*.py` (recursive)
2. AST-parse each file for ClassDef nodes ending in `Agent`, `Executor`, `Orchestrator`
3. Skip files where parent dir is `reasoning/` or `base_agents/`
4. For each hit, check if class inherits `SovereignBaseAgent` (real agent) vs Protocol/dataclass (false positive)

## True Violations (2) — Fixed

| Old Path | Class | Bases | New Path |
|---|---|---|---|
| `L0_maintenance/scripts/integrity_gate_executor.py` | `IntegrityGateExecutorAgent` | `AtomicExecutionMixin, SovereignBaseAgent` | `L0_maintenance/reasoning/IntegrityGateExecutorAgent.py` |
| `L0_maintenance/scripts/routing_decision.py` | `RootCustomsAgent` | `SovereignBaseAgent` | `L0_maintenance/reasoning/RootCustomsAgent.py` |

### Import fixes

- `test_integrity_gate_executor.py`: `importlib.import_module` path updated
- `test_routing_decision.py`: `importlib.import_module` path updated
- No `from ... import` statements existed for either agent

### Pre-existing issue

`IntegrityGateExecutorAgent` has a pre-existing `NameError: name 'AtomicExecutionMixin' is not defined`
at line 300. This was broken BEFORE the move (verified by stash + import at baseline `2835b2641`).
Out of scope for this RCA.

## False Positives (4) — Correctly Placed

| File | Class | Bases | Why NOT an agent |
|---|---|---|---|
| `L0_maintenance/scripts/core_synthesis_executor.py` | `CoreSynthesisExecutor` | (none) | Script utility, no SovereignBaseAgent |
| `L0_maintenance/scripts/execution_context.py` | `BaseTaskExecutor` | `MCPHardenedMixin, HealerMixin, SubatomicTestingMixin` | Shared mixin base, no SovereignBaseAgent |
| `L3_orchestration/types/orchestrator_types.py` | `IOrchestratorAgent` | `Protocol` | Interface/Protocol definition |
| `L3_orchestration/types/recursive_orchestration_types.py` | `RecursiveOrchestrator` | (none) | Dataclass, no SovereignBaseAgent |

## Validation

- FCA `validate_layer_alignment()` returns `None` (compliant) for both moved files
- `test_routing_decision.py`: 3/3 PASS
- `test_integrity_gate_executor.py`: 3/3 FAIL (pre-existing `NameError`, not caused by move)
- Full re-scan: 0 true violations remaining

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

