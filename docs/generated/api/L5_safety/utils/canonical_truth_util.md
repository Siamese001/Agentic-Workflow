# API Documentation: canonical_truth_util

**Target Audience**: developers, api_users

# canonical_truth_util API Documentation

**File**: `canonical_truth_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **calculate_health_score** -> float
- **get_canonical_layer** -> str
- **validate_health_components** -> dict[str, Any]
- **get_health_weights** -> dict[str, float]
- **categorize_agent** -> str
- **get_agent_categories** -> list[str]


## Function: calculate_health_score

**Parameters**: violations, weights
**Returns**: float
**Description**: 
    Calculate a normalized health score (0-100) from violation data.

    Args:
        violations: List of violation dictionaries with 'severity' and 'count' keys
        weights: Optional weights for different severity levels

    Returns:
        Health score from 0 (worst) to 100 (best)
    



## Function: get_canonical_layer

**Parameters**: file_path
**Returns**: str
**Description**: 
    Infer the canonical layer from a file path.

    Args:
        file_path: Path to the file

    Returns:
        Canonical layer string (L0-L6, Apps, Utils, Tests, or 'unknown')
    



## Function: validate_health_components

**Parameters**: components
**Returns**: dict[str, Any]
**Description**: 
    Validate health components and return validation results.

    Args:
        components: Dictionary of health components to validate

    Returns:
        Validation results with valid/invalid components
    



## Function: get_health_weights

**Returns**: dict[str, float]
**Description**: 
    Get default health calculation weights.

    Returns:
        Dictionary of weights for different violation severities
    



## Function: categorize_agent

**Parameters**: class_name, base_classes, docstring
**Returns**: str
**Description**: 
    Categorize an agent based on its name, inheritance, and documentation.

    Args:
        class_name: Name of the agent class (e.g., "BaseClassEnforcerAgent")
        base_classes: List of base class names (e.g., ["L5Agent", "MCPHardenedMixin"])
        docstring: Optional docstring content

    Returns:
        Agent category string
    



## Function: get_agent_categories

**Returns**: list[str]
**Description**: 
    Get list of all valid agent categories.

    Returns:
        List of category strings
    



## Usage Examples

### Function Usage

```python
# Using calculate_health_score
result = calculate_health_score(violations, weights)
```

```python
# Using get_canonical_layer
result = get_canonical_layer(file_path)
```

```python
# Using validate_health_components
result = validate_health_components(components)
```



---
**Generated**: 2026-03-26T09:39:05.610000
**Type**: api_reference
**Quality**: comprehensive
