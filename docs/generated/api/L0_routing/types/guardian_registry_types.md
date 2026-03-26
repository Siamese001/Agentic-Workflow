# API Documentation: guardian_registry_types

**Target Audience**: developers, api_users

# guardian_registry_types API Documentation

**File**: `guardian_registry_types.py`
**Classes**: 2
**Functions**: 4

## Classes

- **GuardianTier** (inherits from str, Enum)
- **GuardianSpec**

## Functions

- **get_guardian_specs** -> tuple[GuardianSpec, ...]
- **get_guardian_by_id** -> GuardianSpec | None
- **get_all_check_ids** -> dict[str, tuple[str, ...]]
- **get_guardian_entrypoints** -> dict[str, tuple[str, str]]


## Class: GuardianTier

**Description**: Execution tier for guardians.

**Inherits from**: str, Enum



## Class: GuardianSpec

**Description**: 
    Specification for a single Guardian.

    Attributes:
        guardian_id: Stable unique identifier (used in artifacts, logs, tests).
        entrypoint_module: Full dotted module path to the guardian script.
        entrypoint_fn: Name of the runner function that returns GuardianResult.
        check_ids: Exhaustive tuple of check_ids this guardian may emit.
        tier: Execution tier (fast/slow) for scheduling.
        enabled_by_default: Whether included in default aggregation runs.
    



## Function: get_guardian_specs

**Returns**: tuple[GuardianSpec, ...]
**Description**: 
    Retrieve guardian specs with optional filtering.

    Args:
        enabled_only: If True, return only guardians with enabled_by_default=True.
        tier: If provided, filter to only guardians of this tier.

    Returns:
        Tuple of GuardianSpec in deterministic sorted order by guardian_id.
    



## Function: get_guardian_by_id

**Parameters**: guardian_id
**Returns**: GuardianSpec | None
**Description**: Lookup a guardian spec by its ID. Returns None if not found.



## Function: get_all_check_ids

**Returns**: dict[str, tuple[str, ...]]
**Description**: 
    Return a mapping of guardian_id → check_ids for all registered guardians.
    Used by behavioral coverage ratchet.
    



## Function: get_guardian_entrypoints

**Returns**: dict[str, tuple[str, str]]
**Description**: 
    Return a mapping of guardian_id → (module, function) for integrity checking.
    



## Usage Examples

### Class Usage

```python
# Using GuardianTier
guardiantier = GuardianTier()
```

```python
# Using GuardianSpec
guardianspec = GuardianSpec()
```

### Function Usage

```python
# Using get_guardian_specs
result = get_guardian_specs()
```

```python
# Using get_guardian_by_id
result = get_guardian_by_id(guardian_id)
```

```python
# Using get_all_check_ids
result = get_all_check_ids()
```



---
**Generated**: 2026-03-26T09:39:03.458237
**Type**: api_reference
**Quality**: comprehensive
