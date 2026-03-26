# API Documentation: tool_registry_util

**Target Audience**: developers, api_users

# tool_registry_util API Documentation

**File**: `tool_registry_util.py`
**Classes**: 1
**Functions**: 13

## Classes

- **ToolRegistry**

## Functions

- **__new__** -> 'ToolRegistry'
- **get_instance** -> 'ToolRegistry'
- **reset_instance** -> None
- **register_tool** -> bool
- **unregister_tool** -> bool
- **get_tool** -> dict[str, Any] | None
- **get_tool_func** -> Callable[..., Any] | None
- **list_tools** -> list[str]
- **get_all_tools** -> dict[str, dict[str, Any]]
- **discover_tools** -> list[Path]
- **auto_register_from_pattern** -> int
- **__len__** -> int
- **__contains__** -> bool


## Class: ToolRegistry

**Description**: 
    SSOT for all tools. Ensures tools reside in Sovereign Territory.

    Features:
    - Singleton pattern for global access
    - Path validation via is_path_allowed
    - Integration with SovereignIndex for tool discovery
    - Logging of registration attempts
    

### Methods

#### __new__
**Parameters**: cls
**Returns**: 'ToolRegistry'

#### get_instance
**Parameters**: cls
**Returns**: 'ToolRegistry'
**Description**: Get the singleton instance of ToolRegistry.

#### reset_instance
**Parameters**: cls
**Returns**: None
**Description**: Reset the singleton instance (for testing).

#### register_tool
**Parameters**: self, tool_name, tool_path, tool_func, description
**Returns**: bool
**Description**: 
        Registers a tool only after verifying its location is sovereign.

        Args:
            tool_name: Unique identifier for the tool
            tool_path: Path to the tool file (absolute or relative)
            tool_func: The callable function/method for the tool
            description: Optional description of the tool

        Returns:
            True if registration succeeded, False if rejected
        

#### unregister_tool
**Parameters**: self, tool_name
**Returns**: bool
**Description**: 
        Removes a tool from the registry.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if removed, False if not found
        

#### get_tool
**Parameters**: self, tool_name
**Returns**: dict[str, Any] | None
**Description**: 
        Retrieves a registered tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool dict with path, func, verified, description or None
        

#### get_tool_func
**Parameters**: self, tool_name
**Returns**: Callable[..., Any] | None
**Description**: 
        Retrieves just the callable function for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            The tool's callable function or None
        

#### list_tools
**Parameters**: self
**Returns**: list[str]
**Description**: Returns list of all registered tool names.

#### get_all_tools
**Parameters**: self
**Returns**: dict[str, dict[str, Any]]
**Description**: Returns the complete tool registry.

#### discover_tools
**Parameters**: self, pattern, project_root
**Returns**: list[Path]
**Description**: 
        Uses SovereignIndex to discover tool files matching a pattern.

        Args:
            pattern: Glob pattern for tool files (default: *_tool.py)
            project_root: Optional project root path (defaults to cwd)

        Returns:
            List of discovered tool file paths
        

#### auto_register_from_pattern
**Parameters**: self, pattern, tool_loader
**Returns**: int
**Description**: 
        Auto-discovers and registers tools matching a pattern.

        Args:
            pattern: Glob pattern for tool files
            tool_loader: Optional function that takes a Path and returns
                        (tool_name, tool_func, description) tuple

        Returns:
            Number of tools successfully registered
        

#### __len__
**Parameters**: self
**Returns**: int

#### __contains__
**Parameters**: self, tool_name
**Returns**: bool



## Function: __new__

**Parameters**: cls
**Returns**: 'ToolRegistry'


## Function: get_instance

**Parameters**: cls
**Returns**: 'ToolRegistry'
**Description**: Get the singleton instance of ToolRegistry.



## Function: reset_instance

**Parameters**: cls
**Returns**: None
**Description**: Reset the singleton instance (for testing).



## Function: register_tool

**Parameters**: self, tool_name, tool_path, tool_func, description
**Returns**: bool
**Description**: 
        Registers a tool only after verifying its location is sovereign.

        Args:
            tool_name: Unique identifier for the tool
            tool_path: Path to the tool file (absolute or relative)
            tool_func: The callable function/method for the tool
            description: Optional description of the tool

        Returns:
            True if registration succeeded, False if rejected
        



## Function: unregister_tool

**Parameters**: self, tool_name
**Returns**: bool
**Description**: 
        Removes a tool from the registry.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if removed, False if not found
        



## Function: get_tool

**Parameters**: self, tool_name
**Returns**: dict[str, Any] | None
**Description**: 
        Retrieves a registered tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool dict with path, func, verified, description or None
        



## Function: get_tool_func

**Parameters**: self, tool_name
**Returns**: Callable[..., Any] | None
**Description**: 
        Retrieves just the callable function for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            The tool's callable function or None
        



## Function: list_tools

**Parameters**: self
**Returns**: list[str]
**Description**: Returns list of all registered tool names.



## Function: get_all_tools

**Parameters**: self
**Returns**: dict[str, dict[str, Any]]
**Description**: Returns the complete tool registry.



## Function: discover_tools

**Parameters**: self, pattern, project_root
**Returns**: list[Path]
**Description**: 
        Uses SovereignIndex to discover tool files matching a pattern.

        Args:
            pattern: Glob pattern for tool files (default: *_tool.py)
            project_root: Optional project root path (defaults to cwd)

        Returns:
            List of discovered tool file paths
        



## Function: auto_register_from_pattern

**Parameters**: self, pattern, tool_loader
**Returns**: int
**Description**: 
        Auto-discovers and registers tools matching a pattern.

        Args:
            pattern: Glob pattern for tool files
            tool_loader: Optional function that takes a Path and returns
                        (tool_name, tool_func, description) tuple

        Returns:
            Number of tools successfully registered
        



## Function: __len__

**Parameters**: self
**Returns**: int


## Function: __contains__

**Parameters**: self, tool_name
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using ToolRegistry
toolregistry = ToolRegistry()
toolregistry.get_instance()
toolregistry.reset_instance()
```

### Function Usage

```python
# Using __new__
result = __new__(cls)
```

```python
# Using get_instance
result = get_instance(cls)
```

```python
# Using reset_instance
result = reset_instance(cls)
```



---
**Generated**: 2026-03-26T09:39:04.073076
**Type**: api_reference
**Quality**: comprehensive
