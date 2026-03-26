# API Documentation: docker_sandbox

**Target Audience**: developers, api_users

# docker_sandbox API Documentation

**File**: `docker_sandbox.py`
**Classes**: 1
**Functions**: 2

## Classes

- **DockerSandbox**

## Functions

- **__init__**
- **run_code** -> dict[str, Any]


## Class: DockerSandbox

**Description**: 
    L2 Execution: The Secure Sandbox.
    Executes generated code in an isolated, temporary environment.
    

### Methods

#### __init__
**Parameters**: self, config

#### run_code
**Parameters**: self, code
**Returns**: dict[str, Any]
**Description**: Executes code and returns the result/stdout.



## Function: __init__

**Parameters**: self, config


## Function: run_code

**Parameters**: self, code
**Returns**: dict[str, Any]
**Description**: Executes code and returns the result/stdout.



## Usage Examples

### Class Usage

```python
# Using DockerSandbox
dockersandbox = DockerSandbox()
dockersandbox.run_code()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using run_code
result = run_code(code)
```



---
**Generated**: 2026-03-26T09:39:03.688110
**Type**: api_reference
**Quality**: comprehensive
