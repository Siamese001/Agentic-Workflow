# API Documentation: component_util

**Target Audience**: developers, api_users

# component_util API Documentation

**File**: `component_util.py`
**Classes**: 1
**Functions**: 10

## Classes

- **ComponentFactory**

## Functions

- **get_verification_gate** -> VerificationGateProtocol | None
- **get_human_review_queue** -> HumanReviewProtocol | None
- **get_detection_emitter** -> DetectionSignalProtocol | None
- **get_meta_learning_service** -> MetaLearningProtocol | None
- **get_verification_gate** -> VerificationGateProtocol | None
- **get_human_review_queue** -> HumanReviewProtocol | None
- **get_detection_emitter** -> DetectionSignalProtocol | None
- **get_meta_learning_service** -> MetaLearningProtocol | None
- **clear_instances** -> None
- **get_component_status** -> dict[str, Any]


## Class: ComponentFactory

**Description**: Factory for creating protocol-compliant components.

    Manages singleton instances of components and provides proper
    feature flag integration for all component creation.
    

### Methods

#### get_verification_gate
**Parameters**: cls, use_adapter
**Returns**: VerificationGateProtocol | None
**Description**: Get verification gate instance.

        Args:
            use_adapter: If True, use protocol-compliant adapter

        Returns:
            VerificationGateProtocol instance or None if disabled
        

#### get_human_review_queue
**Parameters**: cls, use_adapter
**Returns**: HumanReviewProtocol | None
**Description**: Get human review queue instance.

        Args:
            use_adapter: If True, use protocol-compliant adapter

        Returns:
            HumanReviewProtocol instance or None if disabled
        

#### get_detection_emitter
**Parameters**: cls
**Returns**: DetectionSignalProtocol | None
**Description**: Get detection signal emitter instance.

        Returns:
            DetectionSignalProtocol instance or None if disabled
        

#### get_meta_learning_service
**Parameters**: cls
**Returns**: MetaLearningProtocol | None
**Description**: Get meta-learning service instance.

        Returns:
            MetaLearningProtocol instance or None if disabled
        

#### clear_instances
**Parameters**: cls
**Returns**: None
**Description**: Clear all cached instances.

#### get_component_status
**Parameters**: cls
**Returns**: dict[str, Any]
**Description**: Get status of all components.

        Returns:
            Dictionary with component availability and flag status
        



## Function: get_verification_gate

**Parameters**: use_adapter
**Returns**: VerificationGateProtocol | None
**Description**: Get verification gate instance.



## Function: get_human_review_queue

**Parameters**: use_adapter
**Returns**: HumanReviewProtocol | None
**Description**: Get human review queue instance.



## Function: get_detection_emitter

**Returns**: DetectionSignalProtocol | None
**Description**: Get detection signal emitter instance.



## Function: get_meta_learning_service

**Returns**: MetaLearningProtocol | None
**Description**: Get meta-learning service instance.



## Function: get_verification_gate

**Parameters**: cls, use_adapter
**Returns**: VerificationGateProtocol | None
**Description**: Get verification gate instance.

        Args:
            use_adapter: If True, use protocol-compliant adapter

        Returns:
            VerificationGateProtocol instance or None if disabled
        



## Function: get_human_review_queue

**Parameters**: cls, use_adapter
**Returns**: HumanReviewProtocol | None
**Description**: Get human review queue instance.

        Args:
            use_adapter: If True, use protocol-compliant adapter

        Returns:
            HumanReviewProtocol instance or None if disabled
        



## Function: get_detection_emitter

**Parameters**: cls
**Returns**: DetectionSignalProtocol | None
**Description**: Get detection signal emitter instance.

        Returns:
            DetectionSignalProtocol instance or None if disabled
        



## Function: get_meta_learning_service

**Parameters**: cls
**Returns**: MetaLearningProtocol | None
**Description**: Get meta-learning service instance.

        Returns:
            MetaLearningProtocol instance or None if disabled
        



## Function: clear_instances

**Parameters**: cls
**Returns**: None
**Description**: Clear all cached instances.



## Function: get_component_status

**Parameters**: cls
**Returns**: dict[str, Any]
**Description**: Get status of all components.

        Returns:
            Dictionary with component availability and flag status
        



## Usage Examples

### Class Usage

```python
# Using ComponentFactory
componentfactory = ComponentFactory()
componentfactory.get_verification_gate()
componentfactory.get_human_review_queue()
```

### Function Usage

```python
# Using get_verification_gate
result = get_verification_gate(use_adapter)
```

```python
# Using get_human_review_queue
result = get_human_review_queue(use_adapter)
```

```python
# Using get_detection_emitter
result = get_detection_emitter()
```



---
**Generated**: 2026-03-26T09:39:03.510168
**Type**: api_reference
**Quality**: comprehensive
