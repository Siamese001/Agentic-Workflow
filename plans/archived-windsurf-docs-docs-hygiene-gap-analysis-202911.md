---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\docs-hygiene-gap-analysis-202911.md'
original_relative_path: 'docs-hygiene-gap-analysis-202911.md'
source_sha256: deb68cd0b44f587cba29102cf9022b96e9e56ad329cd22b168e5da0d09f0db43
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Docs Folder Hygiene Treatment Gap Analysis

This plan analyzes how the `docs/` folder is treated by hygiene agents in the agentic workflow system and identifies critical gaps in documentation governance.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary

The `docs/` folder contains rich content (506+ files including architecture plans, reports, metrics, and specifications) but is systematically overlooked by hygiene agents, creating a significant governance gap for documentation assets.

## Current State Analysis

### 1. FileClassificationAgent Treatment

**Exclusion Pattern**: `docs/` is NOT in the `exclude_dirs` set (line 116), meaning docs files ARE scanned but with minimal governance.

**Key Findings**:
- Only processes `.py` files, ignoring all documentation formats (`.md`, `.yaml`, `.json`, `.txt`)
- `refactor_non_python_assets()` method (line 3429) only touches docs/ for name updates during refactoring
- No validation of documentation structure, naming conventions, or content quality
- Docs folder treated as "config dump" rather than structured documentation territory

### 2. HygieneGuardianAgent Treatment

**Scope Limitation**: Only processes Python files with extensions `{".py", ".pyi"}`

**Critical Gaps**:
- No detection of orphaned documentation files
- No cleanup of stale backup documentation (`.bak.md`, `.old.md`)
- No validation of documentation file naming patterns
- No detection of duplicate or copy-pattern documentation files

### 3. HierarchyAgent Treatment

**Protected Status**: `docs/` is NOT in `SOVEREIGN_EXCLUDED_FOLDERS`, but gets minimal attention

**Current Behavior**:
- Processes data files with extensions `[".json", ".md", ".yaml", ".yml"]` (lines 800, 943)
- Only enforces depth limits, not documentation structure
- No validation of documentation folder hierarchy or organization
- No enforcement of documentation naming standards

### 4. DocumentationAgent Treatment

**Critical Limitation**: Only validates Python docstrings, NOT documentation files

**Missing Coverage**:
- No validation of markdown file structure
- No checking for missing table of contents
- No validation of cross-references or broken links
- No enforcement of documentation standards

## Identified Gaps

### Gap 1: File Type Coverage
- **Problem**: Hygiene agents only process `.py` files
- **Impact**: 500+ documentation files receive no governance
- **Risk**: Documentation drift, inconsistency, and decay

### Gap 2: Structure Validation
- **Problem**: No enforcement of docs/ folder structure standards
- **Current Structure**: `architecture/`, `contracts/`, `metrics/`, `plans/`, `reports/`, `runbooks/`, `specs/`, `technical/`, `testing/`
- **Risk**: Misplaced files, inconsistent organization

### Gap 3: Naming Convention Enforcement
- **Problem**: No validation of documentation file naming
- **Examples**: Some files use underscores, others hyphens, inconsistent capitalization
- **Risk**: Findability issues, unprofessional appearance

### Gap 4: Content Quality Checks
- **Problem**: No validation of documentation content quality
- **Missing**: Table of contents, proper headings, cross-references
- **Risk**: Poor user experience, ineffective documentation

### Gap 5: Orphaned and Stale Content
- **Problem**: No detection of outdated or orphaned documentation
- **Examples**: Old implementation plans, outdated architecture diagrams
- **Risk**: Confusion, wasted time reading obsolete information

## Proposed Solution Architecture

### 1. Extend FileClassificationAgent
- Add documentation file type classification
- Implement docs-specific naming conventions
- Add structure validation for docs/ hierarchy

### 2. Create DocumentationHygieneAgent
- Specialized agent for documentation governance
- Validate markdown structure and quality
- Detect orphaned and stale content

### 3. Extend HierarchyAgent
- Add docs/ folder structure enforcement
- Validate proper placement of documentation files
- Enforce depth limits for documentation hierarchy

### 4. Documentation Quality Standards
- Define naming conventions for documentation files
- Implement structure validation (TOC, headings, cross-refs)
- Add link checking and reference validation

## Implementation Plan

### Phase 1: Assessment and Documentation
1. Inventory all documentation files and their types
2. Document current naming patterns and inconsistencies
3. Map existing folder structure vs. ideal structure

### Phase 2: Agent Extensions
1. Extend FileClassificationAgent for documentation file types
2. Add docs/ folder processing to HierarchyAgent
3. Create DocumentationHygieneAgent prototype

### Phase 3: Validation and Testing
1. Create comprehensive test suite for documentation hygiene
2. Implement dry-run mode for documentation validation
3. Add reporting mechanisms for documentation violations

### Phase 4: Integration and Deployment
1. Integrate documentation hygiene into existing guardian workflows
2. Add documentation-specific CI checks
3. Implement automated documentation quality reports

## Success Metrics

- **Coverage**: 100% of documentation files under governance
- **Quality**: 90% compliance with naming and structure standards
- **Freshness**: Automated detection of stale content (older than 6 months without updates)
- **Findability**: Consistent folder structure and naming conventions

## Risk Mitigation

- **Backward Compatibility**: Maintain existing documentation during transition
- **Gradual Rollout**: Implement in phases with dry-run validation
- **User Feedback**: Provide clear violation messages and suggested fixes
- **Automation**: Minimize manual intervention through automated fixes

## Next Steps

1. Conduct comprehensive documentation inventory
2. Define documentation standards and conventions
3. Implement DocumentationHygieneAgent prototype
4. Create test suite for documentation validation
5. Integrate with existing hygiene workflows

This analysis reveals a significant governance gap that, when addressed, will dramatically improve documentation quality, consistency, and maintainability across the agentic workflow system.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

