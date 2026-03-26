# API Documentation: execution_proof_emitter

**Target Audience**: developers, api_users

# execution_proof_emitter API Documentation

**File**: `execution_proof_emitter.py`
**Classes**: 3
**Functions**: 21

## Classes

- **ExecutionProof**
- **ExecutionProofEmitter**
- **proof_context**

## Functions

- **_compute_replay_key** -> str
- **_compute_digest** -> str
- **_sign_proof** -> str
- **_sign** -> str
- **_hash_input** -> str
- **_hash_output** -> str
- **_hash_target** -> str
- **verify_replay** -> bool
- **is_signed** -> bool
- **__init__** -> None
- **_trace_id** -> str
- **emit** -> ExecutionProof
- **emit_proof** -> Callable
- **proof_op** -> ExecutionProofEmitter.proof_context
- **ledger** -> list[ExecutionProof]
- **latest** -> ExecutionProof | None
- **__init__** -> None
- **__enter__** -> ExecutionProofEmitter.proof_context
- **__exit__** -> bool
- **decorator** -> Callable
- **wrapper**


## Class: ExecutionProof

**Description**: Signed, reproducible proof of a single L2 execution event.

    Required fields (P1/L2 spec):
        execution_proof_id    — unique per proof
        run_id                — run that produced this execution
        trace_id              — execution trace linkage
        execution_input_hash  — hash of inputs passed to execution
        execution_output_hash — hash of outputs produced
        replay_key            — deterministic replay anchor
        determinism_digest    — digest over replay_key + elapsed
        policy_hash           — active policy hash at execution time
        execution_target_hash — hash of the execution target (fn/tool/op)
        execution_signature   — signed proof binding all fields
        created_at_tick       — clock epoch at proof creation
    

### Methods

#### verify_replay
**Parameters**: self
**Returns**: bool
**Description**: Verify the replay key can be reconstructed from the proof fields.

        Emits ``guards_replay`` ADG edge.
        

#### is_signed
**Parameters**: self
**Returns**: bool
**Description**: True if execution_signature is populated.



## Class: ExecutionProofEmitter

**Description**: Emits signed execution proofs for L2 execution events.

    Usage — context manager::

        emitter = ExecutionProofEmitter("my_module")
        with emitter.proof_context("write_artifact") as ctx:
            do_write()
        proof = ctx.proof  # ExecutionProof, always present after exit

    Usage — decorator::

        emitter = ExecutionProofEmitter("my_module")

        @emitter.emit_proof("run_tool")
        def run_tool(self, args):
            ...
    

### Methods

#### __init__
**Parameters**: self, module
**Returns**: None

#### _trace_id
**Parameters**: self
**Returns**: str

#### emit
**Parameters**: self, operation, elapsed_ms, success
**Returns**: ExecutionProof
**Description**: Emit a signed execution proof for ``operation``.

        Emits ``emits_replay_key`` + ``emits_determinism_digest``
        + ``signs_execution_trace`` ADG edges.
        

#### emit_proof
**Parameters**: self, operation
**Returns**: Callable
**Description**: Decorator: wrap a callable with execution proof emission.

#### proof_op
**Parameters**: self, operation
**Returns**: ExecutionProofEmitter.proof_context
**Description**: Return a context manager that emits a proof for ``operation``.

#### ledger
**Parameters**: self
**Returns**: list[ExecutionProof]

#### latest
**Parameters**: self
**Returns**: ExecutionProof | None



## Class: proof_context

**Description**: Context manager: time an operation and emit a proof on exit.

### Methods

#### __init__
**Parameters**: self, emitter, operation
**Returns**: None

#### __enter__
**Parameters**: self
**Returns**: ExecutionProofEmitter.proof_context

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: bool



## Function: _compute_replay_key

**Parameters**: trace_id, run_id, module, operation, input_hash
**Returns**: str


## Function: _compute_digest

**Parameters**: replay_key, elapsed_ms
**Returns**: str


## Function: _sign_proof

**Parameters**: execution_proof_id, replay_key, digest, policy_hash, output_hash
**Returns**: str


## Function: _sign

**Parameters**: replay_key, digest
**Returns**: str


## Function: _hash_input

**Parameters**: payload
**Returns**: str


## Function: _hash_output

**Parameters**: output
**Returns**: str


## Function: _hash_target

**Parameters**: target_callable
**Returns**: str


## Function: verify_replay

**Parameters**: self
**Returns**: bool
**Description**: Verify the replay key can be reconstructed from the proof fields.

        Emits ``guards_replay`` ADG edge.
        



## Function: is_signed

**Parameters**: self
**Returns**: bool
**Description**: True if execution_signature is populated.



## Function: __init__

**Parameters**: self, module
**Returns**: None


## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: emit

**Parameters**: self, operation, elapsed_ms, success
**Returns**: ExecutionProof
**Description**: Emit a signed execution proof for ``operation``.

        Emits ``emits_replay_key`` + ``emits_determinism_digest``
        + ``signs_execution_trace`` ADG edges.
        



## Function: emit_proof

**Parameters**: self, operation
**Returns**: Callable
**Description**: Decorator: wrap a callable with execution proof emission.



## Function: proof_op

**Parameters**: self, operation
**Returns**: ExecutionProofEmitter.proof_context
**Description**: Return a context manager that emits a proof for ``operation``.



## Function: ledger

**Parameters**: self
**Returns**: list[ExecutionProof]


## Function: latest

**Parameters**: self
**Returns**: ExecutionProof | None


## Function: __init__

**Parameters**: self, emitter, operation
**Returns**: None


## Function: __enter__

**Parameters**: self
**Returns**: ExecutionProofEmitter.proof_context


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: bool


## Function: decorator

**Parameters**: fn
**Returns**: Callable


## Function: wrapper



## Usage Examples

### Class Usage

```python
# Using ExecutionProof
executionproof = ExecutionProof()
executionproof.verify_replay()
executionproof.is_signed()
```

```python
# Using ExecutionProofEmitter
executionproofemitter = ExecutionProofEmitter()
executionproofemitter.emit()
executionproofemitter.emit_proof()
```

```python
# Using proof_context
proof_context = proof_context()
```

### Function Usage

```python
# Using _compute_replay_key
result = _compute_replay_key(trace_id, run_id)
```

```python
# Using _compute_digest
result = _compute_digest(replay_key, elapsed_ms)
```

```python
# Using _sign_proof
result = _sign_proof(execution_proof_id, replay_key)
```



---
**Generated**: 2026-03-26T09:39:03.669434
**Type**: api_reference
**Quality**: comprehensive
