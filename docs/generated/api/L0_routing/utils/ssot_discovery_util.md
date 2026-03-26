# API Documentation: ssot_discovery_util

**Target Audience**: developers, api_users

# ssot_discovery_util API Documentation

**File**: `ssot_discovery_util.py`
**Classes**: 0
**Functions**: 11


## Functions

- **resolve_canonical_class** -> str
- **load_agent_discovery** -> list[dict[str, Any]]
- **get_agent_paths** -> list[Path]
- **get_agents_by_layer** -> list[dict[str, Any]]
- **get_agent_by_name** -> dict[str, Any] | None
- **get_agent_names** -> set[str]
- **get_healers** -> list[dict[str, Any]]
- **get_python_files** -> list[Path]
- **get_data_files** -> list[Path]
- **get_all_files** -> dict[str, list[Path]]
- **invalidate_cache** -> None


## Function: resolve_canonical_class

**Parameters**: agent_entry
**Returns**: str
**Description**: Return the authoritative class name for an agent entry.

    Identity rule: ``verification_status.class`` (AST-verified) is canonical.
    ``class_name`` is non-authoritative / legacy display only.
    



## Function: load_agent_discovery

**Parameters**: project_root, force_reload
**Returns**: list[dict[str, Any]]
**Description**: 
    Load agent discovery data from SSOT JSON file.

    Args:
        project_root: Project root path. If None, uses get_validated_project_root().
        force_reload: If True, bypass cache and reload from disk.

    Returns:
        List of agent discovery entries.
    



## Function: get_agent_paths

**Parameters**: project_root, exclude_patterns
**Returns**: list[Path]
**Description**: 
    Get all agent file paths from SSOT.

    Args:
        project_root: Project root path.
        exclude_patterns: Patterns to exclude (e.g., ['test_', 'mock_']).

    Returns:
        List of Path objects for agent files.
    



## Function: get_agents_by_layer

**Parameters**: project_root, layer
**Returns**: list[dict[str, Any]]
**Description**: 
    Get agents filtered by layer (L0-L6).

    Args:
        project_root: Project root path.
        layer: Layer to filter by (e.g., "L5", "L3").

    Returns:
        List of agent entries matching the layer.
    



## Function: get_agent_by_name

**Parameters**: project_root, name
**Returns**: dict[str, Any] | None
**Description**: 
    Get a specific agent by name.

    Args:
        project_root: Project root path.
        name: Agent name to find.

    Returns:
        Agent entry or None if not found.
    



## Function: get_agent_names

**Parameters**: project_root
**Returns**: set[str]
**Description**: 
    Get set of all agent names from SSOT.

    Args:
        project_root: Project root path.

    Returns:
        Set of agent names.
    



## Function: get_healers

**Parameters**: project_root
**Returns**: list[dict[str, Any]]
**Description**: 
    Get all healer agents from SSOT.

    Args:
        project_root: Project root path.

    Returns:
        List of healer agent entries.
    



## Function: get_python_files

**Parameters**: project_root, exclude_patterns
**Returns**: list[Path]
**Description**: 
    Get all Python files from the project.

    Args:
        project_root: Project root path.
        exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__']).

    Returns:
        List of Path objects for Python files.
    



## Function: get_data_files

**Parameters**: project_root, extensions, exclude_patterns
**Returns**: list[Path]
**Description**: 
    Get all data files from the project with specified extensions.

    Args:
        project_root: Project root path.
        extensions: File extensions to include (e.g., [".json", ".md"]).
        exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__']).

    Returns:
        List of Path objects for data files.
    



## Function: get_all_files

**Parameters**: project_root, exclude_patterns
**Returns**: dict[str, list[Path]]
**Description**: 
    Get all files from the project, grouped by file type.

    Args:
        project_root: Project root path.
        exclude_patterns: Patterns to exclude (e.g., ['__pycache__', '.pyc']).

    Returns:
        Dictionary with file extensions as keys and lists of Path objects as values.
    



## Function: invalidate_cache

**Returns**: None
**Description**: Invalidate the discovery cache to force reload on next access.



## Usage Examples

### Function Usage

```python
# Using resolve_canonical_class
result = resolve_canonical_class(agent_entry)
```

```python
# Using load_agent_discovery
result = load_agent_discovery(project_root, force_reload)
```

```python
# Using get_agent_paths
result = get_agent_paths(project_root, exclude_patterns)
```



---
**Generated**: 2026-03-26T09:39:03.552249
**Type**: api_reference
**Quality**: comprehensive
