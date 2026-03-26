# API Documentation: deterministic_replay_guard

**Target Audience**: developers, api_users

# deterministic_replay_guard API Documentation

**File**: `deterministic_replay_guard.py`
**Classes**: 3
**Functions**: 5

## Classes

- **DeterminismViolation** (inherits from RuntimeError)
- **ReplayVerificationResult**
- **DeterministicReplayGuard**

## Functions

- **get_replay_guard** -> DeterministicReplayGuard
- **reset_replay_guard** -> None
- **mismatch_summary** -> str
- **__init__** -> None
- **verify_routing_replay** -> ReplayVerificationResult


## Class: DeterminismViolation

**Description**: Raised when a routing replay produces a mismatched result.

**Inherits from**: RuntimeError



## Class: ReplayVerificationResult

**Description**: Result of a routing replay verification.

### Methods

#### mismatch_summary
**Parameters**: self
**Returns**: str



## Class: DeterministicReplayGuard

**Description**: Replay guard for L0 routing decisions.

    Usage::

        guard = DeterministicReplayGuard(replay_mode=True)
        result = guard.verify_routing_replay(artifact)
        if not result.passed:
            raise DeterminismViolation(result.mismatch_summary)

    When replay_mode is False, verify_routing_replay is a no-op pass-through.
    

### Methods

#### __init__
**Parameters**: self, replay_mode
**Returns**: None

#### verify_routing_replay
**Parameters**: self, artifact
**Returns**: ReplayVerificationResult
**Description**: Verify a routing artifact can be deterministically replayed.

        Args:
            artifact:    The RoutingArtifact emitted at the original routing decision.
            fail_closed: If True (default), raise DeterminismViolation on mismatch.

        Returns:
            ReplayVerificationResult with pass/fail and key comparison.

        ADG edge: guards_replay
        



## Function: get_replay_guard

**Parameters**: replay_mode
**Returns**: DeterministicReplayGuard
**Description**: Return the process-level deterministic replay guard.



## Function: reset_replay_guard

**Returns**: None
**Description**: Reset the global replay guard (for testing).



## Function: mismatch_summary

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, replay_mode
**Returns**: None


## Function: verify_routing_replay

**Parameters**: self, artifact
**Returns**: ReplayVerificationResult
**Description**: Verify a routing artifact can be deterministically replayed.

        Args:
            artifact:    The RoutingArtifact emitted at the original routing decision.
            fail_closed: If True (default), raise DeterminismViolation on mismatch.

        Returns:
            ReplayVerificationResult with pass/fail and key comparison.

        ADG edge: guards_replay
        



## Usage Examples

### Class Usage

```python
# Using DeterminismViolation
determinismviolation = DeterminismViolation()
```

```python
# Using ReplayVerificationResult
replayverificationresult = ReplayVerificationResult()
replayverificationresult.mismatch_summary()
```

```python
# Using DeterministicReplayGuard
deterministicreplayguard = DeterministicReplayGuard()
deterministicreplayguard.verify_routing_replay()
```

### Function Usage

```python
# Using get_replay_guard
result = get_replay_guard(replay_mode)
```

```python
# Using reset_replay_guard
result = reset_replay_guard()
```

```python
# Using mismatch_summary
result = mismatch_summary()
```



---
**Generated**: 2026-03-26T09:39:02.609441
**Type**: api_reference
**Quality**: comprehensive
