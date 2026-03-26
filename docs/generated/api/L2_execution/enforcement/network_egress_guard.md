# API Documentation: network_egress_guard

**Target Audience**: developers, api_users

# network_egress_guard API Documentation

**File**: `network_egress_guard.py`
**Classes**: 1
**Functions**: 8

## Classes

- **NetworkEgressViolation** (inherits from Exception)

## Functions

- **is_llm_endpoint** -> bool
- **check_network_egress_allowed** -> bool
- **_is_in_gateway_context** -> bool
- **_guarded_connect** -> None
- **install_egress_guard** -> None
- **uninstall_egress_guard** -> None
- **simulate_direct_llm_request** -> None
- **test_egress_guard** -> bool


## Class: NetworkEgressViolation

**Description**: Raised when unauthorized network egress to LLM endpoint is detected.

**Inherits from**: Exception



## Function: is_llm_endpoint

**Parameters**: hostname, port
**Returns**: bool
**Description**: Check if hostname:port matches known LLM endpoint patterns.

    Args:
        hostname: Hostname to check
        port: Optional port number

    Returns:
        True if it's an LLM endpoint, False otherwise
    



## Function: check_network_egress_allowed

**Parameters**: hostname, port, caller_module
**Returns**: bool
**Description**: Check if network egress to LLM endpoint is allowed (REQ-414).

    Args:
        hostname: Target hostname
        port: Target port
        caller_module: Module attempting the connection

    Returns:
        True if allowed, False otherwise

    Raises:
        NetworkEgressViolation: If attempting unauthorized LLM endpoint access
    



## Function: _is_in_gateway_context

**Returns**: bool
**Description**: Check if current execution context is within SovereignLLMGateway.

    Returns:
        True if in gateway context, False otherwise
    



## Function: _guarded_connect

**Parameters**: self, address
**Returns**: None
**Description**: Guarded socket.connect that checks egress permissions.



## Function: install_egress_guard

**Returns**: None
**Description**: Install network egress guard (REQ-414).

    This monkey-patches socket.connect to enforce the egress policy.
    Should be called during system initialization.
    



## Function: uninstall_egress_guard

**Returns**: None
**Description**: Uninstall network egress guard.

    Restores original socket.connect behavior.
    



## Function: simulate_direct_llm_request

**Parameters**: hostname, port
**Returns**: None
**Description**: Simulate a direct LLM request that should be blocked.

    Args:
        hostname: LLM endpoint hostname
        port: LLM endpoint port

    Raises:
        NetworkEgressViolation: Always raised unless guard is disabled
    



## Function: test_egress_guard

**Returns**: bool
**Description**: Test if egress guard is properly installed.

    Returns:
        True if guard is working, False otherwise
    



## Usage Examples

### Class Usage

```python
# Using NetworkEgressViolation
networkegressviolation = NetworkEgressViolation()
```

### Function Usage

```python
# Using is_llm_endpoint
result = is_llm_endpoint(hostname, port)
```

```python
# Using check_network_egress_allowed
result = check_network_egress_allowed(hostname, port)
```

```python
# Using _is_in_gateway_context
result = _is_in_gateway_context()
```



---
**Generated**: 2026-03-26T09:39:03.716507
**Type**: api_reference
**Quality**: comprehensive
