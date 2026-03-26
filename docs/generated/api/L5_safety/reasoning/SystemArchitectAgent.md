# API Documentation: SystemArchitectAgent

**Target Audience**: developers, api_users

# SystemArchitectAgent API Documentation

**File**: `SystemArchitectAgent.py`
**Classes**: 1
**Functions**: 10

## Classes

- **SystemArchitectAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__** -> None
- **heal** -> dict
- **get_validation_keys** -> list[int]
- **check_core_architecture** -> tuple[bool, list[str]]
- **validate_core_architecture** -> dict[str, Any]
- **check_no_deep_nesting** -> tuple[bool, list[str]]
- **check_no_large_files** -> tuple[bool, list[str]]
- **heal_repository** -> dict[str, int]
- **validate_canonical_hierarchy**
- **dfs**


## Class: SystemArchitectAgent

**Description**: 
    System Architect validates core architecture and import dependencies.

    Validates:
    - Core modules exist and are accessible
    - No deep nesting (max 4 levels)
    - No large files (>1000 lines)
    - Import structure, dependencies, architecture
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Architectural violations require manual review.
        Returns a 'manual_required' status to satisfy the protocol without risky auto-changes.
        

#### get_validation_keys
**Parameters**: self
**Returns**: list[int]
**Description**: Return canon keys validated by this agent.

#### check_core_architecture
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        [L6 HARDENING] Core Hierarchy SSOT Verification.
        Reuses centralized hierarchy validation to prevent drift.
        

#### validate_core_architecture
**Parameters**: self, target_path
**Returns**: dict[str, Any]
**Description**: 
        Validate architecture for a specific path with strict scoping.

        Checks:
        - Circular dependencies (Scoped)
        - Layer violations (L3 -> L5)
        - Import validity
        

#### check_no_deep_nesting
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Enforce Physical Folder Nesting (Min 3, Max 5).
        Validates the physical directory depth relative to project root.
        Tests folder requires exactly depth 3.
        

#### check_no_large_files
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for files exceeding 1000 lines.

        Returns:
            Tuple of (passed, list of violations)
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - invoke shared healing chain.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Architectural violations require manual review.
        Returns a 'manual_required' status to satisfy the protocol without risky auto-changes.
        



## Function: get_validation_keys

**Parameters**: self
**Returns**: list[int]
**Description**: Return canon keys validated by this agent.



## Function: check_core_architecture

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        [L6 HARDENING] Core Hierarchy SSOT Verification.
        Reuses centralized hierarchy validation to prevent drift.
        



## Function: validate_core_architecture

**Parameters**: self, target_path
**Returns**: dict[str, Any]
**Description**: 
        Validate architecture for a specific path with strict scoping.

        Checks:
        - Circular dependencies (Scoped)
        - Layer violations (L3 -> L5)
        - Import validity
        



## Function: check_no_deep_nesting

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Enforce Physical Folder Nesting (Min 3, Max 5).
        Validates the physical directory depth relative to project root.
        Tests folder requires exactly depth 3.
        



## Function: check_no_large_files

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for files exceeding 1000 lines.

        Returns:
            Tuple of (passed, list of violations)
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - invoke shared healing chain.



## Function: validate_canonical_hierarchy

**Parameters**: proj_root


## Function: dfs

**Parameters**: current


## Usage Examples

### Class Usage

```python
# Using SystemArchitectAgent
systemarchitectagent = SystemArchitectAgent()
systemarchitectagent.heal()
systemarchitectagent.get_validation_keys()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using heal
result = heal(violation)
```

```python
# Using get_validation_keys
result = get_validation_keys()
```



---
**Generated**: 2026-03-26T09:39:05.435148
**Type**: api_reference
**Quality**: comprehensive
