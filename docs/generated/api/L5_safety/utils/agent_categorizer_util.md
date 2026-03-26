# API Documentation: agent_categorizer_util

**Target Audience**: developers, api_users

# agent_categorizer_util API Documentation

**File**: `agent_categorizer_util.py`
**Classes**: 1
**Functions**: 7

## Classes

- **AgentCategorizer**

## Functions

- **categorize_agents_for_dashboard** -> dict[str, list[str]]
- **__init__**
- **scan_folder** -> dict[str, list[str]]
- **_analyze_file** -> None
- **_categorize_agent** -> str
- **get_category_summary** -> dict[str, int]
- **get_agents_by_category** -> list[str]


## Class: AgentCategorizer

**Description**: Categorizes agents into non-overlapping groups based on AST analysis.

### Methods

#### __init__
**Parameters**: self, folder_path

#### scan_folder
**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: Scan folder and categorize all agents.

#### _analyze_file
**Parameters**: self, py_file
**Returns**: None
**Description**: Analyze a Python file and extract agent classes.

#### _categorize_agent
**Parameters**: self, class_node, source
**Returns**: str
**Description**: Determine category for an agent based on name and docstring.

#### get_category_summary
**Parameters**: self
**Returns**: dict[str, int]
**Description**: Get count of agents per category.

#### get_agents_by_category
**Parameters**: self, category
**Returns**: list[str]
**Description**: Get list of agents in a specific category.



## Function: categorize_agents_for_dashboard

**Parameters**: folder_path
**Returns**: dict[str, list[str]]
**Description**: Main entry point for dashboard categorization.



## Function: __init__

**Parameters**: self, folder_path


## Function: scan_folder

**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: Scan folder and categorize all agents.



## Function: _analyze_file

**Parameters**: self, py_file
**Returns**: None
**Description**: Analyze a Python file and extract agent classes.



## Function: _categorize_agent

**Parameters**: self, class_node, source
**Returns**: str
**Description**: Determine category for an agent based on name and docstring.



## Function: get_category_summary

**Parameters**: self
**Returns**: dict[str, int]
**Description**: Get count of agents per category.



## Function: get_agents_by_category

**Parameters**: self, category
**Returns**: list[str]
**Description**: Get list of agents in a specific category.



## Usage Examples

### Class Usage

```python
# Using AgentCategorizer
agentcategorizer = AgentCategorizer()
agentcategorizer.scan_folder()
agentcategorizer.get_category_summary()
```

### Function Usage

```python
# Using categorize_agents_for_dashboard
result = categorize_agents_for_dashboard(folder_path)
```

```python
# Using __init__
result = __init__(folder_path)
```

```python
# Using scan_folder
result = scan_folder()
```



---
**Generated**: 2026-03-26T09:39:05.603869
**Type**: api_reference
**Quality**: comprehensive
