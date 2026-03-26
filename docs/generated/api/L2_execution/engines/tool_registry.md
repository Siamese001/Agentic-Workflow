# API Documentation: tool_registry

**Target Audience**: developers, api_users

# tool_registry API Documentation

**File**: `tool_registry.py`
**Classes**: 3
**Functions**: 16

## Classes

- **ToolDefinition**
- **ToolMatch**
- **tool_registry**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **ast_analysis** -> dict[str, Any]
- **code_transform_tool** -> dict[str, Any]
- **dependency_graph_tool** -> dict[str, Any]
- **diff_generator_tool** -> dict[str, Any]
- **create_tool_registry** -> tool_registry
- **__init__**
- **register** -> None
- **_generate_match_reason** -> str
- **get_tool** -> ToolDefinition | None
- **list_tools** -> list[ToolDefinition]
- **update_tool_stats** -> Any
- **_generate_description_from_func** -> str
- **_generate_parameters_from_func** -> dict[str, Any]
- **get_stats** -> dict[str, Any]


## Class: ToolDefinition

**Description**: Definition of a tool in the registry.



## Class: ToolMatch

**Description**: A matched tool for a Task.



## Class: tool_registry

**Description**: 
    Dynamic tool registry that enables agents to discover tools at runtime.

    Uses semantic similarity to match Task descriptions to tool capabilities.
    

### Methods

#### __init__
**Parameters**: self, embedder, enable_caching
**Description**: 
        Initialize the tool registry.

        Args:
            embedder: Embedding function
            enable_caching: Whether to cache tool embeddings
        

#### register
**Parameters**: self, name, func, description, parameters, tags, category
**Returns**: None
**Description**: 
        Register a tool in the registry.

        Args:
            name: Unique tool name
            func: The tool function
            description: What the tool does
            parameters: Parameter schema
            tags: Optional tags for categorization
            category: Tool category
        

#### _generate_match_reason
**Parameters**: self, Task, tool, similarity
**Returns**: str
**Description**: Generate a reason why this tool matches the Task.

#### get_tool
**Parameters**: self, name
**Returns**: ToolDefinition | None
**Description**: Get a tool by name.

#### list_tools
**Parameters**: self, category, tags
**Returns**: list[ToolDefinition]
**Description**: List all tools, optionally filtered.

#### update_tool_stats
**Parameters**: self, name, success
**Returns**: Any
**Description**: Update tool usage statistics.

#### _generate_description_from_func
**Parameters**: self, func
**Returns**: str
**Description**: Generate description from function docstring.

#### _generate_parameters_from_func
**Parameters**: self, func
**Returns**: dict[str, Any]
**Description**: Generate parameter schema from function signature.

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get registry statistics.



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: ast_analysis

**Parameters**: code, mode
**Returns**: dict[str, Any]
**Description**: AST tool — analyze Python code for patterns (e.g., snake_case classes).

    Args:
        code: Python source code to analyze
        mode: Analysis mode - "audit_classes", "extract_names", "check_snake_case"

    Returns:
        Dict with analysis results based on mode
    



## Function: code_transform_tool

**Parameters**: args
**Returns**: dict[str, Any]
**Description**: 
    Deterministic AST-based code transformation tool.

    Enables agents to perform safe, syntax-preserving code transformations
    without LLM overhead. Supports rename, extract, decorator operations.

    Args:
        args: CodeTransformArgs with operation details
            - operation: "rename_symbol", "extract_function", "add_decorator", etc.
            - code: Source code to transform
            - target: Symbol name or line range
            - new_name: New name for rename operations
            - extract_name: Name for extracted function
            - line_start/line_end: Line range for extraction

    Returns:
        Dict with success status, transformed code, and change details

    Example:
        >>> args = CodeTransformArgs(
        ...     operation=TransformOperation.RENAME_SYMBOL,
        ...     code="def foo(): pass",
        ...     target="foo",
        ...     new_name="bar"
        ... )
        >>> result = code_transform_tool(args)
        >>> result["transformed_code"]
        'def bar(): pass'
    



## Function: dependency_graph_tool

**Parameters**: args
**Returns**: dict[str, Any]
**Description**: 
    Dependency graph analysis tool for import/call relationships.

    Enables agents to analyze code dependencies for:
    - Cycle detection (circular imports)
    - Impact analysis (what breaks if X changes)
    - Unused import detection

    Args:
        args: DependencyGraphArgs with operation details
            - operation: "build_graph", "detect_cycles", "ImpactAnalysis", etc.
            - target_path: File or directory to analyze
            - symbol: Symbol name for impact analysis

    Returns:
        Dict with graph data, cycles, or impact analysis results

    Example:
        >>> args = DependencyGraphArgs(
        ...     operation=GraphOperation.DETECT_CYCLES,
        ...     target_path="agentic_core/"
        ... )
        >>> result = dependency_graph_tool(args)
        >>> result["data"]["has_cycles"]
        False
    



## Function: diff_generator_tool

**Parameters**: args
**Returns**: dict[str, Any]
**Description**: 
    Diff/patch generation tool for reviewable changes.

    Enables agents to generate human-reviewable diffs before applying changes,
    supporting human-in-loop validation for high-risk operations.

    Args:
        args: DiffGeneratorArgs with diff parameters
            - original: Original code/text
            - modified: Modified code/text
            - format: "unified", "context", "html", "ndiff"

    Returns:
        Dict with diff text, stats, and patch applicability

    Example:
        >>> args = DiffGeneratorArgs(
        ...     original="def foo(): pass",
        ...     modified="def bar(): pass",
        ...     format=DiffFormat.UNIFIED
        ... )
        >>> result = diff_generator_tool(args)
        >>> print(result["diff"])
    



## Function: create_tool_registry

**Parameters**: embedder, enable_caching
**Returns**: tool_registry
**Description**: 
    Factory function to create a tool registry.

    Args:
        embedder: Embedding function
        enable_caching: Whether to enable caching

    Returns:
        tool_registry instance
    



## Function: __init__

**Parameters**: self, embedder, enable_caching
**Description**: 
        Initialize the tool registry.

        Args:
            embedder: Embedding function
            enable_caching: Whether to cache tool embeddings
        



## Function: register

**Parameters**: self, name, func, description, parameters, tags, category
**Returns**: None
**Description**: 
        Register a tool in the registry.

        Args:
            name: Unique tool name
            func: The tool function
            description: What the tool does
            parameters: Parameter schema
            tags: Optional tags for categorization
            category: Tool category
        



## Function: _generate_match_reason

**Parameters**: self, Task, tool, similarity
**Returns**: str
**Description**: Generate a reason why this tool matches the Task.



## Function: get_tool

**Parameters**: self, name
**Returns**: ToolDefinition | None
**Description**: Get a tool by name.



## Function: list_tools

**Parameters**: self, category, tags
**Returns**: list[ToolDefinition]
**Description**: List all tools, optionally filtered.



## Function: update_tool_stats

**Parameters**: self, name, success
**Returns**: Any
**Description**: Update tool usage statistics.



## Function: _generate_description_from_func

**Parameters**: self, func
**Returns**: str
**Description**: Generate description from function docstring.



## Function: _generate_parameters_from_func

**Parameters**: self, func
**Returns**: dict[str, Any]
**Description**: Generate parameter schema from function signature.



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get registry statistics.



## Usage Examples

### Class Usage

```python
# Using ToolDefinition
tooldefinition = ToolDefinition()
```

```python
# Using ToolMatch
toolmatch = ToolMatch()
```

```python
# Using tool_registry
tool_registry = tool_registry()
tool_registry.register()
tool_registry.get_tool()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using ast_analysis
result = ast_analysis(code, mode)
```



---
**Generated**: 2026-03-26T09:39:03.778739
**Type**: api_reference
**Quality**: comprehensive
