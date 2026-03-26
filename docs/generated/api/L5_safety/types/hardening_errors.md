# API Documentation: hardening_errors

**Target Audience**: developers, api_users

# hardening_errors API Documentation

**File**: `hardening_errors.py`
**Classes**: 9
**Functions**: 0

## Classes

- **ExecutionTraceIntegrityError** (inherits from RuntimeError)
- **MutationReplayIntegrityViolation** (inherits from RuntimeError)
- **LedgerIntegrityViolation** (inherits from RuntimeError)
- **MutationCommitFailure** (inherits from RuntimeError)
- **C0AuthorityLeakError** (inherits from RuntimeError)
- **C0MutationViolation** (inherits from RuntimeError)
- **RuntimePolicyMutationViolation** (inherits from RuntimeError)
- **HumanPatchValidationError** (inherits from RuntimeError)
- **HumanPatchL5ClearanceError** (inherits from RuntimeError)


## Class: ExecutionTraceIntegrityError

**Description**: Raised when ExecutionTrace is missing required fields (Addendum 1.1).

**Inherits from**: RuntimeError



## Class: MutationReplayIntegrityViolation

**Description**: Raised when computed diff != UWG state_diff (Addendum 1.2).

**Inherits from**: RuntimeError



## Class: LedgerIntegrityViolation

**Description**: Raised when ledger hash chain is broken (Addendum 2.2).

**Inherits from**: RuntimeError



## Class: MutationCommitFailure

**Description**: Raised when 2PC commit fails (either ACK missing) (Addendum 2.3).

**Inherits from**: RuntimeError



## Class: C0AuthorityLeakError

**Description**: Raised when C0 RAG payload contains authority fields (Addendum 3.1).

**Inherits from**: RuntimeError



## Class: C0MutationViolation

**Description**: Raised when C0 context payload is mutated during assembly (Addendum 3.2).

**Inherits from**: RuntimeError



## Class: RuntimePolicyMutationViolation

**Description**: Raised when runtime config is modified during meta-learning S1-S8 (Addendum 5.2).

**Inherits from**: RuntimeError



## Class: HumanPatchValidationError

**Description**: Raised when a human patch is missing required fields (Addendum 6.1).

**Inherits from**: RuntimeError



## Class: HumanPatchL5ClearanceError

**Description**: Raised when a human patch bypasses L5 re-clearance (Addendum 6.2).

**Inherits from**: RuntimeError



## Usage Examples

### Class Usage

```python
# Using ExecutionTraceIntegrityError
executiontraceintegrityerror = ExecutionTraceIntegrityError()
```

```python
# Using MutationReplayIntegrityViolation
mutationreplayintegrityviolation = MutationReplayIntegrityViolation()
```

```python
# Using LedgerIntegrityViolation
ledgerintegrityviolation = LedgerIntegrityViolation()
```



---
**Generated**: 2026-03-26T09:39:05.507295
**Type**: api_reference
**Quality**: comprehensive
