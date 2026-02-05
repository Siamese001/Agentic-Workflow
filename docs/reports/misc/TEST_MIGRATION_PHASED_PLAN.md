# Test Migration - Phased Execution Plan

## Overview

This document breaks down the test migration into **6 phases**, each designed to be completed in a single Cascade chat session. Each phase includes:

- Specific files to migrate
- File diffs (move operations)
- Import fixes required
- Test cases to verify success
- Rollback instructions

---

## Phase 1: LOW Risk Migration (1 file)

**Estimated Time:** 5-10 minutes
**Risk Level:** LOW
**Files:** 1

### Files to Migrate

| Source | Destination |
|--------|-------------|
| `ops_scripts/maintenance/test_manifest_completion.py` | `tests/e2e/ops_scripts/maintenance/test_manifest_completion.py` |

### Pre-Migration Checklist

```bash
# 1. Verify file exists
ls ops_scripts/maintenance/test_manifest_completion.py

# 2. Create backup
cp ops_scripts/maintenance/test_manifest_completion.py .backup/

# 3. Run existing tests to establish baseline
python -m pytest ops_scripts/maintenance/test_manifest_completion.py -v
```

### Migration Script

```python
# scripts/maintenance/execute_phase1_migration.py
import shutil
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

def execute_phase1():
    """Phase 1: LOW Risk Migration - 1 file"""

    migrations = [
        ("ops_scripts/maintenance/test_manifest_completion.py",
         "tests/e2e/ops_scripts/maintenance/test_manifest_completion.py"),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        # Create destination directory
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True

if __name__ == "__main__":
    execute_phase1()
```

### Import Fix Template

```python
# Add to top of migrated file if needed
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

### Test Cases

```python
# tests/e2e/ops_scripts/maintenance/test_phase1_verification.py
import pytest
import pathlib
import subprocess

class TestPhase1Migration:
    """Verify Phase 1 migration completed successfully."""

    def test_file_exists_at_destination(self):
        """Verify file was moved to correct location."""
        dest = pathlib.Path("tests/e2e/ops_scripts/maintenance/test_manifest_completion.py")
        assert dest.exists(), f"File not found at destination: {dest}"

    def test_file_removed_from_source(self):
        """Verify file no longer exists at source."""
        src = pathlib.Path("ops_scripts/maintenance/test_manifest_completion.py")
        assert not src.exists(), f"File still exists at source: {src}"

    def test_imports_work(self):
        """Verify imports still function after move."""
        result = subprocess.run(
            ["python", "-c", "import tests.e2e.ops_scripts.maintenance.test_manifest_completion"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"

    def test_pytest_discovers_file(self):
        """Verify pytest can discover and collect the test."""
        result = subprocess.run(
            ["python", "-m", "pytest",
             "tests/e2e/ops_scripts/maintenance/test_manifest_completion.py",
             "--collect-only"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Pytest collection failed: {result.stderr}"
```

### Rollback Script

```python
# scripts/maintenance/rollback_phase1.py
import shutil
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

def rollback_phase1():
    """Rollback Phase 1 migration."""

    rollbacks = [
        ("tests/e2e/ops_scripts/maintenance/test_manifest_completion.py",
         "ops_scripts/maintenance/test_manifest_completion.py"),
    ]

    for src_rel, dest_rel in rollbacks:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        if src.exists():
            shutil.move(str(src), str(dest))
            print(f"🔄 Rolled back: {src_rel} → {dest_rel}")
        else:
            print(f"⚠️ Source not found: {src_rel}")

if __name__ == "__main__":
    rollback_phase1()
```

### Success Criteria

- [ ] File moved to `tests/e2e/ops_scripts/maintenance/`
- [ ] Original file removed from `ops_scripts/maintenance/`
- [ ] `pytest --collect-only` discovers the test
- [ ] Test passes when run directly
- [ ] No import errors

---

## Phase 2: MEDIUM Risk Migration (5 files)

**Estimated Time:** 15-20 minutes
**Risk Level:** MEDIUM
**Files:** 5

### Files to Migrate

| Source | Destination |
|--------|-------------|
| `ops_scripts/test_batch_performance_optimization.py` | `tests/e2e/ops_scripts/test_batch_performance_optimization.py` |
| `ops_scripts/test_location_agent_telemetry.py` | `tests/e2e/ops_scripts/test_location_agent_telemetry.py` |
| `ops_scripts/test_mission_script_integrity.py` | `tests/e2e/ops_scripts/test_mission_script_integrity.py` |
| `ops_scripts/test_phase1_interface.py` | `tests/e2e/ops_scripts/test_phase1_interface.py` |
| `ops_scripts/test_phase2_interface.py` | `tests/e2e/ops_scripts/test_phase2_interface.py` |

### Pre-Migration Checklist

```bash
# 1. Verify all files exist
for f in test_batch_performance_optimization.py test_location_agent_telemetry.py \
         test_mission_script_integrity.py test_phase1_interface.py test_phase2_interface.py; do
    ls ops_scripts/$f
done

# 2. Create backups
mkdir -p .backup/phase2
cp ops_scripts/test_batch_performance_optimization.py .backup/phase2/
cp ops_scripts/test_location_agent_telemetry.py .backup/phase2/
cp ops_scripts/test_mission_script_integrity.py .backup/phase2/
cp ops_scripts/test_phase1_interface.py .backup/phase2/
cp ops_scripts/test_phase2_interface.py .backup/phase2/
```

### Migration Script

```python
# scripts/maintenance/execute_phase2_migration.py
import shutil
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

def execute_phase2():
    """Phase 2: MEDIUM Risk Migration - 5 files"""

    migrations = [
        ("ops_scripts/test_batch_performance_optimization.py",
         "tests/e2e/ops_scripts/test_batch_performance_optimization.py"),
        ("ops_scripts/test_location_agent_telemetry.py",
         "tests/e2e/ops_scripts/test_location_agent_telemetry.py"),
        ("ops_scripts/test_mission_script_integrity.py",
         "tests/e2e/ops_scripts/test_mission_script_integrity.py"),
        ("ops_scripts/test_phase1_interface.py",
         "tests/e2e/ops_scripts/test_phase1_interface.py"),
        ("ops_scripts/test_phase2_interface.py",
         "tests/e2e/ops_scripts/test_phase2_interface.py"),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True

if __name__ == "__main__":
    execute_phase2()
```

### Import Fix Pattern

For each file, add this header if imports break:

```python
import sys
from pathlib import Path

# Adjust path for new location (tests/e2e/ops_scripts/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

### Test Cases

```python
# tests/e2e/ops_scripts/test_phase2_verification.py
import pytest
import pathlib
import subprocess

PHASE2_FILES = [
    "test_batch_performance_optimization.py",
    "test_location_agent_telemetry.py",
    "test_mission_script_integrity.py",
    "test_phase1_interface.py",
    "test_phase2_interface.py",
]

class TestPhase2Migration:
    """Verify Phase 2 migration completed successfully."""

    @pytest.mark.parametrize("filename", PHASE2_FILES)
    def test_file_exists_at_destination(self, filename):
        """Verify each file was moved to correct location."""
        dest = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        assert dest.exists(), f"File not found: {dest}"

    @pytest.mark.parametrize("filename", PHASE2_FILES)
    def test_file_removed_from_source(self, filename):
        """Verify each file no longer exists at source."""
        src = pathlib.Path(f"ops_scripts/{filename}")
        assert not src.exists(), f"File still at source: {src}"

    def test_pytest_discovers_all_files(self):
        """Verify pytest can discover all migrated tests."""
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/e2e/ops_scripts/", "--collect-only", "-q"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Collection failed: {result.stderr}"

        # Verify each file appears in collection
        for filename in PHASE2_FILES:
            assert filename in result.stdout, f"{filename} not discovered"
```

### Success Criteria

- [ ] All 5 files moved to `tests/e2e/ops_scripts/`
- [ ] Original files removed from `ops_scripts/`
- [ ] All imports work correctly
- [ ] `pytest --collect-only` discovers all 5 tests
- [ ] No regression in existing test suite

---

## Phase 3: HIGH Risk Migration Batch 1 (10 files)

**Estimated Time:** 25-30 minutes
**Risk Level:** HIGH
**Files:** 10 (ops_scripts root - first batch)

### Files to Migrate

| Source | Destination |
|--------|-------------|
| `ops_scripts/test_autonomous_decision_making.py` | `tests/e2e/ops_scripts/test_autonomous_decision_making.py` |
| `ops_scripts/test_autonomous_end_to_end.py` | `tests/e2e/ops_scripts/test_autonomous_end_to_end.py` |
| `ops_scripts/test_complete_mission_workflow.py` | `tests/e2e/ops_scripts/test_complete_mission_workflow.py` |
| `ops_scripts/test_hop2_sovereign_strategist.py` | `tests/e2e/ops_scripts/test_hop2_sovereign_strategist.py` |
| `ops_scripts/test_hop3_hop4_hop5_foundation.py` | `tests/e2e/ops_scripts/test_hop3_hop4_hop5_foundation.py` |
| `ops_scripts/test_hop6_hop7_crucible_governor.py` | `tests/e2e/ops_scripts/test_hop6_hop7_crucible_governor.py` |
| `ops_scripts/test_hop8_hop9_persistence_handoff.py` | `tests/e2e/ops_scripts/test_hop8_hop9_persistence_handoff.py` |
| `ops_scripts/test_hop_orchestrator_master.py` | `tests/e2e/ops_scripts/test_hop_orchestrator_master.py` |
| `ops_scripts/test_lic_rg_parity.py` | `tests/e2e/ops_scripts/test_lic_rg_parity.py` |
| `ops_scripts/test_master_verification_simulation.py` | `tests/e2e/ops_scripts/test_master_verification_simulation.py` |

### Pre-Migration Checklist

```bash
# 1. Create comprehensive backup
mkdir -p .backup/phase3
cp ops_scripts/test_autonomous_decision_making.py .backup/phase3/
cp ops_scripts/test_autonomous_end_to_end.py .backup/phase3/
cp ops_scripts/test_complete_mission_workflow.py .backup/phase3/
cp ops_scripts/test_hop2_sovereign_strategist.py .backup/phase3/
cp ops_scripts/test_hop3_hop4_hop5_foundation.py .backup/phase3/
cp ops_scripts/test_hop6_hop7_crucible_governor.py .backup/phase3/
cp ops_scripts/test_hop8_hop9_persistence_handoff.py .backup/phase3/
cp ops_scripts/test_hop_orchestrator_master.py .backup/phase3/
cp ops_scripts/test_lic_rg_parity.py .backup/phase3/
cp ops_scripts/test_master_verification_simulation.py .backup/phase3/

# 2. Run baseline test suite
python -m pytest tests/ --collect-only -q | head -20
```

### Migration Script

```python
# scripts/maintenance/execute_phase3_migration.py
import shutil
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

def execute_phase3():
    """Phase 3: HIGH Risk Migration Batch 1 - 10 files"""

    migrations = [
        ("ops_scripts/test_autonomous_decision_making.py",
         "tests/e2e/ops_scripts/test_autonomous_decision_making.py"),
        ("ops_scripts/test_autonomous_end_to_end.py",
         "tests/e2e/ops_scripts/test_autonomous_end_to_end.py"),
        ("ops_scripts/test_complete_mission_workflow.py",
         "tests/e2e/ops_scripts/test_complete_mission_workflow.py"),
        ("ops_scripts/test_hop2_sovereign_strategist.py",
         "tests/e2e/ops_scripts/test_hop2_sovereign_strategist.py"),
        ("ops_scripts/test_hop3_hop4_hop5_foundation.py",
         "tests/e2e/ops_scripts/test_hop3_hop4_hop5_foundation.py"),
        ("ops_scripts/test_hop6_hop7_crucible_governor.py",
         "tests/e2e/ops_scripts/test_hop6_hop7_crucible_governor.py"),
        ("ops_scripts/test_hop8_hop9_persistence_handoff.py",
         "tests/e2e/ops_scripts/test_hop8_hop9_persistence_handoff.py"),
        ("ops_scripts/test_hop_orchestrator_master.py",
         "tests/e2e/ops_scripts/test_hop_orchestrator_master.py"),
        ("ops_scripts/test_lic_rg_parity.py",
         "tests/e2e/ops_scripts/test_lic_rg_parity.py"),
        ("ops_scripts/test_master_verification_simulation.py",
         "tests/e2e/ops_scripts/test_master_verification_simulation.py"),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True

if __name__ == "__main__":
    execute_phase3()
```

### Import Fix Pattern (HIGH Risk)

These files likely have complex `sys.path` manipulations. Standard fix:

```python
# Replace existing sys.path manipulation with:
import sys
from pathlib import Path

# Canonical path resolution for tests/e2e/ops_scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now imports like 'from agentic_core...' will work
```

### Test Cases

```python
# tests/e2e/ops_scripts/test_phase3_verification.py
import pytest
import pathlib
import subprocess
import importlib.util

PHASE3_FILES = [
    "test_autonomous_decision_making.py",
    "test_autonomous_end_to_end.py",
    "test_complete_mission_workflow.py",
    "test_hop2_sovereign_strategist.py",
    "test_hop3_hop4_hop5_foundation.py",
    "test_hop6_hop7_crucible_governor.py",
    "test_hop8_hop9_persistence_handoff.py",
    "test_hop_orchestrator_master.py",
    "test_lic_rg_parity.py",
    "test_master_verification_simulation.py",
]

class TestPhase3Migration:
    """Verify Phase 3 HIGH risk migration completed successfully."""

    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_file_exists_at_destination(self, filename):
        """Verify each file was moved to correct location."""
        dest = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        assert dest.exists(), f"File not found: {dest}"

    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_file_removed_from_source(self, filename):
        """Verify each file no longer exists at source."""
        src = pathlib.Path(f"ops_scripts/{filename}")
        assert not src.exists(), f"File still at source: {src}"

    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_file_is_valid_python(self, filename):
        """Verify each file is syntactically valid Python."""
        filepath = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        result = subprocess.run(
            ["python", "-m", "py_compile", str(filepath)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error in {filename}: {result.stderr}"

    def test_no_import_errors_on_collection(self):
        """Verify pytest can collect without import errors."""
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/e2e/ops_scripts/",
             "--collect-only", "-q", "--ignore-glob=*verification*"],
            capture_output=True, text=True
        )
        # Allow collection to fail on missing deps, but not import errors
        assert "ImportError" not in result.stderr, f"Import errors: {result.stderr}"
```

### Success Criteria

- [ ] All 10 files moved to `tests/e2e/ops_scripts/`
- [ ] Original files removed from `ops_scripts/`
- [ ] All files pass Python syntax check
- [ ] No ImportError during pytest collection
- [ ] Existing test suite still passes

---

## Phase 4: HIGH Risk Migration Batch 2 (4 files)

**Estimated Time:** 15-20 minutes
**Risk Level:** HIGH
**Files:** 4 (ops_scripts/maintenance)

### Files to Migrate

| Source | Destination |
|--------|-------------|
| `ops_scripts/maintenance/test_canon_key_removal.py` | `tests/e2e/ops_scripts/maintenance/test_canon_key_removal.py` |
| `ops_scripts/maintenance/test_cognitive_subset.py` | `tests/e2e/ops_scripts/maintenance/test_cognitive_subset.py` |
| `ops_scripts/maintenance/test_mro_refactor.py` | `tests/e2e/ops_scripts/maintenance/test_mro_refactor.py` |

**Note:** `test_manifest_completion.py` was already migrated in Phase 1.

### Migration Script

```python
# scripts/maintenance/execute_phase4_migration.py
import shutil
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

def execute_phase4():
    """Phase 4: HIGH Risk Migration Batch 2 - 3 files (maintenance)"""

    migrations = [
        ("ops_scripts/maintenance/test_canon_key_removal.py",
         "tests/e2e/ops_scripts/maintenance/test_canon_key_removal.py"),
        ("ops_scripts/maintenance/test_cognitive_subset.py",
         "tests/e2e/ops_scripts/maintenance/test_cognitive_subset.py"),
        ("ops_scripts/maintenance/test_mro_refactor.py",
         "tests/e2e/ops_scripts/maintenance/test_mro_refactor.py"),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True

if __name__ == "__main__":
    execute_phase4()
```

### Import Fix Pattern

```python
# For tests/e2e/ops_scripts/maintenance/ files:
import sys
from pathlib import Path

# Adjust for depth: tests/e2e/ops_scripts/maintenance/ (4 levels)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

### Test Cases

```python
# tests/e2e/ops_scripts/maintenance/test_phase4_verification.py
import pytest
import pathlib

PHASE4_FILES = [
    "test_canon_key_removal.py",
    "test_cognitive_subset.py",
    "test_mro_refactor.py",
]

class TestPhase4Migration:
    """Verify Phase 4 migration completed successfully."""

    @pytest.mark.parametrize("filename", PHASE4_FILES)
    def test_file_exists_at_destination(self, filename):
        dest = pathlib.Path(f"tests/e2e/ops_scripts/maintenance/{filename}")
        assert dest.exists(), f"File not found: {dest}"

    @pytest.mark.parametrize("filename", PHASE4_FILES)
    def test_file_removed_from_source(self, filename):
        src = pathlib.Path(f"ops_scripts/maintenance/{filename}")
        assert not src.exists(), f"File still at source: {src}"
```

### Success Criteria

- [ ] All 3 files moved to `tests/e2e/ops_scripts/maintenance/`
- [ ] Original files removed
- [ ] Imports work correctly
- [ ] No regression in test suite

---

## Phase 5: HIGH Risk Migration Batch 3 (7 files)

**Estimated Time:** 20-25 minutes
**Risk Level:** HIGH
**Files:** 7 (remaining ops_scripts + agentic_core)

### Files to Migrate

| Source | Destination |
|--------|-------------|
| `ops_scripts/test_mission_dry_run.py` | `tests/e2e/ops_scripts/test_mission_dry_run.py` |
| `ops_scripts/test_mission_telemetry_dashboard.py` | `tests/e2e/ops_scripts/test_mission_telemetry_dashboard.py` |
| `ops_scripts/test_phase1_config.py` | `tests/e2e/ops_scripts/test_phase1_config.py` |
| `ops_scripts/test_phase2_core.py` | `tests/e2e/ops_scripts/test_phase2_core.py` |
| `ops_scripts/test_phase3_base.py` | `tests/e2e/ops_scripts/test_phase3_base.py` |
| `ops_scripts/test_phase4_orchestrator.py` | `tests/e2e/ops_scripts/test_phase4_orchestrator.py` |
| `agentic_core/L0_maintenance/scripts/direct_hierarchy_boundary_test.py` | `tests/e2e/agentic_core/L0_maintenance/scripts/test_direct_hierarchy_boundary.py` |
| `agentic_core/L0_maintenance/scripts/run_code_dedup_full_test.py` | `tests/e2e/agentic_core/L0_maintenance/scripts/test_run_code_dedup_full.py` |

### Migration Script

```python
# scripts/maintenance/execute_phase5_migration.py
import shutil
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

def execute_phase5():
    """Phase 5: HIGH Risk Migration Batch 3 - 8 files"""

    migrations = [
        ("ops_scripts/test_mission_dry_run.py",
         "tests/e2e/ops_scripts/test_mission_dry_run.py"),
        ("ops_scripts/test_mission_telemetry_dashboard.py",
         "tests/e2e/ops_scripts/test_mission_telemetry_dashboard.py"),
        ("ops_scripts/test_phase1_config.py",
         "tests/e2e/ops_scripts/test_phase1_config.py"),
        ("ops_scripts/test_phase2_core.py",
         "tests/e2e/ops_scripts/test_phase2_core.py"),
        ("ops_scripts/test_phase3_base.py",
         "tests/e2e/ops_scripts/test_phase3_base.py"),
        ("ops_scripts/test_phase4_orchestrator.py",
         "tests/e2e/ops_scripts/test_phase4_orchestrator.py"),
        # agentic_core files (note: filename standardization)
        ("agentic_core/L0_maintenance/scripts/direct_hierarchy_boundary_test.py",
         "tests/e2e/agentic_core/L0_maintenance/scripts/test_direct_hierarchy_boundary.py"),
        ("agentic_core/L0_maintenance/scripts/run_code_dedup_full_test.py",
         "tests/e2e/agentic_core/L0_maintenance/scripts/test_run_code_dedup_full.py"),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True

if __name__ == "__main__":
    execute_phase5()
```

### Special Considerations

**agentic_core files require extra attention:**

1. **Filename Standardization**: `*_test.py` → `test_*.py`
2. **Deeper Path**: `tests/e2e/agentic_core/L0_maintenance/scripts/` (5 levels)
3. **Import Fix**:

```python
# For tests/e2e/agentic_core/L0_maintenance/scripts/ files:
import sys
from pathlib import Path

# 5 levels deep: tests/e2e/agentic_core/L0_maintenance/scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

### Test Cases

```python
# tests/e2e/test_phase5_verification.py
import pytest
import pathlib

OPS_SCRIPTS_FILES = [
    "test_mission_dry_run.py",
    "test_mission_telemetry_dashboard.py",
    "test_phase1_config.py",
    "test_phase2_core.py",
    "test_phase3_base.py",
    "test_phase4_orchestrator.py",
]

AGENTIC_CORE_FILES = [
    ("agentic_core/L0_maintenance/scripts/direct_hierarchy_boundary_test.py",
     "tests/e2e/agentic_core/L0_maintenance/scripts/test_direct_hierarchy_boundary.py"),
    ("agentic_core/L0_maintenance/scripts/run_code_dedup_full_test.py",
     "tests/e2e/agentic_core/L0_maintenance/scripts/test_run_code_dedup_full.py"),
]

class TestPhase5Migration:
    """Verify Phase 5 migration completed successfully."""

    @pytest.mark.parametrize("filename", OPS_SCRIPTS_FILES)
    def test_ops_scripts_at_destination(self, filename):
        dest = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        assert dest.exists(), f"File not found: {dest}"

    @pytest.mark.parametrize("src,dest", AGENTIC_CORE_FILES)
    def test_agentic_core_migrated(self, src, dest):
        src_path = pathlib.Path(src)
        dest_path = pathlib.Path(dest)
        assert not src_path.exists(), f"Source still exists: {src}"
        assert dest_path.exists(), f"Destination not found: {dest}"
```

### Success Criteria

- [ ] All 8 files moved to correct destinations
- [ ] Filename standardization applied to agentic_core files
- [ ] All imports work correctly
- [ ] No regression in test suite

---

## Phase 6: Final Validation and Cleanup

**Estimated Time:** 10-15 minutes
**Risk Level:** LOW
**Purpose:** Verify complete migration and clean up

### Validation Checklist

```bash
# 1. Verify no test files remain in source locations
find ops_scripts -name "test_*.py" -o -name "*_test.py" 2>/dev/null
find agentic_core -name "test_*.py" -o -name "*_test.py" 2>/dev/null

# 2. Count migrated files
find tests/e2e/ops_scripts -name "test_*.py" | wc -l
# Expected: 22

# 3. Run full test collection
python -m pytest tests/ --collect-only -q

# 4. Run guardian to verify zero remaining violations
python scripts/maintenance/test_migration_guardian.py
```

### Final Verification Script

```python
# scripts/maintenance/verify_migration_complete.py
import pathlib
import subprocess

def verify_migration():
    """Verify all test files have been migrated."""

    base = pathlib.Path.cwd()

    # Check source locations are clean
    source_dirs = ["ops_scripts", "agentic_core", "apps_rg", "apps_lic", "apps_shared"]
    remaining_tests = []

    for src_dir in source_dirs:
        src_path = base / src_dir
        if src_path.exists():
            for test_file in src_path.rglob("test_*.py"):
                if "tests" not in test_file.parts:
                    remaining_tests.append(test_file)
            for test_file in src_path.rglob("*_test.py"):
                if "tests" not in test_file.parts:
                    remaining_tests.append(test_file)

    if remaining_tests:
        print("❌ MIGRATION INCOMPLETE - Remaining test files:")
        for f in remaining_tests:
            print(f"   - {f.relative_to(base)}")
        return False

    # Verify destination structure
    expected_count = 27  # Total files to migrate
    dest_path = base / "tests" / "e2e"
    actual_count = len(list(dest_path.rglob("test_*.py")))

    print(f"✅ Source directories clean")
    print(f"✅ Migrated files: {actual_count}")

    # Run pytest collection
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "--collect-only", "-q"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ Pytest collection successful")
    else:
        print(f"⚠️ Pytest collection issues: {result.stderr[:200]}")

    return True

if __name__ == "__main__":
    verify_migration()
```

### Cleanup Tasks

1. **Remove backup files** (after verification):

```bash
rm -rf .backup/phase1 .backup/phase2 .backup/phase3 .backup/phase4 .backup/phase5
```

2. **Update `.gitignore`** if needed
3. **Update CI/CD** test paths if hardcoded
4. **Update documentation** referencing old paths

### Success Criteria

- [ ] Zero test files in source directories
- [ ] 27 test files in `tests/e2e/`
- [ ] `pytest --collect-only` succeeds
- [ ] Full test suite passes
- [ ] Pre-commit hooks pass
- [ ] CI/CD pipeline passes

---

## Summary

| Phase | Files | Risk | Est. Time | Focus |
|-------|-------|------|-----------|-------|
| 1 | 1 | LOW | 5-10 min | Single simple file |
| 2 | 5 | MEDIUM | 15-20 min | Moderate complexity |
| 3 | 10 | HIGH | 25-30 min | ops_scripts batch 1 |
| 4 | 3 | HIGH | 15-20 min | ops_scripts/maintenance |
| 5 | 8 | HIGH | 20-25 min | Remaining + agentic_core |
| 6 | 0 | LOW | 10-15 min | Validation & cleanup |

**Total: 27 files, ~90-120 minutes across 6 sessions**

---

## Quick Reference: Import Fix by Depth

| Location | Depth | PROJECT_ROOT Path |
|----------|-------|-------------------|
| `tests/e2e/ops_scripts/` | 3 | `Path(__file__).parent.parent.parent` |
| `tests/e2e/ops_scripts/maintenance/` | 4 | `Path(__file__).parent.parent.parent.parent` |
| `tests/e2e/agentic_core/L0_maintenance/scripts/` | 5 | `Path(__file__).parent.parent.parent.parent.parent` |
