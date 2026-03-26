# API Documentation: ToolsmithAgent

**Target Audience**: developers, api_users

# ToolsmithAgent API Documentation

**File**: `ToolsmithAgent.py`
**Classes**: 4
**Functions**: 24

## Classes

- **ToolSpec**
- **GeneratedTool**
- **tool_template**
- **ToolsmithAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_ToolsmithAgent** -> ToolsmithAgent
- **initialize_ToolsmithAgent** -> Any
- **create_file_tool** -> GeneratedTool
- **create_api_tool** -> GeneratedTool
- **to_dict** -> dict
- **to_dict** -> dict
- **__post_init__** -> None
- **_load_templates** -> Any
- **create_tool_from_spec** -> GeneratedTool
- **_is_simple_function** -> bool
- **_generate_function_code** -> str
- **_generate_class_code** -> str
- **_get_implementation** -> str
- **_extract_imports** -> list[str]
- **_identify_dependencies** -> list[str]
- **_generate_test_code** -> str
- **create_file_tool** -> GeneratedTool
- **create_api_tool** -> GeneratedTool
- **get_tool** -> GeneratedTool | None
- **list_tools** -> list[dict]
- **save_tool** -> bool
- **get_statistics** -> dict
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: ToolSpec

**Description**: Specification for a tool.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict
**Description**: Convert to dictionary.



## Class: GeneratedTool

**Description**: A dynamically generated tool.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict
**Description**: Convert to dictionary.



## Class: tool_template

**Description**: Template for generating tools.



## Class: ToolsmithAgent

**Description**: 
    Creates and manages tools dynamically.
    Features:
    - Generates tools from specifications
    - Validates tool implementations
    - Manages tool registry
    - Provides tool templates
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the ToolsmithAgent.

#### _load_templates
**Parameters**: self
**Returns**: Any
**Description**: Load tool generation templates.

#### create_tool_from_spec
**Parameters**: self, spec
**Returns**: GeneratedTool
**Description**: 
        Create a tool from a specification.

        Args:
            spec: Tool specification

        Returns:
            Generated tool
        

#### _is_simple_function
**Parameters**: self, spec
**Returns**: bool
**Description**: Check if tool should be a simple function.

#### _generate_function_code
**Parameters**: self, spec
**Returns**: str
**Description**: Generate function code for a tool.

#### _generate_class_code
**Parameters**: self, spec
**Returns**: str
**Description**: Generate class code for a complex tool.

#### _get_implementation
**Parameters**: self, spec
**Returns**: str
**Description**: Get implementation code based on tool category and name.

#### _extract_imports
**Parameters**: self, code
**Returns**: list[str]
**Description**: Extract import statements from code.

#### _identify_dependencies
**Parameters**: self, code
**Returns**: list[str]
**Description**: Identify external dependencies from code.

#### _generate_test_code
**Parameters**: self, spec
**Returns**: str
**Description**: Generate test code for the tool.

#### create_file_tool
**Parameters**: self, name, operation
**Returns**: GeneratedTool
**Description**: 
        Create a file manipulation tool.

        Args:
            name: Tool name
            operation: Operation type (read/write/delete)

        Returns:
            Generated tool
        

#### create_api_tool
**Parameters**: self, name, endpoint, method
**Returns**: GeneratedTool
**Description**: 
        Create an API interaction tool.

        Args:
            name: Tool name
            endpoint: API endpoint
            method: HTTP method

        Returns:
            Generated tool
        

#### get_tool
**Parameters**: self, name
**Returns**: GeneratedTool | None
**Description**: Get a registered tool by name.

#### list_tools
**Parameters**: self, category
**Returns**: list[dict]
**Description**: 
        List all tools.

        Args:
            category: Filter by category

        Returns:
            List of tool specifications
        

#### save_tool
**Parameters**: self, name, directory
**Returns**: bool
**Description**: 
        Save a tool to file.

        Args:
            name: Tool name
            directory: Output directory

        Returns:
            True if saved successfully
        

#### get_statistics
**Parameters**: self
**Returns**: dict
**Description**: Get tool creation statistics.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Wired Toolsmith Healing - Validates tool specifications and repairs broken tool files.

        WIRED CAPABILITIES:
        - validate_tool_specs(): Checks JSON/YAML tool definitions for schema compliance.
        - _reconcile_tool_files(): Ensures tool Python files match their registered specs.
        - save_tool(): Commits repairs to the filesystem if authorized.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by ToolsmithAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: get_ToolsmithAgent

**Returns**: ToolsmithAgent
**Description**: Get or create the global ToolsmithAgent instance.



## Function: initialize_ToolsmithAgent

**Returns**: Any
**Description**: Initialize the ToolsmithAgent system.



## Function: create_file_tool

**Parameters**: name, operation
**Returns**: GeneratedTool
**Description**: Create a file manipulation tool.



## Function: create_api_tool

**Parameters**: name, endpoint, method
**Returns**: GeneratedTool
**Description**: Create an API interaction tool.



## Function: to_dict

**Parameters**: self
**Returns**: dict
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict
**Description**: Convert to dictionary.



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the ToolsmithAgent.



## Function: _load_templates

**Parameters**: self
**Returns**: Any
**Description**: Load tool generation templates.



## Function: create_tool_from_spec

**Parameters**: self, spec
**Returns**: GeneratedTool
**Description**: 
        Create a tool from a specification.

        Args:
            spec: Tool specification

        Returns:
            Generated tool
        



## Function: _is_simple_function

**Parameters**: self, spec
**Returns**: bool
**Description**: Check if tool should be a simple function.



## Function: _generate_function_code

**Parameters**: self, spec
**Returns**: str
**Description**: Generate function code for a tool.



## Function: _generate_class_code

**Parameters**: self, spec
**Returns**: str
**Description**: Generate class code for a complex tool.



## Function: _get_implementation

**Parameters**: self, spec
**Returns**: str
**Description**: Get implementation code based on tool category and name.



## Function: _extract_imports

**Parameters**: self, code
**Returns**: list[str]
**Description**: Extract import statements from code.



## Function: _identify_dependencies

**Parameters**: self, code
**Returns**: list[str]
**Description**: Identify external dependencies from code.



## Function: _generate_test_code

**Parameters**: self, spec
**Returns**: str
**Description**: Generate test code for the tool.



## Function: create_file_tool

**Parameters**: self, name, operation
**Returns**: GeneratedTool
**Description**: 
        Create a file manipulation tool.

        Args:
            name: Tool name
            operation: Operation type (read/write/delete)

        Returns:
            Generated tool
        



## Function: create_api_tool

**Parameters**: self, name, endpoint, method
**Returns**: GeneratedTool
**Description**: 
        Create an API interaction tool.

        Args:
            name: Tool name
            endpoint: API endpoint
            method: HTTP method

        Returns:
            Generated tool
        



## Function: get_tool

**Parameters**: self, name
**Returns**: GeneratedTool | None
**Description**: Get a registered tool by name.



## Function: list_tools

**Parameters**: self, category
**Returns**: list[dict]
**Description**: 
        List all tools.

        Args:
            category: Filter by category

        Returns:
            List of tool specifications
        



## Function: save_tool

**Parameters**: self, name, directory
**Returns**: bool
**Description**: 
        Save a tool to file.

        Args:
            name: Tool name
            directory: Output directory

        Returns:
            True if saved successfully
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict
**Description**: Get tool creation statistics.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Wired Toolsmith Healing - Validates tool specifications and repairs broken tool files.

        WIRED CAPABILITIES:
        - validate_tool_specs(): Checks JSON/YAML tool definitions for schema compliance.
        - _reconcile_tool_files(): Ensures tool Python files match their registered specs.
        - save_tool(): Commits repairs to the filesystem if authorized.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by ToolsmithAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Usage Examples

### Class Usage

```python
# Using ToolSpec
toolspec = ToolSpec()
toolspec.to_dict()
```

```python
# Using GeneratedTool
generatedtool = GeneratedTool()
generatedtool.to_dict()
```

```python
# Using tool_template
tool_template = tool_template()
```

### Function Usage

```python
# Using get_ToolsmithAgent
result = get_ToolsmithAgent()
```

```python
# Using initialize_ToolsmithAgent
result = initialize_ToolsmithAgent()
```

```python
# Using create_file_tool
result = create_file_tool(name, operation)
```



---
**Generated**: 2026-03-26T09:39:03.886293
**Type**: api_reference
**Quality**: comprehensive
