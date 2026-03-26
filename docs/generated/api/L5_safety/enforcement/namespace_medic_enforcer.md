# API Documentation: namespace_medic_enforcer

**Target Audience**: developers, api_users

# namespace_medic_enforcer API Documentation

**File**: `namespace_medic_enforcer.py`
**Classes**: 0
**Functions**: 4


## Functions

- **find_missing_imports** -> list[str]
- **inject_imports** -> str
- **heal_file** -> tuple[bool, int]
- **main** -> Any


## Function: find_missing_imports

**Parameters**: content
**Returns**: list[str]
**Description**: Detect which standard library imports are Missing from the file.



## Function: inject_imports

**Parameters**: content, imports
**Returns**: str
**Description**: Inject Missing imports at the top of the file (after docstring).



## Function: heal_file

**Parameters**: file_path, dry_run
**Returns**: tuple[bool, int]
**Description**: 
    Heal a single file by injecting Missing imports.
    Returns (was_healed, num_imports_added)
    



## Function: main

**Returns**: Any
**Description**: Main entry point for namespace healing.



## Usage Examples

### Function Usage

```python
# Using find_missing_imports
result = find_missing_imports(content)
```

```python
# Using inject_imports
result = inject_imports(content, imports)
```

```python
# Using heal_file
result = heal_file(file_path, dry_run)
```



---
**Generated**: 2026-03-26T09:39:04.886032
**Type**: api_reference
**Quality**: comprehensive
