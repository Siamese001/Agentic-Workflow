# API Documentation: memory_authority

**Target Audience**: developers, api_users

# memory_authority API Documentation

**File**: `memory_authority.py`
**Classes**: 7
**Functions**: 13

## Classes

- **MemoryNamespace** (inherits from str, Enum)
- **NamespacePolicy**
- **MemoryWriteRecord**
- **MemoryReadResult**
- **DirectMemoryWriteError** (inherits from PermissionError)
- **UnclassifiedNamespaceError** (inherits from ValueError)
- **MemoryAuthority**

## Functions

- **get_namespace_policy** -> NamespacePolicy
- **get_memory_authority** -> MemoryAuthority
- **reset_memory_authority** -> None
- **create** -> MemoryWriteRecord
- **__init__** -> None
- **read** -> MemoryReadResult
- **write** -> MemoryWriteRecord
- **observe** -> None
- **version** -> int
- **snapshot** -> dict[str, Any]
- **write_records** -> list[MemoryWriteRecord]
- **namespace_policy** -> NamespacePolicy
- **get_stats** -> dict[str, Any]


## Class: MemoryNamespace

**Description**: All recognized memory namespaces for MemoryAuthority.

**Inherits from**: str, Enum



## Class: NamespacePolicy

**Description**: Version, retention, and mutation policy for a memory namespace.



## Class: MemoryWriteRecord

**Description**: Immutable record of one governed memory write (P1/L4 spec §3).

### Methods

#### create
**Parameters**: cls, run_id, namespace, key, value, previous_version, new_version, trace_id, policy_hash, actor_id
**Returns**: MemoryWriteRecord



## Class: MemoryReadResult

**Description**: Result of a governed memory read (P1/L4 spec §6).



## Class: DirectMemoryWriteError

**Description**: Raised when a direct mutable write bypasses MemoryAuthority.

**Inherits from**: PermissionError



## Class: UnclassifiedNamespaceError

**Description**: Raised when a write lacks a valid namespace classification.

**Inherits from**: ValueError



## Class: MemoryAuthority

**Description**: Unified memory write governance facade — P1/L4 spec.

    All mutable memory writes flow through write().
    Read-through cache is allowed; write-through side channels are prohibited.

    Write chain:
        MemoryAuthority.write() -> RunStateAuthority.commit() -> durable store
    

### Methods

#### __init__
**Parameters**: self, run_id, run_state_authority, policy_hash
**Returns**: None

#### read
**Parameters**: self, key, namespace, default
**Returns**: MemoryReadResult
**Description**: Governed memory read — returns value + version + namespace + source_hash.

        ADG edge: reads_runtime_state, observes_runtime_state.
        

#### write
**Parameters**: self, key, value, namespace, run_id, actor_id, trace_id, policy_hash
**Returns**: MemoryWriteRecord
**Description**: Mandatory governed write entrypoint.

        All mutable memory writes MUST call this method.
        Produces MemoryWriteRecord with 8 required fields.
        Emits writes_through ADG edge.

        Write chain: MemoryAuthority -> RunStateAuthority.commit() -> durable store.

        Raises:
            UnclassifiedNamespaceError: if namespace is invalid.
        

#### observe
**Parameters**: self, context, namespace, stage, actor_id
**Returns**: None
**Description**: Emit observes_runtime_state signal for the given context.

        ADG edge: observes_runtime_state.
        

#### version
**Parameters**: self, key, namespace
**Returns**: int
**Description**: Return the current MemoryAuthority-local version for key.

        Does NOT emit ADG edges (read-only metadata query).
        

#### snapshot
**Parameters**: self, label, run_id
**Returns**: dict[str, Any]
**Description**: Capture a snapshot of current memory state.

        ADG edge: snapshots_state.
        

#### write_records
**Parameters**: self
**Returns**: list[MemoryWriteRecord]

#### namespace_policy
**Parameters**: self, ns
**Returns**: NamespacePolicy

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]



## Function: get_namespace_policy

**Parameters**: ns
**Returns**: NamespacePolicy


## Function: get_memory_authority

**Parameters**: run_id, policy_hash
**Returns**: MemoryAuthority
**Description**: Return the process-level MemoryAuthority singleton.



## Function: reset_memory_authority

**Returns**: None
**Description**: Reset the singleton (for testing).



## Function: create

**Parameters**: cls, run_id, namespace, key, value, previous_version, new_version, trace_id, policy_hash, actor_id
**Returns**: MemoryWriteRecord


## Function: __init__

**Parameters**: self, run_id, run_state_authority, policy_hash
**Returns**: None


## Function: read

**Parameters**: self, key, namespace, default
**Returns**: MemoryReadResult
**Description**: Governed memory read — returns value + version + namespace + source_hash.

        ADG edge: reads_runtime_state, observes_runtime_state.
        



## Function: write

**Parameters**: self, key, value, namespace, run_id, actor_id, trace_id, policy_hash
**Returns**: MemoryWriteRecord
**Description**: Mandatory governed write entrypoint.

        All mutable memory writes MUST call this method.
        Produces MemoryWriteRecord with 8 required fields.
        Emits writes_through ADG edge.

        Write chain: MemoryAuthority -> RunStateAuthority.commit() -> durable store.

        Raises:
            UnclassifiedNamespaceError: if namespace is invalid.
        



## Function: observe

**Parameters**: self, context, namespace, stage, actor_id
**Returns**: None
**Description**: Emit observes_runtime_state signal for the given context.

        ADG edge: observes_runtime_state.
        



## Function: version

**Parameters**: self, key, namespace
**Returns**: int
**Description**: Return the current MemoryAuthority-local version for key.

        Does NOT emit ADG edges (read-only metadata query).
        



## Function: snapshot

**Parameters**: self, label, run_id
**Returns**: dict[str, Any]
**Description**: Capture a snapshot of current memory state.

        ADG edge: snapshots_state.
        



## Function: write_records

**Parameters**: self
**Returns**: list[MemoryWriteRecord]


## Function: namespace_policy

**Parameters**: self, ns
**Returns**: NamespacePolicy


## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using MemoryNamespace
memorynamespace = MemoryNamespace()
```

```python
# Using NamespacePolicy
namespacepolicy = NamespacePolicy()
```

```python
# Using MemoryWriteRecord
memorywriterecord = MemoryWriteRecord()
memorywriterecord.create()
```

### Function Usage

```python
# Using get_namespace_policy
result = get_namespace_policy(ns)
```

```python
# Using get_memory_authority
result = get_memory_authority(run_id, policy_hash)
```

```python
# Using reset_memory_authority
result = reset_memory_authority()
```



---
**Generated**: 2026-03-26T09:39:04.453910
**Type**: api_reference
**Quality**: comprehensive
