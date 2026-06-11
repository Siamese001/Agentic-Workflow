---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\engines-folder-purity-enforcement-77e747.md'
original_relative_path: 'engines-folder-purity-enforcement-77e747.md'
source_sha256: 5d649130f55508147aea34e6725a85340942ca401943558cbbd6400f051a0f5a
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Engines Folder Full SSOT Remediation for apps_*

Apply full execute_ssot classification and renaming rules to `apps_*/engines/` folders, treating them identically to `agentic_core` engines/ enforcement.

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


## Problem Statement

**apps_lic/engines/ (52 files):**
| Category | Count | Examples |
|----------|-------|----------|
| `*Agent.py` | 35 | `QAConductorAgent.py`, `LogReaderAgent.py` |
| `*_types.py` | 5 | `code_quality_guardrail_types.py`, `lic_vector_memory_types.py` |
| `*Validator.py` | 2 | `MessageDiversityValidator.py`, `PersonaPlannerValidator.py` |
| `*Executor.py` | 2 | `HOPPipelineExecutor.py`, `LICValidationExecutor.py` |
| `*Orchestrator.py` | 1 | `LicHealingOrchestrator.py` |
| `*Strategy.py` | 0 | — |
| `*_util.py` (compound) | 1 | `PIISanitizerSpecialistAgent_util.py` |
| Legacy/deprecated | 3 | `control_plane.py`, `check_schema_policy_validator.py`, `message_body_composer.py` |
| Infrastructure | 3 | `hop_stage_registry.py`, `LicCodeInterpreter.py` |

**apps_rg/engines/ (52 files):**
| Category | Count | Examples |
|----------|-------|----------|
| `*Agent.py` | 2 | `ContentStrategyAgent.py` (shim), `ResumeAssemblyAgent.py` |
| `*_engine.py` | 35 | `base_rg_engine.py`, `resume_orchestrator_engine.py` |
| `*Executor.py` | 2 | `RGStrategyExecutor.py`, `RGValidationExecutor.py` |
| `*Strategy.py` | 1 | `SovereigncontextStrategy.py` |
| `*_task.py` | 3 | `bullet_generation_task.py`, `resume_generation_task.py` |
| Other snake_case | 9 | `competency_item.py`, `hallucination_detector.py` |

**agentic_core violations:** 1 (`DagRuntimeInspectorAgent.py` in engines/)

---

## Classification Rules (Same as execute_ssot)

| Pattern | Target Folder |
|---------|---------------|
| `*Agent.py` | `reasoning/` |
| `*_types.py` | `types/` |
| `*Validator.py`, `*_validator.py` | `validators/` |
| `*Strategy.py`, `*_strategy.py` | `enforcement/` or `reasoning/` |
| `*Orchestrator.py`, `*_orchestrator.py` | `reasoning/` |
| `*Executor.py`, `*_executor.py` | `engines/` (valid) |
| `*_engine.py` | `engines/` (valid) |
| `*_task.py`, `*_registry.py` | `engines/` (valid) |
| `*_util.py` | `utils/` |
| Legacy/deprecated files | `archives/deprecated/` |

---

## Implementation Plan

### Wave 1: Baseline + Full Violation Enumeration
1. Capture baseline: `git rev-parse HEAD`, `git status`, `pytest -q`
2. Enumerate ALL files in `apps_*/engines/` with classification
3. Build deterministic move/rename mapping table
4. Document in evidence file: `docs/reports/plans/engines_ssot_remediation.md`

### Wave 2: Add `engines/` to FOLDER_PURITY_RULES
1. Edit `classification.py` — add `engines` key with allowed patterns:
   ```python
   "engines": [
       r".*_engine\.py$",
       r".*_executor\.py$",
       r".*_task\.py$",
       r".*_registry\.py$",
       r".*_impl\.py$",
       r".*_service\.py$",
       r".*_router\.py$",
       r".*_scanner\.py$",
       r".*_coordinator\.py$",
       r".*Executor\.py$",
       r".*Interpreter\.py$",
       r"^[a-z][a-z0-9_]*\.py$",
   ],
   ```
2. Update `FileClassificationAgent.py` `app_territory_map`:
   - Remove `"engines"` from `AGENT`, `STRATEGY`, `ORCHESTRATOR` allowed folders

### Wave 3: Execute Moves (apps_lic/engines/)
| Action | Files | Target |
|--------|-------|--------|
| MOVE | 35 `*Agent.py` | `apps_lic/reasoning/` |
| MOVE | 5 `*_types.py` | `apps_lic/types/` |
| MOVE | 2 `*Validator.py` | `apps_lic/validators/` |
| MOVE | 1 `*Orchestrator.py` | `apps_lic/reasoning/` |
| RENAME+MOVE | 1 `PIISanitizerSpecialistAgent_util.py` | `apps_lic/utils/pii_sanitizer_util.py` |
| MOVE | 3 legacy files | `archives/deprecated/` |
| KEEP | 5 valid engine files | `apps_lic/engines/` |

### Wave 4: Execute Moves (apps_rg/engines/)
| Action | Files | Target |
|--------|-------|--------|
| MOVE | 2 `*Agent.py` | `apps_rg/reasoning/` |
| MOVE | 1 `*Strategy.py` | `apps_rg/reasoning/` |
| KEEP | 47 valid `*_engine.py`, `*Executor.py`, etc. | `apps_rg/engines/` |

### Wave 5: Execute Moves (agentic_core)
| Action | Files | Target |
|--------|-------|--------|
| MOVE | 1 `DagRuntimeInspectorAgent.py` | `agentic_core/L3_orchestration/reasoning/` |

### Wave 6: Import Fixups
1. Run `rg` to find all imports referencing moved files
2. Update import paths systematically
3. Update `__init__.py` re-exports in affected packages

### Wave 7: Add Invariant Tests
1. Create `tests/architecture/test_engines_folder_purity.py`:
   - Parametrized test for `agentic_core` and `apps_*`
   - Verify no `*Agent.py`, `*_types.py`, `*Validator.py` in `engines/`
   - Verify `engines/` files match FOLDER_PURITY_RULES

### Wave 8: Verification + Commit
1. `pytest -q` — must pass
2. `pre-commit run --all-files` — must pass
3. Violation scans empty
4. Commit: `governance(engines): full SSOT remediation for apps_* engines/`

---

## File Count Summary

| Location | Total | Move | Keep |
|----------|-------|------|------|
| `apps_lic/engines/` | 52 | 47 | 5 |
| `apps_rg/engines/` | 52 | 3 | 49 |
| `agentic_core/*/engines/` | ~60 | 1 | ~59 |
| **TOTAL** | ~164 | **51** | ~113 |

---

## Acceptance Criteria

- [ ] `engines/` contains ONLY valid patterns (`*_engine.py`, `*Executor.py`, `*_task.py`, etc.)
- [ ] No `*Agent.py` in any `engines/` folder
- [ ] No `*_types.py` in any `engines/` folder
- [ ] No `*Validator.py` in any `engines/` folder
- [ ] All imports updated and working
- [ ] `pytest -q` passes
- [ ] `pre-commit run --all-files` passes
- [ ] New invariant test prevents future violations

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

