# API Documentation: l2_phase_spec

**Target Audience**: developers, api_users

# l2_phase_spec API Documentation

**File**: `l2_phase_spec.py`
**Classes**: 2
**Functions**: 0

## Classes

- **PhaseSpec**
- **L2ExecutionPlan**


## Class: PhaseSpec

**Description**: Immutable specification for a single execution phase.

    Attributes:
        name: Canonical phase name (unique within a plan).
        guardian_ids: Guardian IDs to run before this phase (empty for now).
        healer_ids: Healer IDs to invoke during this phase (empty for now).
        rerun_guardians: Guardian IDs to re-run after healing (empty for now).
        approval_required: Whether human approval is needed (False for now).
        inputs_from_prior: Phase names whose outputs feed this phase (empty for now).
    



## Class: L2ExecutionPlan

**Description**: Immutable, ordered sequence of PhaseSpecs defining an execution plan.



## Usage Examples

### Class Usage

```python
# Using PhaseSpec
phasespec = PhaseSpec()
```

```python
# Using L2ExecutionPlan
l2executionplan = L2ExecutionPlan()
```



---
**Generated**: 2026-03-26T09:39:03.974064
**Type**: api_reference
**Quality**: comprehensive
