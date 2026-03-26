# API Documentation: route_decision_artifact_types

**Target Audience**: developers, api_users

# route_decision_artifact_types API Documentation

**File**: `route_decision_artifact_types.py`
**Classes**: 5
**Functions**: 2

## Classes

- **ChosenRoute**
- **CandidateEntry**
- **PolicyContext**
- **DeterminismContext**
- **L3RouteDecisionArtifact**

## Functions

- **build_l3_route_decision_artifact** -> L3RouteDecisionArtifact
- **__post_init__** -> None


## Class: ChosenRoute

**Description**: Selected agent route at the L3 decision boundary.



## Class: CandidateEntry

**Description**: A candidate agent considered during routing.



## Class: PolicyContext

**Description**: Policy context active during routing decision.



## Class: DeterminismContext

**Description**: Determinism parameters for reproducibility.



## Class: L3RouteDecisionArtifact

**Description**: Wave 2.1 — L3 Route Decision Artifact emitted at routing boundary.

    Emitted exactly once per routing decision in delegate_task().
    Not emitted on cache hits or when no candidates are found.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: build_l3_route_decision_artifact

**Parameters**: trace_id, chosen, candidates, policy_context, determinism, semantic_clock
**Returns**: L3RouteDecisionArtifact
**Description**: Factory: build artifact from delegate_task() runtime data.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ChosenRoute
chosenroute = ChosenRoute()
```

```python
# Using CandidateEntry
candidateentry = CandidateEntry()
```

```python
# Using PolicyContext
policycontext = PolicyContext()
```

### Function Usage

```python
# Using build_l3_route_decision_artifact
result = build_l3_route_decision_artifact(trace_id, chosen)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.413170
**Type**: api_reference
**Quality**: comprehensive
