# API Documentation: hitl_gate

**Target Audience**: developers, api_users

# hitl_gate API Documentation

**File**: `hitl_gate.py`
**Classes**: 5
**Functions**: 7

## Classes

- **HitlChoice** (inherits from str, Enum)
- **HitlDecision**
- **HitlRequest**
- **HitlRequiredError** (inherits from RuntimeError)
- **HitlGate**

## Functions

- **_is_protected** -> bool
- **_format_paths** -> str
- **get_hitl_gate** -> HitlGate
- **clear_gate_cache** -> None
- **__init__** -> None
- **request** -> HitlDecision
- **_prompt** -> HitlDecision


## Class: HitlChoice

**Inherits from**: str, Enum



## Class: HitlDecision



## Class: HitlRequest



## Class: HitlRequiredError

**Description**: Raised when a destructive operation is attempted with no TTY available.

    This is a hard abort.  The healing run must stop.  The human must be
    present to approve destructive operations — there is no automated bypass.
    

**Inherits from**: RuntimeError



## Class: HitlGate

**Description**: Central HITL gate.  Use HitlGate.request() for all destructive ops.

    Injection point for tests: pass ``input_fn`` to override stdin reading.
    Set ``_tty_override=True`` in tests to simulate an interactive terminal.
    

### Methods

#### __init__
**Parameters**: self, repo_root
**Returns**: None

#### request
**Parameters**: self, req
**Returns**: HitlDecision
**Description**: Evaluate a destructive operation request and return a decision.

        HITL is mandatory — always prompts when a TTY is present.
        Raises HitlRequiredError when no TTY is available (no silent skip).
        

#### _prompt
**Parameters**: self, req
**Returns**: HitlDecision



## Function: _is_protected

**Parameters**: paths, repo_root
**Returns**: bool
**Description**: Return True if any path's first component is in HITL_PROTECTED_PATHS.



## Function: _format_paths

**Parameters**: paths, limit
**Returns**: str


## Function: get_hitl_gate

**Parameters**: repo_root
**Returns**: HitlGate
**Description**: Return a cached HitlGate for repo_root (or build a new one).



## Function: clear_gate_cache

**Returns**: None
**Description**: Clear singleton cache (for tests).



## Function: __init__

**Parameters**: self, repo_root
**Returns**: None


## Function: request

**Parameters**: self, req
**Returns**: HitlDecision
**Description**: Evaluate a destructive operation request and return a decision.

        HITL is mandatory — always prompts when a TTY is present.
        Raises HitlRequiredError when no TTY is available (no silent skip).
        



## Function: _prompt

**Parameters**: self, req
**Returns**: HitlDecision


## Usage Examples

### Class Usage

```python
# Using HitlChoice
hitlchoice = HitlChoice()
```

```python
# Using HitlDecision
hitldecision = HitlDecision()
```

```python
# Using HitlRequest
hitlrequest = HitlRequest()
```

### Function Usage

```python
# Using _is_protected
result = _is_protected(paths, repo_root)
```

```python
# Using _format_paths
result = _format_paths(paths, limit)
```

```python
# Using get_hitl_gate
result = get_hitl_gate(repo_root)
```



---
**Generated**: 2026-03-26T09:39:04.840774
**Type**: api_reference
**Quality**: comprehensive
