# File Placement Migration Report

**Date:** January 2, 2026  
**Issue:** App-specific files incorrectly placed in `agentic_core`

## Executive Summary

A systematic review identified **23 files** in `agentic_core` that contained application-specific logic for Resume Gen (`apps_rg`) or LinkedIn Canonical (`apps_lic`). These files were misaligned with the Sovereign Architecture principles.

## Rationale for Placement Rules

### The Sovereign Architecture Principle

The repository follows a clear separation of concerns:

| Folder | Purpose | Depth |
|--------|---------|-------|
| `agentic_core/` | **Framework-agnostic** core infrastructure (L0-L5 layers) | 3 |
| `apps_rg/` | Resume Gen application-specific logic | 2 |
| `apps_lic/` | LinkedIn Canonical application-specific logic | 2 |
| `apps_shared/` | Shared utilities across apps | 2 |
| `tests/` | Test suites | 2 |

### Why `rg_company_research_executor.py` Was Misplaced

The file `agentic_core/L2_execution/ToolRegistry/rg_company_research_executor.py`:

1. **Prefix `rg_`** clearly indicates Resume Gen ownership
2. **Line 10 comment**: `# Ownership: apps_rg / L2_execution` confirms intended placement
3. **Function `rg_company_research_executor()`** is business logic, not framework infrastructure
4. **agentic_core** should only contain reusable, app-agnostic components

**Correct placement:** `apps_rg/engines/rg_company_research_executor.py`

## Files Migrated

### To `apps_rg/engines/` (17 files)

| Original Location | File | Reason |
|-------------------|------|--------|
| `agentic_core/L2_execution/ToolRegistry/` | `rg_company_research_executor.py` | `rg_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `rg_contact_research_executor.py` | `rg_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `rg_message_generation_executor.py` | `rg_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `rg_provenance_tracker.py` | `rg_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `rg_provenance_tracker_types.py` | `rg_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `resume_engine_zlg.py` | `resume_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `resume_generator.py` | `resume_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `outreach_engine_zse.py` | `outreach_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `dispatch_outreach_tools.py` | `dispatch_outreach` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `dispatch_resume_tools.py` | `dispatch_resume` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `outreach_orchestration_config.py` | `outreach_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `outreach_orchestration_config_enums.py` | `outreach_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `outreach_orchestration_config_models.py` | `outreach_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `resume_orchestration_config.py` | `resume_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `resume_orchestration_config_types.py` | `resume_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `resume_orchestration_config_types_enums.py` | `resume_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `resume_orchestration_config_types_models.py` | `resume_` prefix |
| `agentic_core/L3_orchestration/workflow_engines/` | `resume_state.py` | `resume_` prefix |
| `agentic_core/L1_cognition/thought_engine/` | `resume_planner.py` | `resume_` prefix |

### To `apps_lic/engines/` (4 files)

| Original Location | File | Reason |
|-------------------|------|--------|
| `agentic_core/L2_execution/ToolRegistry/` | `lic_code_interpreter.py` | `lic_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `lic_code_interpreter_types.py` | `lic_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `lic_company_research_executor.py` | `lic_` prefix |
| `agentic_core/L2_execution/ToolRegistry/` | `lic_contact_research_executor.py` | `lic_` prefix |

## Blueprint Updates

Added to `agentic_core/config/blueprint_sovereign/structure_blueprint.py`:

```python
# === APP-SPECIFIC FILE PLACEMENT RULES ===
APP_SPECIFIC_PREFIXES: Dict[str, str] = {
    'rg_': 'apps_rg',      # Resume Gen executors/tools
    'lic_': 'apps_lic',    # LinkedIn Canonical executors/tools
    'resume_': 'apps_rg',  # Resume-related files
    'outreach_': 'apps_rg', # Outreach-related files
    'dispatch_resume': 'apps_rg',
    'dispatch_outreach': 'apps_rg',
    'contact_research': 'apps_rg',
    'company_research': 'apps_rg',
}

APP_SPECIFIC_PATTERNS: List[str] = [
    r'^rg_.*\.py$',
    r'^lic_.*\.py$',
    r'^resume_.*\.py$',
    r'^outreach_.*\.py$',
    r'^dispatch_(resume|outreach).*\.py$',
]

def get_correct_app_folder(filename: str) -> Optional[str]:
    """Determine the correct app folder for a file based on its prefix."""
    ...

def is_app_specific_file(filename: str) -> bool:
    """Check if a file should be in an app folder, not agentic_core."""
    ...
```

## Enforcement

The following agents should be updated to enforce these rules:

1. **LocationAgent** (`agentic_core/L5_safety/validators/location_agent.py`)
   - Check for app-specific files in agentic_core during validation
   - Emit violation if found

2. **HierarchyAgent** (`agentic_core/L5_safety/validators/HierarchyAgent.py`)
   - Validate file placement against `APP_SPECIFIC_PREFIXES`
   - Suggest correct folder during healing

3. **NamingAgent** (`agentic_core/utils/naming/naming_agent.py`)
   - Flag files with app prefixes in wrong locations

## Import Path Updates Required

After migration, any files importing these modules need path updates:

```python
# Before (incorrect)
from agentic_core.L2_execution.ToolRegistry.rg_company_research_executor import ...

# After (correct)
from apps_rg.engines.rg_company_research_executor import ...
```

## Verification

Run the Canon Validator to confirm:
```bash
python canon_validator_agentic_v2_thin.py
```

Expected: Zero hierarchy violations related to app-specific files in agentic_core.

## Prevention

To prevent future misalignment:

1. **Pre-commit hook**: Check new files against `APP_SPECIFIC_PATTERNS`
2. **CI validation**: Run LocationAgent on PRs
3. **IDE rules**: Configure linting to flag app-prefixed files in agentic_core

---

*Generated by Canon Validator Migration Tool*
