---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt-modularization-rebaseline-8624b1.md'
original_relative_path: 'prompt-modularization-rebaseline-8624b1.md'
source_sha256: 9dd0818f8894203dca102042e9ff62378a3293a9f1ac1c9212e45060ec5f4a21
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt Modularization Rebaseline Plan

This plan rebaselines the prompt modularization effort based on the current repository state, addressing the fragmentation between multiple prompt storage locations and establishing a clean, deterministic SSOT architecture.

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

### Existing Prompt Modularization Infrastructure
- **Phase 0 COMPLETE**: Deterministic assembly gate implemented and working
- **Validation Pipeline**: `validate_assembly.py` passes with 7 modules (version 5.4.2)
- **CI Integration**: GitHub Actions workflow enforces assembly integrity
- **Canonical Artifact**: `Prompt v5.4 State Gap Implementation.md` (1428 lines)

### Prompt Storage Fragmentation (4 Roots)
1. **`agentic_core/prompt_governance/meta_prompts`** (19 files) - 18 unused, 1 test-only
2. **`data/prompt_governance`** (165 files) - Runtime SSOT, 543 code references
3. **`data/prompt_libraries`** (8 files) - 5 unused, 3 doc-only, potential duplicates
4. **`data/prompts`** (4 files) - All unused, orphaned

### Critical Issues Identified
- **P0**: Runtime SSOT fragmentation - code uses `data/prompt_governance` but architecture suggests `agentic_core/prompt_governance`
- **P1**: Cross-root duplication potential between `data/prompt_governance` and `data/prompt_libraries`
- **P2**: Orphaned collections creating maintenance burden

## Rebaseline Strategy

### Phase 1: SSOT Consolidation (P0 Resolution)
**Objective**: Establish `data/prompt_governance` as the definitive runtime SSOT

**Actions**:
1. **Audit Runtime Dependencies**
   - Scan all code references to confirm `data/prompt_governance` as active SSOT
   - Document critical runtime paths (543 references identified)
   - Validate no code dependencies on `agentic_core/prompt_governance/meta_prompts`

2. **Deprecate Meta-Prompts Layer**
   - Mark `agentic_core/prompt_governance/meta_prompts` as deprecated documentation
   - Move the single test-referenced file to appropriate location
   - Add deprecation notices to remaining files

3. **Update Architectural Documentation**
   - Clarify SSOT ownership in prompt modules
   - Update governance documentation to reflect actual usage patterns

### Phase 2: Cross-Root Deduplication (P1 Resolution)
**Objective**: Eliminate potential duplicates between prompt roots

**Actions**:
1. **Hash-Based Duplicate Detection**
   - Compute SHA256 for all files across `data/prompt_governance` and `data/prompt_libraries`
   - Identify exact duplicates by content hash
   - Document near-duplicates for manual review

2. **Consolidation Strategy**
   - For exact duplicates: Keep `data/prompt_governance` version, remove from `data/prompt_libraries`
   - For near-duplicates: Merge improvements into `data/prompt_governance`, deprecate other
   - Update all code references to consolidated location

3. **Reference Cleanup**
   - Update cross-root citations in documentation
   - Fix import paths in code (9 references to `prompt_libraries` identified)
   - Validate all references resolve to consolidated SSOT

### Phase 3: Orphan Cleanup (P2 Resolution)
**Objective**: Remove dead prompt collections to reduce maintenance burden

**Actions**:
1. **Verify Orphan Status**
   - Confirm `data/prompts` (4 files) have zero references
   - Confirm unused `data/prompt_libraries` files (5) have zero references
   - Double-check test coverage doesn't require these files

2. **Safe Removal**
   - Move orphaned files to `archives/deprecated/prompts/` with retention notice
   - Add migration guide for any potential future needs
   - Update documentation to reflect cleaned structure

### Phase 4: Enhanced Modularization Integration
**Objective**: Strengthen the prompt modularization system with current reality

**Actions**:
1. **Update Module Manifest**
   - Add governance documentation modules to `modules.json`
   - Include runtime configuration files from `data/prompt_governance`
   - Expand validation to cover SSOT integrity

2. **Extend Validation Pipeline**
   - Add SSOT consistency checks to `validate_assembly.py`
   - Detect cross-root duplicates automatically
   - Validate all runtime references resolve within SSOT

3. **CI Hardening**
   - Add duplicate detection to GitHub Actions
   - Enforce SSOT boundaries in pre-commit hooks
   - Add orphan detection to prevent future accumulation

## Implementation Waves

### Wave 1: Audit & Documentation (Week 1)
- Complete runtime dependency analysis
- Document current SSOT usage patterns
- Create consolidation roadmap

### Wave 2: SSOT Consolidation (Week 2)
- Deprecate meta-prompts layer
- Resolve cross-root duplicates
- Update all references

### Wave 3: Cleanup & Hardening (Week 3)
- Remove orphaned collections
- Enhance validation pipeline
- Strengthen CI enforcement

### Wave 4: Validation & Sign-off (Week 4)
- End-to-end testing of consolidated system
- Documentation updates
- Release notes and migration guide

## Success Criteria

### Technical Metrics
- **Single SSOT**: All runtime prompts resolve to `data/prompt_governance`
- **Zero Duplicates**: No identical content across multiple roots
- **Zero Orphans**: All retained prompts have runtime or test references
- **CI Passing**: All validation checks pass deterministically

### Governance Metrics
- **Clear Ownership**: Unambiguous architectural authority for prompts
- **Maintainable**: Reduced prompt surface area by 30-40%
- **Traceable**: Complete reference mapping from code to prompt SSOT
- **Enforced**: Automated guards prevent future fragmentation

## Risk Mitigation

### Low Risk
- Orphan removal (no dependencies)
- Documentation updates
- CI enhancements

### Medium Risk
- Cross-root duplicate resolution (potential subtle differences)
- Reference updates (9 locations to fix)
- Meta-prompts deprecation (single test dependency)

### High Risk
- Runtime SSOT clarification (543 references to validate)
- Large-scale file moves (requires careful coordination)

## Rollback Strategy
- All changes tracked with git commits per wave
- Backup of original structure in `archives/`
- Feature flags for gradual migration if needed
- Rollback scripts ready for emergency recovery

## Deliverables

1. **Consolidated Prompt Structure**: Clean SSOT at `data/prompt_governance`
2. **Enhanced Validation**: Extended `validate_assembly.py` with SSOT checks
3. **Updated Documentation**: Reflects new architecture and usage patterns
4. **Migration Guide**: For teams referencing old prompt locations
5. **CI Enhancements**: Automated guards against future fragmentation

This plan establishes a robust, maintainable prompt architecture while preserving all existing functionality and improving system clarity.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

