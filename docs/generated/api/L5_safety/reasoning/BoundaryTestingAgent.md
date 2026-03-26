# API Documentation: BoundaryTestingAgent

**Target Audience**: developers, api_users

# BoundaryTestingAgent API Documentation

**File**: `BoundaryTestingAgent.py`
**Classes**: 1
**Functions**: 13

## Classes

- **BoundaryTestingAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__**
- **_test_empty_input** -> dict[str, Any]
- **_test_null_input** -> dict[str, Any]
- **_test_max_length** -> dict[str, Any]
- **_test_special_characters** -> dict[str, Any]
- **_test_unicode_edge_cases** -> dict[str, Any]
- **_test_numeric_boundaries** -> dict[str, Any]
- **_test_type_mismatches** -> dict[str, Any]
- **_test_malformed_structures** -> dict[str, Any]
- **_test_resource_limits** -> dict[str, Any]
- **_run_self_tests** -> bool
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: BoundaryTestingAgent

**Description**: 
    Red team agent specializing in boundary and edge case testing.
    Tests system limits and unexpected inputs:
    - Empty/null inputs
    - Maximum length inputs
    - Special characters and unicode
    - Numeric boundaries (min/max values)
    - Type mismatches
    - Malformed data structures
    - Resource limit boundaries
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self

#### _test_empty_input
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with empty inputs.

#### _test_null_input
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with null/None inputs.

#### _test_max_length
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior at maximum length boundaries.

#### _test_special_characters
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with special characters.

#### _test_unicode_edge_cases
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with unicode edge cases.

#### _test_numeric_boundaries
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior at numeric boundaries.

#### _test_type_mismatches
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with type mismatches.

#### _test_malformed_structures
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with malformed data structures.

#### _test_resource_limits
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior at resource limit boundaries.

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Validate agent structure.

#### heal_repository
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: Repository healing with parent chain invocation.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal boundary testing violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details.

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __post_init__

**Parameters**: self


## Function: _test_empty_input

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with empty inputs.



## Function: _test_null_input

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with null/None inputs.



## Function: _test_max_length

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior at maximum length boundaries.



## Function: _test_special_characters

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with special characters.



## Function: _test_unicode_edge_cases

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with unicode edge cases.



## Function: _test_numeric_boundaries

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior at numeric boundaries.



## Function: _test_type_mismatches

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with type mismatches.



## Function: _test_malformed_structures

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior with malformed data structures.



## Function: _test_resource_limits

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior at resource limit boundaries.



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Validate agent structure.



## Function: heal_repository

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: Repository healing with parent chain invocation.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal boundary testing violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details.

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using BoundaryTestingAgent
boundarytestingagent = BoundaryTestingAgent()
boundarytestingagent.heal_repository()
boundarytestingagent.heal()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _test_empty_input
result = _test_empty_input()
```

```python
# Using _test_null_input
result = _test_null_input()
```



---
**Generated**: 2026-03-26T09:39:05.060318
**Type**: api_reference
**Quality**: comprehensive
