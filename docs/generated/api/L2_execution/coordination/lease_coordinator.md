# API Documentation: lease_coordinator

**Target Audience**: developers, api_users

# lease_coordinator API Documentation

**File**: `lease_coordinator.py`
**Classes**: 2
**Functions**: 12

## Classes

- **LeaseCoordinator**
- **IdempotencyStore**

## Functions

- **get_lease_coordinator** -> LeaseCoordinator
- **get_idempotency_store** -> IdempotencyStore
- **__init__** -> None
- **acquire** -> bool
- **release** -> bool
- **is_held** -> bool
- **holder_info** -> dict[str, Any] | None
- **__init__** -> None
- **get** -> bytes | None
- **set** -> None
- **exists** -> bool
- **invalidate** -> None


## Class: LeaseCoordinator

**Description**: Cross-process execution-lease manager (DB 1, short TTLs).

    Usage pattern::

        lc = LeaseCoordinator()
        acquired = lc.acquire("plan-abc123", holder_id="worker-1",
                               nonce="<transcript-nonce>",
                               semantic_clock_tick=42)
        if acquired:
            try:
                ...run plan...
            finally:
                lc.release("plan-abc123", holder_id="worker-1",
                            nonce="<transcript-nonce>")

    Parameters
    ----------
    lease_ttl_seconds:
        How long a lease is valid before automatic expiry.
    cache:
        Override the coordination-cache instance (useful for testing).
    

### Methods

#### __init__
**Parameters**: self, lease_ttl_seconds, cache
**Returns**: None

#### acquire
**Parameters**: self, plan_hash, holder_id, nonce, semantic_clock_tick
**Returns**: bool
**Description**: Attempt to acquire the lease for *plan_hash*.

        Returns ``True`` if the lease was acquired; ``False`` if another
        holder currently holds it.  Always returns ``False`` in
        ``replay_mode=True`` — callers should treat replay as lease-free
        (no coordination needed for read-only transcript reconstruction).
        

#### release
**Parameters**: self, plan_hash, holder_id, nonce
**Returns**: bool
**Description**: Release the lease for *plan_hash* held by *holder_id* / *nonce*.

        Returns ``True`` if the lease was successfully released; ``False``
        if the caller did not hold the lease or it had already expired.
        

#### is_held
**Parameters**: self, plan_hash
**Returns**: bool
**Description**: Return ``True`` if any holder currently holds the lease.

#### holder_info
**Parameters**: self, plan_hash
**Returns**: dict[str, Any] | None
**Description**: Return the lease payload dict (holder_id, nonce, clock tick) or None.



## Class: IdempotencyStore

**Description**: Records exact tool-call outputs for deduplication (DB 1).

    When a tool call identified by ``tool_call_hash`` has already been
    executed, its raw output bytes are stored here so that a retry returns
    the same bytes without re-executing the tool.

    Rules
    -----
    * Only store outputs for tools that are **strictly input-hashed** (the
      same hash always produces the same output).  Do NOT store outputs for
      tools with side effects unless those side effects are idempotent.
    * In ``replay_mode=True`` all reads return ``None`` — the transcript
      already contains the canonical output.

    Parameters
    ----------
    ttl_seconds:
        TTL for idempotency records.
    cache:
        Override the coordination-cache instance (useful for testing).
    

### Methods

#### __init__
**Parameters**: self, ttl_seconds, cache
**Returns**: None

#### get
**Parameters**: self, tool_call_hash
**Returns**: bytes | None
**Description**: Return stored tool-output bytes or ``None`` on miss/bypass.

#### set
**Parameters**: self, tool_call_hash, output_bytes
**Returns**: None
**Description**: Record *output_bytes* as the canonical output for *tool_call_hash*.

#### exists
**Parameters**: self, tool_call_hash
**Returns**: bool
**Description**: Return ``True`` if a recorded result exists for *tool_call_hash*.

#### invalidate
**Parameters**: self, tool_call_hash
**Returns**: None
**Description**: Evict the idempotency record (e.g. after a forced retry).



## Function: get_lease_coordinator

**Returns**: LeaseCoordinator
**Description**: Return the process-global ``LeaseCoordinator`` instance.



## Function: get_idempotency_store

**Returns**: IdempotencyStore
**Description**: Return the process-global ``IdempotencyStore`` instance.



## Function: __init__

**Parameters**: self, lease_ttl_seconds, cache
**Returns**: None


## Function: acquire

**Parameters**: self, plan_hash, holder_id, nonce, semantic_clock_tick
**Returns**: bool
**Description**: Attempt to acquire the lease for *plan_hash*.

        Returns ``True`` if the lease was acquired; ``False`` if another
        holder currently holds it.  Always returns ``False`` in
        ``replay_mode=True`` — callers should treat replay as lease-free
        (no coordination needed for read-only transcript reconstruction).
        



## Function: release

**Parameters**: self, plan_hash, holder_id, nonce
**Returns**: bool
**Description**: Release the lease for *plan_hash* held by *holder_id* / *nonce*.

        Returns ``True`` if the lease was successfully released; ``False``
        if the caller did not hold the lease or it had already expired.
        



## Function: is_held

**Parameters**: self, plan_hash
**Returns**: bool
**Description**: Return ``True`` if any holder currently holds the lease.



## Function: holder_info

**Parameters**: self, plan_hash
**Returns**: dict[str, Any] | None
**Description**: Return the lease payload dict (holder_id, nonce, clock tick) or None.



## Function: __init__

**Parameters**: self, ttl_seconds, cache
**Returns**: None


## Function: get

**Parameters**: self, tool_call_hash
**Returns**: bytes | None
**Description**: Return stored tool-output bytes or ``None`` on miss/bypass.



## Function: set

**Parameters**: self, tool_call_hash, output_bytes
**Returns**: None
**Description**: Record *output_bytes* as the canonical output for *tool_call_hash*.



## Function: exists

**Parameters**: self, tool_call_hash
**Returns**: bool
**Description**: Return ``True`` if a recorded result exists for *tool_call_hash*.



## Function: invalidate

**Parameters**: self, tool_call_hash
**Returns**: None
**Description**: Evict the idempotency record (e.g. after a forced retry).



## Usage Examples

### Class Usage

```python
# Using LeaseCoordinator
leasecoordinator = LeaseCoordinator()
leasecoordinator.acquire()
leasecoordinator.release()
```

```python
# Using IdempotencyStore
idempotencystore = IdempotencyStore()
idempotencystore.get()
idempotencystore.set()
```

### Function Usage

```python
# Using get_lease_coordinator
result = get_lease_coordinator()
```

```python
# Using get_idempotency_store
result = get_idempotency_store()
```

```python
# Using __init__
result = __init__(lease_ttl_seconds, cache)
```



---
**Generated**: 2026-03-26T09:39:03.655965
**Type**: api_reference
**Quality**: comprehensive
