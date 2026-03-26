# API Documentation: workflow_learning_bridge

**Target Audience**: developers, api_users

# workflow_learning_bridge API Documentation

**File**: `workflow_learning_bridge.py`
**Classes**: 2
**Functions**: 9

## Classes

- **WorkflowOutcome**
- **WorkflowLearningBridge**

## Functions

- **get_workflow_learning_bridge** -> WorkflowLearningBridge
- **reset_workflow_learning_bridge** -> None
- **capture** -> WorkflowOutcome
- **__init__** -> None
- **register_learner** -> None
- **contribute** -> None
- **ledger** -> list[WorkflowOutcome]
- **success_rate** -> float
- **average_quality** -> float


## Class: WorkflowOutcome

**Description**: Immutable record of a completed workflow, ready for learning.

### Methods

#### capture
**Parameters**: cls, bundle_id, workflow_type, success, elapsed_ms, agent_sequence, quality_score, metadata
**Returns**: WorkflowOutcome



## Class: WorkflowLearningBridge

**Description**: Routes workflow outcomes to system_learning consumers.

    Usage::

        bridge = WorkflowLearningBridge()
        bridge.register_learner("sl_adapter", my_sl_adapter.accept)

        outcome = WorkflowOutcome.capture(
            bundle_id="b-001",
            workflow_type="campaign_research",
            success=True,
            elapsed_ms=3200.0,
            agent_sequence=["ResearchAgent", "BriefAssembler"],
            quality_score=0.91,
        )
        bridge.contribute(outcome)
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register_learner
**Parameters**: self, name, callback
**Returns**: None
**Description**: Register a system_learning consumer.

#### contribute
**Parameters**: self, outcome
**Returns**: None
**Description**: Push a workflow outcome to all registered learners.

        Emits ``triggers_learning`` + ``feeds_back_signal``
        + ``contributes_to_sl`` ADG edges.
        

#### ledger
**Parameters**: self
**Returns**: list[WorkflowOutcome]

#### success_rate
**Parameters**: self
**Returns**: float

#### average_quality
**Parameters**: self
**Returns**: float



## Function: get_workflow_learning_bridge

**Returns**: WorkflowLearningBridge


## Function: reset_workflow_learning_bridge

**Returns**: None


## Function: capture

**Parameters**: cls, bundle_id, workflow_type, success, elapsed_ms, agent_sequence, quality_score, metadata
**Returns**: WorkflowOutcome


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register_learner

**Parameters**: self, name, callback
**Returns**: None
**Description**: Register a system_learning consumer.



## Function: contribute

**Parameters**: self, outcome
**Returns**: None
**Description**: Push a workflow outcome to all registered learners.

        Emits ``triggers_learning`` + ``feeds_back_signal``
        + ``contributes_to_sl`` ADG edges.
        



## Function: ledger

**Parameters**: self
**Returns**: list[WorkflowOutcome]


## Function: success_rate

**Parameters**: self
**Returns**: float


## Function: average_quality

**Parameters**: self
**Returns**: float


## Usage Examples

### Class Usage

```python
# Using WorkflowOutcome
workflowoutcome = WorkflowOutcome()
workflowoutcome.capture()
```

```python
# Using WorkflowLearningBridge
workflowlearningbridge = WorkflowLearningBridge()
workflowlearningbridge.register_learner()
workflowlearningbridge.contribute()
```

### Function Usage

```python
# Using get_workflow_learning_bridge
result = get_workflow_learning_bridge()
```

```python
# Using reset_workflow_learning_bridge
result = reset_workflow_learning_bridge()
```

```python
# Using capture
result = capture(cls, bundle_id)
```



---
**Generated**: 2026-03-26T09:39:04.238701
**Type**: api_reference
**Quality**: comprehensive
