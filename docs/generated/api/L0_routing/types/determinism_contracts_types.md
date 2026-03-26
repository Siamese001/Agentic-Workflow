# API Documentation: determinism_contracts_types

**Target Audience**: developers, api_users

# determinism_contracts_types API Documentation

**File**: `determinism_contracts_types.py`
**Classes**: 4
**Functions**: 17

## Classes

- **ForbiddenInputError** (inherits from Exception)
- **WallClockViolation** (inherits from Exception)
- **RollbackHashMismatch** (inherits from Exception)
- **EpisodicMemoryNotQueried** (inherits from Exception)

## Functions

- **validate_execution_input** -> SurgicalManifest
- **check_forbidden_input_type** -> None
- **validate_manifest_emission** -> SurgicalManifest
- **require_manifest_hash_ok** -> None
- **canonical_ast_serialize** -> CanonicalASTResult
- **verify_ast_determinism** -> bool
- **dedupe_sha256** -> str
- **dedupe_check** -> bool
- **ast_scan_wall_clock** -> list[WallClockViolation]
- **create_boundary_snapshot** -> BoundarySnapshotArtifact
- **verify_rollback_integrity** -> bool
- **enforce_episodic_query_before_planning** -> None
- **knowledge_supervisor_check** -> bool
- **check_velocity_threshold** -> bool
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None


## Class: ForbiddenInputError

**Description**: §1.2 — Raised when a forbidden execution input is detected.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, input_type
**Returns**: None



## Class: WallClockViolation

**Description**: §13.2 — Wall-clock usage detected in hash/signature/dedup path.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, callable_name, file_path, line
**Returns**: None



## Class: RollbackHashMismatch

**Description**: §10.3 — Post-rollback hash does not match pre-wave snapshot.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, field, expected, actual
**Returns**: None



## Class: EpisodicMemoryNotQueried

**Description**: §6.1 — Planning attempted without querying episodic memory first.

**Inherits from**: Exception



## Function: validate_execution_input

**Parameters**: input_obj
**Returns**: SurgicalManifest
**Description**: §1.1/§1.2 — Validate that execution input is exclusively a SurgicalManifest.

    Rejects raw paths, regex, diffs, line numbers, free-form text, etc.
    Fail-closed: anything that is not a SurgicalManifest is rejected.
    



## Function: check_forbidden_input_type

**Parameters**: input_type
**Returns**: None
**Description**: §1.2 — Check if an input type is in the forbidden set.



## Function: validate_manifest_emission

**Parameters**: manifest
**Returns**: SurgicalManifest
**Description**: §2.1 — Validator MUST emit a SurgicalManifest. Fail-closed on wrong type.



## Function: require_manifest_hash_ok

**Parameters**: manifest
**Returns**: None
**Description**: §1.6 — Fail-closed: verify manifest_hash matches ast_snippet SHA-256.

    Call immediately after SurgicalManifest construction, before return.
    Raises ValueError on mismatch.
    



## Function: canonical_ast_serialize

**Parameters**: source, source_path
**Returns**: CanonicalASTResult
**Description**: §1.4 — Deterministic AST serialization via sorted ast.dump.

    Produces a canonical string form of the AST that is stable across runs.
    LibCST or sorted ast.dump; formatter-dependent output is invalid.
    



## Function: verify_ast_determinism

**Parameters**: source
**Returns**: bool
**Description**: §1.4 — Verify AST serialization is deterministic (two runs produce same hash).



## Function: dedupe_sha256

**Parameters**: signal_data
**Returns**: str
**Description**: §5.1 — All deduplication uses cryptographic SHA-256 hashes.



## Function: dedupe_check

**Parameters**: signal_data, seen_hashes
**Returns**: bool
**Description**: §5.1 — Returns True if signal is a duplicate (already seen).



## Function: ast_scan_wall_clock

**Parameters**: source, file_path
**Returns**: list[WallClockViolation]
**Description**: §13.2 — AST scan for wall-clock callables in source code.

    Returns list of violations. Empty list = compliant.
    



## Function: create_boundary_snapshot

**Parameters**: trace_id, filesystem_hash, git_state_hash, agent_memory_hash, semantic_clock
**Returns**: BoundarySnapshotArtifact
**Description**: §10.2 — Create a BoundarySnapshotArtifact at wave start.



## Function: verify_rollback_integrity

**Parameters**: pre_snapshot, post_fs_hash, post_git_hash, post_memory_hash
**Returns**: bool
**Description**: §10.3 — Post-rollback state hash must exactly match pre-wave snapshot.

    Raises RollbackHashMismatch on any mismatch.
    



## Function: enforce_episodic_query_before_planning

**Parameters**: episodic_result
**Returns**: None
**Description**: §6.1 — Fail-closed: episodic memory must be queried before planning.



## Function: knowledge_supervisor_check

**Parameters**: confidence, threshold
**Returns**: bool
**Description**: §6.6 — Returns True if confidence is below threshold (requires retraining).



## Function: check_velocity_threshold

**Parameters**: signal_count, threshold
**Returns**: bool
**Description**: §15.3 — Returns True if signal_count meets or exceeds velocity threshold.



## Function: __init__

**Parameters**: self, input_type
**Returns**: None


## Function: __init__

**Parameters**: self, callable_name, file_path, line
**Returns**: None


## Function: __init__

**Parameters**: self, field, expected, actual
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ForbiddenInputError
forbiddeninputerror = ForbiddenInputError()
```

```python
# Using WallClockViolation
wallclockviolation = WallClockViolation()
```

```python
# Using RollbackHashMismatch
rollbackhashmismatch = RollbackHashMismatch()
```

### Function Usage

```python
# Using validate_execution_input
result = validate_execution_input(input_obj)
```

```python
# Using check_forbidden_input_type
result = check_forbidden_input_type(input_type)
```

```python
# Using validate_manifest_emission
result = validate_manifest_emission(manifest)
```



---
**Generated**: 2026-03-26T09:39:03.435288
**Type**: api_reference
**Quality**: comprehensive
