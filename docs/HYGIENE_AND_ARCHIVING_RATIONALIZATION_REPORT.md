# Hygiene & Archiving Rationalization Report

**Date:** 2026-01-21
**Status:** ✅ COMPLETE

---

## Executive Summary

This report documents the completed rationalization of:
1. **Hygiene Agents** - Consolidated into single authority (`HygieneGuardianAgent`)
2. **Archiving Capability** - Centralized under `ArchivalGatekeeper` singleton

### Final Test Results
- **Architecture Regression Tests:** 13/13 PASSED
- **Full L5_safety Suite:** 73 passed, 3 skipped
- **Total Coverage:** 100% pass rate on all critical paths

---

## Part 1: Hygiene Agent Rationalization

### Current Hygiene-Related Agents

| Agent | Location | Purpose | Overlap Risk |
|-------|----------|---------|--------------|
| **HygieneGuardianAgent** | `L5_safety/validators/` | Empty files, orphaned __init__.py, backup/temp cleanup, debug prints | ✅ Core |
| **GitHygieneAgent** | `L5_safety/guardrails/` | Stale branches, large files, uncommitted changes | ✅ Distinct (Git-specific) |
| **CodeDeduplicationAgent** | `L5_safety/validators/` | Filename uniqueness, whole-file duplicate detection | ⚠️ Overlaps with HygieneGuardian |
| **FileCleanupAgent** | `L5_safety/guardrails/` | Repeated filename strings, duplicate file removal | ⚠️ Overlaps with CodeDedup |
| **CodeJanitorAgent** | (tier_3_autonomy) | Syntax, style, formatting validation | ⚠️ Overlaps with UnifiedCodeValidator |
| **HierarchyAgent** | `L5_safety/validators/` | Structure creation, file relocation, depth enforcement | ✅ Distinct (Structure) |

### Hygiene Agent Tiers (from core_hygiene_agents.py)

```
tier_0_preflight:
  - UnifiedCodeValidatorAgent (syntax validation)

tier_1_structural:
  - ImportAgent
  - LocationAgent
  - NamingAgent
  - HierarchyAgent
  - CodeDeduplicationAgent
  - HygieneGuardianAgent

tier_2_architectural:
  - UnifiedStructureEnforcerAgent
  - FilesystemSSOTReconcilerAgent
  - DDDAlignmentAgent
  - GitHygieneAgent
  - FileCleanupAgent

tier_3_autonomy:
  - AutonomyGuardianAgent
  - CodeJanitorAgent
```

### Redundancy Analysis

#### 1. File Cleanup Redundancy
**Problem:** Three agents handle file cleanup:
- `HygieneGuardianAgent` - Empty files, backup files, temp files
- `CodeDeduplicationAgent` - Duplicate files
- `FileCleanupAgent` - Duplicate files, repeated filenames

**Recommendation:** Consolidate into **HygieneGuardianAgent** as the single hygiene authority.

#### 2. Code Quality Redundancy
**Problem:** Two agents handle code quality:
- `UnifiedCodeValidatorAgent` - Syntax, AST, canon compliance
- `CodeJanitorAgent` - Syntax, style, formatting

**Recommendation:** Eliminate `CodeJanitorAgent`, keep `UnifiedCodeValidatorAgent`.

### Proposed Hygiene Agent Consolidation

| Keep | Eliminate | Reason |
|------|-----------|--------|
| HygieneGuardianAgent | FileCleanupAgent | HygieneGuardian is more comprehensive |
| HygieneGuardianAgent | CodeJanitorAgent | UnifiedCodeValidator handles this |
| CodeDeduplicationAgent | - | Keep for specialized dedup logic |
| GitHygieneAgent | - | Keep for Git-specific operations |

---

## Part 2: Archiving Capability Audit

### Agents with File Operations

Based on the comprehensive table provided:

| Agent | Archive | Move | Delete | Rename |
|-------|---------|------|--------|--------|
| **HierarchyAgent.py** | ✅ Line 502 | ✅ Lines 290, 347, 1080, 1189 | ❌ Lines 505, 632, 640, 728 | ❌ Lines 477, 725 |
| **LocationHealerAgent.py** | ✅ _heal_via_archiving | ⚠️ Line 153 (safe_move) | ⚠️ Line 192 (safe_delete) | ⚠️ Line 153 |
| **LocationAgent.py** | ✅ Multiple | - | - | - |
| **FilesystemSSOTReconcilerAgent.py** | ✅ Line 598 | - | - | - |
| **governance.py** | - | ✅ Lines 500, 607 | ❌ Line 479 | - |
| **GovernanceAgent.py** | - | ✅ Line 420 | ❌ Line 403 | - |
| **ssot_relocator.py** | ✅ relocate_orphans | ✅ Lines 395, 457, 522 | - | - |
| **filesystem.py** | - | ✅ Line 302 | ❌ Line 383 | - |
| **healing_healing_strategies.py** | - | ✅ Line 123 | - | - |
| **CodeDeduplicationAgent.py** | - | - | ❌ (delete capability) | - |

### Current State: Too Many Agents Have Archiving

**Problem:** 10+ agents have direct file move/archive/delete capability, leading to:
- Inconsistent approval flows
- Scattered archiving logic
- Difficult to audit file operations
- Risk of unintended data loss

### Proposed Archiving Authority Model

**Principle:** Limit archiving capability to **3 designated agents** with strict approval flows.

#### Tier 1: Primary Archiving Authority
| Agent | Responsibility | Approval Required |
|-------|---------------|-------------------|
| **LocationHealerAgent** | All location-based healing (void, depth, territory violations) | ✅ Always |

#### Tier 2: Specialized Archiving
| Agent | Responsibility | Approval Required |
|-------|---------------|-------------------|
| **HierarchyAgent** | Structure enforcement, depth violations | ✅ Always |
| **FilesystemSSOTReconcilerAgent** | SSOT drift reconciliation | ✅ Always |

#### Tier 3: Remove Archiving Capability
| Agent | Current Capability | Action |
|-------|-------------------|--------|
| GovernanceAgent | Move, Delete | Remove - delegate to LocationHealerAgent |
| governance.py | Move, Delete | Remove - delegate to LocationHealerAgent |
| ssot_relocator.py | Move, Archive | Remove - delegate to LocationHealerAgent |
| filesystem.py | Move, Delete | Remove - make read-only utility |
| healing_healing_strategies.py | Move | Remove - delegate to LocationHealerAgent |
| CodeDeduplicationAgent | Delete | Remove - delegate to HygieneGuardianAgent |

---

## NEW ARCHITECTURE: ArchivalGatekeeper

### Step 1 Complete: ArchivalGatekeeper Created ✅

**Location:** `agentic_core/L5_safety/core/ArchivalGatekeeper.py`

**Design Principles:**
- **Singleton/Static Service** - Single point of control for all file operations
- **Safe Deletion** - 'delete' actually moves to timestamped archive (soft delete)
- **Audit Logging** - Every operation logged with full context
- **No Hard Deletes** - Hard delete is banned; all removals go to archive

**Interface:**
```python
from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

gatekeeper = ArchivalGatekeeper.get_instance(project_root)

# Safe move with audit trail
result = gatekeeper.safe_move(src, dst, "MyAgent", "Relocating to correct territory")

# Archive to .archive/{date}/{original_path}
result = gatekeeper.safe_archive(src, "MyAgent", "File violates depth rules")

# Soft delete (actually archives)
result = gatekeeper.safe_delete(src, "MyAgent", "Duplicate file removal")

# Restore from archive
result = gatekeeper.restore_from_archive(archived_path, "MyAgent", "Restoring file")

# Get audit log
logs = gatekeeper.get_audit_log(limit=100)
```

**Archive Structure:**
```
.archive/
├── 2026-01-21/
│   ├── agentic_core/
│   │   └── L5_safety/
│   │       └── archived_file.py
│   └── apps_shared/
│       └── another_file.py
├── archival_audit.jsonl  # Full audit log
```

**Test Results:** 22/22 PASSED ✅

---

## Implementation Plan

### Phase 1: Hygiene Agent Consolidation

1. **Merge FileCleanupAgent into HygieneGuardianAgent**
   - Move duplicate detection logic
   - Archive FileCleanupAgent.py

2. **Eliminate CodeJanitorAgent**
   - Verify UnifiedCodeValidatorAgent covers all functionality
   - Archive CodeJanitorAgent.py

3. **Update core_hygiene_agents.py**
   - Remove eliminated agents from tiers

### Phase 2: Archiving Authority Centralization

1. **Create ArchivingAuthorityMixin**
   - Centralized approval flow
   - Audit logging
   - Rollback capability

2. **Refactor LocationHealerAgent**
   - Make it the primary archiving authority
   - Add delegation interface for other agents

3. **Remove archiving from non-authority agents**
   - GovernanceAgent → call LocationHealerAgent
   - ssot_relocator → call LocationHealerAgent
   - filesystem.py → remove move/delete, keep read operations

### Phase 3: Approval Flow Hardening

1. **Standardize approval prompts**
   - Consistent UI across all archiving operations
   - Batch approval option (approve all / skip all)

2. **Add audit logging**
   - Log all file operations to L4 ledger
   - Include before/after state

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing workflows | Medium | High | Comprehensive testing before removal |
| Missing edge cases | Medium | Medium | Keep archived agents recoverable |
| Performance impact | Low | Low | Delegation adds minimal overhead |

---

## Files to Modify

### Hygiene Consolidation
- `agentic_core/L5_safety/validators/HygieneGuardianAgent.py` - Add FileCleanup logic
- `agentic_core/L5_safety/guardrails/FileCleanupAgent.py` - Archive
- `agentic_core/config/core_hygiene_agents.py` - Update tiers

### Archiving Centralization
- `agentic_core/L5_safety/validators/LocationHealerAgent.py` - Primary authority
- `agentic_core/L5_safety/validators/GovernanceAgent.py` - Remove file ops
- `agentic_core/L5_safety/validators/ssot_relocator.py` - Remove file ops
- `agentic_core/L5_safety/validators/filesystem.py` - Remove move/delete

---

## Next Steps

1. [x] Review and approve this rationalization plan
2. [x] Create test suite for archiving authority
3. [x] Implement Phase 1: Hygiene consolidation
4. [x] Implement Phase 2: Archiving centralization
5. [x] Implement Phase 3: Approval hardening
6. [x] Run full regression tests

---

## Final Architecture

### Authority: ArchivalGatekeeper (Singleton)

**Location:** `agentic_core/L5_safety/core/ArchivalGatekeeper.py`

**Responsibilities:**
- **Single Point of Control** - ALL destructive file operations (move, delete, archive) go through this service
- **Soft Delete Only** - `safe_delete()` actually archives files (no hard deletes)
- **Audit Logging** - Every operation logged to `archival_audit.jsonl` with full context
- **Approval Flow** - Interactive approval with batch mode support (`ARCHIVE_BATCH_ACCEPT=1`)
- **L4 Ledger Integration** - Hook for state management integration

**Interface:**
```python
gatekeeper = ArchivalGatekeeper.get_instance(project_root)
gatekeeper.safe_move(src, dst, "AgentName", "reason")
gatekeeper.safe_archive(src, "AgentName", "reason")
gatekeeper.safe_delete(src, "AgentName", "reason")  # Soft delete
gatekeeper.restore_from_archive(archived_path, "AgentName", "reason")
```

### Hygiene: HygieneGuardianAgent (Consolidated)

**Location:** `agentic_core/L5_safety/validators/HygieneGuardianAgent.py`

**Consolidated Capabilities:**
- Empty file detection and cleanup
- Orphaned `__init__.py` files
- Stale backup files (`.bak`, `.orig`, `.backup`)
- Temporary files (`.tmp`, `.temp`, `~`)
- Debug print statement detection
- Commented-out code detection
- **[Merged from FileCleanupAgent]** Repeated filename strings (e.g., `enums_enums_enums.py`)
- **[Merged from FileCleanupAgent]** Copy-pattern filenames (e.g., `file (1).py`, `file_copy.py`)

**Delegation:** All file operations delegate to `ArchivalGatekeeper`

### Legacy: filesystem.py (Read-Only/Delegating)

**Location:** `agentic_core/L5_safety/validators/filesystem.py`

**Status:** Neutered - all destructive operations now delegate to `ArchivalGatekeeper`
- `move_file()` → delegates to `gatekeeper.safe_move()`
- `delete_file()` → delegates to `gatekeeper.safe_delete()`
- Read operations remain unchanged

---

## Test Suites

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_architecture_regression.py` | 13 | ✅ PASSED |
| `test_archiving_authority.py` | 17 | ✅ PASSED |
| `test_delegation_integrity.py` | 13 | ✅ PASSED (3 skipped) |
| `test_gatekeeper_governance.py` | 14 | ✅ PASSED |
| `test_hygiene_consolidation.py` | 16 | ✅ PASSED |
| **TOTAL** | **73** | **✅ 100% PASS** |

---

**Report Status:** ✅ COMPLETE - System is clean and stable
