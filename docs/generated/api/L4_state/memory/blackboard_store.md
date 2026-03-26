# API Documentation: blackboard_store

**Target Audience**: developers, api_users

# blackboard_store API Documentation

**File**: `blackboard_store.py`
**Classes**: 4
**Functions**: 9

## Classes

- **LeaseResult**
- **SecurityEvent**
- **LeaseEntry**
- **BlackboardStore**

## Functions

- **blackboard_lease_verifier**
- **set** -> None
- **lease** -> LeaseResult
- **get** -> Any
- **delete** -> bool
- **verify_healing_lease** -> LeaseResult
- **log_security_event** -> None
- **_get_lease** -> LeaseEntry | None
- **clear** -> None


## Class: LeaseResult



## Class: SecurityEvent



## Class: LeaseEntry

**Description**: Lease metadata for a Blackboard key.



## Class: BlackboardStore

**Description**: Multi-agent Blackboard KV store with tick-based leases.

    - set(): atomic write with agent_id and commit_tick
    - lease(): acquire exclusive lease with TTL in ticks
    - get(): read value (no lease required)
    - delete(): remove key (requires active lease)
    - All operations use commit_tick, not wall-clock time
    

### Methods

#### set
**Parameters**: self, key, value, agent_id, commit_tick
**Returns**: None
**Description**: Atomically set a key value.

        Args:
            key: Blackboard key
            value: Value to store
            agent_id: Agent performing the write
            commit_tick: Current commit tick (monotonic)
        

#### lease
**Parameters**: self, key, agent_id, ttl_ticks, commit_tick
**Returns**: LeaseResult
**Description**: Acquire an exclusive lease on a key.

        Args:
            key: Blackboard key
            agent_id: Agent requesting lease
            ttl_ticks: Time-to-live in ticks
            commit_tick: Current commit tick

        Returns:
            LeaseResult with success status and expiry tick
        

#### get
**Parameters**: self, key
**Returns**: Any
**Description**: Get the value for a key.

        Args:
            key: Blackboard key

        Returns:
            Stored value or raises KeyError if not found

        Raises:
            KeyError: If key not found
        

#### delete
**Parameters**: self, key, agent_id, commit_tick
**Returns**: bool
**Description**: Delete a key (requires active lease).

        Args:
            key: Blackboard key
            agent_id: Agent requesting deletion
            commit_tick: Current commit tick

        Returns:
            True if deleted, False if lease not held

        Raises:
            KeyError: If key not found
        

#### verify_healing_lease
**Parameters**: self, resource_path, agent_id, commit_tick, operation
**Returns**: LeaseResult
**Description**: Verify lease for healing operations.

        Implements IBlackboardLeaseVerifier.verify_healing_lease.
        

#### log_security_event
**Parameters**: self, event
**Returns**: None
**Description**: Log a security event.

        Implements IBlackboardLeaseVerifier.log_security_event.
        Phase 1: No-op (stub for interface compliance).
        

#### _get_lease
**Parameters**: self, key
**Returns**: LeaseEntry | None
**Description**: Get current lease entry for a key (tests only).

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear all stored keys and leases (tests only).



## Function: blackboard_lease_verifier

**Parameters**: cls
**Description**: Minimal decorator for Phase 1 compliance.



## Function: set

**Parameters**: self, key, value, agent_id, commit_tick
**Returns**: None
**Description**: Atomically set a key value.

        Args:
            key: Blackboard key
            value: Value to store
            agent_id: Agent performing the write
            commit_tick: Current commit tick (monotonic)
        



## Function: lease

**Parameters**: self, key, agent_id, ttl_ticks, commit_tick
**Returns**: LeaseResult
**Description**: Acquire an exclusive lease on a key.

        Args:
            key: Blackboard key
            agent_id: Agent requesting lease
            ttl_ticks: Time-to-live in ticks
            commit_tick: Current commit tick

        Returns:
            LeaseResult with success status and expiry tick
        



## Function: get

**Parameters**: self, key
**Returns**: Any
**Description**: Get the value for a key.

        Args:
            key: Blackboard key

        Returns:
            Stored value or raises KeyError if not found

        Raises:
            KeyError: If key not found
        



## Function: delete

**Parameters**: self, key, agent_id, commit_tick
**Returns**: bool
**Description**: Delete a key (requires active lease).

        Args:
            key: Blackboard key
            agent_id: Agent requesting deletion
            commit_tick: Current commit tick

        Returns:
            True if deleted, False if lease not held

        Raises:
            KeyError: If key not found
        



## Function: verify_healing_lease

**Parameters**: self, resource_path, agent_id, commit_tick, operation
**Returns**: LeaseResult
**Description**: Verify lease for healing operations.

        Implements IBlackboardLeaseVerifier.verify_healing_lease.
        



## Function: log_security_event

**Parameters**: self, event
**Returns**: None
**Description**: Log a security event.

        Implements IBlackboardLeaseVerifier.log_security_event.
        Phase 1: No-op (stub for interface compliance).
        



## Function: _get_lease

**Parameters**: self, key
**Returns**: LeaseEntry | None
**Description**: Get current lease entry for a key (tests only).



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear all stored keys and leases (tests only).



## Usage Examples

### Class Usage

```python
# Using LeaseResult
leaseresult = LeaseResult()
```

```python
# Using SecurityEvent
securityevent = SecurityEvent()
```

```python
# Using LeaseEntry
leaseentry = LeaseEntry()
```

### Function Usage

```python
# Using blackboard_lease_verifier
result = blackboard_lease_verifier(cls)
```

```python
# Using set
result = set(key, value)
```

```python
# Using lease
result = lease(key, agent_id)
```



---
**Generated**: 2026-03-26T09:39:04.554583
**Type**: api_reference
**Quality**: comprehensive
