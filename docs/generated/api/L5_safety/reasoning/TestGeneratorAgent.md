# API Documentation: TestGeneratorAgent

**Target Audience**: developers, api_users

# TestGeneratorAgent API Documentation

**File**: `TestGeneratorAgent.py`
**Classes**: 1
**Functions**: 15

## Classes

- **TestGeneratorAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **generate_tests_for_agent** -> dict[str, Any]
- **_extract_classes** -> list[dict[str, Any]]
- **_get_base_name** -> str
- **_extract_args** -> list[str]
- **_has_return** -> bool
- **_generate_test_file** -> str
- **_generate_test_class** -> list[str]
- **_generate_test_method** -> list[str]
- **_generate_healer_tests** -> list[str]
- **_generate_mcp_tests** -> list[str]
- **_path_to_module** -> str | None
- **get_generation_history** -> list[dict[str, Any]]
- **heal_repository** -> dict[str, int]
- **heal**


## Class: TestGeneratorAgent

**Description**: 
    Autonomous agent that generates subatomic tests for agent classes.

    Capabilities:
    - Parses agent source files using AST
    - Identifies public methods and their signatures
    - Generates pytest-compatible test skeletons
    - Detects mixin inheritance for specialized test patterns
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, tests_dir
**Returns**: None
**Description**: 
        Initialize test generator agent.

        Args:
            tests_dir: Optional directory for generated tests (defaults to tests/autogen)
        

#### generate_tests_for_agent
**Parameters**: self, agent_path
**Returns**: dict[str, Any]
**Description**: 
        Scan agent file and generate corresponding test cases.

        Args:
            agent_path: Path to the agent Python file

        Returns:
            Dict with generation result: {success: bool, test_file: str, tests_count: int}
        

#### _extract_classes
**Parameters**: self, tree
**Returns**: list[dict[str, Any]]
**Description**: Extract class definitions and their methods from AST.

#### _get_base_name
**Parameters**: self, base
**Returns**: str
**Description**: Extract base class name from AST node.

#### _extract_args
**Parameters**: self, func
**Returns**: list[str]
**Description**: Extract argument names from function definition.

#### _has_return
**Parameters**: self, func
**Returns**: bool
**Description**: Check if function has a return statement with a value.

#### _generate_test_file
**Parameters**: self, source_path, classes
**Returns**: str
**Description**: Generate pytest-compatible test file content.

#### _generate_test_class
**Parameters**: self, cls
**Returns**: list[str]
**Description**: Generate test class for a source class.

#### _generate_test_method
**Parameters**: self, cls, method
**Returns**: list[str]
**Description**: Generate test method for a source method.

#### _generate_healer_tests
**Parameters**: self, cls
**Returns**: list[str]
**Description**: Generate tests for HealerMixin compliance.

#### _generate_mcp_tests
**Parameters**: self, cls
**Returns**: list[str]
**Description**: Generate tests for MCPHardenedMixin compliance.

#### _path_to_module
**Parameters**: self, path
**Returns**: str | None
**Description**: Convert file path to Python module path.

#### get_generation_history
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Retrieve history of generated tests.

#### heal_repository
**Parameters**: self, dry_run
**Returns**: dict[str, int]
**Description**: Invoke healing chain via super().

#### heal
**Parameters**: self, violation



## Function: __init__

**Parameters**: self, tests_dir
**Returns**: None
**Description**: 
        Initialize test generator agent.

        Args:
            tests_dir: Optional directory for generated tests (defaults to tests/autogen)
        



## Function: generate_tests_for_agent

**Parameters**: self, agent_path
**Returns**: dict[str, Any]
**Description**: 
        Scan agent file and generate corresponding test cases.

        Args:
            agent_path: Path to the agent Python file

        Returns:
            Dict with generation result: {success: bool, test_file: str, tests_count: int}
        



## Function: _extract_classes

**Parameters**: self, tree
**Returns**: list[dict[str, Any]]
**Description**: Extract class definitions and their methods from AST.



## Function: _get_base_name

**Parameters**: self, base
**Returns**: str
**Description**: Extract base class name from AST node.



## Function: _extract_args

**Parameters**: self, func
**Returns**: list[str]
**Description**: Extract argument names from function definition.



## Function: _has_return

**Parameters**: self, func
**Returns**: bool
**Description**: Check if function has a return statement with a value.



## Function: _generate_test_file

**Parameters**: self, source_path, classes
**Returns**: str
**Description**: Generate pytest-compatible test file content.



## Function: _generate_test_class

**Parameters**: self, cls
**Returns**: list[str]
**Description**: Generate test class for a source class.



## Function: _generate_test_method

**Parameters**: self, cls, method
**Returns**: list[str]
**Description**: Generate test method for a source method.



## Function: _generate_healer_tests

**Parameters**: self, cls
**Returns**: list[str]
**Description**: Generate tests for HealerMixin compliance.



## Function: _generate_mcp_tests

**Parameters**: self, cls
**Returns**: list[str]
**Description**: Generate tests for MCPHardenedMixin compliance.



## Function: _path_to_module

**Parameters**: self, path
**Returns**: str | None
**Description**: Convert file path to Python module path.



## Function: get_generation_history

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Retrieve history of generated tests.



## Function: heal_repository

**Parameters**: self, dry_run
**Returns**: dict[str, int]
**Description**: Invoke healing chain via super().



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using TestGeneratorAgent
testgeneratoragent = TestGeneratorAgent()
testgeneratoragent.generate_tests_for_agent()
testgeneratoragent.get_generation_history()
```

### Function Usage

```python
# Using __init__
result = __init__(tests_dir)
```

```python
# Using generate_tests_for_agent
result = generate_tests_for_agent(agent_path)
```

```python
# Using _extract_classes
result = _extract_classes(tree)
```



---
**Generated**: 2026-03-26T09:39:05.441850
**Type**: api_reference
**Quality**: comprehensive
