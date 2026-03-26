# API Documentation: NamingAgent

**Target Audience**: developers, api_users

# NamingAgent API Documentation

**File**: `NamingAgent.py`
**Classes**: 2
**Functions**: 11

## Classes

- **PlacementResult**
- **NamingAgent** (inherits from PromptRenderingMixin, SovereignBaseAgent)

## Functions

- **get_naming_agent** -> NamingAgent
- **__init__** -> None
- **heal_repository** -> dict[str, Any]
- **heal** -> dict
- **__init__** -> None
- **validate_name** -> bool
- **suggest_name** -> str
- **analyze_placement** -> PlacementResult
- **validate_prefix_location_match** -> list
- **scan_repository_duplicates** -> dict
- **move_to_canonical_location** -> dict


## Class: PlacementResult

**Description**: 
    Result of placement analysis.

    Attributes:
        path: Suggested file path for the code
        confidence: Confidence score (0.0 to 1.0) for the placement suggestion
        suggestions: List of alternative placement suggestions
    

### Methods

#### __init__
**Parameters**: self, path, confidence
**Returns**: None
**Description**: 
        Initialize placement result.

        Args:
            path: Suggested file path
            confidence: Confidence score for the suggestion
        



## Class: NamingAgent

**Description**: 
    Stub NamingAgent for backwards compatibility.

    Provides minimal implementation when the full L5_safety NamingAgent
    is not available. Used for testing and development environments.
    

**Inherits from**: PromptRenderingMixin, SovereignBaseAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute, depth
**Returns**: dict[str, Any]
**Description**: Autonomous healing method (Canon Key 51 compliance).

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Standardized healing interface for NamingAgent.
        

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the stub NamingAgent.

#### validate_name
**Parameters**: self, name
**Returns**: bool
**Description**: 
        Validate a name against naming conventions.
        [SSOT] Checks PROJECT_ROOT_METADATA for whitelist exemptions.
        

#### suggest_name
**Parameters**: self, context
**Returns**: str
**Description**: Suggest a name based on context.

#### analyze_placement
**Parameters**: self, code
**Returns**: PlacementResult
**Description**: Analyze code and suggest file placement.

#### validate_prefix_location_match
**Parameters**: self, path
**Returns**: list
**Description**: Stub method for prefix-location validation.

#### scan_repository_duplicates
**Parameters**: self
**Returns**: dict
**Description**: Stub method for duplicate scanning.

#### move_to_canonical_location
**Parameters**: self, path, dry_run
**Returns**: dict
**Description**: Stub method for canonical moves.



## Function: get_naming_agent

**Parameters**: project_root
**Returns**: NamingAgent
**Description**: 
    Get a NamingAgent instance.

    Factory function to create a NamingAgent with optional project root.

    Args:
        project_root: Optional path to project root directory

    Returns:
        Configured NamingAgent instance
    



## Function: __init__

**Parameters**: self, path, confidence
**Returns**: None
**Description**: 
        Initialize placement result.

        Args:
            path: Suggested file path
            confidence: Confidence score for the suggestion
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth
**Returns**: dict[str, Any]
**Description**: Autonomous healing method (Canon Key 51 compliance).



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Standardized healing interface for NamingAgent.
        



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the stub NamingAgent.



## Function: validate_name

**Parameters**: self, name
**Returns**: bool
**Description**: 
        Validate a name against naming conventions.
        [SSOT] Checks PROJECT_ROOT_METADATA for whitelist exemptions.
        



## Function: suggest_name

**Parameters**: self, context
**Returns**: str
**Description**: Suggest a name based on context.



## Function: analyze_placement

**Parameters**: self, code
**Returns**: PlacementResult
**Description**: Analyze code and suggest file placement.



## Function: validate_prefix_location_match

**Parameters**: self, path
**Returns**: list
**Description**: Stub method for prefix-location validation.



## Function: scan_repository_duplicates

**Parameters**: self
**Returns**: dict
**Description**: Stub method for duplicate scanning.



## Function: move_to_canonical_location

**Parameters**: self, path, dry_run
**Returns**: dict
**Description**: Stub method for canonical moves.



## Usage Examples

### Class Usage

```python
# Using PlacementResult
placementresult = PlacementResult()
```

```python
# Using NamingAgent
namingagent = NamingAgent()
namingagent.heal_repository()
namingagent.heal()
```

### Function Usage

```python
# Using get_naming_agent
result = get_naming_agent(project_root)
```

```python
# Using __init__
result = __init__(path, confidence)
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.334100
**Type**: api_reference
**Quality**: comprehensive
