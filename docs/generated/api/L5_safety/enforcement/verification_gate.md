# API Documentation: verification_gate

**Target Audience**: developers, api_users

# verification_gate API Documentation

**File**: `verification_gate.py`
**Classes**: 1
**Functions**: 15

## Classes

- **VerificationGate** (inherits from HallucinationDetectionMixin, SovereignBaseAgent)

## Functions

- **__init__**
- **verify_action** -> bool
- **_verify_target_in_ast** -> bool
- **_verify_import_exists** -> bool
- **_verify_function_exists** -> bool
- **_verify_class_exists** -> bool
- **_verify_variable_exists** -> bool
- **_verify_method_exists** -> bool
- **_verify_any_node_exists** -> bool
- **verify_modification** -> bool
- **_map_violation_to_action** -> str
- **_extract_target_from_violation** -> str | None
- **clear_cache**
- **get_cache_stats** -> dict[str, Any]
- **heal**


## Class: VerificationGate

**Description**: 
    Structural validation layer that verifies actions against actual AST structure.

    Prevents Epistemic Cascade by ensuring agents only act on verified targets
    that actually exist in the codebase structure.

    V10 Refactored: Now inherits from AtomicExecutionMixin for rollback capability
    and HallucinationDetectionMixin for structural validation.

    MRO: VerificationGate -> AtomicExecutionMixin -> HallucinationDetectionMixin -> ...

    Integrates with L4ContextManager for performance optimization.
    

**Inherits from**: HallucinationDetectionMixin, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, context_manager
**Description**: 
        Initialize verification gate.

        Args:
            context_manager: Optional L4ContextManager for shared caching
        

#### verify_action
**Parameters**: self, file_path, action_type, target_node
**Returns**: bool
**Description**: 
        Verify that the target node exists in the file before allowing action.

        Args:
            file_path: Path to the file to verify
            action_type: Type of action (e.g., 'delete_import', 'modify_function', 'remove_class')
            target_node: Target node name to verify exists

        Returns:
            True if target exists and action is valid, False otherwise
        

#### _verify_target_in_ast
**Parameters**: self, tree, action_type, target_node
**Returns**: bool
**Description**: 
        Verify target node exists in AST based on action type.

        Args:
            tree: Parsed AST tree
            action_type: Type of action to verify
            target_node: Target node name

        Returns:
            True if target exists for the given action type
        

#### _verify_import_exists
**Parameters**: self, tree, import_name
**Returns**: bool
**Description**: Verify that an import statement exists.

#### _verify_function_exists
**Parameters**: self, tree, func_name
**Returns**: bool
**Description**: Verify that a function definition exists.

#### _verify_class_exists
**Parameters**: self, tree, class_name
**Returns**: bool
**Description**: Verify that a class definition exists.

#### _verify_variable_exists
**Parameters**: self, tree, var_name
**Returns**: bool
**Description**: Verify that a variable assignment exists.

#### _verify_method_exists
**Parameters**: self, tree, method_name
**Returns**: bool
**Description**: Verify that a method exists within any class.

#### _verify_any_node_exists
**Parameters**: self, tree, node_name
**Returns**: bool
**Description**: Generic verification - check if any node with matching name exists.

#### verify_modification
**Parameters**: self, context
**Returns**: bool
**Description**: 
        Verify all modifications in a SurgicalContext before allowing execution.

        This is the primary method for preventing Epistemic Cascade - it ensures
        that all target nodes actually exist before any surgical changes are made.

        Args:
            context: SurgicalContext containing violations and target coordinates

        Returns:
            True if all targets are verified, False if any hallucination detected
        

#### _map_violation_to_action
**Parameters**: self, violation
**Returns**: str
**Description**: Map violation constraint to action type.

#### _extract_target_from_violation
**Parameters**: self, violation
**Returns**: str | None
**Description**: Extract target node name from violation.

#### clear_cache
**Parameters**: self
**Description**: Clear the verification cache.

#### get_cache_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics for monitoring.

#### heal
**Parameters**: self, violation



## Function: __init__

**Parameters**: self, context_manager
**Description**: 
        Initialize verification gate.

        Args:
            context_manager: Optional L4ContextManager for shared caching
        



## Function: verify_action

**Parameters**: self, file_path, action_type, target_node
**Returns**: bool
**Description**: 
        Verify that the target node exists in the file before allowing action.

        Args:
            file_path: Path to the file to verify
            action_type: Type of action (e.g., 'delete_import', 'modify_function', 'remove_class')
            target_node: Target node name to verify exists

        Returns:
            True if target exists and action is valid, False otherwise
        



## Function: _verify_target_in_ast

**Parameters**: self, tree, action_type, target_node
**Returns**: bool
**Description**: 
        Verify target node exists in AST based on action type.

        Args:
            tree: Parsed AST tree
            action_type: Type of action to verify
            target_node: Target node name

        Returns:
            True if target exists for the given action type
        



## Function: _verify_import_exists

**Parameters**: self, tree, import_name
**Returns**: bool
**Description**: Verify that an import statement exists.



## Function: _verify_function_exists

**Parameters**: self, tree, func_name
**Returns**: bool
**Description**: Verify that a function definition exists.



## Function: _verify_class_exists

**Parameters**: self, tree, class_name
**Returns**: bool
**Description**: Verify that a class definition exists.



## Function: _verify_variable_exists

**Parameters**: self, tree, var_name
**Returns**: bool
**Description**: Verify that a variable assignment exists.



## Function: _verify_method_exists

**Parameters**: self, tree, method_name
**Returns**: bool
**Description**: Verify that a method exists within any class.



## Function: _verify_any_node_exists

**Parameters**: self, tree, node_name
**Returns**: bool
**Description**: Generic verification - check if any node with matching name exists.



## Function: verify_modification

**Parameters**: self, context
**Returns**: bool
**Description**: 
        Verify all modifications in a SurgicalContext before allowing execution.

        This is the primary method for preventing Epistemic Cascade - it ensures
        that all target nodes actually exist before any surgical changes are made.

        Args:
            context: SurgicalContext containing violations and target coordinates

        Returns:
            True if all targets are verified, False if any hallucination detected
        



## Function: _map_violation_to_action

**Parameters**: self, violation
**Returns**: str
**Description**: Map violation constraint to action type.



## Function: _extract_target_from_violation

**Parameters**: self, violation
**Returns**: str | None
**Description**: Extract target node name from violation.



## Function: clear_cache

**Parameters**: self
**Description**: Clear the verification cache.



## Function: get_cache_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics for monitoring.



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using VerificationGate
verificationgate = VerificationGate()
verificationgate.verify_action()
verificationgate.verify_modification()
```

### Function Usage

```python
# Using __init__
result = __init__(context_manager)
```

```python
# Using verify_action
result = verify_action(file_path, action_type)
```

```python
# Using _verify_target_in_ast
result = _verify_target_in_ast(tree, action_type)
```



---
**Generated**: 2026-03-26T09:39:04.983208
**Type**: api_reference
**Quality**: comprehensive
