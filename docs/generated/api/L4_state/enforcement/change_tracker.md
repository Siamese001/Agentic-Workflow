# API Documentation: change_tracker

**Target Audience**: developers, api_users

# change_tracker API Documentation

**File**: `change_tracker.py`
**Classes**: 2
**Functions**: 8

## Classes

- **ChangeRecord**
- **ChangeTracker**

## Functions

- **__init__**
- **__init__**
- **record**
- **_group_by_agent** -> dict[str, list[tuple[str, str]]]
- **_group_by_file** -> dict[str, list[tuple[str, str]]]
- **generate_markdown_report** -> str
- **clear**
- **__len__** -> int


## Class: ChangeRecord

**Description**: Record of a single file modification by a healer/fixer agent.

### Methods

#### __init__
**Parameters**: self, agent, file_path, description



## Class: ChangeTracker

**Description**: 
    Tracks all file modifications during healing operations.

    Provides exact traceability of which healer/fixer touched which file,
    producing a detailed Markdown report with by-agent and by-file views.
    

### Methods

#### __init__
**Parameters**: self

#### record
**Parameters**: self, agent, file_path, description
**Description**: Record a successful file modification immediately after writing.

#### _group_by_agent
**Parameters**: self
**Returns**: dict[str, list[tuple[str, str]]]
**Description**: Group all records by agent name.

#### _group_by_file
**Parameters**: self
**Returns**: dict[str, list[tuple[str, str]]]
**Description**: Group all records by file path.

#### generate_markdown_report
**Parameters**: self
**Returns**: str
**Description**: Generate a detailed Markdown report of all changes.

#### clear
**Parameters**: self
**Description**: Clear all recorded changes.

#### __len__
**Parameters**: self
**Returns**: int
**Description**: Return the number of recorded changes.



## Function: __init__

**Parameters**: self, agent, file_path, description


## Function: __init__

**Parameters**: self


## Function: record

**Parameters**: self, agent, file_path, description
**Description**: Record a successful file modification immediately after writing.



## Function: _group_by_agent

**Parameters**: self
**Returns**: dict[str, list[tuple[str, str]]]
**Description**: Group all records by agent name.



## Function: _group_by_file

**Parameters**: self
**Returns**: dict[str, list[tuple[str, str]]]
**Description**: Group all records by file path.



## Function: generate_markdown_report

**Parameters**: self
**Returns**: str
**Description**: Generate a detailed Markdown report of all changes.



## Function: clear

**Parameters**: self
**Description**: Clear all recorded changes.



## Function: __len__

**Parameters**: self
**Returns**: int
**Description**: Return the number of recorded changes.



## Usage Examples

### Class Usage

```python
# Using ChangeRecord
changerecord = ChangeRecord()
```

```python
# Using ChangeTracker
changetracker = ChangeTracker()
changetracker.record()
changetracker.generate_markdown_report()
```

### Function Usage

```python
# Using __init__
result = __init__(agent, file_path)
```

```python
# Using __init__
result = __init__()
```

```python
# Using record
result = record(agent, file_path)
```



---
**Generated**: 2026-03-26T09:39:04.488235
**Type**: api_reference
**Quality**: comprehensive
