# API Documentation: rollback_refiner

**Target Audience**: developers, api_users

# rollback_refiner API Documentation

**File**: `rollback_refiner.py`
**Classes**: 2
**Functions**: 7

## Classes

- **RollbackRefiner** (inherits from Protocol)
- **DefaultDeterministicRollbackRefiner**

## Functions

- **refine** -> RollbackRefinementDecision
- **__init__**
- **refine** -> RollbackRefinementDecision
- **_parse_history_stats** -> dict[str, RollbackOutcomeStats]
- **_score_candidates** -> list[tuple[float, RollbackStrategyId]]
- **_calculate_score** -> float
- **_generate_reasons** -> list[str]


## Class: RollbackRefiner

**Description**: Protocol for rollback refinement engines.

**Inherits from**: Protocol

### Methods

#### refine
**Returns**: RollbackRefinementDecision
**Description**: Refine rollback strategy selection.



## Class: DefaultDeterministicRollbackRefiner

**Description**: Deterministic rollback refiner with stable tie-breaking.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize deterministic refiner.

#### refine
**Parameters**: self
**Returns**: RollbackRefinementDecision
**Description**: Refine rollback strategy selection deterministically.

#### _parse_history_stats
**Parameters**: self, history_bytes
**Returns**: dict[str, RollbackOutcomeStats]
**Description**: Parse history bytes to extract strategy statistics.

#### _score_candidates
**Parameters**: self, candidates, strategy_stats, failure_signature
**Returns**: list[tuple[float, RollbackStrategyId]]
**Description**: Score candidates based on statistics and deterministic rules.

#### _calculate_score
**Parameters**: self, candidate, strategy_stats, failure_signature
**Returns**: float
**Description**: Calculate deterministic score for a strategy.

#### _generate_reasons
**Parameters**: self, chosen, strategy_stats, failure_signature
**Returns**: list[str]
**Description**: Generate deterministic reasoning for the choice.



## Function: refine

**Returns**: RollbackRefinementDecision
**Description**: Refine rollback strategy selection.



## Function: __init__

**Parameters**: self
**Description**: Initialize deterministic refiner.



## Function: refine

**Parameters**: self
**Returns**: RollbackRefinementDecision
**Description**: Refine rollback strategy selection deterministically.



## Function: _parse_history_stats

**Parameters**: self, history_bytes
**Returns**: dict[str, RollbackOutcomeStats]
**Description**: Parse history bytes to extract strategy statistics.



## Function: _score_candidates

**Parameters**: self, candidates, strategy_stats, failure_signature
**Returns**: list[tuple[float, RollbackStrategyId]]
**Description**: Score candidates based on statistics and deterministic rules.



## Function: _calculate_score

**Parameters**: self, candidate, strategy_stats, failure_signature
**Returns**: float
**Description**: Calculate deterministic score for a strategy.



## Function: _generate_reasons

**Parameters**: self, chosen, strategy_stats, failure_signature
**Returns**: list[str]
**Description**: Generate deterministic reasoning for the choice.



## Usage Examples

### Class Usage

```python
# Using RollbackRefiner
rollbackrefiner = RollbackRefiner()
rollbackrefiner.refine()
```

```python
# Using DefaultDeterministicRollbackRefiner
defaultdeterministicrollbackrefiner = DefaultDeterministicRollbackRefiner()
defaultdeterministicrollbackrefiner.refine()
```

### Function Usage

```python
# Using refine
result = refine()
```

```python
# Using __init__
result = __init__()
```

```python
# Using refine
result = refine()
```



---
**Generated**: 2026-03-26T09:39:03.768142
**Type**: api_reference
**Quality**: comprehensive
