# API Documentation: micro_stage_types

**Target Audience**: developers, api_users

# micro_stage_types API Documentation

**File**: `micro_stage_types.py`
**Classes**: 5
**Functions**: 0

## Classes

- **MicroStage** (inherits from str, Enum)
- **HopState** (inherits from str, Enum)
- **RetryPolicy** (inherits from BaseModel)
- **MicroCheckpoint** (inherits from BaseModel)
- **StageTransition** (inherits from BaseModel)


## Class: MicroStage

**Description**: The 5 atomic micro-stages of a Subatomic Hop.

**Inherits from**: str, Enum



## Class: HopState

**Description**: Overall state of a Subatomic Hop.

**Inherits from**: str, Enum



## Class: RetryPolicy

**Description**: Retry policy for micro-stages.

**Inherits from**: BaseModel



## Class: MicroCheckpoint

**Description**: Checkpoint data for a micro-stage to support recovery.

**Inherits from**: BaseModel



## Class: StageTransition

**Description**: Record of a stage transition within a hop.

**Inherits from**: BaseModel



## Usage Examples

### Class Usage

```python
# Using MicroStage
microstage = MicroStage()
```

```python
# Using HopState
hopstate = HopState()
```

```python
# Using RetryPolicy
retrypolicy = RetryPolicy()
```



---
**Generated**: 2026-03-26T09:39:04.638065
**Type**: api_reference
**Quality**: comprehensive
