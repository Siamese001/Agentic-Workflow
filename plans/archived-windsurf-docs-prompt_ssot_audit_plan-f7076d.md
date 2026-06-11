---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt_ssot_audit_plan-f7076d.md'
original_relative_path: 'prompt_ssot_audit_plan-f7076d.md'
source_sha256: 3a479d7374e1c520b4e9c61c61b0774cdc0c6109ce98427d1c9b36b320f4afe3
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt SSOT Audit Plan

This plan executes a deterministic audit of prompt governance across agentic_core and data directories to identify SSOT violations, duplicates, and architectural ambiguity.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Execution Phases

### Phase 1: Deterministic Inventory
- Enumerate all files across 4 directories using git ls-files
- Generate SHA256 hashes for exact duplicate detection
- Create normalized hashes (CRLF→LF, whitespace normalization, key sorting for JSON/YAML)
- Classify files by content type using deterministic rules:
  - META_PROMPT: System-level framing instructions about other prompts
  - POLICY/CONTRACT: Constraints/validation schemas
  - TEMPLATE: Placeholders for runtime injection
  - RUNTIME_PROMPT: Fully-formed LLM-executable content
  - LIBRARY_PROMPT: Domain-grouped reusable content
  - TEST_ASSET: Referenced only in tests
  - ORPHAN: Never referenced

### Phase 2: SSOT Conflict Detection
- Cluster exact duplicates by SHA256
- Cluster normalized duplicates
- Fuzzy similarity detection (≥0.80 threshold)
- Name collision detection across directories
- Flag shadow files with semantic overlap

### Phase 3: Code Coupling & Authority Mapping
- Search runtime references using ripgrep
- Classify reference types: import, open, config, string
- Determine authority levels: code-critical, runtime, unused
- Map effective authority hierarchy

### Phase 4: Ambiguity Diagnosis
- Analyze each conflict cluster with citations
- Assess architectural risks (drift, override, testing inconsistency)
- Classify severity (P0/P1/P2)

### Phase 5: SSOT Refactor Plan
- Propose evidence-backed canonical ownership rules
- Create 4-wave migration plan:
  - Wave 0: Compatibility mapping
  - Wave 1: Exact duplicate consolidation
  - Wave 2: Shadow resolution
  - Wave 3: Guardian enforcement
  - Wave 4: Deprecation & cleanup
- Include verification commands and rollback strategies

### Phase 6: Acceptance Gate
- Verify all requirements met
- Generate final SSOT declaration
- Create repro commands

## Key Findings So Far
- Initial scan shows 19 files in agentic_core/prompt_governance/meta_prompts
- 47+ files in data/prompt_governance across multiple subdirectories
- 9 files in data/prompt_libraries
- 5 files in data/prompts
- Evidence of duplicate content: INSTRUCTIONAL_INJECTION_PATTERNS.md exists in both agentic_core and data with different layer focuses
- Multiple Python references to prompt_governance modules found in tests

## Next Steps
Execute comprehensive file analysis with hash generation and content classification to complete the audit report.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

