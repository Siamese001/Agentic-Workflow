---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\DEPRECATION_PLAYBOOK.md'
original_relative_path: 'DEPRECATION_PLAYBOOK.md'
source_sha256: 16c817004d03a38bf1bfd2abc5beee39cec48d8760aedbdc19890d189c7dbb30
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deprecation Playbook — Directory & Module Removal Governance

> **SSOT**: This playbook is the single governance reference for deprecating
> directories, modules, or package subtrees in the Agentic-Workflow repo.
>
> **Created**: 2026-02-13 | **RCA Origin**: `RCA_P1_core_dead_imports.md`

---

## 1. Why This Exists

The `P1_core` directory was deleted without an import sweep, leaving **67+
string references** across 22 files and **8 live broken imports** in the healing
subsystem. Tests silently skipped via `pytest.skip(ImportError)`, masking the
breakage for 2+ months.

This playbook prevents recurrence by defining a **mandatory checklist** that
must be completed before any directory or module is removed.

---

## 2. Scope

This playbook applies when:

| Action | Example |
|--------|---------|
| Deleting a directory under a protected root | `agentic_core/L0_maintenance/P1_core/` |
| Renaming a directory (move = delete + create) | `engines/` → `computation/` |
| Removing a `.py` module that is imported elsewhere | `transaction_manager.py` |
| Archiving a package subtree to `archives/deprecated/` | Consolidation retirements |

Protected roots: `agentic_core`, `apps_lic`, `apps_rg`, `apps_shared`.

---

## 3. Pre-Deletion Checklist

### 3.1 Import Sweep (MANDATORY)

```bash
# Run the ImportResolutionGuardian to get current unresolved baseline
python ops_scripts/ci/import_resolution_guardian.py

# AST-grep for all imports referencing the target directory
python -c "
import ast, sys
from pathlib import Path
TARGET = 'P1_core'  # <-- replace with directory being deleted
roots = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared']
for root in roots:
    for f in Path(root).rglob('*.py'):
        try:
            tree = ast.parse(f.read_text('utf-8'), str(f))
        except: continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and TARGET in node.module:
                print(f'{f}:{node.lineno} -> {node.module}')
"
```

**Exit criterion**: Zero live imports referencing the target. If non-zero, fix
all imports BEFORE deleting.

### 3.2 String Reference Audit

```bash
# Search for string constants referencing the target path
python -c "
from pathlib import Path
TARGET = 'P1_core'
for root in ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'ops_scripts', 'tests']:
    for f in Path(root).rglob('*.py'):
        try:
            lines = f.read_text('utf-8').splitlines()
        except: continue
        for i, line in enumerate(lines, 1):
            if TARGET in line:
                print(f'{f}:{i}: {line.strip()[:120]}')
"
```

**Exit criterion**: All string references either removed, updated, or
explicitly waived in the deprecation PR description.

### 3.3 Test Impact Assessment

- [ ] Run `pytest tests/ -x --tb=short` — no new failures introduced
- [ ] Run `pytest tests/ --import-strict` — no new strict-mode failures
- [ ] Check healing subsystem: `pytest tests/guardian/test_healing_subsystem_imports.py -v`
- [ ] Verify guardian tests: `pytest tests/guardian/ -v`

### 3.4 Baseline Update

After all imports are fixed and tests pass:

```bash
# Re-run guardian to update the import health baseline
python ops_scripts/ci/import_resolution_guardian.py --init-baseline
```

**Rule**: Baseline updates are LOCAL ONLY. Never auto-update in CI (§22).

### 3.5 Discovery Update

```bash
# Re-run agent discovery to update the registry
python phase0_discovery.py
```

Verify `agent_discovery_full.json` no longer references the deleted target.

---

## 4. PR Requirements

The deprecation PR **MUST** include:

1. **Title prefix**: `[DEPRECATION]` or `[DIRECTORY-REMOVAL]`
2. **Checklist section** in PR body:
   ```markdown
   ## Deprecation Checklist
   - [x] Import sweep: 0 live imports reference deleted target
   - [x] String reference audit: N references cleaned / M waived
   - [x] Tests pass: pytest exit code 0
   - [x] Import health baseline updated
   - [x] Agent discovery updated
   ```
3. **CI gate**: The `import-resolution-guardian` workflow must pass.
4. **Directory deletion sweep**: The `check_directory_deletion_sweep.py` CI
   step verifies no live imports reference deleted directories in the diff.

---

## 5. Post-Deletion Verification

Within  of merge:

- [ ] Confirm CI pipeline is green on `main`
- [ ] Confirm `import_health_baseline.json` unresolved count did not increase
- [ ] Confirm no new `pytest.skip(ImportError)` patterns were introduced

---

## 6. Emergency Rollback

If broken imports are discovered post-merge:

1. **Do NOT** add `pytest.skip(ImportError)` — this masks the problem (§30).
2. **Option A**: Revert the deletion PR immediately.
3. **Option B**: Fast-fix the broken imports and add them to the
   `KNOWN_BROKEN_IMPORTS` set in `test_healing_subsystem_imports.py` as xfail
   while the fix is prepared.
4. Run `import_resolution_guardian.py --init-baseline` to snapshot the new state.

---

## 7. Tooling Reference

| Tool | Path | Purpose |
|------|------|---------|
| ImportResolutionGuardian | `ops_scripts/ci/import_resolution_guardian.py` | AST-based unresolved import detection with baseline lock |
| Directory Deletion Sweep | `ops_scripts/ci/check_directory_deletion_sweep.py` | CI gate for directory removal PRs |
| Import Resolution Hook | `ops_scripts/hooks/check_import_resolution.py` | Pre-commit T3e real-resolution check |
| Strict Import Mode | `tests/_config/import_strict_mode.py` | `pytest.skip→fail` ramp for ImportError |
| Healing Import Audit | `tests/guardian/test_healing_subsystem_imports.py` | Forces import execution on healing subsystem |
| CI Workflow | `.github/workflows/import-resolution-guardian.yml` | GitHub Actions integration |

---

## 8. Anti-Patterns (FORBIDDEN)

| Anti-Pattern | Why It's Forbidden | Rule |
|-------------|-------------------|------|
| `pytest.skip(ImportError)` in new code | Masks broken imports silently | §30 |
| Delete directory without import sweep | Creates dead imports | This playbook |
| Auto-update baseline in CI | Hides regressions | §22 |
| Regex-based import detection | Misses edge cases, false positives | §6 |
| `try/except ImportError: pass` in production code | Silent failure | §30 |

---

*End of playbook. All modifications must be reviewed via PR.*

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

