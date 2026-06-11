---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p1-p4-enforcement-hardening-8a3f2b.md'
original_relative_path: 'p1-p4-enforcement-hardening-8a3f2b.md'
source_sha256: 2d237defa943f3f02ea67109c639ee4241a5f76afe7cefa4ca59815f77e6f446
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P1-P4 Enforcement Hardening Plan

Hardens the P1-P4 enforcement documentation and infrastructure based on gaps identified in the enforcement table review.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Documentation completeness | P1/P2 exemption mechanisms, P2 enforcement function names | A | 15k 🟢 |
| Wave 2 | Fix script pipeline integration | Wire P2 fix scripts into ADG post-run pipeline | B | 25k 🟢 |
| Wave 3 | Pre-commit clarification | Document T21 dependency for P2 commit blocking | C | 10k 🟢 |

**Total: 50k tokens across 3 waves, all GREEN**

---

## Gap Register

**GAP-0: fix_silent_swallowers.py is broken**
- UnboundLocalError on line 61 (cannot access local variable 'node')
- Path bug: duplicate 'tools' in output path
- Status: ✅ FIXED (line 61: node→tree, line 264: removed duplicate 'tools' path)

**GAP-1: P2 "Blocks Commit" is overstated**
- P2 commit blocking depends on T21 (summary reporter) being active
- Table implied unconditional blocking, which is misleading
- Impact: Developers may not understand why P2 sometimes doesn't block

**GAP-2: P2 fix scripts not wired into ADG pipeline**
- Scripts exist on disk but are not auto-called post-ADG
- Fix scripts: `fix_silent_swallowers.py`, `fix_high_severity_silent_swallowers.py`, `fix_invalid_stubs.py`
- Impact: P2 violations tracked but not automatically rectified

**GAP-3: P1 auto-fix timing ambiguous**
- "Before ADG retry" implies automatic retry loop
- No automatic retry exists — developer must manually re-run ADG
- Impact: Misleading about automation level

**GAP-4: P3/P4 counts lack snapshot context**
- Counts (307, 4391) are point-in-time from snapshot `04062026_0751`
- Will drift over time
- Impact: Readers may treat counts as stable facts

**GAP-5: P2 exemption mechanism undocumented**
- `# guardian: allow-silent-swallow` and `# guardian: allow-invalid-stub` exist
- Not documented in enforcement table
- Impact: Users don't know how to suppress false positives

**GAP-6: P2 ADG enforcement function names vague**
- Table said "architectural detection" without naming functions
- Should name `SilentSwallowerDetector`, `InvalidStubDetector`
- Impact: Hard to trace code paths

**GAP-7: P1 exemption mechanism absent from docs**
- P1 cannot be whitelisted (constitutional)
- Not explicitly stated
- Impact: Users may try to whitelist P1 violations

---

## Execution Plan

### Phase 1.1 — Document P1 exemption mechanism
**Scope**: Add explicit statement that P1 violations cannot be whitelisted

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Verify P1 has no whitelist support in base_detector_validator.py
grep -n "whitelist" agentic_core/L5_safety/validators/base_detector_validator.py

# Update enforcement table
# Edit docs/reports/p1_p4_enforcement_table.md
# Add "Exemption Mechanism" row to P1 detailed breakdown:
# "None — P1 violations cannot be whitelisted"
```

**Acceptance**: P1 detailed breakdown includes explicit exemption mechanism row stating "None — P1 violations cannot be whitelisted"

### Phase 1.2 — Document P2 exemption mechanisms
**Scope**: Add `# guardian: allow-*` exemption details to P2 breakdown

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Verify exemption comment patterns
grep -r "guardian: allow-" agentic_core/L5_safety/validators/ --include="*.py"

# Update enforcement table
# Edit docs/reports/p1_p4_enforcement_table.md
# Add "Exemption Mechanism" row to P2 detailed breakdown:
# "# guardian: allow-silent-swallow (silent swallowers)"
# "# guardian: allow-invalid-stub (invalid stubs)"
# "placed on line immediately before the violation"
```

**Acceptance**: P2 detailed breakdown includes exemption mechanism row with both comment patterns and placement instructions

### Phase 1.3 — Name P2 enforcement functions explicitly
**Scope**: Replace vague "architectural detection" with concrete function names

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Verify detector names in anti_pattern_scanner_validator.py
grep -A 5 "SilentSwallowerDetector\|InvalidStubDetector" agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py

# Update enforcement table
# Edit docs/reports/p1_p4_enforcement_table.md
# Change P2 "ADG Enforcement" from "Architectural detection..." to:
# "SilentSwallowerDetector, InvalidStubDetector in anti_pattern_scanner_validator.py (tracking only — recorded in SQLite, do not block)"
```

**Acceptance**: P2 summary and detailed breakdowns name `SilentSwallowerDetector` and `InvalidStubDetector` explicitly

### Phase 1.4 — Add snapshot reference to P3/P4 counts
**Scope**: Footnote point-in-time counts with snapshot ID

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Find latest ADG snapshot
ls -la artifacts/adg/adg_snapshot_*.json | tail -1

# Update enforcement table
# Edit docs/reports/p1_p4_enforcement_table.md
# Change P3 count from "307 (antipattern)" to "307 ¹"
# Change P4 count from "4391 (antipattern)" to "4391 ¹"
# Add footnote: "¹ Point-in-time counts from ADG snapshot [ID] — will drift over time."
```

**Acceptance**: P3/P4 counts have ¹ footnote referencing snapshot ID with drift warning

---

### Phase 2.1 — Survey fix script landscape
**Scope**: Identify all P2 fix scripts and their current integration status

**Status**: ✅ COMPLETE

**Survey Findings**:
- `fix_invalid_stubs.py` (8214 bytes) - ✅ Working CLI with `--dry-run` and `--apply`
- `fix_high_severity_silent_swallowers.py` (16004 bytes) - ✅ Working CLI with `--phase21` and `--demo`
- `fix_silent_swallowers.py` (10922 bytes) - ❌ **BROKEN** (UnboundLocalError on line 61)
- Integration status: None called in `generate_full_adg.py` or `.pre-commit-config.yaml`
- Only referenced in `generate_final_compliance_report.py`

**Commands**:
```bash
# List fix scripts
ls -la tools/fix/

# Check if scripts are called anywhere
grep -r "fix_silent_swallowers\|fix_invalid_stubs" tools/generate/ --include="*.py"
grep -r "fix_silent_swallowers\|fix_invalid_stubs" .pre-commit-config.yaml

# Verify script signatures
python tools/fix/fix_silent_swallowers.py --help
python tools/fix/fix_invalid_stubs.py --help
```

**Acceptance**: Documented list of P2 fix scripts with their current integration status (called vs. uncalled)

### Phase 2.2 — Design ADG post-run fix script integration
**Scope**: Design mechanism to call fix scripts after ADG generation completes

**Status**: 🔴 BLOCKED (requires fix_silent_swallowers.py fix first)

**Commands**:
```bash
# Review generate_full_adg.py structure
grep -n "def main" tools/generate/generate_full_adg.py
grep -n "print.*complete\|print.*done" tools/generate/generate_full_adg.py

# Identify insertion point for post-run fix script calls
# Target: after ADG artifacts generated, before exit
```

**Acceptance**: Design document specifying:
- Insertion point in `generate_full_adg.py`
- Order of fix script calls (silent swallowers → invalid stubs)
- Error handling strategy (continue on failure vs. fail-fast)
- Logging requirements

### Phase 2.3 — Implement fix script integration
**Scope**: Add fix script calls to ADG generation pipeline

**Status**: 🔴 BLOCKED (requires Phase 2.2 and fix_silent_swallowers.py fix)

**Commands**:
```bash
# Create integration function in generate_full_adg.py
# Function: _run_p2_fix_scripts()
# Logic:
#   - Check if P2 violations detected in SQLite
#   - If yes, call fix_silent_swallowers.py --apply
#   - Call fix_invalid_stubs.py --apply
#   - Log results
#   - Report summary to user

# Wire into main() after artifact generation
# Add parameter --no-fix-scripts to skip if needed
```

**Acceptance**: `generate_full_adg.py` calls P2 fix scripts post-generation when P2 violations detected

### Phase 2.4 — Test fix script integration
**Scope**: Verify fix scripts run correctly in ADG context

**Status**: 🔴 BLOCKED (requires Phase 2.3)

**Commands**:
```bash
# Run ADG generation with test file containing P2 violations
python tools/generate/generate_full_adg.py --strict-mode

# Verify fix scripts were called (check logs)
# Verify violations were fixed (re-run validator)
# Verify SQLite database updated
```

**Acceptance**: Fix scripts execute post-ADG, violations are fixed, database updated, logs show execution

---

### Phase 3.1 — Clarify P1 auto-fix timing
**Scope**: Change "before retry" to "before manual ADG re-run"

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Update enforcement table
# Edit docs/reports/p1_p4_enforcement_table.md
# Change P1 "Auto-Fix Timing" from "✅ YES (before retry)" to
# "✅ Fix scripts run before manual ADG re-run"

# Update P1 detailed breakdown "Fix Script Timing" from
# "Before ADG generation retry (after fix scripts run)" to
# "Fix scripts run before manual ADG re-run (no automatic retry loop)"
```

**Acceptance**: P1 auto-fix timing explicitly states manual re-run required

### Phase 3.2 — Clarify P2 commit blocking dependency
**Scope**: Add T21 summary reporter dependency to P2 commit blocking

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Verify T21 exists
grep -n "T21\|summary.*reporter" .pre-commit-config.yaml
grep -n "critical_high_count\|blocks_commit" ops_scripts/ci/pre_commit_summary_reporter.py

# Update enforcement table
# Edit docs/reports/p1_p4_enforcement_table.md
# Change P2 "Blocks Commit" from "✅ YES" to
# "✅ YES (via T21 summary reporter)"

# Add note to Key Enforcement Principles:
# "P2 commit blocking requires T21 (summary reporter) hook to be active"
```

**Acceptance**: P2 commit blocking explicitly references T21 summary reporter dependency

### Phase 3.3 — Update enforcement flow diagram
**Scope**: Clarify manual vs. automated steps in flow diagram

**Status**: ✅ COMPLETE

**Commands**:
```bash
# Update enforcement flow diagram in docs/reports/p1_p4_enforcement_table.md
# Change "Fix scripts run automatically (P1 before retry, P2 after completion)" to
# "Fix scripts run automatically (P2 after completion)"
# Add note: "P1: Developer must manually re-run ADG after fixes"

# Add T21 check to pre-commit step:
# "Pre-commit hooks (fast checks, seconds)"
# "  ├─ T21 summary reporter: if critical_high_count > 0 → BLOCK commit"
```

**Acceptance**: Flow diagram distinguishes automated vs. manual steps, includes T21 dependency

---

## Rules

- No code changes to validators themselves — only documentation and pipeline integration
- Fix script integration must be non-blocking: continue on individual script failure
- All changes must preserve backward compatibility
- Document all assumptions about ADG pipeline behavior
- Test with real P2 violations before merging

---

## Success Criteria

- [ ] P1/P2 exemption mechanisms documented in enforcement table
- [ ] P2 enforcement function names explicit in table
- [ ] P3/P4 counts have snapshot reference footnote
- [ ] P2 fix scripts wired into ADG post-run pipeline
- [ ] Fix scripts execute automatically when P2 violations detected
- [ ] P1 auto-fix timing clarifies manual re-run requirement
- [ ] P2 commit blocking clarifies T21 dependency
- [ ] Enforcement flow diagram updated with manual/automated distinction
- [ ] Integration tested with real P2 violations
- [ ] No regression in existing ADG generation behavior

---

## Implementation Commands

```bash
# Phase 1: Documentation hardening
# (Manual edits to docs/reports/p1_p4_enforcement_table.md)

# Phase 2: Fix script integration
# Phase 2.1: Survey
ls -la tools/fix/
grep -r "fix_silent_swallowers\|fix_invalid_stubs" tools/generate/ --include="*.py"
grep -r "fix_silent_swallowers\|fix_invalid_stubs" .pre-commit-config.yaml

# Phase 2.2: Design (manual design document creation)

# Phase 2.3: Implementation (code edit to tools/generate/generate_full_adg.py)
# Add _run_p2_fix_scripts() function
# Wire into main() after artifact generation

# Phase 2.4: Testing
python tools/generate/generate_full_adg.py --strict-mode

# Phase 3: Pre-commit clarification
# (Manual edits to docs/reports/p1_p4_enforcement_table.md)
```

---

## Rollback Strategy

If things go wrong:
1. Revert `generate_full_adg.py` changes (remove `_run_p2_fix_scripts()` call)
2. Revert enforcement table changes to previous version
3. Document rollback reason in execution plan
4. Re-test baseline ADG generation to ensure no regression

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Documentation completeness | 100% of gaps addressed | Enforcement table includes all 7 gap fixes |
| Fix script integration | P2 scripts auto-run post-ADG | ADG logs show fix script execution when P2 violations present |
| P1 auto-fix clarity | Manual re-run explicitly stated | Table text says "manual ADG re-run" not "retry" |
| P2 commit blocking clarity | T21 dependency documented | Table text says "via T21 summary reporter" |
| Test coverage | Integration tested with real violations | Test execution log shows fix scripts called |
| Backward compatibility | No regression | Existing ADG generation passes without new behavior |

---

## Implementation Status Summary

**Wave 1: Documentation Hardening** - ✅ COMPLETE
- Phase 1.1: P1 exemption mechanism documented ✅
- Phase 1.2: P2 exemption mechanisms documented ✅
- Phase 1.3: P2 enforcement function names explicit ✅
- Phase 1.4: P3/P4 counts have snapshot reference ✅

**Wave 2: Fix Script Pipeline Integration** - � READY TO PROCEED
- Phase 2.1: Survey complete - found broken fix_silent_swallowers.py ✅
- Phase 2.1a: Fixed fix_silent_swallowers.py (line 61: node→tree, line 264: path fix) ✅
- Phase 2.2: Design - READY (fix_silent_swallowers.py now working) �
- Phase 2.3: Implementation - READY �
- Phase 2.4: Testing - READY �

**Wave 3: Pre-Commit Clarification** - ✅ COMPLETE
- Phase 3.1: P1 auto-fix timing clarified ✅
- Phase 3.2: P2 commit blocking dependency documented ✅
- Phase 3.3: Enforcement flow diagram updated ✅

**Blocker Resolved**: `fix_silent_swallowers.py` UnboundLocalError and path bug fixed. Script now works (found 1626 violations, report generated successfully).

**Next Steps**:
1. Complete Wave 2 phases 2.2-2.4 (design, implement, test fix script integration)
2. Final validation and testing
