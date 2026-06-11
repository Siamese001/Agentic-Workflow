---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ssot-report-storage-protocol-f312d7.md'
original_relative_path: 'ssot-report-storage-protocol-f312d7.md'
source_sha256: b6eddd2efbb863dbc25c6507bfef3a86ab4801ab300c80c526a99961b077ec6d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Report Storage Protocol Implementation

Implement a comprehensive protocol to ensure all reports are stored in the canonical SSOT location `docs/reports` instead of scattered across `.windsurf` directories or other locations.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

Based on codebase analysis:
- **SSOT Location**: `docs/reports/` contains 180+ properly organized reports
- **Scattered Reports**: Found references to `docs/reports/plans/` in multiple phase summaries
- **Root Reports**: Multiple reports in project root (PHASE*.md, RCA*.md, etc.)
- **No `.windsurf` Directory**: The `.windsurf` directory doesn't exist in current workspace

## Recommended Implementation Strategy

### 1. **Pre-commit Hook Enforcement**
Create a new pre-commit hook `check-report-location` that:
- Scans for any files matching report patterns (`*report*.md`, `RCA*.md`, `PHASE*.md`)
- Validates they reside in `docs/reports/` or approved subdirectories
- Auto-moves misplaced files to correct location with git history preservation

### 2. **SSOT Discovery Integration**
Extend `agentic_core/utils/ssot_discovery.py` with:
- `validate_report_location()` function
- `auto_misplaced_report_migration()` utility
- Integration with existing agent discovery system

### 3. **Report Generation Protocol**
Standardize report generation across all agents:
- Update report generation methods to use `docs/reports/` as default
- Implement timestamped subdirectories for organization
- Add report metadata validation

### 4. **Migration Script**
Create `ops_scripts/maintenance/migrate_reports_to_ssot.py` that:
- Identifies all misplaced reports
- Performs git-aware moves to preserve history
- Updates internal references and imports
- Generates migration manifest

### 5. **Guardian Integration**
Add report location validation to existing Guardian tests:
- Extend `test_ssot_compliance.py` with report location checks
- Add report structure validation to `test_hierarchy_agent.py`

## Implementation Phases

**Phase 1**: Create pre-commit hook and validation logic
**Phase 2**: Implement migration script and run initial cleanup
**Phase 3**: Update all report generation methods
**Phase 4**: Add comprehensive test coverage
**Phase 5**: Documentation and team training

## Success Criteria

- Zero reports outside `docs/reports/` structure
- Pre-commit hook prevents future report misplacement
- All existing reports migrated with git history intact
- Automated validation in CI/CD pipeline

## Risk Mitigation

- Backup existing reports before migration
- Gradual rollout with validation at each phase
- Rollback procedures documented
- Team communication plan for location changes

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

