# API Documentation: intelligence_query_validator

**Target Audience**: developers, api_users

# intelligence_query_validator API Documentation

**File**: `intelligence_query_validator.py`
**Classes**: 2
**Functions**: 9

## Classes

- **IntelligenceQueryResult**
- **IntelligenceQueryValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **validate_query** -> IntelligenceQueryResult
- **_validate_query_string** -> list[str]
- **_validate_filters** -> list[str]
- **_generate_cache_key** -> str
- **normalize_query** -> str
- **filter_results** -> list[dict[str, Any]]
- **calculate_query_complexity** -> dict[str, Any]


## Class: IntelligenceQueryResult

**Description**: Result of intelligence query validation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: IntelligenceQueryValidator

**Description**: 
    Pure deterministic intelligence query validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with intelligence librarian configuration.

        Args:
            config: Configuration dictionary containing validation rules
        

#### validate_query
**Parameters**: self, query, filters
**Returns**: IntelligenceQueryResult
**Description**: 
        Validate intelligence query using purely deterministic logic.

        Args:
            query: Query string to validate
            filters: Optional filters dictionary

        Returns:
            IntelligenceQueryResult with deterministic findings
        

#### _validate_query_string
**Parameters**: self, query
**Returns**: list[str]
**Description**: 
        Validate query string using deterministic rules.

        Moved to Deterministic: Pure string validation
        

#### _validate_filters
**Parameters**: self, filters
**Returns**: list[str]
**Description**: 
        Validate filters using deterministic schema validation.

        Moved to Deterministic: Pure schema validation
        

#### _generate_cache_key
**Parameters**: self, query, filters
**Returns**: str
**Description**: 
        Generate cache key using deterministic hashing.

        Moved to Deterministic: Pure hash generation
        

#### normalize_query
**Parameters**: self, query
**Returns**: str
**Description**: 
        Normalize query string using deterministic rules.

        Moved to Deterministic: Pure string normalization
        

#### filter_results
**Parameters**: self, results, filters
**Returns**: list[dict[str, Any]]
**Description**: 
        Filter results using deterministic filtering logic.

        Moved to Deterministic: Pure filtering logic
        

#### calculate_query_complexity
**Parameters**: self, query
**Returns**: dict[str, Any]
**Description**: 
        Calculate query complexity using deterministic analysis.

        Returns complexity metrics for query optimization.
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with intelligence librarian configuration.

        Args:
            config: Configuration dictionary containing validation rules
        



## Function: validate_query

**Parameters**: self, query, filters
**Returns**: IntelligenceQueryResult
**Description**: 
        Validate intelligence query using purely deterministic logic.

        Args:
            query: Query string to validate
            filters: Optional filters dictionary

        Returns:
            IntelligenceQueryResult with deterministic findings
        



## Function: _validate_query_string

**Parameters**: self, query
**Returns**: list[str]
**Description**: 
        Validate query string using deterministic rules.

        Moved to Deterministic: Pure string validation
        



## Function: _validate_filters

**Parameters**: self, filters
**Returns**: list[str]
**Description**: 
        Validate filters using deterministic schema validation.

        Moved to Deterministic: Pure schema validation
        



## Function: _generate_cache_key

**Parameters**: self, query, filters
**Returns**: str
**Description**: 
        Generate cache key using deterministic hashing.

        Moved to Deterministic: Pure hash generation
        



## Function: normalize_query

**Parameters**: self, query
**Returns**: str
**Description**: 
        Normalize query string using deterministic rules.

        Moved to Deterministic: Pure string normalization
        



## Function: filter_results

**Parameters**: self, results, filters
**Returns**: list[dict[str, Any]]
**Description**: 
        Filter results using deterministic filtering logic.

        Moved to Deterministic: Pure filtering logic
        



## Function: calculate_query_complexity

**Parameters**: self, query
**Returns**: dict[str, Any]
**Description**: 
        Calculate query complexity using deterministic analysis.

        Returns complexity metrics for query optimization.
        



## Usage Examples

### Class Usage

```python
# Using IntelligenceQueryResult
intelligencequeryresult = IntelligenceQueryResult()
```

```python
# Using IntelligenceQueryValidator
intelligencequeryvalidator = IntelligenceQueryValidator()
intelligencequeryvalidator.validate_query()
intelligencequeryvalidator.normalize_query()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(config)
```

```python
# Using validate_query
result = validate_query(query, filters)
```



---
**Generated**: 2026-03-26T09:39:05.826605
**Type**: api_reference
**Quality**: comprehensive
