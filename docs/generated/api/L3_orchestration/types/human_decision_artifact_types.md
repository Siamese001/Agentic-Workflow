# API Documentation: human_decision_artifact_types

**Target Audience**: developers, api_users

# human_decision_artifact_types API Documentation

**File**: `human_decision_artifact_types.py`
**Classes**: 3
**Functions**: 7

## Classes

- **HumanAction** (inherits from Enum)
- **StructuredPatchSchema**
- **HumanDecisionArtifact**

## Functions

- **create_human_review_draft** -> HumanDecisionArtifact
- **create_approval_artifact** -> HumanDecisionArtifact
- **create_rejection_artifact** -> HumanDecisionArtifact
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **apply_modify_diff** -> None
- **validate_patch_constraints** -> bool


## Class: HumanAction

**Description**: Actions available for human review.

**Inherits from**: Enum



## Class: StructuredPatchSchema

**Description**: Schema for structured patches in MODIFY_DIFF actions.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: HumanDecisionArtifact

**Description**: Artifact for human review workflow in Path D.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.

#### apply_modify_diff
**Parameters**: self, reviewer_id, modified_plan, rationale
**Returns**: None
**Description**: 
        Apply MODIFY_DIFF action to the artifact.

        Args:
            reviewer_id: ID of the reviewer making changes
            modified_plan: Modified plan content
            rationale: Rationale for the modifications
        

#### validate_patch_constraints
**Parameters**: self, patch
**Returns**: bool
**Description**: 
        Validate that a patch conforms to the structured patch schema.

        Args:
            patch: Patch to validate

        Returns:
            True if patch conforms to schema, False otherwise
        



## Function: create_human_review_draft

**Parameters**: trace_id, policy_hash, plan_hash, governed_payload, allowed_tools, plan_content
**Returns**: HumanDecisionArtifact
**Description**: 
    Create a human decision artifact draft for Path D.

    Args:
        trace_id: Unique trace identifier
        policy_hash: Policy validation hash
        plan_hash: Hash of the original plan
        governed_payload: The governed payload being reviewed
        allowed_tools: Tuple of allowed tools for modifications
        plan_content: Plan content for review (optional)

    Returns:
        HumanDecisionArtifact ready for human review
    



## Function: create_approval_artifact

**Parameters**: trace_id, policy_hash, plan_hash, reviewer_id, rationale
**Returns**: HumanDecisionArtifact
**Description**: 
    Create an approval artifact for Path D.

    Args:
        trace_id: Unique trace identifier
        policy_hash: Policy validation hash
        plan_hash: Hash of the approved plan
        reviewer_id: ID of the approving reviewer
        rationale: Rationale for approval (optional)

    Returns:
        HumanDecisionArtifact with APPROVE action
    



## Function: create_rejection_artifact

**Parameters**: trace_id, policy_hash, plan_hash, reviewer_id, rationale
**Returns**: HumanDecisionArtifact
**Description**: 
    Create a rejection artifact for Path D.

    Args:
        trace_id: Unique trace identifier
        policy_hash: Policy validation hash
        plan_hash: Hash of the rejected plan
        reviewer_id: ID of the rejecting reviewer
        rationale: Rationale for rejection

    Returns:
        HumanDecisionArtifact with REJECT action
    



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: apply_modify_diff

**Parameters**: self, reviewer_id, modified_plan, rationale
**Returns**: None
**Description**: 
        Apply MODIFY_DIFF action to the artifact.

        Args:
            reviewer_id: ID of the reviewer making changes
            modified_plan: Modified plan content
            rationale: Rationale for the modifications
        



## Function: validate_patch_constraints

**Parameters**: self, patch
**Returns**: bool
**Description**: 
        Validate that a patch conforms to the structured patch schema.

        Args:
            patch: Patch to validate

        Returns:
            True if patch conforms to schema, False otherwise
        



## Usage Examples

### Class Usage

```python
# Using HumanAction
humanaction = HumanAction()
```

```python
# Using StructuredPatchSchema
structuredpatchschema = StructuredPatchSchema()
structuredpatchschema.to_dict()
```

```python
# Using HumanDecisionArtifact
humandecisionartifact = HumanDecisionArtifact()
humandecisionartifact.to_dict()
humandecisionartifact.apply_modify_diff()
```

### Function Usage

```python
# Using create_human_review_draft
result = create_human_review_draft(trace_id, policy_hash)
```

```python
# Using create_approval_artifact
result = create_approval_artifact(trace_id, policy_hash)
```

```python
# Using create_rejection_artifact
result = create_rejection_artifact(trace_id, policy_hash)
```



---
**Generated**: 2026-03-26T09:39:04.385285
**Type**: api_reference
**Quality**: comprehensive
