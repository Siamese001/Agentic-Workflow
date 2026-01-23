# Duplicate Files Report - SSOT Cleanup Analysis

**Generated:** Phase 7+ Architecture Guard Analysis
**Scope:** `agentic_core/` (excluding `archived/`, `__pycache__`)

---

## Executive Summary

Found **22 duplicate filename pairs** across the SSOT-approved folders. This report categorizes each duplicate and provides actionable recommendations.

### Categories:
- 🔴 **CRITICAL** - Exact duplicates (byte-for-byte identical) - Archive one immediately
- 🟠 **HIGH** - Same purpose, different implementations - Consolidate to SSOT
- 🟡 **MEDIUM** - Related but distinct functionality - Rename or relocate
- 🟢 **LOW** - Intentional duplicates (`__init__.py`) - No action needed

---

## 🔴 CRITICAL: Exact Duplicates (Archive Immediately)

### 1. `CognitiveBatchProcessor.py` (IDENTICAL - 333 lines each)

| Location | Lines | Purpose |
|----------|-------|---------|
| `L5_safety/cognition/CognitiveBatchProcessor.py` | 333 | Batch processor for cognitive disposition |
| `L5_safety/guardrails/CognitiveBatchProcessor.py` | 333 | **EXACT DUPLICATE** |

**Action:** Archive `L5_safety/guardrails/CognitiveBatchProcessor.py`
**SSOT:** `L5_safety/cognition/CognitiveBatchProcessor.py`

---

### 2. `TieredBatchProcessor.py` (IDENTICAL - 385 lines each)

| Location | Lines | Purpose |
|----------|-------|---------|
| `L5_safety/cognition/TieredBatchProcessor.py` | 385 | Tiered batch processing with semantic caching |
| `L5_safety/guardrails/TieredBatchProcessor.py` | 385 | **EXACT DUPLICATE** |

**Action:** Archive `L5_safety/guardrails/TieredBatchProcessor.py`
**SSOT:** `L5_safety/cognition/TieredBatchProcessor.py`

---

### 3. Maintenance Scripts in Nested `maintenance/` Folder

These scripts exist in both `L0_maintenance/scripts/` AND `L0_maintenance/scripts/maintenance/`:

| Filename | Action |
|----------|--------|
| `archive_duplicates.py` | Archive nested copy |
| `check_duplicate_filenames.py` | Archive nested copy |
| `check_from_utils_duplicates.py` | Archive nested copy |
| `check_heal_schema_compliance.py` | Archive nested copy |
| `check_protected_files.py` | Archive nested copy |
| `fix_heal_schema_violations.py` | Archive nested copy |
| `investigate_overlaps.py` | Archive nested copy |
| `remove_duplicate_suffixes.py` | Archive nested copy |
| `ssot_archive_refactor.py` | Archive nested copy |

**Action:** Archive entire `L0_maintenance/scripts/maintenance/` folder
**SSOT:** `L0_maintenance/scripts/` (flat structure)

---

## 🟠 HIGH: Same Purpose, Different Implementations

### 4. `consensus.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `schemas/models/consensus.py` | 39 | **Pydantic schemas** (`ConsensusVerdict`, `ModelOpinion`) |
| `L1_cognition/thought_engine/consensus.py` | 266 | **Implementation** (`SupremeCourt` class using OpenAI) |

**Analysis:**
- `schemas/models/consensus.py` - Pure data models (Pydantic)
- `L1_cognition/thought_engine/consensus.py` - Business logic with OpenAI SDK

**Action:**
- KEEP BOTH but **rename** `L1_cognition/thought_engine/consensus.py` → `supreme_court.py`
- Update imports in dependent files

**Diff:**
```python
# schemas/models/consensus.py - KEEP (data models)
class ConsensusVerdict(BaseModel): ...
class ModelOpinion(BaseModel): ...

# L1_cognition/thought_engine/consensus.py - RENAME to supreme_court.py
from agentic_core.schemas.models.core_contracts import ConsensusVerdict, ModelOpinion
class SupremeCourt: ...  # Implementation
```

---

### 5. `structured_engine.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L1_cognition/thought_engine/structured_engine.py` | 38 | **Stub** - Imports from SSOT, minimal `StructuredEngine` |
| `L2_execution/ToolRegistry/structured_engine.py` | 118 | **Full implementation** with Instructor library |

**Analysis:**
- L1 version is a residual stub (Phase 2C cleanup note in docstring)
- L2 version is the full implementation with OpenAI + Instructor

**Action:** Archive `L1_cognition/thought_engine/structured_engine.py`
**SSOT:** `L2_execution/ToolRegistry/structured_engine.py`

---

### 6. `constants.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `config/blueprint_sovereign/constants.py` | 95 | **SSOT** - Redis, Agent, Healing config |
| `L1_cognition/thought_engine/constants.py` | 51 | **Re-export** from structure_blueprint.py |

**Analysis:**
- `config/blueprint_sovereign/constants.py` - Primary config constants
- `L1_cognition/thought_engine/constants.py` - Re-exports structural constants

**Action:**
- KEEP BOTH - they serve different purposes
- `config/blueprint_sovereign/constants.py` = Runtime config
- `L1_cognition/thought_engine/constants.py` = Structural constants (depth_map, excluded_dirs)

---

### 7. `context.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L4_state/ValidationContext/context.py` | 84 | `OmniContext` - Global context builder |
| `L5_safety/validators/context.py` | 458 | `ValidationContext` - Full validation infrastructure |

**Analysis:**
- L4 version: Simple context aggregator (84 lines)
- L5 version: Full validation context with LLM integration (458 lines)

**Action:**
- KEEP BOTH - different purposes
- Consider renaming L4 to `omni_context.py` for clarity

---

### 8. `base.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L2_execution/ToolRegistry/base.py` | 104 | `BaseTool`, `ToolRegistry`, `SubAtomicAgent`, `BaseAgent` |
| `schemas/models/base.py` | 44 | `SovereignBaseModel`, `Territory` (Pydantic) |

**Analysis:**
- L2 version: Execution infrastructure classes
- schemas version: Pydantic data models

**Action:** KEEP BOTH - completely different purposes (execution vs data models)

---

### 9. `execution.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L1_cognition/thought_engine/execution.py` | 89 | `ExecutionContext`, `ExecutionResult`, `ExecutionPhase` (dataclasses) |
| `L2_execution/ToolRegistry/execution.py` | 290 | Subprocess execution with sandbox validation |

**Analysis:**
- L1 version: Execution state dataclasses
- L2 version: Actual subprocess execution utilities

**Action:**
- KEEP BOTH - different purposes
- Consider renaming L1 to `execution_types.py`
- Consider renaming L2 to `subprocess_executor.py`

---

### 10. `registry.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `config/blueprint_sovereign/registry.py` | Unknown | Blueprint registry |
| `L2_execution/ToolRegistry/registry.py` | Unknown | Tool registry |

**Action:** KEEP BOTH - different registries for different purposes

---

### 11. `decorators.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L5_safety/validators/decorators.py` | Unknown | `@standard_heal` decorator |
| `utils/core_extensions/decorators.py` | Unknown | General utility decorators |

**Action:** KEEP BOTH - different decorator sets

---

### 12. `dashboard_ssot_definitions.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L0_maintenance/scripts/dashboard_ssot_definitions.py` | Unknown | Dashboard definitions |
| `L5_safety/validators/dashboard_ssot_definitions.py` | Unknown | Validator dashboard definitions |

**Action:** Investigate and consolidate if identical

---

### 13. `intervention_server.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L3_orchestration/workflow_engines/intervention_server.py` | Unknown | Workflow intervention |
| `L5_safety/validators/intervention_server.py` | Unknown | Validator intervention |

**Action:** Investigate and consolidate if identical

---

### 14. `sovereign_domain_constitution.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `config/blueprint_sovereign/sovereign_domain_constitution.py` | Unknown | Constitution definition |
| `L1_cognition/thought_engine/sovereign_domain_constitution.py` | Unknown | Thought engine constitution |

**Action:** Investigate - likely one is a re-export

---

### 15. `gatekeeper_lock.py`

| Location | Lines | Purpose |
|----------|-------|---------|
| `L0_maintenance/scripts/gatekeeper_lock.py` | Unknown | Security lock |
| `L0_maintenance/scripts/security/gatekeeper_lock.py` | Unknown | Nested security lock |

**Action:** Archive nested copy, keep flat structure

---

## 🟢 LOW: Intentional Duplicates (No Action)

### `__init__.py` Files

These are intentional package markers - **NO ACTION REQUIRED**.

---

## Cleanup Script

Add these files to `cleanup_phase4_5_sprawl.py` for archival:

```python
PHASE_7_DUPLICATES = [
    # Exact duplicates
    "agentic_core/L5_safety/guardrails/CognitiveBatchProcessor.py",
    "agentic_core/L5_safety/guardrails/TieredBatchProcessor.py",

    # Stub/residual files
    "agentic_core/L1_cognition/thought_engine/structured_engine.py",

    # Nested maintenance folder (entire folder)
    "agentic_core/L0_maintenance/scripts/maintenance/",

    # Nested security folder
    "agentic_core/L0_maintenance/scripts/security/gatekeeper_lock.py",
]
```

---

## Recommended Renames (Phase 8)

| Current | Proposed | Reason |
|---------|----------|--------|
| `L1_cognition/thought_engine/consensus.py` | `supreme_court.py` | Disambiguate from schema |
| `L1_cognition/thought_engine/execution.py` | `execution_types.py` | Disambiguate from L2 |
| `L2_execution/ToolRegistry/execution.py` | `subprocess_executor.py` | Clearer purpose |
| `L4_state/ValidationContext/context.py` | `omni_context.py` | Disambiguate from L5 |

---

## Summary

| Category | Count | Action |
|----------|-------|--------|
| 🔴 CRITICAL (Exact Duplicates) | 11 | Archive immediately |
| 🟠 HIGH (Consolidate) | 4 | Rename/relocate |
| 🟡 MEDIUM (Investigate) | 4 | Manual review |
| 🟢 LOW (Intentional) | 27+ | No action |

**Total files to archive:** ~15 files + 1 folder
