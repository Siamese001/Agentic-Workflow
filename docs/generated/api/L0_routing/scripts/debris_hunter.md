# API Documentation: debris_hunter

**Target Audience**: developers, api_users

# debris_hunter API Documentation

**File**: `debris_hunter.py`
**Classes**: 1
**Functions**: 5

## Classes

- **DebrisHunter**

## Functions

- **__init__**
- **scan_for_collisions**
- **scan_for_known_redundancies**
- **scan_for_temp_files**
- **execute_cleanup**


## Class: DebrisHunter

### Methods

#### __init__
**Parameters**: self, root, dry_run

#### scan_for_collisions
**Parameters**: self
**Description**: 
        Finds directories containing both 'snake_case.py' and 'PascalCase.py'
        where one is likely the ancestor of the other.
        

#### scan_for_known_redundancies
**Parameters**: self
**Description**: Targeted cleanup for known migration artifacts.

#### scan_for_temp_files
**Parameters**: self
**Description**: Finds stuck __temp_ artifacts from interrupted renames.

#### execute_cleanup
**Parameters**: self



## Function: __init__

**Parameters**: self, root, dry_run


## Function: scan_for_collisions

**Parameters**: self
**Description**: 
        Finds directories containing both 'snake_case.py' and 'PascalCase.py'
        where one is likely the ancestor of the other.
        



## Function: scan_for_known_redundancies

**Parameters**: self
**Description**: Targeted cleanup for known migration artifacts.



## Function: scan_for_temp_files

**Parameters**: self
**Description**: Finds stuck __temp_ artifacts from interrupted renames.



## Function: execute_cleanup

**Parameters**: self


## Usage Examples

### Class Usage

```python
# Using DebrisHunter
debrishunter = DebrisHunter()
debrishunter.scan_for_collisions()
debrishunter.scan_for_known_redundancies()
```

### Function Usage

```python
# Using __init__
result = __init__(root, dry_run)
```

```python
# Using scan_for_collisions
result = scan_for_collisions()
```

```python
# Using scan_for_known_redundancies
result = scan_for_known_redundancies()
```



---
**Generated**: 2026-03-26T09:39:02.847274
**Type**: api_reference
**Quality**: comprehensive
