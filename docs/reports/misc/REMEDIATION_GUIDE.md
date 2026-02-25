# Guardian Test Remediation Guide

This document maps Guardian test violations to the agents and scripts needed to fix them.

## Violation Categories and Remediation Paths

### 1. Import Safety Violations

#### Ghost Imports (Missing Modules)
**Detection:** `test_import_safety.py::test_ghost_import_detection_with_find_spec`

**Remediation Agents:**
1. **Manual Review Required** - Identify if import is:
   - Typo → Fix import statement
   - Missing dependency → Add to requirements.txt
   - Wrong module path → Update import path
   - Dead code → Remove import

**No automated agent available** - Requires human judgment

---

#### Circular Dependencies
**Detection:** `test_import_safety.py::test_circular_dependency_trap`

**Remediation Agents:**
1. **Manual Refactoring Required** - Break circular dependency by:
   - Extracting shared code to new module
   - Using dependency injection
   - Moving imports to function scope
   - Restructuring module hierarchy

**No automated agent available** - Requires architectural decision

---

#### Import Waterfall Violations
**Detection:** `test_import_safety.py::test_import_waterfall_detection`

**Remediation Agents:**
1. **LocationAgent** - Move files to correct layer
   - Script: `agentic_core/L5_safety/validators/LocationAgent.py`
   - Method: `validate_and_heal_location()`

**Automated:** Partial (can suggest moves, requires approval)

---

#### Gravity Leaks (Layer Violations)
**Detection:** `test_import_safety.py::test_internal_gravity_leak_detection`

**Remediation Agents:**
1. **HierarchyAgent** - Fix layer violations
   - Script: `agentic_core/L0_maintenance/scripts/HierarchyAgent.py`
   - Method: `heal_gravity_violations()`

**Automated:** Yes (with --auto-apply flag)

---

### 2. SSOT Structure Violations

#### File Placement Violations
**Detection:** `test_comprehensive_structure.py::test_comprehensive_file_placement`

**Remediation Agents:**
1. **LocationAgent** - Move files to valid territories
   - Script: `agentic_core/L5_safety/validators/LocationAgent.py`
   - Command: `python -m agentic_core.L5_safety.validators.LocationAgent --heal`

**Automated:** Yes (with confirmation)

---

#### Missing __init__.py Files
**Detection:** `test_comprehensive_structure.py::test_package_structure_completeness`

**Remediation Script:**
```bash
# Create missing __init__.py files
python scripts/create_missing_init_files.py --auto-apply
```

**Remediation Agents:**
1. **SovereignHealingEngine** - Create missing __init__.py
   - Script: `agentic_core/L0_maintenance/scripts/SovereignHealingEngine.py`
   - Strategy: `PackageStructureHealingStrategy`

**Automated:** Yes (safe auto-fix)

---

#### Forbidden Directory Usage
**Detection:** `test_comprehensive_structure.py::test_forbidden_directory_usage`

**Remediation Agents:**
1. **LocationAgent** - Move files out of forbidden directories
   - Script: `agentic_core/L5_safety/validators/LocationAgent.py`
   - Method: `move_from_forbidden_location()`

**Automated:** Yes (with confirmation)

---

#### Misplaced Test Files
**Detection:** `test_comprehensive_structure.py::test_test_file_placement`

**Remediation Script:**
```bash
# Move test files to tests/ hierarchy
python scripts/move_misplaced_tests.py --dry-run
python scripts/move_misplaced_tests.py --apply
```

**Remediation Agents:**
1. **TestFileOrganizerAgent** (to be created)
   - Analyzes test file context
   - Determines correct tests/ subdirectory
   - Moves file and updates imports

**Automated:** Partial (requires context analysis)

---

### 3. Code Quality Violations

#### Monolith Files (Large Files)
**Detection:** `test_code_quality_metrics.py::test_file_size_validation`

**Remediation Agents:**
1. **Manual Refactoring Required** - Split large files:
   - Extract classes to separate files
   - Group related functions into modules
   - Use composition over inheritance

**No automated agent available** - Requires design decisions

---

#### High Cyclomatic Complexity
**Detection:** `test_code_quality_metrics.py::test_cyclomatic_complexity`

**Remediation Agents:**
1. **Manual Refactoring Required** - Simplify complex functions:
   - Extract helper functions
   - Use early returns
   - Simplify conditional logic
   - Apply design patterns

**No automated agent available** - Requires code understanding

---

#### Missing Documentation
**Detection:** `test_code_quality_metrics.py::test_documentation_coverage`

**Remediation Agents:**
1. **DocstringGeneratorAgent** (to be created)
   - Uses LLM to generate docstrings
   - Analyzes function signature and body
   - Creates comprehensive documentation

**Automated:** Yes (with LLM)

---

#### Import Organization
**Detection:** `test_code_quality_metrics.py::test_import_organization`

**Remediation Script:**
```bash
# Auto-fix import order
ruff check --select I --fix .
```

**Automated:** Yes (using ruff)

---

### 4. MRO Integrity Violations

#### Diamond of Death
**Detection:** `test_mro_integrity.py::test_diamond_of_death_detection`

**Remediation Agents:**
1. **Manual Refactoring Required** - Fix MRO conflicts:
   - Remove problematic mixin
   - Reorder base classes
   - Use composition instead of multiple inheritance

**No automated agent available** - Requires inheritance redesign

---

### 5. SSOT Compliance Violations

#### Base Agent Location Violations
**Detection:** `test_ssot_compliance.py::test_base_agent_location_lock`

**Remediation Agents:**
1. **LocationAgent** - Move base agents to canonical location
   - Script: `agentic_core/L5_safety/validators/LocationAgent.py`
   - Method: `heal_base_agent_location()`
   - Target: `agentic_core/base_agents/`

**Automated:** Yes (constitutional rule, auto-enforced)

---

## Remediation Workflow

### Quick Reference: Violation → Agent Mapping

| Violation Type | Agent/Script | Automation Level | Command |
|----------------|--------------|------------------|---------|
| Missing __init__.py | SovereignHealingEngine | Full | `python -m agentic_core.L0_maintenance.scripts.SovereignHealingEngine --fix-init` |
| Import order | ruff | Full | `ruff check --select I --fix .` |
| Base agent location | LocationAgent | Full | `python -m agentic_core.L5_safety.validators.LocationAgent --heal-base-agents` |
| Gravity leaks | HierarchyAgent | Full | `python -m agentic_core.L0_maintenance.scripts.HierarchyAgent --heal-gravity` |
| File placement | LocationAgent | Partial | `python -m agentic_core.L5_safety.validators.LocationAgent --heal` |
| Misplaced tests | TestFileOrganizerAgent | Partial | `python scripts/move_misplaced_tests.py` |
| Ghost imports | Manual | None | Review and fix manually |
| Circular deps | Manual | None | Refactor architecture |
| Monoliths | Manual | None | Split files manually |
| Complexity | Manual | None | Refactor functions |
| MRO conflicts | Manual | None | Fix inheritance |

### Recommended Remediation Order

1. **Phase 1: Safe Auto-Fixes (Run First)**
   ```bash
   # Fix import order
   ruff check --select I --fix .

   # Create missing __init__.py
   python -m agentic_core.L0_maintenance.scripts.SovereignHealingEngine --fix-init

   # Fix base agent locations (constitutional)
   python -m agentic_core.L5_safety.validators.LocationAgent --heal-base-agents
   ```

2. **Phase 2: Agent-Assisted Fixes (Review Required)**
   ```bash
   # Fix gravity leaks
   python -m agentic_core.L0_maintenance.scripts.HierarchyAgent --heal-gravity --dry-run
   python -m agentic_core.L0_maintenance.scripts.HierarchyAgent --heal-gravity --apply

   # Move files to correct locations
   python -m agentic_core.L5_safety.validators.LocationAgent --heal --dry-run
   python -m agentic_core.L5_safety.validators.LocationAgent --heal --apply
   ```

3. **Phase 3: Manual Fixes (Human Required)**
   - Review ghost imports and fix manually
   - Refactor circular dependencies
   - Split monolith files
   - Simplify complex functions
   - Fix MRO conflicts

### Dry-Run Mode

All automated agents support `--dry-run` mode:
```bash
# Preview changes without applying
python -m agentic_core.L0_maintenance.scripts.HierarchyAgent --heal-gravity --dry-run
```

### Rollback

All agents use transactional healing with rollback:
```bash
# Rollback last healing operation
python -m agentic_core.L0_maintenance.scripts.SovereignHealingEngine --rollback
```

## Creating New Remediation Agents

To create a new remediation agent for a violation type:

1. **Extend SovereignHealingEngine**
   ```python
   from agentic_core.L0_maintenance.scripts.SovereignHealingEngine import SovereignHealingEngine

   class MyHealingStrategy:
       async def heal(self, violations):
           # Implement healing logic
           pass
   ```

2. **Register Strategy**
   ```python
   engine = SovereignHealingEngine()
   engine.register_strategy("my_violation_type", MyHealingStrategy())
   ```

3. **Add to This Guide**
   - Document the violation type
   - Specify the agent/script
   - Provide usage examples
   - Note automation level

## Support

For questions about remediation:
- Check agent documentation in `agentic_core/L0_maintenance/scripts/`
- Review healing strategies in `agentic_core/L0_maintenance/P1_core/`
- Consult SSOT structure blueprint in `agentic_core/L5_safety/validators/structure_blueprint.py`
