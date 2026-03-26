# API Documentation: blast_radius

**Target Audience**: developers, api_users

# blast_radius API Documentation

**File**: `blast_radius.py`
**Classes**: 3
**Functions**: 17

## Classes

- **BlastRadiusMetrics**
- **BlastRadiusCalculator**
- **BlastRadiusEnforcer**

## Functions

- **enforce_blast_radius** -> BlastRadiusMetrics
- **get_proposal_metrics** -> BlastRadiusMetrics | None
- **clear_proposal** -> None
- **validate_total_impact** -> bool
- **__init__**
- **calculate_blast_radius** -> BlastRadiusMetrics
- **_count_affected_objects** -> int
- **_estimate_state_surface** -> int
- **_calculate_mutation_depth** -> int
- **_count_cross_layer_impacts** -> int
- **__init__**
- **enforce_blast_radius** -> BlastRadiusMetrics
- **get_proposal_metrics** -> BlastRadiusMetrics | None
- **clear_proposal** -> None
- **get_total_blast_radius** -> int
- **validate_total_impact** -> bool
- **_is_nested** -> bool


## Class: BlastRadiusMetrics

**Description**: Metrics for blast radius calculation.



## Class: BlastRadiusCalculator

**Description**: Calculates deterministic blast radius for meta-learning proposals.

### Methods

#### __init__
**Parameters**: self, max_radius, max_bytes

#### calculate_blast_radius
**Parameters**: self, proposal
**Returns**: BlastRadiusMetrics
**Description**: Calculate deterministic blast radius for a proposal.

        Args:
            proposal: Meta-learning proposal to analyze

        Returns:
            BlastRadiusMetrics with calculated values

        Raises:
            ValueError: If blast radius exceeds limits
        

#### _count_affected_objects
**Parameters**: self, proposal
**Returns**: int
**Description**: Count objects that would be affected by this proposal.

        Args:
            proposal: Proposal to analyze

        Returns:
            Number of affected objects
        

#### _estimate_state_surface
**Parameters**: self, proposal
**Returns**: int
**Description**: Estimate the size of state surface this proposal affects.

        Args:
            proposal: Proposal to analyze

        Returns:
            Size in bytes
        

#### _calculate_mutation_depth
**Parameters**: self, proposal
**Returns**: int
**Description**: Calculate the depth of mutations this proposal would cause.

        Args:
            proposal: Proposal to analyze

        Returns:
            Mutation depth (1-5 scale)
        

#### _count_cross_layer_impacts
**Parameters**: self, proposal
**Returns**: int
**Description**: Count impacts that cross layer boundaries.

        Args:
            proposal: Proposal to analyze

        Returns:
            Number of cross-layer impacts
        



## Class: BlastRadiusEnforcer

**Description**: Enforces blast radius containment policies.

### Methods

#### __init__
**Parameters**: self, calculator

#### enforce_blast_radius
**Parameters**: self, proposal_id, proposal
**Returns**: BlastRadiusMetrics
**Description**: Enforce blast radius containment for a proposal.

        Args:
            proposal_id: Unique identifier for the proposal
            proposal: The proposal to enforce

        Returns:
            BlastRadiusMetrics for the approved proposal

        Raises:
            ValueError: If blast radius exceeds limits
            RuntimeError: If proposal already exists
        

#### get_proposal_metrics
**Parameters**: self, proposal_id
**Returns**: BlastRadiusMetrics | None
**Description**: Get metrics for an active proposal.

        Args:
            proposal_id: Proposal identifier

        Returns:
            BlastRadiusMetrics or None if not found
        

#### clear_proposal
**Parameters**: self, proposal_id
**Returns**: None
**Description**: Clear a proposal from active tracking.

        Args:
            proposal_id: Proposal identifier to clear
        

#### get_total_blast_radius
**Parameters**: self
**Returns**: int
**Description**: Get total blast radius across all active proposals.

        Returns:
            Total blast radius
        

#### validate_total_impact
**Parameters**: self
**Returns**: bool
**Description**: Validate that total impact across all proposals is acceptable.

        Returns:
            True if total impact is acceptable

        Raises:
            ValueError: If total impact exceeds limits
        



## Function: enforce_blast_radius

**Parameters**: proposal_id, proposal
**Returns**: BlastRadiusMetrics
**Description**: Exported function for blast radius enforcement.



## Function: get_proposal_metrics

**Parameters**: proposal_id
**Returns**: BlastRadiusMetrics | None
**Description**: Exported function to get proposal metrics.



## Function: clear_proposal

**Parameters**: proposal_id
**Returns**: None
**Description**: Exported function to clear a proposal.



## Function: validate_total_impact

**Returns**: bool
**Description**: Exported function to validate total impact.



## Function: __init__

**Parameters**: self, max_radius, max_bytes


## Function: calculate_blast_radius

**Parameters**: self, proposal
**Returns**: BlastRadiusMetrics
**Description**: Calculate deterministic blast radius for a proposal.

        Args:
            proposal: Meta-learning proposal to analyze

        Returns:
            BlastRadiusMetrics with calculated values

        Raises:
            ValueError: If blast radius exceeds limits
        



## Function: _count_affected_objects

**Parameters**: self, proposal
**Returns**: int
**Description**: Count objects that would be affected by this proposal.

        Args:
            proposal: Proposal to analyze

        Returns:
            Number of affected objects
        



## Function: _estimate_state_surface

**Parameters**: self, proposal
**Returns**: int
**Description**: Estimate the size of state surface this proposal affects.

        Args:
            proposal: Proposal to analyze

        Returns:
            Size in bytes
        



## Function: _calculate_mutation_depth

**Parameters**: self, proposal
**Returns**: int
**Description**: Calculate the depth of mutations this proposal would cause.

        Args:
            proposal: Proposal to analyze

        Returns:
            Mutation depth (1-5 scale)
        



## Function: _count_cross_layer_impacts

**Parameters**: self, proposal
**Returns**: int
**Description**: Count impacts that cross layer boundaries.

        Args:
            proposal: Proposal to analyze

        Returns:
            Number of cross-layer impacts
        



## Function: __init__

**Parameters**: self, calculator


## Function: enforce_blast_radius

**Parameters**: self, proposal_id, proposal
**Returns**: BlastRadiusMetrics
**Description**: Enforce blast radius containment for a proposal.

        Args:
            proposal_id: Unique identifier for the proposal
            proposal: The proposal to enforce

        Returns:
            BlastRadiusMetrics for the approved proposal

        Raises:
            ValueError: If blast radius exceeds limits
            RuntimeError: If proposal already exists
        



## Function: get_proposal_metrics

**Parameters**: self, proposal_id
**Returns**: BlastRadiusMetrics | None
**Description**: Get metrics for an active proposal.

        Args:
            proposal_id: Proposal identifier

        Returns:
            BlastRadiusMetrics or None if not found
        



## Function: clear_proposal

**Parameters**: self, proposal_id
**Returns**: None
**Description**: Clear a proposal from active tracking.

        Args:
            proposal_id: Proposal identifier to clear
        



## Function: get_total_blast_radius

**Parameters**: self
**Returns**: int
**Description**: Get total blast radius across all active proposals.

        Returns:
            Total blast radius
        



## Function: validate_total_impact

**Parameters**: self
**Returns**: bool
**Description**: Validate that total impact across all proposals is acceptable.

        Returns:
            True if total impact is acceptable

        Raises:
            ValueError: If total impact exceeds limits
        



## Function: _is_nested

**Parameters**: val
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using BlastRadiusMetrics
blastradiusmetrics = BlastRadiusMetrics()
```

```python
# Using BlastRadiusCalculator
blastradiuscalculator = BlastRadiusCalculator()
blastradiuscalculator.calculate_blast_radius()
```

```python
# Using BlastRadiusEnforcer
blastradiusenforcer = BlastRadiusEnforcer()
blastradiusenforcer.enforce_blast_radius()
blastradiusenforcer.get_proposal_metrics()
```

### Function Usage

```python
# Using enforce_blast_radius
result = enforce_blast_radius(proposal_id, proposal)
```

```python
# Using get_proposal_metrics
result = get_proposal_metrics(proposal_id)
```

```python
# Using clear_proposal
result = clear_proposal(proposal_id)
```



---
**Generated**: 2026-03-26T09:39:04.485414
**Type**: api_reference
**Quality**: comprehensive
