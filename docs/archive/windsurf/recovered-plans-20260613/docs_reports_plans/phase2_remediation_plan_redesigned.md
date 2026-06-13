# Phase 2 Remediation Plan - Deterministic Structural Realignment

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

Phase 2 addresses 21 systemic naming violations through deterministic structural realignment based on role semantics, not heuristic-driven mass renaming.

## Governance-Compliant Approach

### Core Principles
- **Explicit enumeration**: Each file individually justified
- **Deterministic mapping**: Pre-computed rename table
- **No active agent mutation**: Manual controlled renames
- **Import dependency analysis**: rg-based mapping before mutation
- **Structural proof**: Classification justification per file

## Wave 1 - Static Rename Map Construction (NO MUTATION)

### Step 1.1: File Classification Analysis

For each MISNAMED_UTILITY file, provide:
- Current filename
- Proposed filename
- Classification justification (AST analysis)
- Import reference count (rg output)
- Structural role proof

### Step 1.2: Import Dependency Mapping

Use `rg` to map all import dependencies:
```bash
rg "from.*config_loader_config|import.*config_loader_config" --type py
```

### Step 1.3: Evidence File Generation

Create deterministic mapping table in evidence file before any mutations.

## Wave 2 - Controlled Rename + Import Update

### Step 2.1: Explicit File Renames

Apply renames individually with explicit commands:
```bash
mv apps_shared/config/config_loader_config.py apps_shared/config/config_loader_util.py
```

### Step 2.2: Deterministic Import Updates

Update imports using `rg` + sed:
```bash
rg -l "config_loader_config" --type py | xargs sed -i 's/config_loader_config/config_loader_util/g'
```

### Step 2.3: Diff Summary Generation

Capture all changes for audit trail.

## Wave 3 - Reclassification Validation

### Step 3.1: Post-Mutation Analysis

Re-run FileClassificationAgent in validate_only mode:
```bash
python -c "from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent; agent=FileClassificationAgent(project_root=Path('apps_shared'), dry_run=True, validate_only=True); result=agent.run()"
```

### Step 3.2: Before/After Delta

Document violation count changes:
- MISNAMED_UTILITY: 21 → 0 (target)
- PASSIVE_AGENT_NAMING: 1 → 0 (target)
- DUAL-TAG: Monitor only (folder context resolution)

## Detailed File Analysis

### apps_shared - MISNAMED_UTILITY Files

Each file requires individual structural proof:

1. **config_loader_config.py**
   - Contains: `ConfigLoader` class with active methods
   - Methods: `load_config`, `_find_config_file`, `_load_from_file`
   - Justification: Active logic = UTILITY, not CONFIG
   - Import count: TBD

2. **environment_config.py**
   - Contains: `EnvironmentValidator` class with active methods
   - Methods: `validate`, `_format_error_message`, `get_config`
   - Justification: Active validation logic = UTILITY
   - Import count: TBD

[Continue for all 17 files...]

### DUAL-TAG Resolution - Correct Hierarchy

Apply proper classification priority:
1. Explicit decorator metadata
2. Inheritance tree
3. Filename suffix
4. Directory territory
5. Heuristic fallback

**Examples**:
- `checkpoint_manager_types.py`: Analyze inheritance first
- `execution_orchestrator_types.py`: Check for decorator metadata
- Do not assume folder context precedence

## Required Evidence Artifacts

### Evidence File Structure
```markdown
## Phase 2 Evidence - Deterministic Realignment

### Rename Mapping Table
| Current File | Proposed File | Justification | Import Count | Status |
|--------------|---------------|---------------|--------------|---------|

### Import Dependency Analysis
[rg outputs for each file]

### Before/After Classification
[FileClassificationAgent outputs]

### Diff Summary
[git diff --stat output]

### Test Results
[pytest outputs]
```

## Risk Mitigation

### Import Impact Validation
- Map all dependencies before rename
- Test critical paths after each rename
- Rollback capability for each file

### Structural Integrity
- Preserve all existing functionality
- No semantic drift in classification
- Maintain agent discovery compatibility

## Success Criteria

### Quantitative
- MISNAMED_UTILITY violations: 21 → 0
- PASSIVE_AGENT_NAMING violations: 1 → 0
- Zero broken imports
- All tests pass

### Qualitative
- Deterministic execution
- Full audit trail
- No heuristic dependencies
- Structural alignment maintained

## Implementation Constraints

### Forbidden Approaches
- ❌ FileClassificationAgent active mode
- ❌ Bulk heuristic renaming
- ❌ Folder-first classification
- ❌ Time estimates in plan

### Required Approaches
- ✅ Explicit file enumeration
- ✅ rg-based import analysis
- ✅ Manual controlled mutations
- ✅ Structural justification per file

---
**Phase 2 Status**: REDESIGNED FOR GOVERNANCE COMPLIANCE
**Ready for Deterministic Execution**

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

