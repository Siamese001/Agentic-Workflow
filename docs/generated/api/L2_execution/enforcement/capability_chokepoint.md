# API Documentation: capability_chokepoint

**Target Audience**: developers, api_users

# capability_chokepoint API Documentation

**File**: `capability_chokepoint.py`
**Classes**: 1
**Functions**: 8

## Classes

- **CapabilityChokepoint**

## Functions

- **authorize_and_execute** -> T
- **get_chokepoint** -> CapabilityChokepoint
- **reset_chokepoint** -> None
- **__init__** -> None
- **decisions** -> list[CapabilityDecisionArtifact]
- **freeze** -> None
- **issue_token** -> None
- **authorize_and_execute** -> T


## Class: CapabilityChokepoint

**Description**: Singleton-style chokepoint enforcer for the L2 execution boundary.

    Tracks all decisions emitted during the lifetime of this instance.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### decisions
**Parameters**: self
**Returns**: list[CapabilityDecisionArtifact]
**Description**: All decisions emitted through this chokepoint.

#### freeze
**Parameters**: self
**Returns**: None
**Description**: REQ-091: Tier III freeze — token issuance and execution blocked.

#### issue_token
**Parameters**: self, scope, trace_id
**Returns**: None
**Description**: REQ-091: Issue a capability token for a given scope.

        Raises PermissionError if the chokepoint is frozen.
        

#### authorize_and_execute
**Parameters**: self
**Returns**: T
**Description**: Single L2 execution chokepoint — P5.1 enforcement.

        Args:
            token: CapabilityTokenArtifact. None => FAIL-CLOSED.
            fn: The callable to execute on ALLOW.
            args: Positional arguments for fn.
            kwargs: Keyword arguments for fn.
            tool_name: Name of the tool being invoked.
            action: Action being performed.
            requested_resource: Resource path being accessed.
            required_permission: Permission code required.
            semantic_clock: Current semantic clock snapshot.

        Returns:
            Result of fn(*args, **kwargs) on ALLOW.

        Raises:
            PermissionError: On DENY or missing/invalid token (FAIL-CLOSED).
        



## Function: authorize_and_execute

**Returns**: T
**Description**: Module-level entry — delegates to the singleton CapabilityChokepoint.

    This is the ONLY function external callers should use for L2 execution.
    



## Function: get_chokepoint

**Returns**: CapabilityChokepoint
**Description**: Return the module-level singleton for inspection/testing.



## Function: reset_chokepoint

**Returns**: None
**Description**: Reset the singleton (testing only).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: decisions

**Parameters**: self
**Returns**: list[CapabilityDecisionArtifact]
**Description**: All decisions emitted through this chokepoint.



## Function: freeze

**Parameters**: self
**Returns**: None
**Description**: REQ-091: Tier III freeze — token issuance and execution blocked.



## Function: issue_token

**Parameters**: self, scope, trace_id
**Returns**: None
**Description**: REQ-091: Issue a capability token for a given scope.

        Raises PermissionError if the chokepoint is frozen.
        



## Function: authorize_and_execute

**Parameters**: self
**Returns**: T
**Description**: Single L2 execution chokepoint — P5.1 enforcement.

        Args:
            token: CapabilityTokenArtifact. None => FAIL-CLOSED.
            fn: The callable to execute on ALLOW.
            args: Positional arguments for fn.
            kwargs: Keyword arguments for fn.
            tool_name: Name of the tool being invoked.
            action: Action being performed.
            requested_resource: Resource path being accessed.
            required_permission: Permission code required.
            semantic_clock: Current semantic clock snapshot.

        Returns:
            Result of fn(*args, **kwargs) on ALLOW.

        Raises:
            PermissionError: On DENY or missing/invalid token (FAIL-CLOSED).
        



## Usage Examples

### Class Usage

```python
# Using CapabilityChokepoint
capabilitychokepoint = CapabilityChokepoint()
capabilitychokepoint.decisions()
capabilitychokepoint.freeze()
```

### Function Usage

```python
# Using authorize_and_execute
result = authorize_and_execute()
```

```python
# Using get_chokepoint
result = get_chokepoint()
```

```python
# Using reset_chokepoint
result = reset_chokepoint()
```



---
**Generated**: 2026-03-26T09:39:03.681782
**Type**: api_reference
**Quality**: comprehensive
