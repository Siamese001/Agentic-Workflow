# API Documentation: StructuralEngineerAgent

**Target Audience**: developers, api_users

# StructuralEngineerAgent API Documentation

**File**: `StructuralEngineerAgent.py`
**Classes**: 1
**Functions**: 7

## Classes

- **StructuralEngineerAgent** (inherits from SovereignBaseAgent, HealerMixin)

## Functions

- **get_validation_keys** -> list[int]
- **check_no_large_classes** -> tuple[bool, list[str]]
- **check_no_large_functions** -> tuple[bool, list[str]]
- **check_cyclomatic_complexity** -> tuple[bool, list[str]]
- **_calculate_complexity** -> int
- **heal_repository** -> dict[str, int]
- **heal**


## Class: StructuralEngineerAgent

**Description**: 
    Structural Engineer validates code structure and organization.

    Validates:
    - No large classes (>20 methods or >500 lines)
    - Proper function size (<50 lines)
    - Cyclomatic complexity (<10)
    - Modularity, cohesion, coupling
    

**Inherits from**: SovereignBaseAgent, HealerMixin

### Methods

#### get_validation_keys
**Parameters**: self
**Returns**: list[int]
**Description**: Return canon keys validated by this agent.

#### check_no_large_classes
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for classes with >20 methods or >500 lines.

        Returns:
            Tuple of (passed, list of violations)
        

#### check_no_large_functions
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for functions exceeding 50 lines.

        Returns:
            Tuple of (passed, list of violations)
        

#### check_cyclomatic_complexity
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for high cyclomatic complexity (>10).

        Returns:
            Tuple of (passed, list of violations)
        

#### _calculate_complexity
**Parameters**: self, node
**Returns**: int
**Description**: 
        Calculate cyclomatic complexity of a function.

        CONSOLIDATED: Delegates to shared L4 utility.
        See agentic_core.L4_state.utils.complexity_analyzer
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - invoke shared healing chain.

#### heal
**Parameters**: self, violation



## Function: get_validation_keys

**Parameters**: self
**Returns**: list[int]
**Description**: Return canon keys validated by this agent.



## Function: check_no_large_classes

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for classes with >20 methods or >500 lines.

        Returns:
            Tuple of (passed, list of violations)
        



## Function: check_no_large_functions

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for functions exceeding 50 lines.

        Returns:
            Tuple of (passed, list of violations)
        



## Function: check_cyclomatic_complexity

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for high cyclomatic complexity (>10).

        Returns:
            Tuple of (passed, list of violations)
        



## Function: _calculate_complexity

**Parameters**: self, node
**Returns**: int
**Description**: 
        Calculate cyclomatic complexity of a function.

        CONSOLIDATED: Delegates to shared L4 utility.
        See agentic_core.L4_state.utils.complexity_analyzer
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - invoke shared healing chain.



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using StructuralEngineerAgent
structuralengineeragent = StructuralEngineerAgent()
structuralengineeragent.get_validation_keys()
structuralengineeragent.check_no_large_classes()
```

### Function Usage

```python
# Using get_validation_keys
result = get_validation_keys()
```

```python
# Using check_no_large_classes
result = check_no_large_classes()
```

```python
# Using check_no_large_functions
result = check_no_large_functions()
```



---
**Generated**: 2026-03-26T09:39:05.413644
**Type**: api_reference
**Quality**: comprehensive
