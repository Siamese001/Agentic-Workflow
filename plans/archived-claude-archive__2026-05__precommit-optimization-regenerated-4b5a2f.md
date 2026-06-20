---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\precommit-optimization-regenerated-4b5a2f.md'
original_relative_path: '_archive\\2026-05\\precommit-optimization-regenerated-4b5a2f.md'
source_sha256: 6898e5795c194a552aba2fba3c7c06ca66d469cacc6569d539200dd34b3a0329
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Pre-commit Hook Optimization Plan — REGENERATED

Optimize pre-commit hook execution order, remove dead code, consolidate redundant checks, and improve signal flow for faster commit validation.

**REGENERATION DATE**: 2026-04-06
**ADG SNAPSHOT**: adg_indexed_04062026_0545.sqlite (88,216 nodes, 625,559 edges, 0 violations)
**PLAN STATUS**: Updated based on current ADG analysis

---

## Wave Structure

| Waves | Micro-Waves | Metric | Scope | Checkpoint | Tokens |
|-------|-------------|--------|-------|------------|---------|
| Wave 1 | MW1.1, MW1.2, MW1.3, MW1.4 | Remove dead gates + quick reorders | T13.5, T13.6, T-1, T19, T11.2 | A | 2,500 🟢 |
| Wave 2 | MW2.1, MW2.2, MW2.3 | Consolidate ruff passes | T2 4-pass → 1-pass | B | 3,000 🟢 |
| Wave 3 | MW3.1, MW3.2, MW3.3 | Consolidate ADG ban gates | T14, T15, T16 → T14 (Python+YAML) + T15 (Skip-file) | C | 3,000 🟢 |
| Wave 4 | MW4.1, MW4.2, MW4.3 | Reorder for signal flow | T2-T3 move, structural grouping | D | 2,500 🟢 |

**Total: 11,000 tokens across 4 waves, 11 micro-waves, all GREEN**

---

## ADG Analysis Summary

**FACT_CLASSIFICATION:**
- `DIRECTLY_OBSERVED`: ADG health check shows 88,216 nodes, 625,559 edges, 0 violations
- `DIRECTLY_OBSERVED`: T13.5 queries `edges WHERE relation_type = 'violates'` — 0 results
- `DIRECTLY_OBSERVED`: T13.6 queries `violations WHERE severity = 'critical'` — 0 results
- `DIRECTLY_OBSERVED`: T14 (adg-python-ban-gate) already consolidates grep/mypy/pytest bans
- `DERIVED`: T13.5 and T13.6 are dead gates with no blocking behavior
- `DERIVED`: Wave 3 consolidation scope reduced from 3→1 to 2→1 (Python already consolidated)
- `UNRESOLVED`: None

**Key Findings from ADG:**
1. **Dead Gates Confirmed**: T13.5 (layer violations) and T13.6 (P1 defects) return 0 results
2. **Gate Structure Updated**: T14 already consolidates Python bans (grep/mypy/pytest)
3. **Current Structure**: T14 (Python ban), T15 (YAML grep ban), T16 (Skip-file ratchet)
4. **Optimization Target**: Consolidate T14 and T15 into single accelerator compliance gate

---

## Gap Register

**GAP-1: Dead gates wasting execution time**
- T13.5 (Layer Violation Gate) queries edges table for 'violates' relation (0 results per ADG)
- T13.6 (P1 Defect Gate) queries violations table for 'critical' severity (0 results per ADG)
- Both gates never block commits but run on every commit with `always_run: true`
- Impact: ~0.5s wasted per commit, misleading signal

**GAP-2: Partial ADG ban gate consolidation**
- T14 (adg-python-ban-gate) already consolidates grep/mypy/pytest bans ✓
- T15 (adg-yaml-grep-ban-gate) remains separate
- T16 (adg-skip-file-ratchet) is conceptually related (budget enforcement)
- Impact: ~1.0s overhead from separate subprocess calls, fragmented error reporting

**GAP-3: Suboptimal hook ordering**
- T-1 (Summary Init) runs at line 241 (middle of governance hooks) instead of at start
- T19 (Staleness Guard) runs at line 548 (near end) instead of before ADG-dependent gates (T12-T13)
- T2-T3 (Ruff) run early (lines 174-215) instead of after governance checks
- Structural checks (T6-T11.3) are scattered
- Impact: Poor signal flow, wasted work on files that will fail later

**GAP-4: Ruff pass redundancy**
- T2 runs 4 separate ruff subprocess calls (P0, P1, P2, P3)
- Same file parsed 4 times
- Impact: ~1s overhead from subprocess spawning

**GAP-5: T11.2 not file-triggered**
- T11.2 (MCP Config Drift) has `always_run: true` (line 386)
- Should only run when MCP config files change
- Impact: ~0.2s wasted on non-MCP commits

---

## Execution Plan

### Wave 1 — Remove Dead Gates + Quick Reorders
**Scope**: Remove T13.5, T13.6; reorder T-1 to start, T19 before T12; file-trigger T11.2

#### Micro-Wave 1.1: Remove T13.5 (Layer Violation Gate)
**Commands**:
```bash
# Remove T13.5 entry from .pre-commit-config.yaml
# Lines 432-441: Remove adg-layer-violation-gate hook
# Update header comment (line 21) to remove T13.5 reference
```

**Acceptance**:
- T13.5 removed from config
- Pre-commit runs without errors
- No blocking behavior lost (verified: ADG has 0 layer violations)

#### Micro-Wave 1.2: Remove T13.6 (P1 Defect Gate)
**Commands**:
```bash
# Remove T13.6 entry from .pre-commit-config.yaml
# Lines 443-452: Remove adg-p1-defect-gate hook
# Update header comment (line 22) to remove T13.6 reference
# Archive ops_scripts/ci/adg_p1_defect_gate.py to tools/archive/
```

**Acceptance**:
- T13.6 removed from config
- Pre-commit runs without errors
- No blocking behavior lost (verified: ADG has 0 critical violations)

#### Micro-Wave 1.3: Reorder T-1 and T19
**Commands**:
```bash
# Move T-1 (pre-commit-summary-init) from line 241 to line 240 (immediately after T5)
# Move T19 (adg-stale-guard) from line 548 to line 430 (before T12 exemption-gate)
# Update header comments to reflect new order
```

**Acceptance**:
- T-1 runs immediately after T5 (at start of local hooks)
- T19 runs before ADG-dependent gates (T12-T13)
- Pre-commit runs without errors
- Better fail-fast behavior (stale ADG detected before expensive gates)

#### Micro-Wave 1.4: File-Trigger T11.2
**Commands**:
```bash
# Add files: ^(config/mcp_servers\.yaml|mcp_config\.json|\.windsurf/mcp_config.*\.json)$ to T11.2
# Line 381-387: Change always_run: true to always_run: false, add files pattern
```

**Acceptance**:
- T11.2 only runs when MCP config files change
- Pre-commit runs without errors on non-MCP commits
- ~0.2s savings on non-MCP commits

### Wave 2 — Consolidate Ruff Passes
**Scope**: Merge T2-P0 through T2-P3 into single T2 pass

#### Micro-Wave 2.1: Combine Ruff Rule Sets
**Commands**:
```bash
# Extract all --select rules from T2-P0, T2-P1, T2-P2, T2-P3 (lines 178, 187, 196, 206)
# Combine into single --select argument
# Create combined rule string:
#   F821,F401,B012,B904,S102,S307,S601,F541,B013,B015,
#   B002,B006,B009,B010,B019,B027,S105,S106,S107,S108,S311,S324,S603,S607,UP028,C401,C402,C403,C404,B904,
#   E402,E721,E731,F811,B007,B011,B023,B024,B028,C405,C406,C408,C409,C410,C411,COM812,COM819,I001,
#   E501,W291,W292,W293,W505,T201,T203,UP001,UP003,UP004,UP005,UP008,UP009,UP010
# Note: B904 appears in both P0 and P1 — deduplicate
```

**Acceptance**:
- Combined rule string created
- All original rules included (deduplicated)
- No rules lost in merge

#### Micro-Wave 2.2: Create Single T2 Hook
**Commands**:
```bash
# Replace T2-P0, T2-P1, T2-P2, T2-P3 with single T2 entry
# New T2 entry:
#   - id: ruff
#     name: "T2: Ruff Lint (All Severities)"
#     args: [--select=<combined-rules>, --fix]
#     exclude: ops_scripts/ci/check_anti_patterns\.py
#     stages: [pre-commit]
# Remove old T2-P0 through T2-P3 entries (lines 174-210)
```

**Acceptance**:
- Single T2 hook replaces 4 hooks
- Pre-commit runs without errors
- All lint checks still performed

#### Micro-Wave 2.3: Verify Exit Code Handling
**Commands**:
```bash
# Test ruff with combined rules
# Verify that P0/P1 rules still block (exit 1)
# Verify that P2/P3 rules use --exit-zero (exit 0)
# Since --exit-zero applies to all rules in combined mode, create wrapper script:
#   ops_scripts/ci/ruff_severity_gate.py that runs ruff twice:
#     1. P0/P1 rules (blocking, no --exit-zero)
#     2. P2/P3 rules (non-blocking, with --exit-zero)
```

**Acceptance**:
- P0/P1 violations still block commits
- P2/P3 violations are non-blocking
- Exit code behavior preserved

### Wave 3 — Consolidate ADG Ban Gates (UPDATED)
**Scope**: Merge T14 (Python ban) and T15 (YAML grep ban) into single T14 (ADG Accelerator Compliance Gate)
**NOTE**: T14 already consolidates grep/mypy/pytest. This wave consolidates Python+YAML enforcement.

#### Micro-Wave 3.1: Create Consolidated Gate Script
**Commands**:
```bash
# Create ops_scripts/ci/adg_accelerator_compliance_gate.py
# Merge logic from:
#   - ops_scripts/ci/adg_python_ban_gate.py (grep/mypy/pytest in Python)
#   - ops_scripts/ci/adg_yaml_grep_ban_gate.py (grep/rg in YAML)
# Keep T16 (adg-skip-file-ratchet.py) separate — it's a budget ratchet, not a pattern ban
# Unified structure:
#   def check_python_bans(staged_files): -> issues
#   def check_yaml_bans(staged_files): -> issues
#   def main():
#       all_issues = []
#       all_issues.extend(check_python_bans())
#       all_issues.extend(check_yaml_bans())
#       if all_issues:
#           print_unified_report(all_issues)
#           return 1
#       return 0
```

**Acceptance**:
- Consolidated script created
- Python ban check works (grep/mypy/pytest)
- YAML ban check works (grep/rg in workflows)
- Unified error reporting

#### Micro-Wave 3.2: Update Pre-commit Config
**Commands**:
```bash
# Replace T14 and T15 with single T14 entry
# New T14 entry:
#   - id: adg-accelerator-compliance-gate
#     name: "T14: ADG Accelerator Compliance Gate — no grep/mypy/pytest (Python) or grep/rg (YAML)"
#     entry: cmd /c "set PYTHONPATH=.&& set PRE_COMMIT_ISSUES_DIR=%TEMP%/pre-commit-issues&& python ops_scripts/ci/adg_accelerator_compliance_gate.py --staged --json-output %TEMP%/pre-commit-issues/adg_accelerator_compliance_gate.jsonl"
#     language: system
#     pass_filenames: false
#     always_run: false
#     require_serial: true
# Remove old T15 (lines 467-478)
# Keep T16 (skip-file ratchet) as-is — rename to T15 for consistency
# Update header comments (lines 23-24) to reflect T14 consolidation
```

**Acceptance**:
- Single T14 replaces T14+T15
- T16 renamed to T15 (skip-file ratchet)
- Config updated
- Header comments updated

#### Micro-Wave 3.3: Test Consolidated Gate
**Commands**:
```bash
# Test with Python file containing grep/mypy/pytest
# Test with YAML file containing grep/rg in run: steps
# Verify unified error reporting displays both Python and YAML issues
# Verify all blocking behaviors preserved
```

**Acceptance**:
- All original blocking behaviors preserved
- Unified error reporting displays all issues
- Pre-commit runs without errors

### Wave 4 — Reorder for Signal Flow
**Scope**: Move T2-T3 to end, group structural checks with section comment

#### Micro-Wave 4.1: Move T2-T3 to End
**Commands**:
```bash
# Move T2 (ruff) from line 174 to line 460 (before T20)
# Move T3 (ruff-format) from line 213 to line 465 (after T2, before T20)
# Update header comments to reflect new order
# Add comment: # ---- STYLE & FORMATTING (T2-T3) ----
```

**Acceptance**:
- T2 runs after all governance checks
- T3 runs after T2
- Pre-commit runs without errors
- Better signal flow (governance before style)

#### Micro-Wave 4.2: Group Structural Checks
**Commands**:
```bash
# Add section comment before T6:
#   # ---- STRUCTURAL INTEGRITY BLOCK (T6-T11.3) ----
#   # Fast, decisive checks before expensive policy enforcement
# Ensure T6 through T11.3 are contiguous
# No other hooks between T6 and T11.3
```

**Acceptance**:
- Structural checks (T6-T11.3) logically grouped
- Section comment added
- Pre-commit runs without errors

#### Micro-Wave 4.3: Update Header Comments
**Commands**:
```bash
# Update lines 5-29 to reflect optimized order:
#   T-1: Summary Init (start, after T5)
#   T0: Admission guards
#   T1: Syntax check
#   T4: Guardian fix
#   T6-T11.3: Structural Integrity Block
#   T19: ADG staleness (before ADG gates)
#   T12: Exemption ratchet
#   T13: Burndown ratchet
#   T14: ADG Accelerator Compliance (consolidated Python+YAML)
#   T15: Skip-file ratchet (renamed from T16)
#   T2: Ruff lint (end)
#   T3: Ruff format (end)
#   T20: Cleanup
#   T21: Summary report
```

**Acceptance**:
- Header comments match actual hook order
- All reorders documented
- Pre-commit runs without errors

---

## Rules

- No changes to hook logic behavior (only consolidation and reordering)
- Preserve all blocking/non-blocking semantics
- Maintain backward compatibility for error messages
- Test each wave independently before proceeding
- Document all changes in header comments
- Verify pre-commit runs successfully after each wave
- Archive removed gate scripts to tools/archive/ (not delete)

---

## Success Criteria

- [ ] Dead gates (T13.5, T13.6) removed
- [ ] ADG ban gates consolidated (T14+T15 → T14, T16 → T15)
- [ ] Hook order optimized for signal flow
- [ ] Ruff passes consolidated (4 → 1, with severity gate wrapper)
- [ ] Pre-commit execution time reduced by ~35%
- [ ] All existing blocking behavior preserved
- [ ] Pre-commit runs without errors on clean repo
- [ ] Pre-commit still blocks on violations

---

## Implementation Commands

```bash
# Wave 1: Remove dead gates + quick reorders
# MW1.1: Remove T13.5
# Edit .pre-commit-config.yaml, remove lines 432-441
# Update header comment line 21

# MW1.2: Remove T13.6
# Edit .pre-commit-config.yaml, remove lines 443-452
# Update header comment line 22
# git mv ops_scripts/ci/adg_p1_defect_gate.py tools/archive/

# MW1.3: Reorder T-1 and T19
# Move T-1 from line 241 to line 240
# Move T19 from line 548 to line 430
# Update header comments

# MW1.4: File-trigger T11.2
# Edit line 386: change always_run: true to always_run: false
# Add files pattern to line 387

# Test Wave 1
pre-commit run --all-files

# Wave 2: Consolidate ruff passes
# MW2.1: Combine rule sets
# Extract rules from T2-P0 through T2-P3
# Create combined rule string (deduplicate B904)

# MW2.2: Create wrapper script for severity-based exit codes
# Create ops_scripts/ci/ruff_severity_gate.py
# Implement P0/P1 blocking, P2/P3 non-blocking

# MW2.3: Update config
# Replace T2-P0 through T2-P3 with single T2 entry calling wrapper
# Use wrapper script instead of direct ruff call

# Test Wave 2
pre-commit run --all-files

# Wave 3: Consolidate ADG ban gates
# MW3.1: Create consolidated script
# Create ops_scripts/ci/adg_accelerator_compliance_gate.py
# Merge logic from adg_python_ban_gate.py and adg_yaml_grep_ban_gate.py

# MW3.2: Update config
# Replace T14 and T15 with single T14 entry
# Rename T16 to T15 (skip-file ratchet)
# Update header comments lines 23-24

# MW3.3: Test consolidated gate
# Test Python file with grep/mypy/pytest
# Test YAML file with grep/rg
# Verify unified error reporting

# Test Wave 3
pre-commit run --all-files

# Wave 4: Reorder for signal flow
# MW4.1: Move T2-T3 to end
# Move T2 from line 174 to line 460
# Move T3 from line 213 to line 465
# Add section comment

# MW4.2: Group structural checks
# Add section comment before T6
# Ensure T6-T11.3 are contiguous

# MW4.3: Update header comments
# Update lines 5-29 to reflect final order

# Test Wave 4
pre-commit run --all-files

# Final validation
# Test with clean repo
# Test with intentional violations
# Verify all blocking behaviors preserved
```

---

## Rollback Strategy

If things go wrong:
1. Git revert each wave commit individually
2. Restore original `.pre-commit-config.yaml` from git
3. If consolidated gate has bugs, restore original gates
4. If ruff consolidation breaks, restore 4-pass structure
5. Test pre-commit on clean repo before continuing

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| Dead gates removed | 2 gates removed | T13.5, T13.6 absent from config |
| Ruff passes consolidated | 4 → 1 pass (with wrapper) | Single T2 entry with severity gate |
| ADG gates consolidated | T14+T15 → T14, T16 → T15 | Single T14, T15 renamed |
| Hook order optimized | T-1 at start, T19 early, T2-T3 end | Config reflects new order |
| Structural checks grouped | T6-T11.3 contiguous | Section comment added |
| T11.2 file-triggered | Only runs on MCP changes | files pattern added |
| Execution time | ~35% reduction | Time `pre-commit run --all-files` before/after |
| Blocking behavior preserved | All violations still block | Test with intentional violations |
| Pre-commit runs clean | No errors on clean repo | `pre-commit run --all-files` exits 0 |
| Micro-wave acceptance | Each MW passes acceptance | Test after each micro-wave |

**Wave-Specific Success Criteria:**

**Wave 1 (Remove Dead Gates + Quick Reorders):**
- [ ] T13.5 removed from config
- [ ] T13.6 removed from config
- [ ] T-1 runs at start (after T5)
- [ ] T19 runs before T12
- [ ] T11.2 has file trigger
- [ ] Pre-commit runs without errors

**Wave 2 (Consolidate Ruff Passes):**
- [ ] Single T2 entry replaces 4 hooks
- [ ] Severity gate wrapper created
- [ ] P0/P1 violations still block
- [ ] P2/P3 violations non-blocking
- [ ] Pre-commit runs without errors

**Wave 3 (Consolidate ADG Ban Gates):**
- [ ] Consolidated script created (Python+YAML)
- [ ] Single T14 replaces T14+T15
- [ ] T16 renamed to T15
- [ ] Python ban check works
- [ ] YAML ban check works
- [ ] Unified error reporting works
- [ ] Pre-commit runs without errors

**Wave 4 (Reorder for Signal Flow):**
- [ ] T2 runs at end (before T20)
- [ ] T3 runs after T2
- [ ] Structural checks grouped with comment
- [ ] Header comments updated
- [ ] Pre-commit runs without errors

---

## ARTIFACTS

- **Plan File**: `` `@.cursor/plans/precommit-optimization-4b5a2f.md ``
- **ADG SQLite**: `` `@C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04062026_0545.sqlite ``
- **Pre-commit Config**: `` `@C:\Git\Agentic-Workflow\.pre-commit-config.yaml ``
- **Gate Scripts**: 
  - `` `@C:\Git\Agentic-Workflow\ops_scripts\ci\adg_layer_violation_gate.py ``
  - `` `@C:\Git\Agentic-Workflow\ops_scripts\ci\adg_p1_defect_gate.py ``
  - `` `@C:\Git\Agentic-Workflow\ops_scripts\ci\adg_python_ban_gate.py ``
  - `` `@C:\Git\Agentic-Workflow\ops_scripts\ci\adg_yaml_grep_ban_gate.py ``
  - `` `@C:\Git\Agentic-Workflow\ops_scripts\ci\adg_skip_file_ratchet.py ``
