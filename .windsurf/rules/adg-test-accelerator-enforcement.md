---
trigger: glob
globs:
  - "**/test_*_adg.py"
  - "tools/adg/**"
description: Apply when reading or writing ADG test files or tools to enforce mandatory use of adg_test_accelerator.py for gap analysis, scoped test selection, and parallel grouping.
---

> **Claude always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Claude retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Claude enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# ADG Test Accelerator Mandatory Enforcement

## Overview

This rule mandates the use of `tools/adg/adg_test_accelerator.py` (Accelerator #5) for comprehensive test planning and validation. The accelerator provides five commands: `gap`, `scope`, `groups`, `report`, and `collection-safety`.

## When to Run

| Scenario | Mandatory Command | Exit Code Handling |
|----------|-------------------|-------------------|
| Changed files detected | `python tools/adg/adg_test_accelerator.py scope --changed <files> --format pytest` | Non-zero = stop, use full suite with SCOPE_LOSSINESS note |
| Pre-refactor (T2/T3) | `python tools/adg/adg_test_accelerator.py gap --top 30` | Non-zero = block refactor until gaps addressed |
| Import modifications | `python tools/adg/adg_test_accelerator.py collection-safety --json` | Non-zero = fix imports before proceeding |
| Parallel test execution | `python tools/adg/adg_test_accelerator.py groups --workers 4 --format json` | Parse JSON for `--dist worksteal` groups |
| Phase completion | `python tools/adg/adg_test_accelerator.py report --out docs/reports/plans/adg_test_report.json` | Artifact required for convergence |

## Command Reference

### gap — Coverage Gap Analysis
```bash
python tools/adg/adg_test_accelerator.py gap [--top N] [--layer L5]
```
Ranks uncovered production modules by fan-in (risk). Use before refactors to identify what needs tests.

### scope — Scoped Test Selection
```bash
python tools/adg/adg_test_accelerator.py scope --changed <file> [<file>...] [--format {lines,pytest,json}] [--stdin]
```
Given changed production files, emits test files that cover them (direct covers + transitive importers).

### groups — Parallel Worker Groups
```bash
python tools/adg/adg_test_accelerator.py groups --workers N [--format {text,json}]
```
Partitions test files into N balanced groups by ADG layer for pytest-xdist `--dist worksteal`.

### collection-safety — Import Safety Check
```bash
python tools/adg/adg_test_accelerator.py collection-safety [--layer L0] [--json out.json]
```
Analyzes test file imports via ADG: resolvable, missing, syntax errors, cycles, stale paths.

### report — Full JSON Report
```bash
python tools/adg/adg_test_accelerator.py report --out <path>
```
Combines gap analysis, layer distribution, coverage map, and risk gaps into single artifact.

## Failure Modes

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Proceed with scoped tests |
| 1 | No tests found / Error | Run full suite, record SCOPE_LOSSINESS |
| 130 | Keyboard interrupt | Abort operation |
| Non-zero (other) | ADG scan failure | Check `adg_stale_guard.py`, regenerate ADG if needed |

## Tier-Based Enforcement

| Tier | Requirement |
|------|-------------|
| T0 — Question | Optional; use if ADG cache hot |
| T1 — Trivial | Optional; verify with scoped tests if convenient |
| T2 — Scoped | **Required:** `scope` for changed files; `collection-safety` if imports modified |
| T3 — Architectural | **Required:** `gap` before refactor, `scope` for selection, `collection-safety` after changes, `groups` for parallel run |

## Audit Trail Requirements

Every accelerator invocation MUST include:
- **Command**: Full command with arguments
- **Timestamp**: ISO8601 execution time
- **Exit code**: Numeric exit status
- **Output summary**: Brief result description
- **Scoped tests**: Count of tests identified (if applicable)
- **Coverage gaps**: Count and list of gaps (if gap command)
- **Collection safety**: Pass/fail count (if collection-safety command)
- **ADG snapshot**: ADG ID used for analysis

Missing audit fields = gate failure.

```markdown
## ADG_TEST_ACCELERATOR
**Command**: `python tools/adg/adg_test_accelerator.py <cmd> <args>`
**Timestamp**: <ISO8601>
**Exit Code**: <0|1|...>
**Output Summary**: <brief summary>
**Scoped Tests**: <count> (if applicable)
**Coverage Gaps**: <count> (if gap command)
**Collection Safe**: <count>/<total> (if collection-safety command)
```

## Integration with CI Gates

The accelerator is enforced via `ops_scripts/ci/run_contract_gates.py`:
- T2/T3 phases without accelerator evidence = gate failure
- Missing `scope` when changed files exist = gate failure
- Missing `collection-safety` when imports modified = gate failure

## Workflow Example

```bash
# 1. Pre-refactor: identify coverage gaps
python tools/adg/adg_test_accelerator.py gap --top 30

# 2. After making changes: identify impacted tests
python tools/adg/adg_test_accelerator.py scope --changed agentic_core/L2_execution/cid_registry.py --format pytest

# 3. Verify no import regressions
python tools/adg/adg_test_accelerator.py collection-safety --json collection_report.json

# 4. Run parallel test groups
python tools/adg/adg_test_accelerator.py groups --workers 4 --format json > worker_groups.json

# 5. Generate final report
python tools/adg/adg_test_accelerator.py report --out docs/reports/plans/adg_test_report.json
```

## Guardrails

- **No bypassing:** Using raw pytest, grep, or manual test selection instead of accelerator = §2.3 violation
- **No stale ADG:** Accelerator requires fresh ADG; run `python tools/generate_full_adg.py` after refactoring
- **No silent failures:** Non-zero exit codes must be documented; "works on my machine" without accelerator validation = constitutional violation
- **Pure static analysis:** Accelerator queries ADG only; no runtime emissions, no fake telemetry
