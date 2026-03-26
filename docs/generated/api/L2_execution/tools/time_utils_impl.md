# API Documentation: time_utils_impl

**Target Audience**: developers, api_users

# time_utils_impl API Documentation

**File**: `time_utils_impl.py`
**Classes**: 1
**Functions**: 4

## Classes

- **TimeTools**

## Functions

- **__init__**
- **_get_current_time_fallback** -> str
- **get_current_time** -> str
- **convert_time** -> str


## Class: TimeTools

**Description**: 
    Provides time-related functionalities, including current time and conversion.
    Tool ID Prefix: ACT-008
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initializes TimeTools. No specific state needed.

#### _get_current_time_fallback
**Parameters**: self, timezone
**Returns**: str
**Description**: 
        Helper to get current time using datetime/pytz if mcp_time_client is unavailable.

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").

        Returns:
            str: The current time in ISO 8601 format or an error message.
        

#### get_current_time
**Parameters**: self, timezone
**Returns**: str
**Description**: 
        Gets the current date, time, and timezone in ISO 8601 format.
        Tool ID: ACT-008

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").
                            Defaults to "UTC".

        Returns:
            str: The current time in ISO 8601 format or an error message.
        

#### convert_time
**Parameters**: self, source_timezone, time, target_timezone
**Returns**: str
**Description**: 
        Converts a time string between two specified IANA timezones.
        Tool ID: ACT-009

        Args:
            source_timezone (str): The IANA timezone of the input `time`.
            time (str): The time string to convert (e.g., "2023-10-27T10:00:00+00:00").
            target_timezone (str): The IANA timezone to convert the time to.

        Returns:
            str: The converted time string in ISO 8601 format or an error message.
        



## Function: __init__

**Parameters**: self
**Description**: Initializes TimeTools. No specific state needed.



## Function: _get_current_time_fallback

**Parameters**: self, timezone
**Returns**: str
**Description**: 
        Helper to get current time using datetime/pytz if mcp_time_client is unavailable.

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").

        Returns:
            str: The current time in ISO 8601 format or an error message.
        



## Function: get_current_time

**Parameters**: self, timezone
**Returns**: str
**Description**: 
        Gets the current date, time, and timezone in ISO 8601 format.
        Tool ID: ACT-008

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").
                            Defaults to "UTC".

        Returns:
            str: The current time in ISO 8601 format or an error message.
        



## Function: convert_time

**Parameters**: self, source_timezone, time, target_timezone
**Returns**: str
**Description**: 
        Converts a time string between two specified IANA timezones.
        Tool ID: ACT-009

        Args:
            source_timezone (str): The IANA timezone of the input `time`.
            time (str): The time string to convert (e.g., "2023-10-27T10:00:00+00:00").
            target_timezone (str): The IANA timezone to convert the time to.

        Returns:
            str: The converted time string in ISO 8601 format or an error message.
        



## Usage Examples

### Class Usage

```python
# Using TimeTools
timetools = TimeTools()
timetools.get_current_time()
timetools.convert_time()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using _get_current_time_fallback
result = _get_current_time_fallback(timezone)
```

```python
# Using get_current_time
result = get_current_time(timezone)
```



---
**Generated**: 2026-03-26T09:39:03.920278
**Type**: api_reference
**Quality**: comprehensive
