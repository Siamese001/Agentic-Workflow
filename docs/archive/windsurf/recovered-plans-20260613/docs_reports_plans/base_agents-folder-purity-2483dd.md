# Base_Agents Folder Purity Treatment Plan

This plan explains how base_agents is treated in execute_ssot and what changes are needed to include it in folder purity governance.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current Treatment of base_agents

### 1. Current Status
- **base_agents is NOT in FOLDER_PURITY_RULES** - it's ungoverned
- **base_agents is in CANONICAL_LOCATION_PRIORITY** (position 3) - high priority for routing
- **Files in base_agents return None from _enforce_folder_purity** - no violations detected
- **Classification result is "CLASS"** - treated as generic class files

### 2. Why base_agents is Special
- Contains base classes and abstract agents (e.g., SovereignBaseAgent, L0MaintenanceBase)
- High-level infrastructure that other files inherit from
- Contains its own mixins/ subfolder
- Has decorators.py and timeout_decorator.py for cross-cutting concerns

### 3. Current execute_ssot Behavior
- Phase 1: FileClassificationAgent scans base_agents but finds no violations (not governed)
- Phase 2.5: No healing applied to base_agents files
- Result: base_agents files are ignored by folder purity enforcement

## Proposed Treatment

### Option 1: Add base_agents to FOLDER_PURITY_RULES
Add base_agents with appropriate patterns:
```python
"base_agents": [
    r".*Base\.py$",      # Base classes like L0MaintenanceBase
    r".*BaseAgent\.py$", # Base agents like SovereignBaseAgent
    r".*\.py$",          # Allow any for infrastructure flexibility
],
```

### Option 2: Keep base_agents Ungoverned (Recommended)
- base_agents serves as infrastructure/foundation code
- Files here are meant to be flexible in naming
- Other folders have stricter rules that inherit from these bases
- Focus folder purity on implementation folders, not base infrastructure

## Recommendation

**Keep base_agents ungoverned** but document this decision clearly:

1. **base_agents is infrastructure** - like runtime/, interfaces/, core/
2. **Files here are foundational** - other folders build on them
3. **Naming flexibility is important** - base classes need descriptive names
4. **Folder purity focuses on implementation** - L*_, apps_* folders

## Implementation

If we choose to govern base_agents (Option 1):

1. Add to FOLDER_PURITY_RULES in classification.py
2. Update test_folder_purity_invariants.py to check global folders
3. Run execute_ssot to verify no violations
4. Commit changes

If we choose to keep ungoverned (Option 2):

1. Document this decision in code comments
2. Add base_agents to an EXEMPT_FOLDERS list if needed
3. No code changes required

## Current Files in base_agents
- L0MaintenanceBase.py, L1CognitionBase.py, ..., L6ObservabilityBase.py
- SovereignBaseAgent.py (main base agent)
- LightweightBase.py
- decorators.py, timeout_decorator.py, timeout_decorator_impl.py
- mixins/ subfolder (with its own governance)

All these files follow reasonable naming patterns already, so no immediate action is needed unless we want stricter governance.

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

