# API Documentation: agent_dispatch_registry

**Target Audience**: developers, api_users

# agent_dispatch_registry API Documentation

**File**: `agent_dispatch_registry.py`
**Classes**: 5
**Functions**: 12

## Classes

- **DispatchDeniedError** (inherits from PermissionError)
- **UnregisteredAgentError** (inherits from LookupError)
- **DispatchRecord**
- **_RegisteredInstance**
- **AgentDispatchRegistry**

## Functions

- **_extract_token_id** -> str
- **get_agent_dispatch_registry** -> AgentDispatchRegistry
- **reset_agent_dispatch_registry** -> None
- **__init__** -> None
- **register_instance** -> None
- **dispatch** -> Any
- **dispatch_by_name** -> Any
- **_check_capability** -> tuple[bool, str]
- **get_dispatch_ledger** -> list[DispatchRecord]
- **get_stats** -> dict[str, Any]
- **set_enforce_mode** -> None
- **set_guardrail_enforce** -> None


## Class: DispatchDeniedError

**Description**: Raised when dispatch is denied due to capability or token failure.

**Inherits from**: PermissionError



## Class: UnregisteredAgentError

**Description**: Raised when caller or target is not registered in the capability registry.

**Inherits from**: LookupError



## Class: DispatchRecord

**Description**: Immutable record of a single typed agent dispatch.



## Class: _RegisteredInstance

**Description**: Internal record binding an agent name to its live instance.



## Class: AgentDispatchRegistry

**Description**: Typed dispatch layer for L3 agent-to-agent handoffs.

    Shim mode (default)
    -------------------
    All dispatches succeed via ``getattr`` regardless of capability check
    result. Failures are logged as WARN but do not block execution.
    This is Wave 2 policy: warn for one sprint, then enforce.

    Enforce mode (shim_mode=False)
    ------------------------------
    Dispatches to unregistered agents or without a valid capability token
    raise ``DispatchDeniedError``. Enable at Wave 2 acceptance gate.
    

### Methods

#### __init__
**Parameters**: self, capability_registry, shim_mode, guardrail_gate, guardrail_mode
**Returns**: None
**Description**: Initialise the dispatch registry.

        Args:
            capability_registry: Capability registry for handoff validation.
            shim_mode: If True, capability failures warn but do not block.
            guardrail_gate: Pre-execution guardrail gate. Defaults to process-level gate.
            guardrail_mode: ``"warn"`` (log only) or ``"enforce"`` (raise on DENY).
                            Wave 3 hardening: start ``warn``, switch to ``enforce`` per sublayer.
        

#### register_instance
**Parameters**: self, agent_name, instance, capabilities
**Returns**: None
**Description**: Bind a live agent instance to its registered name.

        The instance is looked up by name on every ``dispatch()`` call.
        Capabilities list is informational and supplements the capability registry.
        

#### dispatch
**Parameters**: self, caller, target_instance, method, args, kwargs, capability_token
**Returns**: Any
**Description**: Dispatch ``target_instance.method(*args, **kwargs)`` via the governed path.

        Emits an ``agent_executes_agent`` structured log record on success.

        Args:
            caller: Name of the dispatching agent (for graph edge ``src``).
            target_instance: The agent object receiving the call.
            method: Method name to invoke.
            args: Positional arguments.
            kwargs: Keyword arguments.
            capability_token: Optional token object (must have ``.token_id`` attr
                              or be a non-empty string).

        Returns:
            The return value of ``target_instance.method(*args, **kwargs)``.

        Raises:
            DispatchDeniedError: In enforce mode if capability check fails.
            AttributeError: If the method does not exist on the target.
        

#### dispatch_by_name
**Parameters**: self, caller, target_name, method, args, kwargs, capability_token
**Returns**: Any
**Description**: Dispatch to a registered instance by name.

        Raises:
            UnregisteredAgentError: If ``target_name`` is not registered.
        

#### _check_capability
**Parameters**: self, caller, target_class, method, capability_token
**Returns**: tuple[bool, str]
**Description**: Return (permitted, reason). permitted=True means dispatch may proceed.

#### get_dispatch_ledger
**Parameters**: self
**Returns**: list[DispatchRecord]
**Description**: Return append-only copy of all dispatch records.

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return dispatch statistics.

#### set_enforce_mode
**Parameters**: self
**Returns**: None
**Description**: Disable shim fallback — enable at Wave 2 acceptance gate.

#### set_guardrail_enforce
**Parameters**: self
**Returns**: None
**Description**: Switch guardrail from warn to enforce — enable at Wave 3 acceptance gate.



## Function: _extract_token_id

**Parameters**: capability_token
**Returns**: str
**Description**: Extract a string token_id from various token shapes.



## Function: get_agent_dispatch_registry

**Returns**: AgentDispatchRegistry
**Description**: Return the singleton AgentDispatchRegistry (shim mode by default).



## Function: reset_agent_dispatch_registry

**Returns**: None
**Description**: Reset singleton (for testing).



## Function: __init__

**Parameters**: self, capability_registry, shim_mode, guardrail_gate, guardrail_mode
**Returns**: None
**Description**: Initialise the dispatch registry.

        Args:
            capability_registry: Capability registry for handoff validation.
            shim_mode: If True, capability failures warn but do not block.
            guardrail_gate: Pre-execution guardrail gate. Defaults to process-level gate.
            guardrail_mode: ``"warn"`` (log only) or ``"enforce"`` (raise on DENY).
                            Wave 3 hardening: start ``warn``, switch to ``enforce`` per sublayer.
        



## Function: register_instance

**Parameters**: self, agent_name, instance, capabilities
**Returns**: None
**Description**: Bind a live agent instance to its registered name.

        The instance is looked up by name on every ``dispatch()`` call.
        Capabilities list is informational and supplements the capability registry.
        



## Function: dispatch

**Parameters**: self, caller, target_instance, method, args, kwargs, capability_token
**Returns**: Any
**Description**: Dispatch ``target_instance.method(*args, **kwargs)`` via the governed path.

        Emits an ``agent_executes_agent`` structured log record on success.

        Args:
            caller: Name of the dispatching agent (for graph edge ``src``).
            target_instance: The agent object receiving the call.
            method: Method name to invoke.
            args: Positional arguments.
            kwargs: Keyword arguments.
            capability_token: Optional token object (must have ``.token_id`` attr
                              or be a non-empty string).

        Returns:
            The return value of ``target_instance.method(*args, **kwargs)``.

        Raises:
            DispatchDeniedError: In enforce mode if capability check fails.
            AttributeError: If the method does not exist on the target.
        



## Function: dispatch_by_name

**Parameters**: self, caller, target_name, method, args, kwargs, capability_token
**Returns**: Any
**Description**: Dispatch to a registered instance by name.

        Raises:
            UnregisteredAgentError: If ``target_name`` is not registered.
        



## Function: _check_capability

**Parameters**: self, caller, target_class, method, capability_token
**Returns**: tuple[bool, str]
**Description**: Return (permitted, reason). permitted=True means dispatch may proceed.



## Function: get_dispatch_ledger

**Parameters**: self
**Returns**: list[DispatchRecord]
**Description**: Return append-only copy of all dispatch records.



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return dispatch statistics.



## Function: set_enforce_mode

**Parameters**: self
**Returns**: None
**Description**: Disable shim fallback — enable at Wave 2 acceptance gate.



## Function: set_guardrail_enforce

**Parameters**: self
**Returns**: None
**Description**: Switch guardrail from warn to enforce — enable at Wave 3 acceptance gate.



## Usage Examples

### Class Usage

```python
# Using DispatchDeniedError
dispatchdeniederror = DispatchDeniedError()
```

```python
# Using UnregisteredAgentError
unregisteredagenterror = UnregisteredAgentError()
```

```python
# Using DispatchRecord
dispatchrecord = DispatchRecord()
```

### Function Usage

```python
# Using _extract_token_id
result = _extract_token_id(capability_token)
```

```python
# Using get_agent_dispatch_registry
result = get_agent_dispatch_registry()
```

```python
# Using reset_agent_dispatch_registry
result = reset_agent_dispatch_registry()
```



---
**Generated**: 2026-03-26T09:39:04.336441
**Type**: api_reference
**Quality**: comprehensive
