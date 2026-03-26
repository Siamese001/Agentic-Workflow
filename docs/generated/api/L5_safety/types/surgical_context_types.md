# API Documentation: surgical_context_types

**Target Audience**: developers, api_users

# surgical_context_types API Documentation

**File**: `surgical_context_types.py`
**Classes**: 4
**Functions**: 8

## Classes

- **ASTCoordinate**
- **ViolationConstraint**
- **SurgicalContext**
- **SurgicalContextBuilder**

## Functions

- **get_target_node** -> ast.AST | None
- **get_nodes_by_type** -> list[ast.AST]
- **get_line_range** -> tuple[int, int]
- **extract_source_segment** -> str
- **to_dict** -> dict[str, Any]
- **from_dict** -> SurgicalContext
- **__init__**
- **build_context** -> SurgicalContext


## Class: ASTCoordinate

**Description**: Precise AST node coordinate.



## Class: ViolationConstraint

**Description**: Specific constraint that was violated.



## Class: SurgicalContext

**Description**: 
    Comprehensive context for surgical healing operations.

    This structure ensures zero information loss between detection and healing.
    All coordinates are preserved for AST-level mutations.
    

### Methods

#### get_target_node
**Parameters**: self, coordinate
**Returns**: ast.AST | None
**Description**: Get AST node by coordinate.

#### get_nodes_by_type
**Parameters**: self, node_type
**Returns**: list[ast.AST]
**Description**: Get all nodes of a specific type.

#### get_line_range
**Parameters**: self, coordinate
**Returns**: tuple[int, int]
**Description**: Get line range for a coordinate.

#### extract_source_segment
**Parameters**: self, coordinate
**Returns**: str
**Description**: Extract source code for the coordinate.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.

#### from_dict
**Parameters**: cls, data
**Returns**: SurgicalContext
**Description**: Create from dictionary.



## Class: SurgicalContextBuilder

**Description**: Builder for creating SurgicalContext from detection results.

### Methods

#### __init__
**Parameters**: self, file_path, detector_agent, detection_method

#### build_context
**Parameters**: self, violation_id, violations, target_nodes
**Returns**: SurgicalContext
**Description**: Build SurgicalContext from detection results.



## Function: get_target_node

**Parameters**: self, coordinate
**Returns**: ast.AST | None
**Description**: Get AST node by coordinate.



## Function: get_nodes_by_type

**Parameters**: self, node_type
**Returns**: list[ast.AST]
**Description**: Get all nodes of a specific type.



## Function: get_line_range

**Parameters**: self, coordinate
**Returns**: tuple[int, int]
**Description**: Get line range for a coordinate.



## Function: extract_source_segment

**Parameters**: self, coordinate
**Returns**: str
**Description**: Extract source code for the coordinate.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: from_dict

**Parameters**: cls, data
**Returns**: SurgicalContext
**Description**: Create from dictionary.



## Function: __init__

**Parameters**: self, file_path, detector_agent, detection_method


## Function: build_context

**Parameters**: self, violation_id, violations, target_nodes
**Returns**: SurgicalContext
**Description**: Build SurgicalContext from detection results.



## Usage Examples

### Class Usage

```python
# Using ASTCoordinate
astcoordinate = ASTCoordinate()
```

```python
# Using ViolationConstraint
violationconstraint = ViolationConstraint()
```

```python
# Using SurgicalContext
surgicalcontext = SurgicalContext()
surgicalcontext.get_target_node()
surgicalcontext.get_nodes_by_type()
```

### Function Usage

```python
# Using get_target_node
result = get_target_node(coordinate)
```

```python
# Using get_nodes_by_type
result = get_nodes_by_type(node_type)
```

```python
# Using get_line_range
result = get_line_range(coordinate)
```



---
**Generated**: 2026-03-26T09:39:05.586316
**Type**: api_reference
**Quality**: comprehensive
