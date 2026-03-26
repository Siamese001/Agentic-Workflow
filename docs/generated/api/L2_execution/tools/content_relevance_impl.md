# API Documentation: content_relevance_impl

**Target Audience**: developers, api_users

# content_relevance_impl API Documentation

**File**: `content_relevance_impl.py`
**Classes**: 1
**Functions**: 6

## Classes

- **AssessContentRelevance**

## Functions

- **__init__** -> None
- **score** -> ScoreResult
- **_extract_factors** -> dict[str, float]
- **_compute_weighted** -> float
- **_compute_confidence** -> float
- **compute_score** -> ScoreResult


## Class: AssessContentRelevance

**Description**: Scorer for resume domain.



## Function: __init__

**Parameters**: self, config
**Returns**: None


## Function: score

**Parameters**: self, data
**Returns**: ScoreResult
**Description**: Compute score for data.



## Function: _extract_factors

**Parameters**: self, data
**Returns**: dict[str, float]
**Description**: Extract scoring factors.



## Function: _compute_weighted

**Parameters**: self, factors
**Returns**: float
**Description**: Compute weighted score.



## Function: _compute_confidence

**Parameters**: self, factors
**Returns**: float
**Description**: Compute confidence.



## Function: compute_score

**Parameters**: data, config
**Returns**: ScoreResult
**Description**: Compute relevance score based on input parameters.



## Usage Examples

### Class Usage

```python
# Using AssessContentRelevance
assesscontentrelevance = AssessContentRelevance()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using score
result = score(data)
```

```python
# Using _extract_factors
result = _extract_factors(data)
```



---
**Generated**: 2026-03-26T09:39:03.900996
**Type**: api_reference
**Quality**: comprehensive
