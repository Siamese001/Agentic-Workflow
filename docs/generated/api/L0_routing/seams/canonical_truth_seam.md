# API Documentation: canonical_truth_seam

**Target Audience**: developers, api_users

# canonical_truth_seam API Documentation

**File**: `canonical_truth_seam.py`
**Classes**: 1
**Functions**: 5

## Classes

- **CanonicalTruthProvider** (inherits from Protocol)

## Functions

- **get_canonical_truth_provider** -> CanonicalTruthProvider
- **get_canonical_layer** -> int
- **categorize_agent** -> str
- **get_layer** -> int
- **categorize_agent** -> str


## Class: CanonicalTruthProvider

**Description**: Protocol for canonical truth operations.

**Inherits from**: Protocol

### Methods

#### get_layer
**Parameters**: self, file_path
**Returns**: int
**Description**: Get the canonical layer for a file path.

#### categorize_agent
**Parameters**: self, class_name, base_classes, docstring
**Returns**: str
**Description**: Categorize an agent based on its characteristics.



## Function: get_canonical_truth_provider

**Returns**: CanonicalTruthProvider
**Description**: Get the canonical truth provider implementation.

    This function uses dynamic import to avoid static L0→L5 dependency
    while providing runtime access to L5 canonical truth logic.
    



## Function: get_canonical_layer

**Parameters**: file_path
**Returns**: int
**Description**: Get the canonical layer for a file path.



## Function: categorize_agent

**Parameters**: class_name, base_classes, docstring
**Returns**: str
**Description**: Categorize an agent based on its characteristics.



## Function: get_layer

**Parameters**: self, file_path
**Returns**: int
**Description**: Get the canonical layer for a file path.



## Function: categorize_agent

**Parameters**: self, class_name, base_classes, docstring
**Returns**: str
**Description**: Categorize an agent based on its characteristics.



## Usage Examples

### Class Usage

```python
# Using CanonicalTruthProvider
canonicaltruthprovider = CanonicalTruthProvider()
canonicaltruthprovider.get_layer()
canonicaltruthprovider.categorize_agent()
```

### Function Usage

```python
# Using get_canonical_truth_provider
result = get_canonical_truth_provider()
```

```python
# Using get_canonical_layer
result = get_canonical_layer(file_path)
```

```python
# Using categorize_agent
result = categorize_agent(class_name, base_classes)
```



---
**Generated**: 2026-03-26T09:39:03.395227
**Type**: api_reference
**Quality**: comprehensive
