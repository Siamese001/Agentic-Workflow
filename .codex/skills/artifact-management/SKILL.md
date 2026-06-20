---
name: artifact-management
description: Manages evidence capture, SSOT path validation, bounded operations, and progress display for long-running or artifact-producing work. Use when writing plans or reports, emitting evidence bundles, validating plan/report locations, or running any operation over 5 seconds that requires a progress bar.
metadata:
  enforcement_layer: pre-commit
  enforcement_timing: after_work
  enforcement_type: structural
---

# Artifact Management Skill (Consolidated)

Consolidated skill that merges `evidence-bundle`, `ssot-write-gate`, and `progress-display` into unified artifact management with progress tracking.

## Files

- **`path_validation_checklist.md`** — Pre-write checklist for SSOT path validation and canonical directory mapping
- **`evidence_standards.md`** — Evidence section requirements, fact classification, and artifact location rules
- **`progress_display_protocol.md`** — Bounded operations with colored progress bars and ETA tracking
- **`artifact_type_resolver.md`** — Mapping of artifact types to canonical SSOT directories
- **`bounded_operations_guide.md`** — File limits, early termination, and PowerShell compatibility

## When to use

- Before writing ANY `.md` plan, report, or evidence file
- Before writing ANY `.json` artifact, registry, or snapshot
- Before writing ANY `.py` script to a directory not yet confirmed as SSOT-approved
- When a path contains `C:\Users\`, `.codex/plans/`, or any absolute user-home path
- During any long-running operation (>5s) that processes files
- When creating evidence artifacts for phase documentation

## Path Validation Rules (ALL must pass)

1. **Repository root check** — Path MUST be under `c:\Git\Agentic-Workflow\`
2. **Whitelist check** — First path component MUST be in `PROJECT_ROOT_WHITELIST`:
   `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `ops_scripts`, `tests`, `docs`, `data`, `tools`, `artifacts`, `system_learning`
3. **Artifact type check** — Artifact type MUST match canonical directory per `artifact_type_resolver.md`
4. **No IDE-system paths** — NEVER write to `.cursor/`, `.vscode/` for project artifacts

## Canonical Paths Quick Reference

| Artifact Type | Canonical Path |
|---|---|
| Plans / evidence / RCAs | `.codex/plans/` |
| Governance reports | `.codex/plans/` |
| Telemetry | `docs/reports/telemetry/` |
| Freeze reports | `data/freeze_reports/` |
| Architecture docs | `docs/architecture/` |
| Test files | `tests/<category>/` |

## Evidence Standards

### Required Evidence Sections (in order)
1. `# <Phase Title>`
2. `## Scope` — with graph justification
3. `## INSPECTED_FILES`
4. `## FACT_CLASSIFICATION` — three tiers: DIRECTLY OBSERVED / DERIVED / UNRESOLVED
5. Command output sections
6. `## DEPENDENCY_GRAPH` — roots, impacted nodes, upstream set, downstream set, edge classes, boundary/cycle findings, reason each changed file is in scope
7. `## BRANCH_INVENTORY`
8. `## ROBUSTNESS_MATRIX` — success/edge/failure/recovery/determinism/side-effect tests per changed surface
9. `## DEFECT_MODEL`

### Conditional Sections (add when applicable)
- `## TIMEOUT_RECOVERY` — when timeout occurs
- `## CLUSTER_ANALYSIS` — for every repair
- `## FAILURE_CAPTURE` — before any repair edit
- `## PROOF_ARTIFACT_TRUTHFULNESS` — when ADG proof artifact referenced
- `## POLICY_DRIFT` — when policy regression classified
- `## CONTRACT_CONFLICT` — when contract conflict identified
- `## ENVIRONMENT_CONTRACT` — when environment dependency involved

### Three-Tier Fact Classification

| Tier | Label | Meaning |
|---|---|---|
| 1 | `DIRECTLY OBSERVED` | Read directly from raw artifact/command stdout — no inference |
| 2 | `DERIVED` | Computed from secondary command — source command MUST be named |
| 3 | `UNRESOLVED` | Not yet proven — MUST be listed explicitly, never omitted |

### Artifact Links

Every artifact reference in a response MUST use backtick citation format: `` `@<absolute_path>` ``. Plain text paths = CONSTITUTIONAL VIOLATION.

### Evidence Contract

Each phase produces exactly one evidence file under `.codex/plans/`.

**Commands executed via:** `subprocess.run(argv, shell=False, encoding="utf-8", errors="replace")`
**PowerShell invocation is FORBIDDEN.**
**File-based Python scripts REQUIRED for complex analysis** — write to `ops_scripts/ci/` or `tools/evidence/`, then execute via subprocess. Never inline Python via PowerShell.

Evidence files MUST be ASCII-only with ANSI escape sequences stripped.

## Progress Display & Bounded Operations

### Mandatory Progress Display (operations >5s)
- **Progress bars** with colored percentage completion (standard 40-character format)
- **Real-time status updates** at least every 5 seconds
- **Color-coded indicators**: 🟢 Green (success), 🔵 Blue (in-progress), 🟡 Yellow (warning/slow), 🔴 Red (error), ⚪ White (neutral)
- **ETA display** for operations >30s (formatted as Xs, Xm, or Xh)
- **Current item tracking** with descriptive status messages
- **ANSI color codes** for terminal compatibility

### Bounded Operations Enforcement
All file analysis operations MUST include:
- **Maximum file limits** (default: 1000 files, configurable)
- **Early termination conditions** (stop when patterns converge)
- **Batch processing** with progress reporting (never process all files in one unbounded loop)
- **PowerShell compatibility** verification (no Unix-only commands like `head`, `tail` without Windows equivalents)

### Timeout Ranges
- **Fast** (grep, file reads, simple AST): 5–30s
- **Medium** (graph construction, test collection): 30–120s
- **Heavy** (full repo analysis): 120–600s
- **External API**: 10–60s

## Pre-Write Validation Checklist

**Before any artifact write:**

1. **Verify path**: Is path under repository root?
2. **Check whitelist**: Is first component in PROJECT_ROOT_WHITELIST?
3. **Match artifact type**: Does file type match canonical directory?
4. **Validate format**: Is this the correct location for this artifact type?
5. **Check conflicts**: Will this overwrite existing artifact inappropriately?

**If any check fails → STOP. Do not write artifact.**

## Progress Tracking Implementation

### Example Progress Display
```python
from .cursor.skills.artifact_management import ProgressTracker

# Create progress tracker
tracker = ProgressTracker(total_items, "Processing files")
tracker.start()

# Update progress during operation
for i, item in enumerate(items):
    process_item(item)
    tracker.update(1, f"Processing {item.name}")

# Complete with success
tracker.complete(f"Processed {total_items} items")
```

### ANSI Color Codes
- `\033[92m` for bright green (success)
- `\033[93m` for bright yellow (warning)
- `\033[91m` for bright red (error)
- `\033[94m` for bright blue (in-progress)
- `\033[97m` for bright white (neutral)
- `\033[0m` to reset color

## Constitutional Requirements Enforced

- **§8:** All plans and reports MUST reside in `.codex/plans/`
- **§2.1:** Evidence files MUST be within repository sovereign territories
- **§5.3:** Query timeout & progress reporting requirements
- **IDE system paths:** `.codex/plans/`, `.codex/skills/`, `.codex/commands/`

## Enforcement Scripts

| Requirement | Enforcement Script(s) |
|-------------|---------------------|
| Path validation | Custom path validation script |
| Evidence standards | Evidence format validation |
| Progress display | Progress tracking verification |
| Bounded operations | File limit and timeout enforcement |

**Single entrypoint:** `python ops_scripts/ci/run_contract_gates.py`

## RCA Auto-Closure Integration

When creating RCA documents, this skill ensures:
1. **Document the violation** — incident summary, root cause, impact
2. **Execute corrective actions IMMEDIATELY** — do not wait for user prompt
3. **Update RCA status** — mark as RESOLVED with timestamp
4. **Document evidence** — link to corrective action artifacts
5. **Update preventive measures** — mark completed items with [x]

## Forbidden Patterns

- ❌ Writing artifacts outside repository sovereign territories
- ❌ Using `docs/reports/plans/` for IDE-generated plans
- ❌ Long operations (>5s) without progress display
- ❌ Unbounded file operations (processing unlimited files)
- ❌ Missing PowerShell compatibility
- ❌ Evidence without proper fact classification
- ❌ Plain text paths without backtick citation format
- ❌ DERIVED facts without naming the deriving command
- ❌ Omitting UNRESOLVED facts
- ❌ Complex inline Python scripts in shell commands
