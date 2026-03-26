# API Documentation: AdapterBase

**Target Audience**: developers, api_users

# AdapterBase API Documentation

**File**: `AdapterBase.py`
**Classes**: 4
**Functions**: 18

## Classes

- **AdapterContext**
- **AdapterResult**
- **AdapterBase** (inherits from ABC, <ast.Subscript object at 0x000001CBFCC42D10>)
- **HealingAdapter** (inherits from <ast.Subscript object at 0x000001CBFB9F5450>)

## Functions

- **to_dict** -> dict[str, Any]
- **__init__**
- **legacy_agent** -> T
- **circuit_breaker** -> CircuitBreaker
- **_get_verification_gate**
- **_execute_legacy** -> Any
- **_validate_input** -> bool
- **_validate_output** -> bool
- **_pre_execute_hook** -> AdapterResult | None
- **_post_execute_hook** -> Any
- **_on_error** -> AdapterResult | None
- **_log_audit** -> None
- **execute** -> AdapterResult
- **get_audit_log** -> list[dict[str, Any]]
- **clear_audit_log** -> None
- **get_status** -> dict[str, Any]
- **__init__**
- **verify_healing_target** -> bool


## Class: AdapterContext

**Description**: Context passed through adapter chain.



## Class: AdapterResult

**Description**: Standardized result from adapter operations.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: AdapterBase

**Description**: 
    Base class for V10-compliant Legacy Adapters.

    Implements the Bridge Pattern per V10 specification:
    - Wraps legacy/orphan agents without modification
    - Injects V10 compliance (circuit breaker, validation, audit)
    - Preserves exact legacy behavior

    Usage:
        class EmbeddingAdapter(AdapterBase[EmbeddingSovereignAgent]):
            def __init__(self, legacy_agent: EmbeddingSovereignAgent):
                super().__init__(legacy_agent, "embedding_service")

            def _execute_legacy(self, context, *args, **kwargs):
                return self._legacy_agent.get_embedding(*args, **kwargs)

            def _validate_input(self, context, *args, **kwargs):
                # V10 validation logic
                return True

            def _validate_output(self, result, context):
                # V10 output validation
                return True
    

**Inherits from**: ABC, Generic[T]

### Methods

#### __init__
**Parameters**: self, legacy_agent, service_name, circuit_breaker_config
**Description**: 
        Initialize adapter with legacy agent.

        Args:
            legacy_agent: The orphan agent to wrap
            service_name: Name for circuit breaker and logging
            circuit_breaker_config: Optional circuit breaker configuration
        

#### legacy_agent
**Parameters**: self
**Returns**: T
**Description**: Access the wrapped legacy agent (read-only).

#### circuit_breaker
**Parameters**: self
**Returns**: CircuitBreaker
**Description**: Access the circuit breaker for this adapter.

#### _get_verification_gate
**Parameters**: self
**Description**: Lazy-load verification gate to avoid circular imports.

#### _execute_legacy
**Parameters**: self, context
**Returns**: Any
**Description**: 
        Execute the legacy agent's operation.

        Subclasses MUST implement this to call the appropriate
        legacy agent method.

        Args:
            context: Adapter context with request metadata
            *args: Positional arguments for legacy method
            **kwargs: Keyword arguments for legacy method

        Returns:
            Raw result from legacy agent
        

#### _validate_input
**Parameters**: self, context
**Returns**: bool
**Description**: 
        V10 Input validation before legacy execution.

        Override to add input validation. Default: allow all.

        Args:
            context: Adapter context
            *args: Input arguments
            **kwargs: Input keyword arguments

        Returns:
            True if input is valid, False to reject
        

#### _validate_output
**Parameters**: self, result, context
**Returns**: bool
**Description**: 
        V10 Output validation after legacy execution.

        Override to add output validation. Default: allow all.

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        

#### _pre_execute_hook
**Parameters**: self, context
**Returns**: AdapterResult | None
**Description**: 
        Hook called before execution.

        Override to add pre-execution logic. Return AdapterResult
        to short-circuit execution.

        Args:
            context: Adapter context
            *args: Input arguments
            **kwargs: Input keyword arguments

        Returns:
            None to continue, AdapterResult to short-circuit
        

#### _post_execute_hook
**Parameters**: self, result, context
**Returns**: Any
**Description**: 
        Hook called after successful execution.

        Override to transform or enrich results.

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            Transformed result
        

#### _on_error
**Parameters**: self, error, context
**Returns**: AdapterResult | None
**Description**: 
        Error handler for legacy execution failures.

        Override to customize error handling. Default: re-raise.

        Args:
            error: Exception from legacy execution
            context: Adapter context

        Returns:
            AdapterResult to return instead of raising, or None to raise
        

#### _log_audit
**Parameters**: self, action, context, result, error
**Returns**: None
**Description**: Log to audit trail for V10 observability.

#### execute
**Parameters**: self, context
**Returns**: AdapterResult
**Description**: 
        Execute the adapted operation with V10 compliance.

        This is the main entry point that:
        1. Checks circuit breaker state
        2. Validates input (V10 guardrail)
        3. Calls pre-execute hook
        4. Executes legacy agent
        5. Validates output (V10 guardrail)
        6. Calls post-execute hook
        7. Records to audit trail

        Args:
            context: Optional adapter context (created if not provided)
            *args: Arguments for legacy method
            **kwargs: Keyword arguments for legacy method

        Returns:
            AdapterResult with operation outcome
        

#### get_audit_log
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get the audit log for this adapter.

#### clear_audit_log
**Parameters**: self
**Returns**: None
**Description**: Clear the audit log.

#### get_status
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get adapter status for dashboard.



## Class: HealingAdapter

**Description**: 
    Specialized adapter for healing operations.

    Adds V10 healing-specific logic:
    - Verification gate integration
    - Atomic execution support
    - Symmetric AST manifest handling
    

**Inherits from**: AdapterBase[T]

### Methods

#### __init__
**Parameters**: self, legacy_agent, service_name, project_root

#### verify_healing_target
**Parameters**: self, file_path, action_type, target_node
**Returns**: bool
**Description**: 
        Verify healing target exists before execution.

        Per V10 Validation Gate specification.

        Args:
            file_path: File to verify
            action_type: Type of healing action
            target_node: Target node name

        Returns:
            True if target exists, False if hallucinated
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: __init__

**Parameters**: self, legacy_agent, service_name, circuit_breaker_config
**Description**: 
        Initialize adapter with legacy agent.

        Args:
            legacy_agent: The orphan agent to wrap
            service_name: Name for circuit breaker and logging
            circuit_breaker_config: Optional circuit breaker configuration
        



## Function: legacy_agent

**Parameters**: self
**Returns**: T
**Description**: Access the wrapped legacy agent (read-only).



## Function: circuit_breaker

**Parameters**: self
**Returns**: CircuitBreaker
**Description**: Access the circuit breaker for this adapter.



## Function: _get_verification_gate

**Parameters**: self
**Description**: Lazy-load verification gate to avoid circular imports.



## Function: _execute_legacy

**Parameters**: self, context
**Returns**: Any
**Description**: 
        Execute the legacy agent's operation.

        Subclasses MUST implement this to call the appropriate
        legacy agent method.

        Args:
            context: Adapter context with request metadata
            *args: Positional arguments for legacy method
            **kwargs: Keyword arguments for legacy method

        Returns:
            Raw result from legacy agent
        



## Function: _validate_input

**Parameters**: self, context
**Returns**: bool
**Description**: 
        V10 Input validation before legacy execution.

        Override to add input validation. Default: allow all.

        Args:
            context: Adapter context
            *args: Input arguments
            **kwargs: Input keyword arguments

        Returns:
            True if input is valid, False to reject
        



## Function: _validate_output

**Parameters**: self, result, context
**Returns**: bool
**Description**: 
        V10 Output validation after legacy execution.

        Override to add output validation. Default: allow all.

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        



## Function: _pre_execute_hook

**Parameters**: self, context
**Returns**: AdapterResult | None
**Description**: 
        Hook called before execution.

        Override to add pre-execution logic. Return AdapterResult
        to short-circuit execution.

        Args:
            context: Adapter context
            *args: Input arguments
            **kwargs: Input keyword arguments

        Returns:
            None to continue, AdapterResult to short-circuit
        



## Function: _post_execute_hook

**Parameters**: self, result, context
**Returns**: Any
**Description**: 
        Hook called after successful execution.

        Override to transform or enrich results.

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            Transformed result
        



## Function: _on_error

**Parameters**: self, error, context
**Returns**: AdapterResult | None
**Description**: 
        Error handler for legacy execution failures.

        Override to customize error handling. Default: re-raise.

        Args:
            error: Exception from legacy execution
            context: Adapter context

        Returns:
            AdapterResult to return instead of raising, or None to raise
        



## Function: _log_audit

**Parameters**: self, action, context, result, error
**Returns**: None
**Description**: Log to audit trail for V10 observability.



## Function: execute

**Parameters**: self, context
**Returns**: AdapterResult
**Description**: 
        Execute the adapted operation with V10 compliance.

        This is the main entry point that:
        1. Checks circuit breaker state
        2. Validates input (V10 guardrail)
        3. Calls pre-execute hook
        4. Executes legacy agent
        5. Validates output (V10 guardrail)
        6. Calls post-execute hook
        7. Records to audit trail

        Args:
            context: Optional adapter context (created if not provided)
            *args: Arguments for legacy method
            **kwargs: Keyword arguments for legacy method

        Returns:
            AdapterResult with operation outcome
        



## Function: get_audit_log

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get the audit log for this adapter.



## Function: clear_audit_log

**Parameters**: self
**Returns**: None
**Description**: Clear the audit log.



## Function: get_status

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get adapter status for dashboard.



## Function: __init__

**Parameters**: self, legacy_agent, service_name, project_root


## Function: verify_healing_target

**Parameters**: self, file_path, action_type, target_node
**Returns**: bool
**Description**: 
        Verify healing target exists before execution.

        Per V10 Validation Gate specification.

        Args:
            file_path: File to verify
            action_type: Type of healing action
            target_node: Target node name

        Returns:
            True if target exists, False if hallucinated
        



## Usage Examples

### Class Usage

```python
# Using AdapterContext
adaptercontext = AdapterContext()
```

```python
# Using AdapterResult
adapterresult = AdapterResult()
adapterresult.to_dict()
```

```python
# Using AdapterBase
adapterbase = AdapterBase()
adapterbase.legacy_agent()
adapterbase.circuit_breaker()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using __init__
result = __init__(legacy_agent, service_name)
```

```python
# Using legacy_agent
result = legacy_agent()
```



---
**Generated**: 2026-03-26T09:39:04.758465
**Type**: api_reference
**Quality**: comprehensive
