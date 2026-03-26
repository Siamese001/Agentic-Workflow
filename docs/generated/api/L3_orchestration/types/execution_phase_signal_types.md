# API Documentation: execution_phase_signal_types

**Target Audience**: developers, api_users

# execution_phase_signal_types API Documentation

**File**: `execution_phase_signal_types.py`
**Classes**: 3
**Functions**: 1

## Classes

- **ExecutionPhaseSignal** (inherits from Enum)
- **ExecutionPhase**
- **WorkflowSnapshot**

## Functions

- **__post_init__**


## Class: ExecutionPhaseSignal

**Description**: Signal enum for phase logic checks.

**Inherits from**: Enum



## Class: ExecutionPhase

**Description**: Definition of an execution phase - sovereign template for apps to extend.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Map name to signal enum for logic checks.



## Class: WorkflowSnapshot

**Description**: Snapshot of workflow state for rollback - sovereign core type.



## Function: __post_init__

**Parameters**: self
**Description**: Map name to signal enum for logic checks.



## Usage Examples

### Class Usage

```python
# Using ExecutionPhaseSignal
executionphasesignal = ExecutionPhaseSignal()
```

```python
# Using ExecutionPhase
executionphase = ExecutionPhase()
```

```python
# Using WorkflowSnapshot
workflowsnapshot = WorkflowSnapshot()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.370463
**Type**: api_reference
**Quality**: comprehensive
