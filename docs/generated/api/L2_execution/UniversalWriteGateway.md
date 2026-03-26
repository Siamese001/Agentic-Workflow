# API Documentation: UniversalWriteGateway

**Target Audience**: developers, api_users

# UniversalWriteGateway API Documentation

**File**: `UniversalWriteGateway.py`
**Classes**: 4
**Functions**: 36

## Classes

- **ToolNotAllowedError** (inherits from PermissionError)
- **MutationRecord**
- **SimulationResult**
- **UniversalWriteGateway**

## Functions

- **get_write_gateway** -> UniversalWriteGateway
- **set_write_gateway** -> None
- **reset_write_gateway** -> None
- **write_json** -> MutationRecord | SimulationResult
- **write_text** -> MutationRecord | SimulationResult
- **append_to_file** -> MutationRecord | SimulationResult
- **atomic_write** -> MutationRecord | SimulationResult
- **write_pickle** -> MutationRecord | SimulationResult
- **build** -> MutationRecord
- **__init__**
- **_validate_four_field_requirements** -> None
- **check_write_permission** -> bool
- **record_mutation** -> MutationRecord
- **write_through** -> MutationRecord | SimulationResult
- **snapshot_state** -> dict
- **get_state_snapshots** -> list[dict]
- **verify_mutation_record** -> bool
- **simulate_write** -> SimulationResult
- **grant_write_permission** -> None
- **revoke_write_permission** -> None
- **get_mutation_ledger** -> list[MutationRecord]
- **clear_mutation_ledger** -> None
- **execute_instruction** -> None
- **write_file** -> SimulationResult | MutationRecord
- **append_file** -> SimulationResult | MutationRecord
- **delete_file** -> SimulationResult | MutationRecord
- **rename_file** -> SimulationResult | MutationRecord
- **_verify_signature** -> bool
- **_verify_replay_hash** -> bool
- **_verify_plan_hash** -> bool
- **freeze** -> None
- **write** -> None
- **get_write_stats** -> dict[str, Any]
- **validate_promotion_pointer_update** -> bool
- **_simulate_promotion_validation** -> bool
- **update_pointer** -> bool


## Class: ToolNotAllowedError

**Description**: Raised when an instruction attempts to execute a tool not on the allowlist.

**Inherits from**: PermissionError



## Class: MutationRecord

**Description**: Immutable record of a write operation for audit trails.

    Wave 1 hardening: mutation_hash is sha256(actor_id + run_id + operation + path + data_hash).
    This makes the record deterministically reproducible and tamper-evident.
    The timestamp field is a deterministic digest, NOT os.urandom or datetime.now.
    

### Methods

#### build
**Parameters**: cls
**Returns**: MutationRecord
**Description**: Construct a MutationRecord with a deterministic mutation_hash.



## Class: SimulationResult

**Description**: Result of a simulated write operation in replay mode.



## Class: UniversalWriteGateway

**Description**: Single mutation authority for all FS/DB/vector writes.

    Enforces write permissions, records mutations, and supports replay mode
    for deterministic simulation.
    

### Methods

#### __init__
**Parameters**: self, replay_mode, policy_hash, actor_id, run_id, parent_snapshot_hash

#### _validate_four_field_requirements
**Parameters**: self
**Returns**: None
**Description**: Wave 5: Validate that all 4 required fields are present for ADG writes.

        Required fields:
        1. replay_key - for deterministic replay
        2. policy_hash - for policy verification
        3. mutation_signature - for signature verification
        4. parent_snapshot_hash - for snapshot lineage

        In production mode, all fields must be non-empty.
        In replay mode, validation is relaxed for testing.
        

#### check_write_permission
**Parameters**: self, path, operation
**Returns**: bool
**Description**: Check if write operation is permitted.

#### record_mutation
**Parameters**: self, path, operation, data, permitted, replay_key
**Returns**: MutationRecord
**Description**: Record mutation for audit trail with deterministic mutation_hash.

#### write_through
**Parameters**: self, path, data
**Returns**: MutationRecord | SimulationResult
**Description**: Sovereign write path — all governed writes MUST use this method.

        This is the only method that produces a ``writes_through`` ADG edge.
        Direct ``writes_to`` callers must be migrated to this entry point.

        Wave 5: Requires 4 fields for ADG writes:
        - replay_key: deterministic replay hash
        - policy_hash: verified via constructor
        - mutation_signature: for signature verification
        - parent_snapshot_hash: verified via constructor
        

#### snapshot_state
**Parameters**: self, label, state
**Returns**: dict
**Description**: Record a versioned state snapshot into the UWG ledger.

        Produces a ``snapshots_state`` ADG edge. Each snapshot is append-only
        and carries a deterministic content hash so it can be verified during replay.
        

#### get_state_snapshots
**Parameters**: self
**Returns**: list[dict]
**Description**: Return append-only copy of all state snapshots.

#### verify_mutation_record
**Parameters**: record
**Returns**: bool
**Description**: Verify that a MutationRecord's mutation_hash matches its fields.

        Returns True if the record is internally consistent (not tampered).
        

#### simulate_write
**Parameters**: self, path, operation, data
**Returns**: SimulationResult
**Description**: Simulate write operation in replay mode.

#### grant_write_permission
**Parameters**: self, path
**Returns**: None
**Description**: Grant write permission for a specific path.

#### revoke_write_permission
**Parameters**: self, path
**Returns**: None
**Description**: Revoke write permission for a specific path.

#### get_mutation_ledger
**Parameters**: self
**Returns**: list[MutationRecord]
**Description**: Get immutable copy of mutation ledger.

#### clear_mutation_ledger
**Parameters**: self
**Returns**: None
**Description**: Clear mutation ledger (for testing only).

#### execute_instruction
**Parameters**: self, instruction
**Returns**: None
**Description**: 
        The sovereign entry point for all tool executions.

        Validates the tool name from the InstructionPacket against the allowlist
        before allowing any operation to proceed.

        Raises:
            ToolNotAllowedError: If the tool is not in the allowlist.
        

#### write_file
**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Write data to path via the UWG sovereign gate.

        Spec: L2 [UWG] UNIVERSAL WRITE GATEWAY, Guarantee #6.
        - replay_mode=True: returns SimulationResult (no real write).
        - replay_mode=False: raises ToolNotAllowedError on blocked paths/extensions.
        

#### append_file
**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Append data to path via the UWG sovereign gate.

        Same blocking semantics as write_file.
        

#### delete_file
**Parameters**: self, path
**Returns**: SimulationResult | MutationRecord
**Description**: Delete a file via the UWG sovereign gate.

        Same blocking semantics: replay_mode returns SimulationResult; live raises on disallowed.
        

#### rename_file
**Parameters**: self, src, dst
**Returns**: SimulationResult | MutationRecord
**Description**: Rename/move a file via the UWG sovereign gate.

        Both src and dst must be in the allowed write set.
        

#### _verify_signature
**Parameters**: self, signature
**Returns**: bool
**Description**: REQ-019/177/354: verify a write-payload signature.

        Stub implementation — returns True for any non-empty signature.
        Override in subclasses or inject via test doubles for stricter verification.
        

#### _verify_replay_hash
**Parameters**: self, payload, replay_key
**Returns**: bool
**Description**: REQ-354: verify deterministic replay hash.

        Checks that hash(payload) matches the declared replay_key so the
        write is reproducible and has not been tampered with in transit.
        Override in subclasses for production-strength verification.
        

#### _verify_plan_hash
**Parameters**: self, plan_hash
**Returns**: bool
**Description**: REQ-354: verify mutation originated from an authorised execution plan.

        Stub returns True for any non-empty plan_hash.  Override in subclasses
        to compare against the active execution plan registry.
        

#### freeze
**Parameters**: self
**Returns**: None
**Description**: REQ-091: Tier III freeze — all writes blocked until process restart.

#### write
**Parameters**: self, payload, signature, store
**Returns**: None
**Description**: REQ-019/177/354: signature-before-side-effect write gate.

        Wave 5: Enforces 4-field requirement for ADG writes:
        1. Guardrail pre-check — applies_guardrail before any mutation.
        2. Signature verification — payload must be signed (mutation_signature).
        3. Replay hash verification — payload hash must match replay_key.
        4. Plan hash verification — mutation must originate from an authorised plan.

        All checks must pass.  store is never touched on any failure.
        

#### get_write_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return statistics about write operations.

#### validate_promotion_pointer_update
**Parameters**: self, namespace, old_pointer, new_pointer, capability_token
**Returns**: bool
**Description**: Validate promotion pointer update with capability token.

#### _simulate_promotion_validation
**Parameters**: self, namespace, old_pointer, new_pointer, capability_token
**Returns**: bool
**Description**: Simulate promotion validation in replay mode.

#### update_pointer
**Parameters**: self, namespace, old_pointer, new_pointer, capability_token
**Returns**: bool
**Description**: Update pointer with validation.



## Function: get_write_gateway

**Returns**: UniversalWriteGateway
**Description**: Get the global write gateway instance.



## Function: set_write_gateway

**Parameters**: gateway
**Returns**: None
**Description**: Set the global write gateway instance (for testing).



## Function: reset_write_gateway

**Returns**: None
**Description**: Reset the global write gateway (for testing).



## Function: write_json

**Parameters**: path, data
**Returns**: MutationRecord | SimulationResult
**Description**: Convenience method for JSON writes through UWG.

    Args:
        path: Target file path
        data: Dictionary to serialize as JSON
        **kwargs: Additional arguments for write_through

    Returns:
        MutationRecord or SimulationResult from write_through
    



## Function: write_text

**Parameters**: path, content
**Returns**: MutationRecord | SimulationResult
**Description**: Convenience method for text writes through UWG.

    Args:
        path: Target file path
        content: Text content to write
        **kwargs: Additional arguments for write_through

    Returns:
        MutationRecord or SimulationResult from write_through
    



## Function: append_to_file

**Parameters**: path, content
**Returns**: MutationRecord | SimulationResult
**Description**: Safe append operations through UWG.

    Args:
        path: Target file path
        content: Content to append
        **kwargs: Additional arguments for write_through

    Returns:
        MutationRecord or SimulationResult from write_through
    



## Function: atomic_write

**Parameters**: path, data
**Returns**: MutationRecord | SimulationResult
**Description**: Atomic write with temp file + rename through UWG.

    Args:
        path: Target file path
        data: Data to write (will be converted to string)
        **kwargs: Additional arguments for write_through

    Returns:
        MutationRecord or SimulationResult from write_through
    



## Function: write_pickle

**Parameters**: path, obj
**Returns**: MutationRecord | SimulationResult
**Description**: Pickle serialization with governance through UWG.

    Args:
        path: Target file path
        obj: Python object to pickle
        **kwargs: Additional arguments for write_through

    Returns:
        MutationRecord or SimulationResult from write_through
    



## Function: build

**Parameters**: cls
**Returns**: MutationRecord
**Description**: Construct a MutationRecord with a deterministic mutation_hash.



## Function: __init__

**Parameters**: self, replay_mode, policy_hash, actor_id, run_id, parent_snapshot_hash


## Function: _validate_four_field_requirements

**Parameters**: self
**Returns**: None
**Description**: Wave 5: Validate that all 4 required fields are present for ADG writes.

        Required fields:
        1. replay_key - for deterministic replay
        2. policy_hash - for policy verification
        3. mutation_signature - for signature verification
        4. parent_snapshot_hash - for snapshot lineage

        In production mode, all fields must be non-empty.
        In replay mode, validation is relaxed for testing.
        



## Function: check_write_permission

**Parameters**: self, path, operation
**Returns**: bool
**Description**: Check if write operation is permitted.



## Function: record_mutation

**Parameters**: self, path, operation, data, permitted, replay_key
**Returns**: MutationRecord
**Description**: Record mutation for audit trail with deterministic mutation_hash.



## Function: write_through

**Parameters**: self, path, data
**Returns**: MutationRecord | SimulationResult
**Description**: Sovereign write path — all governed writes MUST use this method.

        This is the only method that produces a ``writes_through`` ADG edge.
        Direct ``writes_to`` callers must be migrated to this entry point.

        Wave 5: Requires 4 fields for ADG writes:
        - replay_key: deterministic replay hash
        - policy_hash: verified via constructor
        - mutation_signature: for signature verification
        - parent_snapshot_hash: verified via constructor
        



## Function: snapshot_state

**Parameters**: self, label, state
**Returns**: dict
**Description**: Record a versioned state snapshot into the UWG ledger.

        Produces a ``snapshots_state`` ADG edge. Each snapshot is append-only
        and carries a deterministic content hash so it can be verified during replay.
        



## Function: get_state_snapshots

**Parameters**: self
**Returns**: list[dict]
**Description**: Return append-only copy of all state snapshots.



## Function: verify_mutation_record

**Parameters**: record
**Returns**: bool
**Description**: Verify that a MutationRecord's mutation_hash matches its fields.

        Returns True if the record is internally consistent (not tampered).
        



## Function: simulate_write

**Parameters**: self, path, operation, data
**Returns**: SimulationResult
**Description**: Simulate write operation in replay mode.



## Function: grant_write_permission

**Parameters**: self, path
**Returns**: None
**Description**: Grant write permission for a specific path.



## Function: revoke_write_permission

**Parameters**: self, path
**Returns**: None
**Description**: Revoke write permission for a specific path.



## Function: get_mutation_ledger

**Parameters**: self
**Returns**: list[MutationRecord]
**Description**: Get immutable copy of mutation ledger.



## Function: clear_mutation_ledger

**Parameters**: self
**Returns**: None
**Description**: Clear mutation ledger (for testing only).



## Function: execute_instruction

**Parameters**: self, instruction
**Returns**: None
**Description**: 
        The sovereign entry point for all tool executions.

        Validates the tool name from the InstructionPacket against the allowlist
        before allowing any operation to proceed.

        Raises:
            ToolNotAllowedError: If the tool is not in the allowlist.
        



## Function: write_file

**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Write data to path via the UWG sovereign gate.

        Spec: L2 [UWG] UNIVERSAL WRITE GATEWAY, Guarantee #6.
        - replay_mode=True: returns SimulationResult (no real write).
        - replay_mode=False: raises ToolNotAllowedError on blocked paths/extensions.
        



## Function: append_file

**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Append data to path via the UWG sovereign gate.

        Same blocking semantics as write_file.
        



## Function: delete_file

**Parameters**: self, path
**Returns**: SimulationResult | MutationRecord
**Description**: Delete a file via the UWG sovereign gate.

        Same blocking semantics: replay_mode returns SimulationResult; live raises on disallowed.
        



## Function: rename_file

**Parameters**: self, src, dst
**Returns**: SimulationResult | MutationRecord
**Description**: Rename/move a file via the UWG sovereign gate.

        Both src and dst must be in the allowed write set.
        



## Function: _verify_signature

**Parameters**: self, signature
**Returns**: bool
**Description**: REQ-019/177/354: verify a write-payload signature.

        Stub implementation — returns True for any non-empty signature.
        Override in subclasses or inject via test doubles for stricter verification.
        



## Function: _verify_replay_hash

**Parameters**: self, payload, replay_key
**Returns**: bool
**Description**: REQ-354: verify deterministic replay hash.

        Checks that hash(payload) matches the declared replay_key so the
        write is reproducible and has not been tampered with in transit.
        Override in subclasses for production-strength verification.
        



## Function: _verify_plan_hash

**Parameters**: self, plan_hash
**Returns**: bool
**Description**: REQ-354: verify mutation originated from an authorised execution plan.

        Stub returns True for any non-empty plan_hash.  Override in subclasses
        to compare against the active execution plan registry.
        



## Function: freeze

**Parameters**: self
**Returns**: None
**Description**: REQ-091: Tier III freeze — all writes blocked until process restart.



## Function: write

**Parameters**: self, payload, signature, store
**Returns**: None
**Description**: REQ-019/177/354: signature-before-side-effect write gate.

        Wave 5: Enforces 4-field requirement for ADG writes:
        1. Guardrail pre-check — applies_guardrail before any mutation.
        2. Signature verification — payload must be signed (mutation_signature).
        3. Replay hash verification — payload hash must match replay_key.
        4. Plan hash verification — mutation must originate from an authorised plan.

        All checks must pass.  store is never touched on any failure.
        



## Function: get_write_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return statistics about write operations.



## Function: validate_promotion_pointer_update

**Parameters**: self, namespace, old_pointer, new_pointer, capability_token
**Returns**: bool
**Description**: Validate promotion pointer update with capability token.



## Function: _simulate_promotion_validation

**Parameters**: self, namespace, old_pointer, new_pointer, capability_token
**Returns**: bool
**Description**: Simulate promotion validation in replay mode.



## Function: update_pointer

**Parameters**: self, namespace, old_pointer, new_pointer, capability_token
**Returns**: bool
**Description**: Update pointer with validation.



## Usage Examples

### Class Usage

```python
# Using ToolNotAllowedError
toolnotallowederror = ToolNotAllowedError()
```

```python
# Using MutationRecord
mutationrecord = MutationRecord()
mutationrecord.build()
```

```python
# Using SimulationResult
simulationresult = SimulationResult()
```

### Function Usage

```python
# Using get_write_gateway
result = get_write_gateway()
```

```python
# Using set_write_gateway
result = set_write_gateway(gateway)
```

```python
# Using reset_write_gateway
result = reset_write_gateway()
```



---
**Generated**: 2026-03-26T09:39:03.592269
**Type**: api_reference
**Quality**: comprehensive
