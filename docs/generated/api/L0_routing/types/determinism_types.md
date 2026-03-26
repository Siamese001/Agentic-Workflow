# API Documentation: determinism_types

**Target Audience**: developers, api_users

# determinism_types API Documentation

**File**: `determinism_types.py`
**Classes**: 14
**Functions**: 17

## Classes

- **FixConstraint** (inherits from str, Enum)
- **SurgicalManifest**
- **CanonicalASTResult**
- **SemanticClock**
- **StateCommitInvalid** (inherits from Exception)
- **SemanticClockSnapshot**
- **BoundarySnapshotArtifact**
- **EpisodicMemoryQueryResult**
- **TrajectoryReuseConstraint**
- **KnowledgeSupervisorResult**
- **MemoryHypostate**
- **EpisodicSemanticLink**
- **ForensicTraceBuffer**
- **SemanticClockAdvancementArtifact**

## Functions

- **validate_semantic_clock** -> SemanticClockSnapshot
- **__post_init__** -> None
- **verify_hash** -> bool
- **verify** -> bool
- **prepare_commit** -> None
- **tick** -> int
- **current_tick** -> int
- **__post_init__** -> None
- **to_dict** -> dict[str, object]
- **from_clock** -> SemanticClockSnapshot
- **reusable** -> bool
- **__post_init__** -> None
- **ingest** -> None
- **signal_count** -> int
- **velocity_exceeded** -> bool
- **flush** -> list[dict[str, Any]]
- **__post_init__**


## Class: FixConstraint

**Description**: §1.3 — Fix constraint for SurgicalManifest.

**Inherits from**: str, Enum



## Class: SurgicalManifest

**Description**: §1.1/§1.3 — Exclusive execution input. All 10 fields required.

    Fields per spec:
      schema_version, correlation_id, node_id, target_layer,
      ast_snippet, serialization_canon, fix_constraint,
      manifest_hash, change_history, provenance_chain
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### verify_hash
**Parameters**: self
**Returns**: bool
**Description**: §1.6 — manifest_hash must match SHA-256 of ast_snippet bytes.



## Class: CanonicalASTResult

**Description**: §1.4 — Result of deterministic AST serialization.

### Methods

#### verify
**Parameters**: self
**Returns**: bool
**Description**: Hash must match canonical_form bytes.



## Class: SemanticClock

**Description**: §13.1 — Time measured exclusively via Step ID + Vector Clock.

    No wall-clock time. Tick advances only on valid StateCommit (§13.1.1).
    

### Methods

#### prepare_commit
**Parameters**: self, layer
**Returns**: None
**Description**: Prepare a state commit for a layer. Does NOT advance clock.

#### tick
**Parameters**: self, layer, state_commit_valid
**Returns**: int
**Description**: §13.1.1 — Advance only on valid StateCommit. Fail-closed otherwise.

#### current_tick
**Parameters**: self
**Returns**: int



## Class: StateCommitInvalid

**Description**: §13.1.1 — StateCommit validation failed; clock must not advance.

**Inherits from**: Exception



## Class: SemanticClockSnapshot

**Description**: §Phase3.2 — Immutable snapshot of SemanticClock for embedding in frozen artifacts.

    Serializes as {"tick": <int>, "vector_clock": {<layer>: <int>, ...}}.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, object]
**Description**: Deterministic serialization: sorted vector_clock keys.

#### from_clock
**Parameters**: cls, clock
**Returns**: SemanticClockSnapshot
**Description**: Capture a snapshot from a live SemanticClock.



## Class: BoundarySnapshotArtifact

**Description**: §10.2 — Snapshot of filesystem, git state, agent memory at wave start.

    Required fields: trace_id, filesystem_hash, git_state_hash,
                     agent_memory_hash, semantic_clock_tick
    



## Class: EpisodicMemoryQueryResult

**Description**: §6.1 — Episodic memory must be queried before planning.

    Planning functions must accept this as a required input.
    



## Class: TrajectoryReuseConstraint

**Description**: §6.2 — Trajectory reuse requires similarity AND exact failure_reason match.

### Methods

#### reusable
**Parameters**: self
**Returns**: bool



## Class: KnowledgeSupervisorResult

**Description**: §6.6 — Knowledge Supervisor audit result for low-confidence retrievals.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: MemoryHypostate

**Description**: §6.8 — Extended Trace Hypostate linked to the Semantic Clock.



## Class: EpisodicSemanticLink

**Description**: §6.10 — Episodic memory records outcome links used in reasoning.



## Class: ForensicTraceBuffer

**Description**: §15.3 — Ephemeral buffer for high-velocity signal capture.

    Signals >= TRACE_BUFFER_VELOCITY_THRESHOLD per semantic clock tick
    must be captured here before persistence.
    

### Methods

#### ingest
**Parameters**: self, signal
**Returns**: None
**Description**: Ingest a signal into the buffer.

#### signal_count
**Parameters**: self
**Returns**: int

#### velocity_exceeded
**Parameters**: self
**Returns**: bool

#### flush
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Flush buffer contents for persistence. Returns copy and clears.



## Class: SemanticClockAdvancementArtifact

**Description**: Wave 19: Semantic clock advancement artifact for replay verification.

    Captures semantic clock advancement events with L4 version binding
    and provider identification for deterministic replay.
    

### Methods

#### __post_init__
**Parameters**: self



## Function: validate_semantic_clock

**Parameters**: semantic_clock, context
**Returns**: SemanticClockSnapshot
**Description**: §Phase3.2 — Hard-fail if semantic_clock is None at a determinism chokepoint.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: verify_hash

**Parameters**: self
**Returns**: bool
**Description**: §1.6 — manifest_hash must match SHA-256 of ast_snippet bytes.



## Function: verify

**Parameters**: self
**Returns**: bool
**Description**: Hash must match canonical_form bytes.



## Function: prepare_commit

**Parameters**: self, layer
**Returns**: None
**Description**: Prepare a state commit for a layer. Does NOT advance clock.



## Function: tick

**Parameters**: self, layer, state_commit_valid
**Returns**: int
**Description**: §13.1.1 — Advance only on valid StateCommit. Fail-closed otherwise.



## Function: current_tick

**Parameters**: self
**Returns**: int


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, object]
**Description**: Deterministic serialization: sorted vector_clock keys.



## Function: from_clock

**Parameters**: cls, clock
**Returns**: SemanticClockSnapshot
**Description**: Capture a snapshot from a live SemanticClock.



## Function: reusable

**Parameters**: self
**Returns**: bool


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: ingest

**Parameters**: self, signal
**Returns**: None
**Description**: Ingest a signal into the buffer.



## Function: signal_count

**Parameters**: self
**Returns**: int


## Function: velocity_exceeded

**Parameters**: self
**Returns**: bool


## Function: flush

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Flush buffer contents for persistence. Returns copy and clears.



## Function: __post_init__

**Parameters**: self


## Usage Examples

### Class Usage

```python
# Using FixConstraint
fixconstraint = FixConstraint()
```

```python
# Using SurgicalManifest
surgicalmanifest = SurgicalManifest()
surgicalmanifest.verify_hash()
```

```python
# Using CanonicalASTResult
canonicalastresult = CanonicalASTResult()
canonicalastresult.verify()
```

### Function Usage

```python
# Using validate_semantic_clock
result = validate_semantic_clock(semantic_clock, context)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using verify_hash
result = verify_hash()
```



---
**Generated**: 2026-03-26T09:39:03.441077
**Type**: api_reference
**Quality**: comprehensive
