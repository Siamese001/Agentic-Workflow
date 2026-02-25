# Phase 4: Full apps_* Remediation (Moves + Import Fixes)

## Wave 4.1: Fix Classification Routing + apps_lic Bulk Moves

### Commit

```text
994d7ec14b2b2bffd055d1730f2605454dd60c93
refactor(folder-purity): apps_lic remediation + classification routing fix
```

### Files Changed (43 files)

- 38 Agent files moved from apps_lic/engines/ to apps_lic/reasoning/
- 1 Strategy file moved to apps_lic/enforcement/
- 2 Validator files moved to apps_lic/validators/
- 2 Executor files moved to apps_lic/reasoning/

### python -m pytest -q

```text
9 failed, 160 passed in 20.34s
```

### pre-commit run --all-files

```text
All hooks passed
```

---

## Wave 4.2: apps_rg Bulk Moves + Import Fixes

### Commit

```text
bf50433dab051c551eaac828bbcad5cd8281df3c
refactor(folder-purity): apps_rg remediation
```

### Files Changed

- apps_rg/engines/ResumeAssemblyAgent.py -> apps_rg/reasoning/
- apps_rg/engines/RGStrategyExecutor.py -> apps_rg/reasoning/
- apps_rg/engines/RGValidationExecutor.py -> apps_rg/reasoning/
- apps_rg/engines/SovereigncontextStrategy.py -> apps_rg/enforcement/
- apps_rg/engines/ContentStrategyAgent.py (deleted - duplicate)

### python -m pytest -q

```text
9 failed, 160 passed in 20.29s
```

### pre-commit run --all-files

```text
All hooks passed
```

---

## Wave 4.3: apps_shared + Final Verification

### Commit

```text
844929524bc9350db2a5eb9b81597d727ec21a3c
refactor(folder-purity): apps_shared remediation + verify
```

### Files Changed (11 files)

- 11 Strategy files moved from apps_shared/reasoning/ to apps_shared/enforcement/

### python -m pytest -q

```text
9 failed, 160 passed in 20.22s
```

### pre-commit run --all-files

```text
All hooks passed
```

---

## Remaining Violations Summary

The strict rules expose many remaining violations that require additional moves:
- reasoning/: 18 files (Orchestrators, scripts)
- validators/: 2 files
- config/: 2 files
- types/: 20 files
- utils/: 12 files
- enforcement/: 71 files
- engines/: 29 files
- tools/: 77 files

Total: ~231 files need remediation in future waves.
