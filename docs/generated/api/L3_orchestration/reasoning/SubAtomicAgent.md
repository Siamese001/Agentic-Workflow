# API Documentation: SubAtomicAgent

**Target Audience**: developers, api_users

# SubAtomicAgent API Documentation

**File**: `SubAtomicAgent.py`
**Classes**: 3
**Functions**: 20

## Classes

- **SubAtomicAgent** (inherits from SovereignBaseAgent)
- **SubAtomicAgent_impl**
- **nesting_depth_visitor** (inherits from <ast.Attribute object at 0x000001CBFADA9410>)

## Functions

- **get_SubAtomicAgent** -> Any
- **heal** -> dict
- **heal_repository** -> dict[str, int]
- **__init__**
- **can_run** -> bool
- **execute** -> None
- **__init__**
- **_report_violation_message** -> str
- **_generic_visit_with_depth**
- **visit_FunctionDef**
- **visit_AsyncFunctionDef**
- **visit_ClassDef**
- **visit_If**
- **visit_For**
- **visit_AsyncFor**
- **visit_While**
- **visit_With**
- **visit_AsyncWith**
- **visit_Try**
- **visit_ExceptHandler**


## Class: SubAtomicAgent

**Description**: Base class stub for structural agents.

**Inherits from**: SovereignBaseAgent

### Methods

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: 
        Heal violations in subatomic agent logic.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with status, details, artifacts, and errors
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L1 cognition - operational only.



## Class: SubAtomicAgent_impl

**Description**: Brief description of functionality and purpose.

### Methods

#### __init__
**Parameters**: self, ctx, name

#### can_run
**Parameters**: self
**Returns**: bool

#### execute
**Parameters**: self
**Returns**: None



## Class: nesting_depth_visitor

**Description**: 
    A visitor to calculate and report violations for excessive nesting depth within an AST.
    

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, max_allowed_depth, filepath

#### _report_violation_message
**Parameters**: self, node, current_depth_val
**Returns**: str
**Description**: 
        Constructs the Violation message string, flattening expressions to reduce syntactic nesting.
        

#### _generic_visit_with_depth
**Parameters**: self, node

#### visit_FunctionDef
**Parameters**: self, node

#### visit_AsyncFunctionDef
**Parameters**: self, node

#### visit_ClassDef
**Parameters**: self, node

#### visit_If
**Parameters**: self, node

#### visit_For
**Parameters**: self, node

#### visit_AsyncFor
**Parameters**: self, node

#### visit_While
**Parameters**: self, node

#### visit_With
**Parameters**: self, node

#### visit_AsyncWith
**Parameters**: self, node

#### visit_Try
**Parameters**: self, node

#### visit_ExceptHandler
**Parameters**: self, node



## Function: get_SubAtomicAgent

**Returns**: Any
**Description**: Brief description of functionality and purpose.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: 
        Heal violations in subatomic agent logic.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with status, details, artifacts, and errors
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L1 cognition - operational only.



## Function: __init__

**Parameters**: self, ctx, name


## Function: can_run

**Parameters**: self
**Returns**: bool


## Function: execute

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, max_allowed_depth, filepath


## Function: _report_violation_message

**Parameters**: self, node, current_depth_val
**Returns**: str
**Description**: 
        Constructs the Violation message string, flattening expressions to reduce syntactic nesting.
        



## Function: _generic_visit_with_depth

**Parameters**: self, node


## Function: visit_FunctionDef

**Parameters**: self, node


## Function: visit_AsyncFunctionDef

**Parameters**: self, node


## Function: visit_ClassDef

**Parameters**: self, node


## Function: visit_If

**Parameters**: self, node


## Function: visit_For

**Parameters**: self, node


## Function: visit_AsyncFor

**Parameters**: self, node


## Function: visit_While

**Parameters**: self, node


## Function: visit_With

**Parameters**: self, node


## Function: visit_AsyncWith

**Parameters**: self, node


## Function: visit_Try

**Parameters**: self, node


## Function: visit_ExceptHandler

**Parameters**: self, node


## Usage Examples

### Class Usage

```python
# Using SubAtomicAgent
subatomicagent = SubAtomicAgent()
subatomicagent.heal()
subatomicagent.heal_repository()
```

```python
# Using SubAtomicAgent_impl
subatomicagent_impl = SubAtomicAgent_impl()
subatomicagent_impl.can_run()
subatomicagent_impl.execute()
```

```python
# Using nesting_depth_visitor
nesting_depth_visitor = nesting_depth_visitor()
nesting_depth_visitor.visit_FunctionDef()
nesting_depth_visitor.visit_AsyncFunctionDef()
```

### Function Usage

```python
# Using get_SubAtomicAgent
result = get_SubAtomicAgent()
```

```python
# Using heal
result = heal(violation)
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:04.314665
**Type**: api_reference
**Quality**: comprehensive
