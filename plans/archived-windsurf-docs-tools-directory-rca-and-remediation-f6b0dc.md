---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\tools-directory-rca-and-remediation-f6b0dc.md'
original_relative_path: 'tools-directory-rca-and-remediation-f6b0dc.md'
source_sha256: b82976b81c65ded9b235443cb6139ae7346427b4fb5aab00385f66cfe633b40b
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Tools Directory RCA and Remediation Plan

The `tools/` directory violates SSOT governance by housing utility files that should be aligned to canonical agentic core or apps_* folders. This creates architectural drift and bypasses the established structure_blueprint enforcement.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## RCA Findings

### 1. **SSOT Violation - tools/ Not in SCAN_ROOTS**
- `tools/` directory contains 6 utility files across 3 subdirectories
- NOT listed in `structure_blueprint._verify.py` SCAN_ROOTS tuple
- Creates governance blind spot since structural verification doesn't scan tools/

### 2. **Content Analysis - Guard/Utility Files**
```
tools/architectural/module_collision_guard.py (402 lines)
tools/governance/artifacts_guard.py (145 lines)
tools/governance/cache_guard.py (6487 bytes)
tools/governance/docs_structure_guard.py (4880 bytes)
tools/governance/logs_guard.py (7271 bytes)
tools/security/credential_guard.py (177 lines)
```

### 3. **Functional Classification**
- **Architectural guards**: Module collision detection (should be L5_safety)
- **Governance guards**: Artifacts/cache/docs/logs enforcement (should be L5_safety)
- **Security guards**: Credential scanning (should be L5_safety)

### 4. **Constitutional Rule Violations**
- Rule §1B: "Agent Invocation Lock" - These utilities implement agent-like governance logic
- Rule §2: "SSOT Authority" - Bypasses structure_blueprint as structural SSOT
- Rule §5: "Scan Scope Determinism" - tools/ not in explicit SCAN_ROOTS

## Remediation Plan

### Phase 1: Migration to L5_safety
1. **Move architectural guard**
   - `tools/architectural/module_collision_guard.py` → `agentic_core/L5_safety/enforcement/module_collision_guardrail.py`

2. **Move governance guards**
   - `tools/governance/*.py` → `agentic_core/L5_safety/enforcement/governance/`
   - Rename to maintain naming consistency (remove _guard suffix if redundant)

3. **Move security guard**
   - `tools/security/credential_guard.py` → `agentic_core/L5_safety/enforcement/security/credential_guard.py`

### Phase 2: Update SCAN_ROOTS
4. **Add tools/ to SCAN_ROOTS temporarily** during migration to ensure no files are left behind
5. **Remove tools/ from SCAN_ROOTS** after successful migration
6. **Delete empty tools/ directory structure**

### Phase 3: Import Path Updates
7. **Update all import references** from `tools.*` to `agentic_core.L5_safety.enforcement.*`
8. **Update any CI/CD scripts** that reference tools/ paths
9. **Update documentation** that references tools/ directory

### Phase 4: Validation
10. **Run structure_blueprint verification** to ensure no violations
11. **Run full test suite** to verify import path changes
12. **Update module_collision_guard baseline** to reflect new file locations

## Acceptance Criteria
- [ ] tools/ directory completely removed
- [ ] All utility files migrated to appropriate L5_safety subdirectories
- [ ] All import paths updated and functional
- [ ] structure_blueprint verification passes with 0 errors
- [ ] Full test suite passes
- [ ] No references to tools/ remain in codebase

## Risk Mitigation
- Backup tools/ directory before migration
- Update imports in atomic commits per file
- Run tests after each migration batch
- Maintain backward compatibility during transition if needed

## Implementation Notes
- L5_safety already has enforcement/engines/ structure - these guards fit naturally
- Module collision guard is architectural enforcement → L5_safety/enforcement/
- Governance guards are safety enforcement → L5_safety/enforcement/governance/
- Security guard is credential safety → L5_safety/enforcement/security/

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

