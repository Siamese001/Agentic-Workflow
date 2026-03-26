# API Documentation: omni_context_engine

**Target Audience**: developers, api_users

# omni_context_engine API Documentation

**File**: `omni_context_engine.py`
**Classes**: 1
**Functions**: 3

## Classes

- **OmniContext** (inherits from SubAtomicAgent)

## Functions

- **__init__**
- **_build_context_buffer**
- **consult** -> str


## Class: OmniContext

**Description**: 
    ROLE: Global Architectural Context. Concatenates all non-excluded .py files
    into a single context buffer for agents to consult.
    

**Inherits from**: SubAtomicAgent

### Methods

#### __init__
**Parameters**: self, context

#### _build_context_buffer
**Parameters**: self
**Description**: Build a concatenated buffer of all Python code.

#### consult
**Parameters**: self, query
**Returns**: str
**Description**: Consult the global context for architectural patterns.



## Function: __init__

**Parameters**: self, context


## Function: _build_context_buffer

**Parameters**: self
**Description**: Build a concatenated buffer of all Python code.



## Function: consult

**Parameters**: self, query
**Returns**: str
**Description**: Consult the global context for architectural patterns.



## Usage Examples

### Class Usage

```python
# Using OmniContext
omnicontext = OmniContext()
omnicontext.consult()
```

### Function Usage

```python
# Using __init__
result = __init__(context)
```

```python
# Using _build_context_buffer
result = _build_context_buffer()
```

```python
# Using consult
result = consult(query)
```



---
**Generated**: 2026-03-26T09:39:04.173088
**Type**: api_reference
**Quality**: comprehensive
