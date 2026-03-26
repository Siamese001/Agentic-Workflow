# API Documentation: territories

**Target Audience**: developers, api_users

# territories API Documentation

**File**: `territories.py`
**Classes**: 0
**Functions**: 3


## Functions

- **get_territory_metadata** -> TerritoryDefinition | None
- **get_all_territories** -> Mapping[str, TerritoryDefinition]
- **is_valid_root_folder** -> bool


## Function: get_territory_metadata

**Parameters**: territory_name
**Returns**: TerritoryDefinition | None
**Description**: Get metadata for a specific territory.

    Args:
        territory_name: Name of the territory (e.g., "apps_shared", "agentic_core")

    Returns:
        Territory definition dict with keys like 'purpose', 'subfolders', 'depth', etc.
        Returns None if territory not found.

    Example:
        >>> meta = get_territory_metadata("apps_shared")
        >>> if meta:
        ...     print(meta.get("purpose"))
    



## Function: get_all_territories

**Returns**: Mapping[str, TerritoryDefinition]
**Description**: Get all territory definitions (read-only).

    Returns:
        Immutable mapping of territory_name -> TerritoryDefinition.
        This is a read-only view — mutations will raise TypeError.

    Example:
        >>> territories = get_all_territories()
        >>> for name, meta in territories.items():
        ...     print(f"{name}: {meta.get('purpose')}")
    



## Function: is_valid_root_folder

**Parameters**: folder_name
**Returns**: bool
**Description**: Check if folder is allowed at project root.

    Args:
        folder_name: Name of the folder to check (e.g., "apps_shared", ".git")

    Returns:
        True if folder is in the project root whitelist, False otherwise.

    Example:
        >>> is_valid_root_folder("apps_shared")
        True
        >>> is_valid_root_folder("random_folder")
        False
    



## Usage Examples

### Function Usage

```python
# Using get_territory_metadata
result = get_territory_metadata(territory_name)
```

```python
# Using get_all_territories
result = get_all_territories()
```

```python
# Using is_valid_root_folder
result = is_valid_root_folder(folder_name)
```



---
**Generated**: 2026-03-26T09:39:05.946304
**Type**: api_reference
**Quality**: comprehensive
