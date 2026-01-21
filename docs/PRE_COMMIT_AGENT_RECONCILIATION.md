# Pre-Commit and Agent Responsibility Reconciliation

**Date:** January 21, 2026  
**Purpose:** Ensure pre-commit hooks and agent responsibilities do not overlap

---

## Executive Summary

This document identifies overlaps between `.pre-commit-config.yaml` hooks and agent capabilities, and provides recommendations to eliminate redundancy while maintaining safety.

---

## Overlap Analysis

### 1. **Duplicate Filename Detection**

#### Pre-Commit Hook
```yaml
- id: check-agent-duplicates
  name: Check for Agent Duplicate Filenames
  entry: python
  args: [scripts/maintenance/check_duplicate_filenames.py]
```

#### Agent Responsibilities
- **CodeDeduplicationAgent** (`agentic_core/L5_safety/validators/CodeDeduplicationAgent.py`)
  - Method: `scan_filename_duplicates()`
  - Detects duplicate basenames with safety check (identical vs divergent content)
  - Lines 431-482

- **NamingAgent** (via LocationAgent)
  - Method: `scan_repository_duplicates()`
  - Called by LocationAgent for post-healing validation
  - Lines 724-726 in LocationAgent.py

- **HierarchyAgent**
  - Uses `ALLOWED_DUPLICATE_FILENAMES` from structure_blueprint
  - Skips allowed duplicates like `__init__.py`
  - Lines 426, 504

#### **OVERLAP SEVERITY: HIGH**

**Recommendation:** **REMOVE** pre-commit hook `check-agent-duplicates`

**Rationale:**
1. CodeDeduplicationAgent provides more sophisticated duplicate detection (content hash comparison)
2. NamingAgent already runs duplicate scans during healing workflows
3. Pre-commit hook is redundant and adds commit latency
4. Agents have access to `ALLOWED_DUPLICATE_FILENAMES` SSOT, pre-commit script may not

**Action:** Delete lines 72-78 from `.pre-commit-config.yaml`

---

### 2. **Deprecated Import Detection**

#### Pre-Commit Hook
```yaml
- id: check-deprecated-imports
  name: Check for Deprecated Agent Imports
  entry: pytest
  args: [tests/infrastructure/test_agent_consolidation_hardening.py::TestConsolidationStaticAnalysis, -v, --tb=short]
```

#### Agent Responsibilities
- **CanonDependencySentinelAgent** (`agentic_core/L5_safety/validators/CanonDependencySentinelAgent.py`)
  - Method: `check_no_duplicate_imports()`
  - Detects duplicate import statements within files
  - Lines 543-546

#### **OVERLAP SEVERITY: MEDIUM**

**Recommendation:** **KEEP** pre-commit hook (different scope)

**Rationale:**
1. Pre-commit hook checks for *deprecated* imports (removed/consolidated agents)
2. CanonDependencySentinelAgent checks for *duplicate* imports (same import twice)
3. Different concerns - no actual overlap
4. Pre-commit provides fast feedback before commit

**Action:** No change needed

---

### 3. **SSOT Folder Structure Validation**

#### Pre-Commit Hook
```yaml
- id: ssot-folder-structure
  name: SSOT Folder Structure
  entry: python -m agentic_core.L5_safety.validators.ssot_folder_check
```

#### Agent Responsibilities
- **ArchitectureGovernorAgent** (`agentic_core/L5_safety/validators/ArchitectureGovernorAgent.py`)
  - Method: `validate_layer_boundaries()`
  - Validates files respect L0-L6 layer boundaries
  - Uses CognitiveDispositionAgent for intelligent triage

- **HierarchyAgent** (`agentic_core/L5_safety/validators/HierarchyAgent.py`)
  - Method: `heal_repository()`
  - Validates sovereign territory structure
  - Enforces depth rules (depth-2 for apps, depth-3 for core)

- **SSOTFolderCleanupAgent** (`agentic_core/L5_safety/unified/SSOTFolderCleanupAgent.py`)
  - Method: `is_path_ssot_approved()`
  - Identifies files in non-approved folders
  - Moves files to SSOT-approved locations

#### **OVERLAP SEVERITY: HIGH**

**Recommendation:** **REMOVE** pre-commit hook `ssot-folder-structure`

**Rationale:**
1. Three agents already enforce SSOT folder structure
2. ArchitectureGovernorAgent + CognitiveDispositionAgent provide intelligent triage
3. SSOTFolderCleanupAgent can automatically fix violations
4. Pre-commit hook is redundant and blocks commits unnecessarily
5. Agents run as part of CI/CD and healing workflows

**Action:** Delete lines 122-128 from `.pre-commit-config.yaml`

---

### 4. **Heal Schema Compliance**

#### Pre-Commit Hook
```yaml
- id: check-heal-schema-compliance
  name: Check @standard_heal Schema Compliance
  entry: python
  args: [scripts/maintenance/check_heal_schema_compliance.py, --strict]
```

#### Agent Responsibilities
- **None** - This is enforced by decorator at runtime

#### **OVERLAP SEVERITY: NONE**

**Recommendation:** **KEEP** pre-commit hook

**Rationale:**
1. Static analysis catches schema violations before runtime
2. No agent performs this check
3. Provides fast feedback during development

**Action:** No change needed

---

### 5. **Protected Files Check**

#### Pre-Commit Hook
```yaml
- id: check-protected-files
  name: Gatekeeper Protection (Block ArchivalGatekeeper.py changes)
  entry: python
  args: [scripts/maintenance/check_protected_files.py]
```

#### Agent Responsibilities
- **ArchivalGatekeeper** (`agentic_core/L5_safety/core/ArchivalGatekeeper.py`)
  - Self-protection mechanism
  - But cannot prevent its own modification

#### **OVERLAP SEVERITY: NONE**

**Recommendation:** **KEEP** pre-commit hook

**Rationale:**
1. Gatekeeper cannot protect itself from modification
2. Pre-commit provides external protection layer
3. Critical security control

**Action:** No change needed

---

### 6. **Secret Detection**

#### Pre-Commit Hook
```yaml
- id: detect-secrets
  name: Detect Secrets (Prevent API keys in audit logs)
  args: ['--baseline', '.secrets.baseline']
```

#### Agent Responsibilities
- **PIISanitizer** (`agentic_core/L4_state/memory/SemanticCacheManager.py`)
  - Redacts PII including API keys from memory/logs
  - Lines 37-167

#### **OVERLAP SEVERITY: LOW**

**Recommendation:** **KEEP** both (defense in depth)

**Rationale:**
1. Pre-commit prevents secrets from entering repo
2. PIISanitizer prevents secrets from entering memory/logs
3. Different layers of defense - complementary, not overlapping

**Action:** No change needed

---

## Summary of Changes

| Hook ID | Action | Reason |
|---------|--------|--------|
| `check-agent-duplicates` | **REMOVE** | Redundant with CodeDeduplicationAgent |
| `check-deprecated-imports` | **KEEP** | Different scope (deprecated vs duplicate) |
| `check-heal-schema-compliance` | **KEEP** | No agent equivalent |
| `check-protected-files` | **KEEP** | External protection layer |
| `gatekeeper-security-lock` | **KEEP** | Security critical |
| `test-hygiene-consolidation` | **KEEP** | Test-specific validation |
| `ssot-folder-structure` | **REMOVE** | Redundant with 3 agents |
| `sovereign-lockdown-verification` | **KEEP** | Phase 7 security |
| `detect-secrets` | **KEEP** | Defense in depth |

---

## Agent Responsibility Matrix

| Responsibility | Agent(s) | Pre-Commit Hook | Recommendation |
|----------------|----------|-----------------|----------------|
| Duplicate filenames | CodeDeduplicationAgent, NamingAgent | ✅ `check-agent-duplicates` | Remove hook |
| SSOT folder structure | ArchitectureGovernorAgent, HierarchyAgent, SSOTFolderCleanupAgent | ✅ `ssot-folder-structure` | Remove hook |
| Deprecated imports | N/A | ✅ `check-deprecated-imports` | Keep hook |
| Heal schema | Decorator (runtime) | ✅ `check-heal-schema-compliance` | Keep hook |
| Protected files | N/A | ✅ `check-protected-files` | Keep hook |
| Secret detection | PIISanitizer (runtime) | ✅ `detect-secrets` | Keep both |

---

## Implementation Plan

1. **Remove `check-agent-duplicates` hook**
   - Agents: CodeDeduplicationAgent, NamingAgent
   - Trigger: Run during `heal_repository()` workflows
   - CI: Add explicit CodeDeduplicationAgent run to CI pipeline

2. **Remove `ssot-folder-structure` hook**
   - Agents: ArchitectureGovernorAgent, HierarchyAgent, SSOTFolderCleanupAgent
   - Trigger: Run during validation and healing workflows
   - CI: Add explicit ArchitectureGovernorAgent validation to CI pipeline

3. **Update CI pipeline**
   - Add: `python -m agentic_core.L5_safety.validators.CodeDeduplicationAgent`
   - Add: `python -m agentic_core.L5_safety.validators.ArchitectureGovernorAgent --validate`

---

## Verification

After removing hooks, verify:

1. **Duplicate detection still works:**
   ```bash
   python -c "from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent; agent = CodeDeduplicationAgent(); agent.scan_filename_duplicates(...)"
   ```

2. **SSOT validation still works:**
   ```bash
   python -c "from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent; agent = ArchitectureGovernorAgent(); agent.validate_layer_boundaries(...)"
   ```

3. **CI pipeline includes agent checks:**
   - Check `.github/workflows/` or CI config
   - Ensure agents run on every PR

---

## Conclusion

**Overlaps Identified:** 2 (duplicate filenames, SSOT folder structure)  
**Hooks to Remove:** 2  
**Hooks to Keep:** 7  
**Result:** Reduced commit latency, eliminated redundancy, maintained safety
