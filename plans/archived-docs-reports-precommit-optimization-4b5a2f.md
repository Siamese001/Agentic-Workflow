---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\precommit-optimization-4b5a2f.md'
original_relative_path: 'precommit-optimization-4b5a2f.md'
source_sha256: e07bc49597b97bd2758437e4893ad2442608671fecb3d1971cd7ee7ec3e9189e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Pre-commit Hook Optimization Plan

Optimize pre-commit hook execution order, remove dead code, consolidate redundant checks, and improve signal flow for faster commit validation.

---

## Wave Structure

| Waves | Micro-Waves | Metric | Scope | Checkpoint | Tokens |
|-------|-------------|--------|-------|------------|---------|
| Wave 1 | MW1.1, MW1.2, MW1.3, MW1.4 | Remove dead gates + quick reorders | T13.5, T13.6, T-1, T19, T11.2 | A | 2,500 🟢 |
| Wave 2 | MW2.1, MW2.2, MW2.3 | Consolidate ruff passes | T2 4-pass → 1-pass | B | 3,000 🟢 |
| Wave 3 | MW3.1, MW3.2, MW3.3 | Consolidate ADG ban gates | T14-T16 → T14 | C | 3,500 🟢 |
| Wave 4 | MW4.1, MW4.2, MW4.3 | Reorder for signal flow | T2-T3 move, structural grouping | D | 2,500 🟢 |

**Total: 11,500 tokens across 4 waves, 11 micro-waves, all GREEN**

---

## Gap Register

**GAP-1: Dead gates wasting execution time**
- T13.5 (Layer Violation Gate) queries edges table for 'violates' relation (0 results)
- T13.6 (P1 Defect Gate) queries violations table for 'critical' severity (0 results)
- Both gates never block commits but run on every commit
- Impact: ~0.5s wasted per commit, misleading signal

**GAP-2: Redundant ADG ban gate structure**
- T14 (Python Ban), T15 (YAML Ban), T16 (Skip-File Ratchet) are conceptually similar
- All check ADG accelerator compliance patterns
- Separate subprocess calls for related checks
- Impact: ~1.5s overhead, fragmented error reporting

**GAP-3: Suboptimal hook ordering**
- T-1 (Summary Init) runs after T4 instead of at start
- T19 (Staleness Guard) runs near end instead of before ADG-dependent gates
- Structural checks (T6-T10.6) are scattered
- Impact: Poor signal flow, wasted work on files that will fail later

**GAP-4: Ruff pass redundancy**
- T2 runs 4 separate ruff subprocess calls (P0, P1, P2, P3)
- Same file parsed 4 times
- Impact: ~1s overhead from subprocess spawning

---

## Execution Plan

### Wave 1 — Remove Dead Gates + Quick Reorders
**Scope**: Remove T13.5, T13.6; reorder T-1 to start, T19 before T12; file-trigger T11.2

#### Micro-Wave 1.1: Remove T13.5 (Layer Violation Gate)
**Commands**:
```bash
# Remove T13.5 entry from .pre-commit-config.yaml
# Lines 439-448: Remove adg-layer-violation-gate hook
# Update header comment to remove T13.5 reference
```

**Acceptance**:
- T13.5 removed from config
- Pre-commit runs without errors
- No blocking behavior lost

#### Micro-Wave 1.2: Remove T13.6 (P1 Defect Gate)
**Commands**:
```bash
# Remove T13.6 entry from .pre-commit-config.yaml
# Lines 450-459: Remove adg-p1-defect-gate hook
# Update header comment to remove T13.6 reference
# Delete ops_scripts/ci/adg_p1_defect_gate.py (optional, can archive)
```

**Acceptance**:
- T13.6 removed from config
- Pre-commit runs without errors
- No blocking behavior lost

#### Micro-Wave 1.3: Reorder T-1 and T19
**Commands**:
```bash
# Move T-1 (pre-commit-summary-init) from line 248 to line 246 (before T5)
# Move T19 (adg-stale-guard) from line 559 to line 408 (before T12)
# Update header comments to reflect new order
```

**Acceptance**:
- T-1 runs at start of governance hooks
- T19 runs before ADG-dependent gates (T12-T13)
- Pre-commit runs without errors
- Better fail-fast behavior

#### Micro-Wave 1.4: File-Trigger T11.2
**Commands**:
```bash
# Add files: ^(config/mcp_servers\.yaml|mcp_config\.json)$ to T11.2
# Line 393: Add files pattern to mcp-config-drift-check
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
# Extract all --select rules from T2-P0, T2-P1, T2-P2, T2-P3
# Combine into single --select argument
# Create combined rule string:
#   F821,F401,B012,B904,S102,S307,S601,F541,B013,B015,
#   B002,B006,B009,B010,B019,B027,S105,S106,S107,S108,S311,S324,S603,S607,UP028,C401,C402,C403,C404,
#   E402,E721,E731,F811,B007,B011,B023,B024,B028,C405,C406,C408,C409,C410,C411,COM812,COM819,I001,
#   E501,W291,W292,W293,W505,T201,T203,UP001,UP003,UP004,UP005,UP008,UP009,UP010
```

**Acceptance**:
- Combined rule string created
- All original rules included
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
# Remove old T2-P0 through T2-P3 entries (lines 181-217)
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
# If needed, create wrapper script to handle severity-based exit codes
```

**Acceptance**:
- P0/P1 violations still block commits
- P2/P3 violations are non-blocking
- Exit code behavior preserved

### Wave 3 — Consolidate ADG Ban Gates
**Scope**: Merge T14, T15, T16 into single T14 (ADG Accelerator Compliance Gate)

#### Micro-Wave 3.1: Create Consolidated Gate Script
**Commands**:
```bash
# Create ops_scripts/ci/adg_accelerator_compliance_gate.py
# Merge logic from:
#   - ops_scripts/ci/adg_python_ban_gate.py (grep/mypy/pytest in Python)
#   - ops_scripts/ci/adg_yaml_grep_ban_gate.py (grep/rg in YAML)
#   - ops_scripts/ci/adg_skip_file_ratchet.py (skip-file budget)
# Unified structure:
#   def check_python_bans(staged_files): -> issues
#   def check_yaml_bans(staged_files): -> issues
#   def check_skip_file_budget(): -> issues
#   def main():
#       all_issues = []
#       all_issues.extend(check_python_bans())
#       all_issues.extend(check_yaml_bans())
#       all_issues.extend(check_skip_file_budget())
#       if all_issues:
#           print_unified_report(all_issues)
#           return 1
#       return 0
```

**Acceptance**:
- Consolidated script created
- All three checks implemented
- Unified error reporting

#### Micro-Wave 3.2: Update Pre-commit Config
**Commands**:
```bash
# Replace T14, T15, T16 with single T14 entry
# New T14 entry:
#   - id: adg-accelerator-compliance-gate
#     name: "T14: ADG Accelerator Compliance Gate"
#     entry: python ops_scripts/ci/adg_accelerator_compliance_gate.py --staged
#     language: system
#     pass_filenames: false
#     always_run: false
#     require_serial: true
# Remove old T15 (lines 474-485) and T16 (lines 487-498)
# Remove types: [python] and types: [yaml] (now handled in script)
```

**Acceptance**:
- Single T14 replaces T14-T16
- Config updated
- Header comments updated

#### Micro-Wave 3.3: Test Consolidated Gate
**Commands**:
```bash
# Test with Python file containing grep/mypy/pytest
# Test with YAML file containing grep/rg
# Test with skip-file directive without budget update
# Verify all blocking behaviors preserved
# Verify unified error reporting works
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
# Move T2 (ruff) from line 181 to line 460 (before T20)
# Move T3 (ruff-format) from line 220 to line 465 (after T2, before T20)
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
#   # ---- STRUCTURAL INTEGRITY BLOCK (T6-T10.6) ----
#   # Fast, decisive checks before expensive policy enforcement
# Ensure T6 through T10.6 are contiguous
# No other hooks between T6 and T10.6
```

**Acceptance**:
- Structural checks (T6-T10.6) logically grouped
- Section comment added
- Pre-commit runs without errors

#### Micro-Wave 4.3: Update Header Comments
**Commands**:
```bash
# Update line 6-29 to reflect optimized order:
#   T-1: Summary Init (start)
#   T0: Admission guards
#   T1: Syntax check
#   T4: Guardian fix
#   T6-T10.6: Structural Integrity Block
#   T11-T11.3: Config SSOT
#   T19: ADG staleness (before ADG gates)
#   T12: Exemption ratchet
#   T13: Burndown ratchet
#   T14: ADG Accelerator Compliance (consolidated)
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

- No changes to hook logic behavior (only consolidation)
- Preserve all blocking/non-blocking semantics
- Maintain backward compatibility for error messages
- Test each wave independently before proceeding
- Document all changes in header comments
- Verify pre-commit runs successfully after each wave

---

## Success Criteria

- [ ] Dead gates (T13.5, T13.6) removed
- [ ] ADG ban gates consolidated (T14-T16 → T14)
- [ ] Hook order optimized for signal flow
- [ ] Ruff passes consolidated (4 → 1)
- [ ] Pre-commit execution time reduced by ~30%
- [ ] All existing blocking behavior preserved
- [ ] Pre-commit runs without errors on clean repo
- [ ] Pre-commit still blocks on violations

---

## Implementation Commands

```bash
# Wave 1: Remove dead gates + quick reorders
# MW1.1: Remove T13.5
# Edit .pre-commit-config.yaml, remove lines 439-448
# Update header comment

# MW1.2: Remove T13.6
# Edit .pre-commit-config.yaml, remove lines 450-459
# Update header comment
# git rm ops_scripts/ci/adg_p1_defect_gate.py

# MW1.3: Reorder T-1 and T19
# Move T-1 from line 248 to line 246
# Move T19 from line 559 to line 408
# Update header comments

# MW1.4: File-trigger T11.2
# Add files pattern to mcp-config-drift-check at line 393

# Test Wave 1
pre-commit run --all-files

# Wave 2: Consolidate ruff passes
# MW2.1: Combine rule sets
# Extract rules from T2-P0 through T2-P3
# Create combined rule string

# MW2.2: Create single T2 hook
# Replace T2-P0 through T2-P3 with single T2 entry
# Use combined --select rules

# MW2.3: Verify exit codes
# Test with P0/P1 violations (should block)
# Test with P2/P3 violations (should not block)

# Test Wave 2
pre-commit run --all-files

# Wave 3: Consolidate ADG ban gates
# MW3.1: Create consolidated script
# Create ops_scripts/ci/adg_accelerator_compliance_gate.py
# Merge logic from adg_python_ban_gate.py
# Merge logic from adg_yaml_grep_ban_gate.py
# Merge logic from adg_skip_file_ratchet.py

# MW3.2: Update config
# Replace T14-T16 with single T14 entry
# Remove T15 (lines 474-485)
# Remove T16 (lines 487-498)

# MW3.3: Test consolidated gate
# Test Python file with grep/mypy/pytest
# Test YAML file with grep/rg
# Test skip-file without budget update

# Test Wave 3
pre-commit run --all-files

# Wave 4: Reorder for signal flow
# MW4.1: Move T2-T3 to end
# Move T2 from line 181 to line 460
# Move T3 from line 220 to line 465
# Add section comment

# MW4.2: Group structural checks
# Add section comment before T6
# Ensure T6-T10.6 are contiguous

# MW4.3: Update header comments
# Update lines 6-29 to reflect final order

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
3. If consolidated gate has bugs, restore original three gates
4. If ruff consolidation breaks, restore 4-pass structure
5. Test pre-commit on clean repo before continuing

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| Dead gates removed | 2 gates removed | T13.5, T13.6 absent from config |
| Ruff passes consolidated | 4 → 1 pass | Single T2 entry with combined rules |
| ADG gates consolidated | 3 → 1 gate | Single T14 entry, T15/T16 removed |
| Hook order optimized | T-1 at start, T19 early, T2-T3 end | Config reflects new order |
| Structural checks grouped | T6-T10.6 contiguous | Section comment added |
| T11.2 file-triggered | Only runs on MCP changes | files pattern added |
| Execution time | ~40% reduction | Time `pre-commit run --all-files` before/after |
| Blocking behavior preserved | All violations still block | Test with intentional violations |
| Pre-commit runs clean | No errors on clean repo | `pre-commit run --all-files` exits 0 |
| Micro-wave acceptance | Each MW passes acceptance | Test after each micro-wave |

**Wave-Specific Success Criteria:**

**Wave 1 (Remove Dead Gates + Quick Reorders):**
- [ ] T13.5 removed from config
- [ ] T13.6 removed from config
- [ ] T-1 runs at start
- [ ] T19 runs before T12
- [ ] T11.2 has file trigger
- [ ] Pre-commit runs without errors

**Wave 2 (Consolidate Ruff Passes):**
- [ ] Single T2 entry replaces 4 hooks
- [ ] Combined rule string includes all original rules
- [ ] P0/P1 violations still block
- [ ] P2/P3 violations non-blocking
- [ ] Pre-commit runs without errors

**Wave 3 (Consolidate ADG Ban Gates):**
- [ ] Consolidated script created
- [ ] Single T14 replaces T14-T16
- [ ] Python ban check works
- [ ] YAML ban check works
- [ ] Skip-file ratchet works
- [ ] Unified error reporting works
- [ ] Pre-commit runs without errors

**Wave 4 (Reorder for Signal Flow):**
- [ ] T2 runs at end (before T20)
- [ ] T3 runs after T2
- [ ] Structural checks grouped with comment
- [ ] Header comments updated
- [ ] Pre-commit runs without errors
