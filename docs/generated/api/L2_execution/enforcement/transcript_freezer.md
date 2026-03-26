# API Documentation: transcript_freezer

**Target Audience**: developers, api_users

# transcript_freezer API Documentation

**File**: `transcript_freezer.py`
**Classes**: 2
**Functions**: 5

## Classes

- **TranscriptMutationViolation** (inherits from Exception)
- **FrozenTranscript** (inherits from <ast.Subscript object at 0x000001CBFB9BDDD0>)

## Functions

- **freeze_transcript** -> FrozenTranscript
- **__init__**
- **__getitem__** -> Any
- **__len__** -> int
- **_raise_violation** -> None


## Class: TranscriptMutationViolation

**Description**: Raised when an attempt is made to mutate a frozen execution transcript.

**Inherits from**: Exception



## Class: FrozenTranscript

**Description**: A read-only wrapper around a transcript that raises an error on mutation.

**Inherits from**: MutableSequence[Any]

### Methods

#### __init__
**Parameters**: self, transcript_data

#### __getitem__
**Parameters**: self, index
**Returns**: Any

#### __len__
**Parameters**: self
**Returns**: int

#### _raise_violation
**Parameters**: self
**Returns**: None



## Function: freeze_transcript

**Parameters**: transcript
**Returns**: FrozenTranscript
**Description**: 
    Freezes an execution transcript, making it immutable.

    This is a critical sovereign gate that must be called before computing the
    determinism digest. It prevents late-arriving or asynchronous operations
    from silently altering the transcript after it has been used as input for
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_writes_through
_emit_pulls_context("p1", "transcript_freezer", "context_pull")
_emit_pulls_context("p1", "transcript_freezer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "transcript_freezer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "transcript_freezer", "uwg_term_secondary")
_emit_writes_through("p1", "transcript_freezer", "write_through")
_emit_writes_through("p1", "transcript_freezer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "transcript_freezer", "safety_validation")
_emit_invokes_eval("p1", "transcript_freezer", "eval_call")
_emit_proposal_commits_routing("p1", "transcript_freezer", "routing_commit")
    the digest, which would break determinism.

    Args:
        transcript: The mutable list representing the execution transcript.

    Returns:
        A FrozenTranscript instance that provides a read-only view of the transcript.
    



## Function: __init__

**Parameters**: self, transcript_data


## Function: __getitem__

**Parameters**: self, index
**Returns**: Any


## Function: __len__

**Parameters**: self
**Returns**: int


## Function: _raise_violation

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using TranscriptMutationViolation
transcriptmutationviolation = TranscriptMutationViolation()
```

```python
# Using FrozenTranscript
frozentranscript = FrozenTranscript()
```

### Function Usage

```python
# Using freeze_transcript
result = freeze_transcript(transcript)
```

```python
# Using __init__
result = __init__(transcript_data)
```

```python
# Using __getitem__
result = __getitem__(index)
```



---
**Generated**: 2026-03-26T09:39:03.744209
**Type**: api_reference
**Quality**: comprehensive
