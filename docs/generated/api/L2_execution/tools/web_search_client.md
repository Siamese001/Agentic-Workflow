# API Documentation: web_search_client

**Target Audience**: developers, api_users

# web_search_client API Documentation

**File**: `web_search_client.py`
**Classes**: 1
**Functions**: 4

## Classes

- **WebSearchTools**

## Functions

- **__init__**
- **_parse_mcp_response** -> str
- **_format_web_json** -> str
- **_format_local_json** -> str


## Class: WebSearchTools

**Description**: 
    Standardized toolset for external intelligence.
    Routes all traffic through L3 Sovereign router.
    Tool ID Prefix: ACT-001
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize with sovereign MCP router — L5 shielded

#### _parse_mcp_response
**Parameters**: self, result, mode
**Returns**: str
**Description**: 
        Normalizes MCP output regardless of server return format.

        Args:
            result: The MCP response object
            mode: "web" or "local" for format selection

        Returns:
            str: Formatted search results
        

#### _format_web_json
**Parameters**: self, data
**Returns**: str
**Description**: 
        Formats web search results into standardized output.

        Args:
            data: The Brave web search response data

        Returns:
            str: Formatted web search results
        

#### _format_local_json
**Parameters**: self, data
**Returns**: str
**Description**: 
        Formats local search results into standardized output.

        Args:
            data: The Brave local search response data

        Returns:
            str: Formatted local search results
        



## Function: __init__

**Parameters**: self
**Description**: Initialize with sovereign MCP router — L5 shielded



## Function: _parse_mcp_response

**Parameters**: self, result, mode
**Returns**: str
**Description**: 
        Normalizes MCP output regardless of server return format.

        Args:
            result: The MCP response object
            mode: "web" or "local" for format selection

        Returns:
            str: Formatted search results
        



## Function: _format_web_json

**Parameters**: self, data
**Returns**: str
**Description**: 
        Formats web search results into standardized output.

        Args:
            data: The Brave web search response data

        Returns:
            str: Formatted web search results
        



## Function: _format_local_json

**Parameters**: self, data
**Returns**: str
**Description**: 
        Formats local search results into standardized output.

        Args:
            data: The Brave local search response data

        Returns:
            str: Formatted local search results
        



## Usage Examples

### Class Usage

```python
# Using WebSearchTools
websearchtools = WebSearchTools()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using _parse_mcp_response
result = _parse_mcp_response(result, mode)
```

```python
# Using _format_web_json
result = _format_web_json(data)
```



---
**Generated**: 2026-03-26T09:39:03.931035
**Type**: api_reference
**Quality**: comprehensive
