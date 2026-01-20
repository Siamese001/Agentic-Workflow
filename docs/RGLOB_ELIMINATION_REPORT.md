# RGLOB Elimination Report

**Date:** January 20, 2026  
**Author:** Cascade  
**Status:** Findings & Recommendations (No Execution)

---

## Executive Summary

This report identifies all `rglob` usage in the active codebase and provides a detailed implementation plan to replace them with SSOT-based alternatives. The codebase already has excellent SSOT infrastructure (`ssot_discovery.py`, `file_cache.py`) but adoption is incomplete.

**Key Findings:**
- **93 rglob calls** found in active code (excluding archives)
- **56 files** contain rglob usage
- **3 SSOT modules** already exist for replacement
- **Estimated effort:** 2-3 days for full migration

---

## Current SSOT Infrastructure

The codebase already has three high-performance alternatives to rglob:

### 1. `agentic_core/utils/ssot_discovery.py`
- **Purpose:** Centralized file discovery with built-in exclusions
- **Key Functions:**
  - `get_python_files(project_root)` - All Python files
  - `get_data_files(project_root, extensions)` - JSON, YAML, etc.
  - `get_json_files(project_root)` - JSON files specifically
  - `get_markdown_files(project_root)` - Markdown files
- **Exclusions:** `.sovereign_healing_backup/`, `archives/`, `__pycache__/`, `.git/`

### 2. `agentic_core/utils/file_cache.py`
- **Purpose:** Singleton cache with lazy loading
- **Key Functions:**
  - `FileCache.get_instance(project_root)` - Get singleton
  - `cache.get_python_files()` - Cached Python files
  - `cache.invalidate()` - Clear cache after file changes
- **Performance:** Uses `os.walk` with directory pruning (faster than rglob)

### 3. `agentic_core/utils/scan_guard.py`
- **Purpose:** Audit utility for migration tracking
- **Key Functions:**
  - `guarded_rglob()` - Drop-in replacement that logs warnings
  - `audit_rglob_usage()` - Count rglob calls in project
  - `@deprecate_rglob` - Decorator for marking functions

---

## Findings by Location

### Category 1: Core Agents (HIGH PRIORITY)

| File | rglob Count | Purpose | SSOT Replacement |
|------|-------------|---------|------------------|
| `apps_rg/engines/NamingAgent.py` | 6 | Agent discovery, import updates | `ssot_discovery.get_python_files()` |
| `agentic_core/L5_safety/validators/SemanticTerritoryMapperAgent.py` | 1 | Territory scanning | `ssot_discovery.get_python_files()` |
| `agentic_core/L5_safety/validators/GovernanceAgent.py` | 1 | Compliance scanning | `ssot_discovery.get_python_files()` |
| `agentic_core/L5_safety/validators/DependencyDiplomatAgent.py` | 1 | Dependency analysis | `ssot_discovery.get_python_files()` |
| `agentic_core/L5_safety/validators/ReportingAgent.py` | 1 | File counting | `ssot_discovery.get_python_files()` |
| `agentic_core/L4_state/ValidationContext/UnifiedStateManagementAgent.py` | 1 | State file discovery | `ssot_discovery.get_data_files()` |

### Category 2: Utility Modules (MEDIUM PRIORITY)

| File | rglob Count | Purpose | SSOT Replacement |
|------|-------------|---------|------------------|
| `agentic_core/utils/scan_guard.py` | 6 | Audit utility (intentional) | Keep as-is (audit tool) |
| `agentic_core/utils/ssot_discovery.py` | 2 | Comparison functions | Keep as-is (verification) |
| `agentic_core/utils/file_cache.py` | 1 | Documentation only | Keep as-is (uses os.walk) |
| `agentic_core/utils/core_extensions/airlock_flush.py` | 1 | Backup cleanup | `ssot_discovery.get_python_files()` |
| `agentic_core/utils/core_extensions/bridge_builder.py` | 1 | Import fixing | `ssot_discovery.get_python_files()` |
| `agentic_core/utils/core_extensions/fix_all_tunnels.py` | 1 | Tunnel fixing | `ssot_discovery.get_python_files()` |
| `agentic_core/utils/core_extensions/fix_all_type_imports.py` | 1 | Type import fixing | `ssot_discovery.get_python_files()` |

### Category 3: Scripts (MEDIUM PRIORITY)

| File | rglob Count | Purpose | SSOT Replacement |
|------|-------------|---------|------------------|
| `scripts/full_agent_discovery.py` | 1 | Agent discovery | `ssot_discovery.get_python_files()` |
| `scripts/archive_consolidation_report_agents.py` | 3 | Archive scanning | `ssot_discovery.get_python_files()` |
| `scripts/archive_legacy_orchestrators.py` | 3 | Archive scanning | `ssot_discovery.get_python_files()` |
| `scripts/archive_legacy_validators.py` | 3 | Archive scanning | `ssot_discovery.get_python_files()` |
| `scripts/scan_archives_for_restoration.py` | 3 | Archive scanning | `ssot_discovery.get_python_files()` |
| `scripts/archive_phase3_legacy_agents.py` | 2 | Archive scanning | `ssot_discovery.get_python_files()` |
| `scripts/archive_phase4_legacy_agents.py` | 1 | Archive scanning | `ssot_discovery.get_python_files()` |
| `scripts/restore_all_archived_agents.py` | 2 | Restoration | `ssot_discovery.get_python_files()` |
| `scripts/restore_app_agents.py` | 1 | Restoration | `ssot_discovery.get_python_files()` |
| `scripts/audit_residual_rglob.py` | 2 | Audit (intentional) | Keep as-is (audit tool) |
| `scripts/check_rglob_usage.py` | 2 | Audit (intentional) | Keep as-is (audit tool) |
| `scripts/MalformedAgent.py` | 1 | Malformed file scan | `ssot_discovery.get_python_files()` |
| `scripts/compare_agent_lists.py` | 1 | Comparison | `ssot_discovery.get_python_files()` |
| `scripts/diagnose_syntax.py` | 1 | Syntax checking | `ssot_discovery.get_python_files()` |
| `scripts/paranoid_audit_sleeping_giants.py` | 1 | Audit | `ssot_discovery.get_python_files()` |
| `scripts/phase4_batch1_*.py` (4 files) | 4 | Batch processing | `ssot_discovery.get_python_files()` |
| `scripts/phase4_batch4_*.py` (2 files) | 2 | Batch processing | `ssot_discovery.get_python_files()` |
| `scripts/test_log_analysis_fixes.py` | 2 | Testing | `ssot_discovery.get_python_files()` |
| `scripts/test_healing_agents_ssot_compliance.py` | 1 | Testing | `ssot_discovery.get_python_files()` |
| `scripts/update_*_imports.py` (3 files) | 3 | Import updates | `ssot_discovery.get_python_files()` |
| `scripts/waterfall_reconciliation.py` | 1 | Reconciliation | `ssot_discovery.get_python_files()` |

### Category 4: Tests (LOW PRIORITY)

| File | rglob Count | Purpose | SSOT Replacement |
|------|-------------|---------|------------------|
| `tests/core/architecture/test_depth_healing_smart_realignment.py` | 5 | Test scanning | `ssot_discovery.get_python_files()` |
| `tests/core/architecture/test_location_agent_comprehensive.py` | 4 | Test scanning | `ssot_discovery.get_python_files()` |
| `tests/dashboard/test_javascript.py` | 3 | JS file scanning | Custom (JS files, not Python) |
| `tests/core/architecture/test_genai_migration.py` | 2 | Test scanning | `ssot_discovery.get_python_files()` |
| `tests/core/architecture/test_phase6_*.py` (4 files) | 6 | Test scanning | `ssot_discovery.get_python_files()` |
| `tests/core/architecture/test_phase2_zero_loss.py` | 1 | Test scanning | `ssot_discovery.get_python_files()` |
| `tests/core/performance/test_location_agent_opt.py` | 1 | Performance test | `ssot_discovery.get_python_files()` |
| `tests/test_code_deduplication_non_python.py` | 1 | Non-Python scan | Custom (non-Python files) |
| `tests/test_ssot_backup_folder_compliance.py` | 1 | Backup compliance | `ssot_discovery.get_python_files()` |

### Category 5: Apps (MEDIUM PRIORITY)

| File | rglob Count | Purpose | SSOT Replacement |
|------|-------------|---------|------------------|
| `apps_rg/engines/full_agent_discovery.py` | 2 | Agent discovery | `ssot_discovery.get_python_files()` |
| `apps_rg/engines/void_compliance.py` | 1 | Compliance check | `ssot_discovery.get_python_files()` |

---

## Exceptions (Keep rglob)

The following files should **retain** rglob usage:

1. **`agentic_core/utils/scan_guard.py`** - This IS the audit tool for rglob usage
2. **`agentic_core/utils/ssot_discovery.py`** - Contains `compare_with_rglob()` for verification
3. **`scripts/audit_residual_rglob.py`** - Audit tool
4. **`scripts/check_rglob_usage.py`** - Audit tool
5. **`tests/dashboard/test_javascript.py`** - Scans JS files, not Python (SSOT is Python-focused)
6. **`tests/test_code_deduplication_non_python.py`** - Scans non-Python files

---

## Implementation Plan

### Phase 1: Core Agents (Day 1)

**Priority:** HIGH - These are production agents

#### 1.1 NamingAgent.py (6 rglob calls)

```python
# BEFORE (line 227)
for py_file in agentic_core_dir.rglob("*Agent.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
agent_files = [f for f in get_python_files(self.project_root) 
               if f.name.endswith("Agent.py")]
for py_file in agent_files:
```

```python
# BEFORE (line 828)
all_matching = [p for p in self.project_root.rglob(f"{stem_check}.py") ...]

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
all_py = get_python_files(self.project_root)
all_matching = [p for p in all_py if p.stem == stem_check]
```

```python
# BEFORE (line 897)
files.extend(self.project_root.rglob(f"*{ext}"))

# AFTER
from agentic_core.utils.ssot_discovery import get_data_files
files = get_data_files(self.project_root, extensions=target_extensions)
```

```python
# BEFORE (line 1251)
for py_file in dir_obj.rglob("*.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
py_files = [f for f in get_python_files(self.project_root) 
            if str(f).startswith(str(dir_obj))]
for py_file in py_files:
```

```python
# BEFORE (line 1693)
python_files = list(self.project_root.rglob("*.py"))

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
python_files = get_python_files(self.project_root)
```

```python
# BEFORE (line 1878) - _update_imports_rglob method
for py_file in self.project_root.rglob("*.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
for py_file in get_python_files(self.project_root):
```

#### 1.2 SemanticTerritoryMapperAgent.py (1 rglob call)

```python
# BEFORE (line 198)
for py_file in self.project_root.rglob("*.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
for py_file in get_python_files(self.project_root):
```

#### 1.3 GovernanceAgent.py (1 rglob call)

```python
# BEFORE (line 803)
file_paths = [str(p) for p in self.root_dir.rglob("*.py")]

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
file_paths = [str(p) for p in get_python_files(self.root_dir)]
```

#### 1.4 DependencyDiplomatAgent.py (1 rglob call)

```python
# BEFORE (line 145)
for py_file in Path('agentic_core').rglob('*.py'):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
for py_file in get_python_files(project_root):
    if 'agentic_core' in str(py_file):
```

#### 1.5 ReportingAgent.py (1 rglob call)

```python
# BEFORE (line 111)
py_files = list(folder_path.rglob("*.py"))

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
all_py = get_python_files(self.project_root)
py_files = [f for f in all_py if str(f).startswith(str(folder_path))]
```

#### 1.6 UnifiedStateManagementAgent.py (1 rglob call)

```python
# BEFORE
for state_file in state_dir.rglob("*.json"):

# AFTER
from agentic_core.utils.ssot_discovery import get_json_files
state_files = [f for f in get_json_files(self.project_root) 
               if str(f).startswith(str(state_dir))]
for state_file in state_files:
```

### Phase 2: Utility Modules (Day 1-2)

**Priority:** MEDIUM

#### 2.1 core_extensions/*.py (4 files)

Each file follows the same pattern:

```python
# BEFORE
for py_file in project_root.rglob("*.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
for py_file in get_python_files(project_root):
```

### Phase 3: Scripts (Day 2)

**Priority:** MEDIUM

#### 3.1 full_agent_discovery.py

```python
# BEFORE (line 1321)
all_py_files = [p for p in PROJECT_ROOT.rglob('*.py') if not should_exclude_path(p)]

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
all_py_files = get_python_files(PROJECT_ROOT)
# Note: ssot_discovery already excludes the same paths
```

#### 3.2 Archive scripts (archive_*.py, restore_*.py)

All archive scripts follow the same pattern and can use a helper:

```python
# Create helper in scripts/utils/archive_helpers.py
from agentic_core.utils.ssot_discovery import get_python_files

def get_archive_python_files(archive_dir: Path) -> List[Path]:
    """Get Python files from archive directory."""
    # Archives are excluded from ssot_discovery, so use direct scan
    # This is acceptable for archive-specific scripts
    return list(archive_dir.rglob("*.py"))
```

#### 3.3 Batch processing scripts (phase4_batch*.py)

```python
# BEFORE
for py_file in project_root.rglob("*.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
for py_file in get_python_files(project_root):
```

### Phase 4: Tests (Day 2-3)

**Priority:** LOW

#### 4.1 Architecture tests

```python
# BEFORE
python_files = list(project_root.rglob("*.py"))

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
python_files = get_python_files(project_root)
```

#### 4.2 test_javascript.py (EXCEPTION)

Keep rglob for JS files - SSOT is Python-focused:

```python
# KEEP AS-IS (scans JS files, not Python)
js_files = list((dashboard_dir / "js").rglob("*.js"))
```

### Phase 5: Apps (Day 3)

**Priority:** MEDIUM

#### 5.1 apps_rg/engines/*.py

Same pattern as core agents:

```python
# BEFORE
for py_file in project_root.rglob("*.py"):

# AFTER
from agentic_core.utils.ssot_discovery import get_python_files
for py_file in get_python_files(project_root):
```

---

## Verification Checklist

After each phase, run these verification steps:

### 1. Unit Tests
```bash
pytest tests/core/architecture/ -v
pytest tests/dashboard/ -v
```

### 2. SSOT Comparison
```python
from agentic_core.utils.ssot_discovery import compare_with_rglob
result = compare_with_rglob(project_root)
assert result['delta'] == 0, f"Mismatch: {result}"
```

### 3. Audit Remaining rglob
```bash
python scripts/audit_residual_rglob.py
# Should show only exceptions (audit tools, non-Python scans)
```

### 4. Full Agent Discovery
```bash
python scripts/full_agent_discovery.py
# Verify agent count matches previous run
```

---

## Risk Mitigation

### Risk 1: Missing Files
**Mitigation:** `ssot_discovery.compare_with_rglob()` verifies zero-loss

### Risk 2: Performance Regression
**Mitigation:** FileCache uses `os.walk` with directory pruning (faster than rglob)

### Risk 3: Breaking Archive Scripts
**Mitigation:** Archive scripts can keep rglob since archives are excluded from SSOT

### Risk 4: Non-Python File Scans
**Mitigation:** Keep rglob for JS, JSON, etc. or extend `ssot_discovery.get_data_files()`

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| rglob calls in active code | 93 | ~10 (exceptions only) |
| Files with rglob | 56 | ~6 (audit tools only) |
| SSOT adoption | Partial | Complete |
| Scan performance | Variable | Cached/optimized |

---

## Appendix: SSOT Discovery API Reference

```python
from agentic_core.utils.ssot_discovery import (
    get_python_files,      # All Python files (excludes backups, archives)
    get_data_files,        # Data files by extension
    get_json_files,        # JSON files specifically
    get_markdown_files,    # Markdown files
    compare_with_rglob,    # Verification function
)

from agentic_core.utils.file_cache import (
    FileCache,             # Singleton cache
    get_python_files,      # Cached Python files
)

# Usage
project_root = Path(__file__).parent.parent.parent
python_files = get_python_files(project_root)  # List[Path]
json_files = get_json_files(project_root)      # List[Path]
```

---

## Conclusion

The codebase has excellent SSOT infrastructure already in place. This migration is primarily about **adoption** rather than building new tools. The implementation plan prioritizes production agents first, followed by utilities and scripts, with tests last.

**Estimated Total Effort:** 2-3 days
**Risk Level:** Low (SSOT already verified against rglob)
**Recommendation:** Proceed with Phase 1 (Core Agents) immediately
