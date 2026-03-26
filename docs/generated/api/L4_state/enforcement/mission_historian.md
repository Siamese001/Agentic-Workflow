# API Documentation: mission_historian

**Target Audience**: developers, api_users

# mission_historian API Documentation

**File**: `mission_historian.py`
**Classes**: 1
**Functions**: 5

## Classes

- **MissionHistorian**

## Functions

- **_get_write_gateway**
- **__init__**
- **record** -> Any
- **get_history** -> list
- **get_summary** -> dict[str, Any]


## Class: MissionHistorian

**Description**: 
    L4 State: Mission History Tracking
    Records all mission actions, decisions, and outcomes for audit trails.
    

### Methods

#### __init__
**Parameters**: self, log_path
**Description**: 
        Initialize the MissionHistorian.

        Args:
            log_path: Path to the audit log CSV file
        

#### record
**Parameters**: self, file_name, action, source, destination, reason
**Returns**: Any
**Description**: 
        Record a mission action to the audit log.

        Args:
            file_name: Name of the file affected
            action: Action performed (e.g., 'move', 'delete', 'create')
            source: Source location
            destination: Destination location
            reason: Reason for the action
        

#### get_history
**Parameters**: self, file_name
**Returns**: list
**Description**: 
        Retrieve mission history.

        Args:
            file_name: Optional filter by file name

        Returns:
            List of history records
        

#### get_summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get summary statistics of mission history.

        Returns:
            Dictionary with summary statistics
        



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: __init__

**Parameters**: self, log_path
**Description**: 
        Initialize the MissionHistorian.

        Args:
            log_path: Path to the audit log CSV file
        



## Function: record

**Parameters**: self, file_name, action, source, destination, reason
**Returns**: Any
**Description**: 
        Record a mission action to the audit log.

        Args:
            file_name: Name of the file affected
            action: Action performed (e.g., 'move', 'delete', 'create')
            source: Source location
            destination: Destination location
            reason: Reason for the action
        



## Function: get_history

**Parameters**: self, file_name
**Returns**: list
**Description**: 
        Retrieve mission history.

        Args:
            file_name: Optional filter by file name

        Returns:
            List of history records
        



## Function: get_summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get summary statistics of mission history.

        Returns:
            Dictionary with summary statistics
        



## Usage Examples

### Class Usage

```python
# Using MissionHistorian
missionhistorian = MissionHistorian()
missionhistorian.record()
missionhistorian.get_history()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using __init__
result = __init__(log_path)
```

```python
# Using record
result = record(file_name, action)
```



---
**Generated**: 2026-03-26T09:39:04.508146
**Type**: api_reference
**Quality**: comprehensive
