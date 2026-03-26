# API Documentation: dependency_graph_enforcer

**Target Audience**: developers, api_users

# dependency_graph_enforcer API Documentation

**File**: `dependency_graph_enforcer.py`
**Classes**: 1
**Functions**: 7

## Classes

- **DependencyGraph**

## Functions

- **__init__**
- **build** -> None
- **get_impact_radius** -> list[str]
- **get_imports** -> list[str]
- **get_classes** -> list[str]
- **get_all_files** -> list[str]
- **clear** -> None


## Class: DependencyGraph

**Description**: Builds a directed graph of imports and class hierarchies.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize empty dependency graph.

#### build
**Parameters**: self, files
**Returns**: None
**Description**: Build the dependency graph from a list of Python files.

        Args:
            files: List of Python file paths to analyze
        

#### get_impact_radius
**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Returns files that import modules defined in file_path.

        Args:
            file_path: Path to file to analyze

        Returns:
            List of file paths that would be impacted by changes
        

#### get_imports
**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Get all imports for a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of imported module names
        

#### get_classes
**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Get all class definitions in a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of class names defined in the file
        

#### get_all_files
**Parameters**: self
**Returns**: list[str]
**Description**: Get all files in the dependency graph.

        Returns:
            List of all analyzed file paths
        

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear all graph data.



## Function: __init__

**Parameters**: self
**Description**: Initialize empty dependency graph.



## Function: build

**Parameters**: self, files
**Returns**: None
**Description**: Build the dependency graph from a list of Python files.

        Args:
            files: List of Python file paths to analyze
        



## Function: get_impact_radius

**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Returns files that import modules defined in file_path.

        Args:
            file_path: Path to file to analyze

        Returns:
            List of file paths that would be impacted by changes
        



## Function: get_imports

**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Get all imports for a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of imported module names
        



## Function: get_classes

**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Get all class definitions in a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of class names defined in the file
        



## Function: get_all_files

**Parameters**: self
**Returns**: list[str]
**Description**: Get all files in the dependency graph.

        Returns:
            List of all analyzed file paths
        



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear all graph data.



## Usage Examples

### Class Usage

```python
# Using DependencyGraph
dependencygraph = DependencyGraph()
dependencygraph.build()
dependencygraph.get_impact_radius()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using build
result = build(files)
```

```python
# Using get_impact_radius
result = get_impact_radius(file_path)
```



---
**Generated**: 2026-03-26T09:39:04.807351
**Type**: api_reference
**Quality**: comprehensive
