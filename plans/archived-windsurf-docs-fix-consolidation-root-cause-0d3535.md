---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\fix-consolidation-root-cause-0d3535.md'
original_relative_path: 'fix-consolidation-root-cause-0d3535.md'
source_sha256: 83e1559e4819b185b44fe8fcf6ee96939eaf0481d07262d47c5ba47e3c7127c8
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Fix Root Cause of Architectural Violation in Consolidation

This plan addresses the root cause of why 37 Agent files were incorrectly placed in engines/ and 3 _types files had mixed content, which occurred during the consolidation pass because folder purity validation was missing.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Root Cause Summary

The consolidation pass (2026-02-08) focused only on agent count reduction (190→149) but lacked folder structure validation, causing it to accept and preserve existing architectural violations without questioning them.

## Implementation Plan

### Phase 1: Add Folder Purity Validation to Consolidation Pipeline

1. **Create consolidation validator module** (`agentic_core/L5_safety/config/structure_blueprint/consolidation_validator.py`)
   - Add `validate_agent_placement()` - ensures Agent files are in reasoning/
   - Add `validate_types_purity()` - ensures _types files only contain type definitions
   - Add `validate_folder_structure()` - comprehensive folder purity checks

2. **Update consolidation script** (`artifacts/consolidation/implement_consolidation.py`)
   - Import and call validator before processing each target
   - Fail fast on architectural violations with clear error messages
   - Add auto-correction suggestions for misplaced files

### Phase 2: Strengthen Guardian Tests

3. **Add comprehensive folder purity tests** (`tests/guardian/test_folder_purity_hardening.py`)
   - `test_agents_in_reasoning_only()` - detect Agent files in engines/
   - `test_types_files_purity()` - detect mixed content in _types files
   - `test_no_engines_in_reasoning()` - detect engine files in reasoning/
   - `test_executors_placement()` - validate Executor placement rules

4. **Add consolidation validation test** (`tests/guardian/test_consolidation_folder_purity.py`)
   - Test that consolidation validator catches violations
   - Test auto-correction suggestions
   - Test validator with current fixed state

### Phase 3: Harden Structure Blueprint Config

5. **Add folder placement rules to config** (`agentic_core/L5_safety/config/structure_blueprint/placement_rules.py`)
   - Define `REQUIRED_PLACEMENT_RULES` mapping file patterns to required folders
   - Define `FORBIDDEN_PLACEMENT_RULES` mapping file patterns to forbidden folders
   - Add `validate_placement()` function using these rules

6. **Update FCA to use placement rules** (`agentic_core/L5_safety/reasoning/FileClassificationAgent.py`)
   - Add placement validation to `classify_file()` method
   - Add `get_placement_violations()` method
   - Integrate with existing folder purity checks

### Phase 4: Create Prevention Mechanisms

7. **Add pre-commit hook for folder purity** (`.pre-commit-config.yaml`)
   - Run folder purity validation on staged files
   - Block commits that violate architectural rules
   - Provide auto-fix suggestions

8. **Add CI enforcement** (`.github/workflows/folder-purity-guard.yml`)
   - Run comprehensive folder purity checks on PR
   - Fail builds on violations
   - Generate violation reports

### Phase 5: Documentation and Training

9. **Update consolidation documentation** (`docs/reports/plans/canonicalization-plan.md`)
   - Add folder purity requirements section
   - Document validation process
   - Add troubleshooting guide

10. **Create architectural decision record** (`docs/architecture/adr-001-folder-purity.md`)
    - Document why folder purity matters
    - Explain consolidation lessons learned
    - Provide migration guidelines

## Success Criteria

- ✅ All Agent files are in reasoning/ folders
- ✅ All _types files contain only type definitions
- ✅ All engine files are in engines/ folders
- ✅ Consolidation validator prevents future violations
- ✅ Guardian tests catch folder purity violations
- ✅ CI prevents merging architectural violations
- ✅ Documentation clearly explains requirements

## Risk Mitigation

- **Backward compatibility**: Validator only validates, doesn't auto-move files
- **Gradual rollout**: Phase 1-2 implement validation, Phase 3-4 add enforcement
- **Clear error messages**: Validator provides specific guidance for fixes
- **Test coverage**: Comprehensive tests ensure validator works correctly

## Files to Create/Modify

### New Files
- `agentic_core/L5_safety/config/structure_blueprint/consolidation_validator.py`
- `agentic_core/L5_safety/config/structure_blueprint/placement_rules.py`
- `tests/guardian/test_consolidation_folder_purity.py`
- `.github/workflows/folder-purity-guard.yml`
- `docs/architecture/adr-001-folder-purity.md`

### Modified Files
- `artifacts/consolidation/implement_consolidation.py`
- `tests/guardian/test_folder_purity_hardening.py`
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- `docs/reports/plans/canonicalization-plan.md`
- `.pre-commit-config.yaml`

This plan ensures the root cause is fixed by adding validation to prevent future architectural violations during any consolidation or refactoring efforts.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

