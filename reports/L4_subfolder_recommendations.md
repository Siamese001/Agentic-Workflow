# L4 Subfolder Recommendations Report

## Executive Summary

This report analyzes L3 folders in the `agentic_core` directory that warrant L4 subfolders due to complexity and scope. Currently, `structure_blueprint.py` mandates L3 depth for all folders, but several L3 folders have grown beyond manageable size.

## Analysis Criteria

A folder warrants L4 subfolders if it meets ANY of these criteria:
1. **File Count**: >50 Python files at L3 level
2. **Subdirectory Count**: >5 existing subdirectories
3. **Functional Diversity**: Contains multiple distinct functional domains
4. **Size**: Total code exceeds 500KB

---

## HIGH PRIORITY: Folders Requiring L4 Subfolders

### 1. `agentic_core/L6_observability/dashboards/` ⭐ CRITICAL
- **Current State**: 13 .py files, 7 subdirectories, 18 total files
- **Existing Subdirs**: `js/`, `css/`, `data/`, `scripts/`, `core/`, `config/`, `tests/`
- **Issue**: Mixed concerns - Python generators, HTML templates, JS components, test files
- **Recommendation**: Formalize L4 structure

**Proposed L4 Subfolders:**
```
dashboards/
├── generators/      # Python dashboard generation scripts
├── templates/       # HTML templates
├── components/      # Reusable UI components
├── data/           # Data files and JSON
├── tests/          # Dashboard-specific tests
├── js/             # JavaScript modules (existing)
├── css/            # Stylesheets (existing)
└── config/         # Dashboard configuration
```

### 2. `agentic_core/L0_maintenance/scripts/` ⭐ CRITICAL
- **Current State**: 181 .py files, 13 subdirectories
- **Issue**: Massive flat structure with mixed concerns
- **Recommendation**: Organize by function

**Proposed L4 Subfolders:**
```
scripts/
├── healing/         # Healing and repair scripts
├── validation/      # Validation scripts (existing)
├── utilities/       # General utilities
├── workflows/       # Workflow scripts
├── runtime/         # Runtime scripts (existing)
├── schemas/         # Schema-related scripts (existing)
├── installation/    # Installation scripts (existing)
├── documentation/   # Documentation scripts (existing)
├── maintenance/     # Maintenance scripts (existing)
├── canon_validator/ # Canon validator scripts (existing)
└── test_utilities/  # Test utility scripts (existing)
```

### 3. `agentic_core/L3_orchestration/workflow_engines/` ⭐ HIGH
- **Current State**: 130 .py files, 5 subdirectories
- **Issue**: Too many orchestrators in flat structure
- **Recommendation**: Group by orchestration type

**Proposed L4 Subfolders:**
```
workflow_engines/
├── core/            # Core orchestration (base classes, types)
├── dag/             # DAG-related orchestrators
├── rl/              # Reinforcement learning orchestrators
├── mission/         # Mission control orchestrators
├── mcp/             # MCP-related orchestrators
├── safety/          # Safety-related orchestrators (existing)
├── state/           # State management (existing)
├── rag/             # RAG orchestrators (existing)
└── telemetry/       # Telemetry and monitoring
```

### 4. `agentic_core/L1_cognition/thought_engine/` ⭐ HIGH
- **Current State**: 160 .py files, 6 subdirectories
- **Issue**: Massive cognitive processing in flat structure
- **Recommendation**: Organize by cognitive function

**Proposed L4 Subfolders:**
```
thought_engine/
├── reasoning/       # Reasoning engines
├── planning/        # Planning components
├── memory/          # Memory management
├── analysis/        # Analysis tools
├── synthesis/       # Synthesis engines
└── evaluation/      # Evaluation components
```

### 5. `agentic_core/L5_safety/guardrails/` ⭐ HIGH
- **Current State**: 79 .py files, 0 subdirectories
- **Issue**: All guardrails in flat structure
- **Recommendation**: Group by guardrail type

**Proposed L4 Subfolders:**
```
guardrails/
├── security/        # Security guardrails (PII, injection, etc.)
├── quality/         # Code quality guardrails
├── structural/      # Structural healing guardrails
├── constitutional/  # Constitutional AI guardrails
├── resource/        # Resource management guardrails
├── mcp/             # MCP security guardrails
└── detection/       # Detection agents (duplicates, threats)
```

### 6. `agentic_core/L2_execution/ToolRegistry/` ⭐ MEDIUM
- **Current State**: 145 .py files, 1 subdirectory
- **Issue**: Large tool registry without organization
- **Recommendation**: Group by tool category

**Proposed L4 Subfolders:**
```
ToolRegistry/
├── core/            # Core registry functionality
├── tools/           # Tool implementations (existing)
├── handlers/        # Tool handlers
├── validators/      # Tool validators
└── adapters/        # Tool adapters
```

### 7. `agentic_core/utils/core_extensions/` ⭐ MEDIUM
- **Current State**: 98 .py files, 0 subdirectories
- **Issue**: All extensions in flat structure
- **Recommendation**: Group by extension type

**Proposed L4 Subfolders:**
```
core_extensions/
├── mixins/          # Mixin classes
├── decorators/      # Decorator utilities
├── validators/      # Validation utilities
├── formatters/      # Formatting utilities
└── helpers/         # General helpers
```

---

## MEDIUM PRIORITY: Folders to Monitor

| Folder | Files | Subdirs | Notes |
|--------|-------|---------|-------|
| `L5_safety/validators/` | 58 | 0 | Growing, may need L4 soon |
| `L4_state/ValidationContext/` | 39 | 0 | Stable, monitor |
| `schemas/models/` | 51 | 11 | Already has L4 structure |
| `prompt_governance/meta_prompts/` | 14 | 5 | Already has L4 structure |

---

## Implementation Priority

1. **Immediate** (This Sprint):
   - `L6_observability/dashboards/` - Critical for dashboard maintenance
   - `L0_maintenance/scripts/` - Critical for maintainability

2. **Short-term** (Next Sprint):
   - `L3_orchestration/workflow_engines/` - High complexity
   - `L5_safety/guardrails/` - Growing rapidly

3. **Medium-term** (Backlog):
   - `L1_cognition/thought_engine/` - Large but stable
   - `L2_execution/ToolRegistry/` - Moderate complexity
   - `utils/core_extensions/` - Utility organization

---

## SSOT Changes Required

Update `structure_blueprint.py` to add:
1. `L4_SUBFOLDER_MAP` - New constant for L4 definitions
2. Update `CORE_SUBFOLDER_MAP` to include L4 references
3. Add validation for L4 depth in appropriate folders

---

*Generated: 2026-01-18*
*Analysis based on file counts and structural complexity*
