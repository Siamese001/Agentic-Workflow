# API Documentation: capability_extractor_util

**Target Audience**: developers, api_users

# capability_extractor_util API Documentation

**File**: `capability_extractor_util.py`
**Classes**: 1
**Functions**: 5

## Classes

- **CapabilityExtractor**

## Functions

- **extract_capabilities** -> dict[str, any]
- **_tag_by_method_name** -> None
- **_analyze_method_body** -> None
- **get_all_capabilities** -> set[str]
- **filter_unique_methods** -> set[str]


## Class: CapabilityExtractor

**Description**: Extracts semantic capabilities from agent class definitions.

### Methods

#### extract_capabilities
**Parameters**: self, class_node
**Returns**: dict[str, any]
**Description**: Extract rich capability metadata from an agent class.

        Args:
            class_node: AST ClassDef node to analyze

        Returns:
            Dictionary with semantic_tags, unique_methods, patterns, and valuable_methods
        

#### _tag_by_method_name
**Parameters**: self, method_name, caps
**Returns**: None
**Description**: Tag capabilities based on method name patterns.

        Args:
            method_name: Name of the method
            caps: Capabilities dictionary to update
        

#### _analyze_method_body
**Parameters**: self, item, method_name, method_loc, caps
**Returns**: None
**Description**: Analyze method body for specialized patterns.

        Args:
            item: AST FunctionDef node
            method_name: Name of the method
            method_loc: Line number of method
            caps: Capabilities dictionary to update
        

#### get_all_capabilities
**Parameters**: self, caps
**Returns**: set[str]
**Description**: Get all capabilities (semantic tags + patterns) as a unified set.

        Args:
            caps: Capabilities dictionary

        Returns:
            Set of all capability identifiers
        

#### filter_unique_methods
**Parameters**: self, method_names
**Returns**: set[str]
**Description**: Filter out common methods, returning only unique ones.

        Args:
            method_names: Set of method names to filter

        Returns:
            Set of unique (non-common) method names
        



## Function: extract_capabilities

**Parameters**: self, class_node
**Returns**: dict[str, any]
**Description**: Extract rich capability metadata from an agent class.

        Args:
            class_node: AST ClassDef node to analyze

        Returns:
            Dictionary with semantic_tags, unique_methods, patterns, and valuable_methods
        



## Function: _tag_by_method_name

**Parameters**: self, method_name, caps
**Returns**: None
**Description**: Tag capabilities based on method name patterns.

        Args:
            method_name: Name of the method
            caps: Capabilities dictionary to update
        



## Function: _analyze_method_body

**Parameters**: self, item, method_name, method_loc, caps
**Returns**: None
**Description**: Analyze method body for specialized patterns.

        Args:
            item: AST FunctionDef node
            method_name: Name of the method
            method_loc: Line number of method
            caps: Capabilities dictionary to update
        



## Function: get_all_capabilities

**Parameters**: self, caps
**Returns**: set[str]
**Description**: Get all capabilities (semantic tags + patterns) as a unified set.

        Args:
            caps: Capabilities dictionary

        Returns:
            Set of all capability identifiers
        



## Function: filter_unique_methods

**Parameters**: self, method_names
**Returns**: set[str]
**Description**: Filter out common methods, returning only unique ones.

        Args:
            method_names: Set of method names to filter

        Returns:
            Set of unique (non-common) method names
        



## Usage Examples

### Class Usage

```python
# Using CapabilityExtractor
capabilityextractor = CapabilityExtractor()
capabilityextractor.extract_capabilities()
capabilityextractor.get_all_capabilities()
```

### Function Usage

```python
# Using extract_capabilities
result = extract_capabilities(class_node)
```

```python
# Using _tag_by_method_name
result = _tag_by_method_name(method_name, caps)
```

```python
# Using _analyze_method_body
result = _analyze_method_body(item, method_name)
```



---
**Generated**: 2026-03-26T09:39:05.613168
**Type**: api_reference
**Quality**: comprehensive
