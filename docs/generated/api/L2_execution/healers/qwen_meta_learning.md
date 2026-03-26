# API Documentation: qwen_meta_learning

**Target Audience**: developers, api_users

# qwen_meta_learning API Documentation

**File**: `qwen_meta_learning.py`
**Classes**: 0
**Functions**: 5


## Functions

- **get_historical_success_rate** -> float
- **set_historical_success_rate** -> None
- **update_qwen_confidence_prior** -> None
- **validate_threshold_immutability** -> None
- **clear_historical_success_rates** -> None


## Function: get_historical_success_rate

**Parameters**: error_signature
**Returns**: float
**Description**: Look up historical success rate for an error signature.



## Function: set_historical_success_rate

**Parameters**: error_signature, rate
**Returns**: None
**Description**: Record historical success rate (allowed meta-learning operation).



## Function: update_qwen_confidence_prior

**Parameters**: error_signature, success
**Returns**: None
**Description**: 
    Qwen metrics may update healer confidence priors ONLY.

    ALLOWED:
    - Historical success rate updates
    - Failure class prior adjustments
    - Tool readiness certainty updates

    FORBIDDEN:
    - HEALING_CONFIDENCE_X modification
    - HEALING_CONFIDENCE_Y modification
    - Routing election logic changes
    - Safety threshold modifications
    - Embedding scoring changes
    - RAG cutoff modifications
    



## Function: validate_threshold_immutability

**Returns**: None
**Description**: Ensure healing thresholds cannot be modified.



## Function: clear_historical_success_rates

**Returns**: None
**Description**: Clear all historical success rates (for testing).



## Usage Examples

### Function Usage

```python
# Using get_historical_success_rate
result = get_historical_success_rate(error_signature)
```

```python
# Using set_historical_success_rate
result = set_historical_success_rate(error_signature, rate)
```

```python
# Using update_qwen_confidence_prior
result = update_qwen_confidence_prior(error_signature, success)
```



---
**Generated**: 2026-03-26T09:39:03.844151
**Type**: api_reference
**Quality**: comprehensive
