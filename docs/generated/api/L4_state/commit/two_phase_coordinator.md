# API Documentation: two_phase_coordinator

**Target Audience**: developers, api_users

# two_phase_coordinator API Documentation

**File**: `two_phase_coordinator.py`
**Classes**: 1
**Functions**: 2

## Classes

- **TwoPhaseCoordinator**

## Functions

- **execute_commit** -> tuple[Any, Any]
- **safe_commit** -> dict[str, Any]


## Class: TwoPhaseCoordinator

**Description**: Coordinates a 2PC write: resource + ledger must both ACK.

    Usage:
        coordinator = TwoPhaseCoordinator()
        coordinator.execute_commit(
            resource_write=lambda: write_to_file(path, content),
            ledger_write=lambda: append_ledger(entry),
            context={"file": str(path)},
        )
    

### Methods

#### execute_commit
**Parameters**: self, resource_write, ledger_write, context
**Returns**: tuple[Any, Any]
**Description**: Execute 2PC commit. Both writes must succeed or both are rolled back.

        Returns (resource_result, ledger_result) on success.
        Raises MutationCommitFailure if either ACK fails.
        

#### safe_commit
**Parameters**: self, resource_write, ledger_write, context
**Returns**: dict[str, Any]
**Description**: Wrapper that returns a status dict instead of raising.

        Returns {"success": True, ...} or {"success": False, "error": ...}.
        



## Function: execute_commit

**Parameters**: self, resource_write, ledger_write, context
**Returns**: tuple[Any, Any]
**Description**: Execute 2PC commit. Both writes must succeed or both are rolled back.

        Returns (resource_result, ledger_result) on success.
        Raises MutationCommitFailure if either ACK fails.
        



## Function: safe_commit

**Parameters**: self, resource_write, ledger_write, context
**Returns**: dict[str, Any]
**Description**: Wrapper that returns a status dict instead of raising.

        Returns {"success": True, ...} or {"success": False, "error": ...}.
        



## Usage Examples

### Class Usage

```python
# Using TwoPhaseCoordinator
twophasecoordinator = TwoPhaseCoordinator()
twophasecoordinator.execute_commit()
twophasecoordinator.safe_commit()
```

### Function Usage

```python
# Using execute_commit
result = execute_commit(resource_write, ledger_write)
```

```python
# Using safe_commit
result = safe_commit(resource_write, ledger_write)
```



---
**Generated**: 2026-03-26T09:39:04.471080
**Type**: api_reference
**Quality**: comprehensive
