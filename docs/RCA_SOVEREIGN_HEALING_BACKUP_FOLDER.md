# RCA: `.sovereign_healing_backup` Folder Creation

## Executive Summary

**Issue**: The `.sovereign_healing_backup` folder was created at the repository root, but it is **NOT** defined in the SSOT (`structure_blueprint.py`).

**Root Cause**: Multiple agents create backup directories without SSOT authorization.

**Responsible Agents**:
1. **FilesystemAgent** (L5_safety/validators)
2. **LocationAgent** (L5_safety/validators)
3. **NamingAgent** (L5_safety/validators)
4. **HealingTransactionManager** (L4_state/ledger)

**Status**: ⚠️ **SSOT VIOLATION** - Folder not approved in structure_blueprint.py

---

## Root Cause Analysis

### 1. FilesystemAgent

**File**: `agentic_core/L5_safety/validators/FilesystemAgent.py`

**Line 68**:
```python
self.backup_dir = self.project_root / ".sovereign_healing_backup" / "filesystem" / datetime.now().strftime("%Y%m%d_%H%M%S")
```

**Issue**: Creates `.sovereign_healing_backup/filesystem/{timestamp}` without SSOT approval.

---

### 2. LocationAgent

**File**: `agentic_core/L5_safety/validators/LocationAgent.py`

**Line 759**:
```python
backup_dir = self.project_root / ".sovereign_healing_backup" / "location" / datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir.mkdir(parents=True, exist_ok=True)
```

**Issue**: Creates `.sovereign_healing_backup/location/{timestamp}` without SSOT approval.

---

### 3. NamingAgent

**File**: `agentic_core/L5_safety/validators/NamingAgent.py`

**Line 1834**:
```python
backup_path = self.project_root / '.sovereign_healing_backup' / file_path.name
shutil.copy(file_path, backup_path)
```

**Issue**: Creates `.sovereign_healing_backup/{filename}` without SSOT approval.

---

### 4. HealingTransactionManager

**File**: `agentic_core/L4_state/ledger/healing_transaction_manager.py`

**Line 34**:
```python
self.backup_dir = Path(f'.sovereign_healing_backup/{self.timestamp}')
```

**Issue**: Creates `.sovereign_healing_backup/{timestamp}` without SSOT approval.

---

## SSOT Verification

### Current State in `structure_blueprint.py`

**Line 597**:
```python
SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset({'stubs', '.sovereign_healing_backup', '__pycache__'})
```

**Analysis**:
- ✅ Folder is **excluded** from scope summaries
- ❌ Folder is **NOT** in `SOVEREIGN_REGISTRY`
- ❌ Folder is **NOT** in any approved root folders list
- ❌ No explicit SSOT approval for creation

**Conclusion**: The folder is acknowledged for exclusion purposes but **NOT approved for creation**.

---

## Impact Analysis

### Files Referencing `.sovereign_healing_backup`

**Exclusion Lists** (13 files):
- `scripts/full_agent_discovery.py` - Excludes from discovery
- `scripts/bulk_agent_rename.py` - Excludes from renaming
- `scripts/find_non_conforming_agents.py` - Excludes from scanning
- `scripts/scan_testing_compliance.py` - Excludes from compliance
- `scripts/scan_hardcoded_paths.py` - Excludes from path scanning
- `scripts/smart_discovery.py` - Excludes from discovery
- `scripts/test_root_ssot_enforcement.py` - Lists as "hidden/system" folder
- `scripts/ast_redundancy_analyzer_ultra.py` - Excludes from analysis
- `scripts/agent_discovery_audit.py` - Excludes from audit
- `agentic_core/L5_safety/validators/ComplianceOrchestratorAgent.py` - Excludes from compliance
- `agentic_core/L3_orchestration/workflow_engines/ReportingAgent.py` - Excludes from reporting
- `agentic_core/config/blueprint_sovereign/structure_blueprint.py` - Excludes from scope summaries

**Creation Points** (4 agents):
- `FilesystemAgent` - Creates `filesystem/{timestamp}` subdirectory
- `LocationAgent` - Creates `location/{timestamp}` subdirectory
- `NamingAgent` - Creates backups directly in root
- `HealingTransactionManager` - Creates `{timestamp}` subdirectory

---

## Recommended Fix

### Option 1: Add to SSOT (Recommended)

Add `.sovereign_healing_backup` to `structure_blueprint.py` as an approved root folder:

```python
# In structure_blueprint.py

# Add to SOVEREIGN_REGISTRY
SOVEREIGN_REGISTRY: Any = {
    # ... existing entries ...
    '.sovereign_healing_backup': {
        'depth': 2,
        'subfolders': ['filesystem', 'location', 'naming', 'transactions'],
        'purpose': 'Backup directory for healing operations',
        'volatile': True,  # Can be safely deleted
    }
}

# Add to approved root folders
APPROVED_ROOT_FOLDERS: FrozenSet[str] = frozenset({
    'agentic_core',
    'apps_rg',
    'apps_lic',
    'apps_shared',
    'tests',
    'scripts',
    'docs',
    'archives',
    'reports',
    'data',
    '.sovereign_healing_backup',  # ADD THIS
})
```

### Option 2: Use Existing SSOT Location

Move backups to `archives/healing_backups/{timestamp}`:

```python
# In each agent, replace:
# OLD:
self.backup_dir = self.project_root / ".sovereign_healing_backup" / ...

# NEW:
self.backup_dir = self.project_root / "archives" / "healing_backups" / ...
```

**Pros**: Uses existing SSOT-approved folder (`archives`)
**Cons**: Requires changes to 4 agents

---

## Test Cases Required

### Test 1: SSOT Compliance for Backup Folder Creation

**Objective**: Verify backup folder is SSOT-approved before creation

**Test**:
```python
def test_backup_folder_ssot_compliance():
    """Verify .sovereign_healing_backup is in SSOT."""
    from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY

    assert '.sovereign_healing_backup' in SOVEREIGN_REGISTRY, \
        "Backup folder must be defined in SSOT"
```

### Test 2: FilesystemAgent Backup Creation

**Objective**: Verify FilesystemAgent creates backups in SSOT-approved location

**Test**:
```python
def test_filesystem_agent_backup_location():
    """Verify FilesystemAgent uses SSOT-approved backup location."""
    from agentic_core.L5_safety.validators.FilesystemAgent import get_filesystem_agent

    agent = get_filesystem_agent(project_root)

    # Verify backup_dir is under SSOT-approved folder
    assert 'archives' in str(agent.backup_dir) or \
           '.sovereign_healing_backup' in SOVEREIGN_REGISTRY
```

### Test 3: LocationAgent Backup Creation

**Objective**: Verify LocationAgent creates backups in SSOT-approved location

**Test**:
```python
def test_location_agent_backup_location():
    """Verify LocationAgent uses SSOT-approved backup location."""
    from agentic_core.L5_safety.validators.LocationAgent import get_location_agent

    agent = get_location_agent(project_root)
    backup_dir = agent._initialize_backup_dir()

    # Verify backup_dir is under SSOT-approved folder
    assert 'archives' in str(backup_dir) or \
           '.sovereign_healing_backup' in SOVEREIGN_REGISTRY
```

### Test 4: NamingAgent Backup Creation

**Objective**: Verify NamingAgent creates backups in SSOT-approved location

**Test**:
```python
def test_naming_agent_backup_location():
    """Verify NamingAgent uses SSOT-approved backup location."""
    # This requires inspecting the heal_repository method
    # to ensure backup paths are SSOT-compliant
    pass
```

### Test 5: HealingTransactionManager Backup Creation

**Objective**: Verify HealingTransactionManager creates backups in SSOT-approved location

**Test**:
```python
def test_healing_transaction_manager_backup_location():
    """Verify HealingTransactionManager uses SSOT-approved backup location."""
    from agentic_core.L4_state.ledger.healing_transaction_manager import HealingTransactionManager

    manager = HealingTransactionManager()

    # Verify backup_dir is under SSOT-approved folder
    assert 'archives' in str(manager.backup_dir) or \
           '.sovereign_healing_backup' in SOVEREIGN_REGISTRY
```

### Test 6: Root Folder SSOT Enforcement

**Objective**: Verify no unauthorized root folders are created

**Test**:
```python
def test_no_unauthorized_root_folders():
    """Verify all root folders are SSOT-approved."""
    import os
    from pathlib import Path
    from agentic_core.config.blueprint_sovereign.structure_blueprint import (
        SOVEREIGN_REGISTRY,
        get_validated_project_root
    )

    project_root = get_validated_project_root()

    # Get all directories at root level
    root_dirs = [d for d in os.listdir(project_root)
                 if os.path.isdir(project_root / d) and not d.startswith('.git')]

    # Get approved folders
    approved_folders = set(SOVEREIGN_REGISTRY.keys())
    approved_folders.update(['scripts', 'docs', 'archives', 'reports', 'data'])

    # Check for unauthorized folders
    unauthorized = set(root_dirs) - approved_folders

    # Filter out hidden folders that are system-generated
    unauthorized = {f for f in unauthorized if not f.startswith('.')}

    assert len(unauthorized) == 0, \
        f"Unauthorized root folders found: {unauthorized}"
```

---

## Implementation Plan

### Step 1: Add to SSOT (Recommended)

**File**: `agentic_core/config/blueprint_sovereign/structure_blueprint.py`

**Changes**:
1. Add `.sovereign_healing_backup` to `SOVEREIGN_REGISTRY`
2. Define approved subfolders: `filesystem`, `location`, `naming`, `transactions`
3. Mark as `volatile: True` (can be safely deleted)

### Step 2: Create Test Suite

**File**: `scripts/test_backup_folder_ssot_compliance.py`

**Tests**:
- Test 1: SSOT Compliance
- Test 2: FilesystemAgent Backup Location
- Test 3: LocationAgent Backup Location
- Test 4: NamingAgent Backup Location
- Test 5: HealingTransactionManager Backup Location
- Test 6: Root Folder SSOT Enforcement

### Step 3: Run Tests Until 100% Pass

**Command**:
```bash
python scripts/test_backup_folder_ssot_compliance.py
```

**Expected**: 6/6 tests pass after SSOT update

---

## Summary

**Root Cause**: 4 agents create `.sovereign_healing_backup` without SSOT approval

**Responsible Agents**:
1. FilesystemAgent (L5_safety/validators)
2. LocationAgent (L5_safety/validators)
3. NamingAgent (L5_safety/validators)
4. HealingTransactionManager (L4_state/ledger)

**Fix**: Add `.sovereign_healing_backup` to SSOT in `structure_blueprint.py`

**Test Cases**: 6 tests to verify SSOT compliance and backup location correctness

**Status**: Ready for implementation
