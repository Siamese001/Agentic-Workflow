# API Documentation: architecture_governance_healer

**Target Audience**: developers, api_users

# architecture_governance_healer API Documentation

**File**: `architecture_governance_healer.py`
**Classes**: 0
**Functions**: 2


## Functions

- **heal_import_compliance** -> HealCheckResult
- **heal_layer_gravity** -> HealCheckResult


## Function: heal_import_compliance

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal import_compliance violations (upward layer imports).

    Import rewiring is inherently risky — changing import statements can
    break runtime behaviour across the codebase. This healer always
    reports planned actions but never applies changes automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (import rewiring requires human review).
    



## Function: heal_layer_gravity

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal layer_gravity violations (agents in wrong layers).

    Agent relocation requires moving files AND updating all imports across
    the codebase. This healer always reports planned actions but never
    applies relocations automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (agent relocation requires human review).
    



## Usage Examples

### Function Usage

```python
# Using heal_import_compliance
result = heal_import_compliance(check)
```

```python
# Using heal_layer_gravity
result = heal_layer_gravity(check)
```



---
**Generated**: 2026-03-26T09:39:03.788085
**Type**: api_reference
**Quality**: comprehensive
