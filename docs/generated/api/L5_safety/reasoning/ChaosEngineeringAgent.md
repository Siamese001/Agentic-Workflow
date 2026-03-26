# API Documentation: ChaosEngineeringAgent

**Target Audience**: developers, api_users

# ChaosEngineeringAgent API Documentation

**File**: `ChaosEngineeringAgent.py`
**Classes**: 1
**Functions**: 11

## Classes

- **ChaosEngineeringAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__**
- **_test_network_failure** -> dict[str, Any]
- **_test_high_latency** -> dict[str, Any]
- **_test_resource_exhaustion** -> dict[str, Any]
- **_test_cascading_failure** -> dict[str, Any]
- **_test_timeout** -> dict[str, Any]
- **_test_partial_failure** -> dict[str, Any]
- **_test_recovery** -> dict[str, Any]
- **_run_self_tests** -> bool
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: ChaosEngineeringAgent

**Description**: 
    Red team agent specializing in chaos engineering and fault injection.
    Tests system resilience under:
    - Network failures and latency
    - Resource exhaustion (memory, CPU, tokens)
    - Cascading failures
    - Timeout scenarios
    - Partial failures and degradation
    - Recovery and self-healing
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self

#### _test_network_failure
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under network failure.

#### _test_high_latency
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under high latency.

#### _test_resource_exhaustion
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under resource exhaustion.

#### _test_cascading_failure
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under cascading failures.

#### _test_timeout
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under timeout conditions.

#### _test_partial_failure
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under partial failures.

#### _test_recovery
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system recovery and self-healing.

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Validate agent structure.

#### heal_repository
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: Repository healing with parent chain invocation.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal chaos engineering violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details.

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __post_init__

**Parameters**: self


## Function: _test_network_failure

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under network failure.



## Function: _test_high_latency

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under high latency.



## Function: _test_resource_exhaustion

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under resource exhaustion.



## Function: _test_cascading_failure

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under cascading failures.



## Function: _test_timeout

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under timeout conditions.



## Function: _test_partial_failure

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system behavior under partial failures.



## Function: _test_recovery

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system recovery and self-healing.



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Validate agent structure.



## Function: heal_repository

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: Repository healing with parent chain invocation.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal chaos engineering violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details.

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using ChaosEngineeringAgent
chaosengineeringagent = ChaosEngineeringAgent()
chaosengineeringagent.heal_repository()
chaosengineeringagent.heal()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _test_network_failure
result = _test_network_failure()
```

```python
# Using _test_high_latency
result = _test_high_latency()
```



---
**Generated**: 2026-03-26T09:39:05.063460
**Type**: api_reference
**Quality**: comprehensive
