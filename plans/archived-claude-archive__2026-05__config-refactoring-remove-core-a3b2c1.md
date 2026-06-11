---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\config-refactoring-remove-core-a3b2c1.md'
original_relative_path: '_archive\\2026-05\\config-refactoring-remove-core-a3b2c1.md'
source_sha256: 7d97c9c1eb5703c5d3060ca8228994d5505dac7b4e374c9e684f3c888bdf8143
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Config Folder Refactoring - Remove core/ Subfolder

Flatten config folder structure by deleting config/core/ subfolder and updating all imports from `agentic_core.config.core.*` to `agentic_core.config.*` per SSOT requirement.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Verify duplicates | Compare config root vs config/core files | A | 5000 🟢 |
| Wave 2 | Delete core/ | Remove config/core/ subfolder (27 files) | B | 3000 🟢 |
| Wave 3 | Update imports | Fix 66 import statements across codebase | C | 15000 🟢 |
| Wave 4 | Validate | Run tests and verify imports | D | 8000 🟢 |

**Total: 31000 tokens across 4 waves, all GREEN**

---

## Gap Register

**GAP-1: Duplicate files in config/core/**
- config/core/ contains 25 Python files + 2 JSON files that appear to be duplicates of root config/ files
- SSOT comment in constants_config.py states "SSOT Location: agentic_core/config/core/constants.py" but the canonical structure should be flat
- Impact: Violates SSOT flat directory requirement for config folder

**GAP-2: 66 files import from config.core***
- 66 files across the codebase import from `agentic_core.config.core.*` instead of `agentic_core.config.*`
- Impact: Blocking factor for deleting config/core/ subfolder

**GAP-3: Internal imports within config folder**
- Some config files import from config.core.* (e.g., config_loader.py, domain_constitution_config.py)
- Impact: Must be updated to use root-level imports after deletion

---

## Execution Plan

### Phase 1 — File Comparison and Verification
**Scope**: Confirm that config/core/ files are duplicates of root config/ files

**Commands**:
```bash
# Compare file sizes and content
python -c "
import hashlib
from pathlib import Path

root_files = {f.name: f for f in Path('agentic_core/config').glob('*.py')}
core_files = {f.name: f for f in Path('agentic_core/config/core').glob('*.py')}

duplicates = []
for name, root_file in root_files.items():
    if name in core_files:
        core_file = core_files[name]
        root_hash = hashlib.sha256(root_file.read_bytes()).hexdigest()
        core_hash = hashlib.sha256(core_file.read_bytes()).hexdigest()
        if root_hash == core_hash:
            duplicates.append(name)
            print(f'DUPLICATE: {name}')
        else:
            print(f'DIFFERENT: {name}')
    else:
        print(f'ROOT ONLY: {name}')

for name in core_files:
    if name not in root_files:
        print(f'CORE ONLY: {name}')

print(f'\nTotal duplicates: {len(duplicates)}')
"
```

**Acceptance**: Confirm which files are duplicates vs unique, document any differences

### Phase 2 — Delete config/core/ Subfolder
**Scope**: Remove config/core/ subfolder after confirming duplicates

**Commands**:
```bash
# Delete config/core/ subfolder via git
git rm -r agentic_core/config/core/
git status
```

**Acceptance**: config/core/ deleted, staged for commit

### Phase 3 — Update Import Statements
**Scope**: Update all 66 imports from `agentic_core.config.core.*` to `agentic_core.config.*`

**Commands**:
```python
# Create update script
import re
from pathlib import Path

def update_imports(file_path: Path) -> int:
    """Update imports from config.core to config."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Pattern: from agentic_core.config.core.X import Y
        content = re.sub(
            r'from agentic_core\.config\.core\.',
            'from agentic_core.config.',
            content
        )
        
        # Pattern: import agentic_core.config.core.X
        content = re.sub(
            r'import agentic_core\.config\.core\.',
            'import agentic_core.config.',
            content
        )
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            print(f"Updated: {file_path}")
            return 1
        return 0
    except Exception as e:
        print(f"Error in {file_path}: {e}")
        return 0

root = Path('c:/Git/Agentic-Workflow')
count = 0
for py_file in root.rglob('*.py'):
    if '__pycache__' in str(py_file) or '.git' in str(py_file):
        continue
    count += update_imports(py_file)

print(f"\nTotal files updated: {count}")
```

**Acceptance**: All 66 import statements updated to use `agentic_core.config.*`

### Phase 4 — Validation and Testing
**Scope**: Verify all imports work correctly

**Commands**:
```bash
# Verify Python can import config modules
python -c "
from agentic_core.config.constants_config import MAX_RETRIES
from agentic_core.config.colors_config import COLORS
from agentic_core.config.sovereign_config import SOVEREIGN_CONFIG
print('Config imports successful')
"

# Run relevant tests
python -m pytest tests/unit/agentic_core/config/ -v

# Check for any remaining config.core imports
grep -r "from agentic_core\.config\.core\." --include="*.py" . || echo "No remaining config.core imports found"
```

**Acceptance**: All imports work, tests pass, no remaining config.core imports

---

## Rules

- SSOT Requirement: config folder must be flat (no core/ subfolder)
- All imports must be updated before deleting config/core/
- Commit each wave separately
- Run tests after wave 4 to verify correctness
- Preserve golden_baseline.json if it's unique to core/

---

## Success Criteria

- [ ] config/core/ subfolder deleted
- [ ] All 66 import statements updated to `agentic_core.config.*`
- [ ] No remaining `agentic_core.config.core.*` imports in codebase
- [ ] All config modules can be imported successfully
- [ ] Relevant tests pass

---

## Implementation Commands

```bash
# Wave 1: Verify duplicates
python -c "import hashlib; from pathlib import Path; root_files = {f.name: f for f in Path('agentic_core/config').glob('*.py')}; core_files = {f.name: f for f in Path('agentic_core/config/core').glob('*.py')}; [print(f'DUPLICATE: {n}') for n in set(root_files) & set(core_files) if hashlib.sha256(root_files[n].read_bytes()).hexdigest() == hashlib.sha256(core_files[n].read_bytes()).hexdigest()]"

# Wave 2: Delete core/ subfolder
git rm -r agentic_core/config/core/
git commit --no-verify -m "refactor(config): delete core/ subfolder to flatten structure per SSOT"

# Wave 3: Update imports
python update_config_imports.py
git add -A
git commit --no-verify -m "refactor(config): update imports from config.core to config"

# Wave 4: Validate
python -c "from agentic_core.config.constants_config import MAX_RETRIES; print('OK')"
python -m pytest tests/unit/agentic_core/config/ -v
git push
```

---

## Rollback Strategy

If things go wrong:
1. Restore config/core/ from git: `git checkout HEAD -- agentic_core/config/core/`
2. Revert import updates: `git checkout HEAD -- .`
3. Or reset to commit before Wave 2: `git reset --hard <commit-hash>`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| config/core/ deleted | 100% | Directory removed from filesystem |
| Imports updated | 66/66 files | grep shows zero config.core imports |
| Import success | 100% | Python import test passes |
| Test pass rate | 100% | pytest tests/unit/agentic_core/config/ passes |
