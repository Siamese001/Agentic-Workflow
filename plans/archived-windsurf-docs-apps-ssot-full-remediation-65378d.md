---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\apps-ssot-full-remediation-65378d.md'
original_relative_path: 'apps-ssot-full-remediation-65378d.md'
source_sha256: bed9b3103df4c9f8017531822022c65b1f85176d8d99dcbc33f0dc1c334cb3e6
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps SSOT Full Remediation Plan

Add `engines/` and `tools/` to existing `FOLDER_PURITY_RULES` so apps_* uses identical enforcement as agentic_core. Zero new logic — just extend the existing dict.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State: FOLDER_PURITY_RULES vs All Territories

| Folder | In Rules? | L0 | L1 | L2 | L3 | L4 | L5 | L6 | apps_lic | apps_rg | apps_shared |
|--------|-----------|----|----|----|----|----|----|----|----|----|----|
| `config/` | ✅ YES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `reasoning/` | ✅ YES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `utils/` | ✅ YES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `types/` | ✅ YES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `validators/` | ✅ YES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `scripts/` | ✅ YES | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `enforcement/` | ✅ YES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `engines/` | ❌ **MISSING** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| `tools/` | ❌ **MISSING** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| `dashboards/` | ✅ YES | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |

**5 LCD folders enforced everywhere:** `config`, `reasoning`, `utils`, `types`, `validators`

**2 folders need to be added to FOLDER_PURITY_RULES:** `engines`, `tools`

---

## Part 0: Add Missing Folders to FOLDER_PURITY_RULES

**Zero new logic.** Just add `engines` and `tools` to the existing dict in `classification.py`.

### 0.1 Add to FOLDER_PURITY_RULES in classification.py

```python
# Add these two entries to existing FOLDER_PURITY_RULES dict:
"engines": [
    r".*_engine\.py$",
    r".*_executor\.py$",
    r".*_task\.py$",
    r".*_registry\.py$",
    r".*_impl\.py$",
    r".*Executor\.py$",
    r".*Interpreter\.py$",
    r"^[a-z][a-z0-9_]*\.py$",
],
"tools": [
    r".*_impl\.py$",
    r".*_client\.py$",
    r".*_tool\.py$",
    r"^[A-Z][a-zA-Z0-9]*\.py$",
],
```

### 0.2 Update FileClassificationAgent.py app_territory_map

Remove `"engines"` from AGENT/ORCHESTRATOR/STRATEGY (they belong in `reasoning/`):

```python
# BEFORE:
"AGENT": ["engines", "reasoning"],
"ORCHESTRATOR": ["engines", "reasoning"],
"STRATEGY": ["engines", "reasoning"],

# AFTER:
"AGENT": ["reasoning"],
"ORCHESTRATOR": ["reasoning"],
"STRATEGY": ["reasoning", "enforcement"],
```

### 0.3 No changes to execute_ssot.py

`execute_ssot.py` delegates folder purity to `FileClassificationAgent` (line 2658):
```python
"file_classification": FileClassificationAgent,
```

The `FileClassificationAgent._enforce_folder_purity()` method:
1. Reads from `FOLDER_PURITY_RULES`
2. Applies to BOTH agentic_core AND apps_* (no bypass - see line 2194-2197)
3. Will automatically enforce new `engines/` and `tools/` rules

**Diff for execute_ssot.py: NONE REQUIRED**

---

## Part 1: engines/ Remediation

**Rule:** `engines/` contains ONLY `*_engine.py`, `*Executor.py`, `*_task.py`, `*_registry.py`, `*_impl.py`

### apps_lic/engines/ (52 files)

| Action | Count | Target |
|--------|-------|--------|
| MOVE `*Agent.py` | 35 | `apps_lic/reasoning/` |
| MOVE `*_types.py` | 5 | `apps_lic/types/` |
| MOVE `*Validator.py` | 2 | `apps_lic/validators/` |
| MOVE `*Orchestrator.py` | 1 | `apps_lic/reasoning/` |
| MOVE legacy files | 3 | `archives/deprecated/` |
| KEEP valid | 6 | `apps_lic/engines/` |

### apps_rg/engines/ (52 files)

| Action | Count | Target |
|--------|-------|--------|
| MOVE `*Agent.py` | 2 | `apps_rg/reasoning/` |
| MOVE `*Strategy.py` | 1 | `apps_rg/reasoning/` |
| KEEP valid `*_engine.py` | 49 | `apps_rg/engines/` |

### agentic_core/*/engines/ (1 violation)

| Action | File | Target |
|--------|------|--------|
| MOVE | `L3_orchestration/engines/DagRuntimeInspectorAgent.py` | `L3_orchestration/reasoning/` |

---

## Part 2: tools/ Remediation

**Rule:** `tools/` contains ONLY `*_impl.py`, `*_client.py`, `*_executor.py`, snake_case tool files

### agentic_core/L2_execution/tools/ (14 files) — FIX VIOLATIONS

| Action | Files | Target |
|--------|-------|--------|
| MOVE `*_util.py` | 4 | `agentic_core/L2_execution/utils/` |
| KEEP valid `*_impl.py`, `*_client.py` | 10 | stays |

Files to move:
- `data_serializer_util.py` → `utils/`
- `gemini_spy_util.py` → `utils/`
- `payload_formatter_util.py` → `utils/`
- `text_similarity_util.py` → `utils/`

### apps_lic/tools/ (48 files)

| Pattern | Count | Action |
|---------|-------|--------|
| PascalCase tool classes | 27 | KEEP (valid tool implementations) |
| `*_util.py` | 0 | — |
| snake_case scripts | 21 | Review: move to `scripts/` if runnable |

### apps_rg/tools/ (35 files)

| Pattern | Count | Action |
|---------|-------|--------|
| PascalCase tool classes | 22 | KEEP (valid tool implementations) |
| `*_util.py` | 1 | MOVE to `utils/` |
| snake_case | 12 | Review: keep if `*_tool.py`, else move |

---

## Part 3: scripts/ Alignment

**Rule:** `apps_*/scripts/` = `ops_scripts/` equivalent (runnable utilities)

No structural changes needed — already aligned.

---

## Part 4: Rename ops_scripts/ → scripts/

| Action | Details |
|--------|---------|
| Rename | `ops_scripts/` → `scripts/` at repo root |
| Update imports | All `from ops_scripts.` → `from scripts.` |
| Update CI | `.github/workflows/*.yml` references |
| Update pre-commit | `.pre-commit-config.yaml` references |

---

## Part 5: Add FOLDER_PURITY_RULES

Add to `classification.py`:

```python
"engines": [
    r".*_engine\.py$",
    r".*_executor\.py$",
    r".*_task\.py$",
    r".*_registry\.py$",
    r".*_impl\.py$",
    r".*Executor\.py$",
    r".*Interpreter\.py$",
    r"^[a-z][a-z0-9_]*\.py$",
],
"tools": [
    r".*_impl\.py$",
    r".*_client\.py$",
    r".*_tool\.py$",
    r".*Tool\.py$",
    r"^[A-Z][a-zA-Z0-9]*\.py$",  # PascalCase tool classes
],
```

---

## Part 6: Invariant Tests

Create `tests/architecture/test_folder_purity_enforcement.py`:
- `engines/` contains no `*Agent.py`, `*_types.py`, `*Validator.py`
- `tools/` contains no `*_util.py`
- Parametrized for `agentic_core` and `apps_*`

---

## Execution Waves

1. **Wave 1:** Baseline capture + violation enumeration
2. **Wave 2:** Add FOLDER_PURITY_RULES to classification.py
3. **Wave 3:** Fix agentic_core violations (tools/ + engines/)
4. **Wave 4:** Fix apps_lic violations (engines/ + tools/)
5. **Wave 5:** Fix apps_rg violations (engines/ + tools/)
6. **Wave 6:** Import fixups across codebase
7. **Wave 7:** Rename `ops_scripts/` → `scripts/` + update imports
8. **Wave 8:** Add invariant tests
9. **Wave 9:** Verification + commit

---

## File Count Summary

| Location | Move | Keep |
|----------|------|------|
| `apps_lic/engines/` | 46 | 6 |
| `apps_rg/engines/` | 3 | 49 |
| `agentic_core/*/engines/` | 1 | ~59 |
| `agentic_core/L2_execution/tools/` | 4 | 10 |
| `apps_lic/tools/` | ~5 | ~43 |
| `apps_rg/tools/` | ~2 | ~33 |
| **TOTAL MOVES** | **~61** | — |

---

## Acceptance Criteria

- [ ] No `*Agent.py` in any `engines/` folder
- [ ] No `*_types.py` in any `engines/` folder
- [ ] No `*_util.py` in any `tools/` folder
- [ ] `ops_scripts/` renamed to `scripts/`
- [ ] All imports updated
- [ ] `pytest -q` passes
- [ ] `pre-commit run --all-files` passes
- [ ] Invariant tests prevent future violations

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

