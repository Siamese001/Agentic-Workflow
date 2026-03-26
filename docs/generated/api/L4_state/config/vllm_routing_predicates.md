# API Documentation: vllm_routing_predicates

**Target Audience**: developers, api_users

# vllm_routing_predicates API Documentation

**File**: `vllm_routing_predicates.py`
**Classes**: 3
**Functions**: 5

## Classes

- **Provider** (inherits from Enum)
- **RoutingDecision**
- **RoutingPredicate** (inherits from NamedTuple)

## Functions

- **requires_policy_read** -> bool
- **iteration_count_exceeded** -> bool
- **invalid_ast_detected** -> bool
- **default_routing** -> bool
- **evaluate** -> RoutingDecision


## Class: Provider

**Description**: Routing provider enumeration.

**Inherits from**: Enum



## Class: RoutingDecision

**Description**: Immutable routing decision with audit trail.



## Class: RoutingPredicate

**Description**: A named predicate entry: (name, test_function, target_provider).

**Inherits from**: NamedTuple



## Function: requires_policy_read

**Parameters**: ctx
**Returns**: bool
**Description**: True when the context requires a policy read.



## Function: iteration_count_exceeded

**Parameters**: ctx
**Returns**: bool
**Description**: True when iteration count exceeds the configured threshold.



## Function: invalid_ast_detected

**Parameters**: ctx
**Returns**: bool
**Description**: True when the context signals an invalid AST.



## Function: default_routing

**Parameters**: ctx
**Returns**: bool
**Description**: Default fallback predicate — always matches.



## Function: evaluate

**Parameters**: context
**Returns**: RoutingDecision
**Description**: Evaluate routing predicates against context.

    First-match-wins. Context is not mutated.
    Deterministic: key-order independent, hash-stable.
    



## Usage Examples

### Class Usage

```python
# Using Provider
provider = Provider()
```

```python
# Using RoutingDecision
routingdecision = RoutingDecision()
```

```python
# Using RoutingPredicate
routingpredicate = RoutingPredicate()
```

### Function Usage

```python
# Using requires_policy_read
result = requires_policy_read(ctx)
```

```python
# Using iteration_count_exceeded
result = iteration_count_exceeded(ctx)
```

```python
# Using invalid_ast_detected
result = invalid_ast_detected(ctx)
```



---
**Generated**: 2026-03-26T09:39:04.479741
**Type**: api_reference
**Quality**: comprehensive
