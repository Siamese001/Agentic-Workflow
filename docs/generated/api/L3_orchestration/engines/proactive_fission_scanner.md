# API Documentation: proactive_fission_scanner

**Target Audience**: developers, api_users

# proactive_fission_scanner API Documentation

**File**: `proactive_fission_scanner.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ProactiveFissionScanner**

## Functions

- **get_proactive_scanner** -> ProactiveFissionScanner
- **__init__**
- **get_line_count** -> int
- **_calculate_severity** -> str
- **_recommend_split** -> dict[str, str]


## Class: ProactiveFissionScanner

**Description**: 
    L3 Orchestrator: Scans the L4 State for structural patterns
    matching known 'Critical Bloat' profiles.

    Process:
    1. Scan repository for files exceeding line threshold
    2. Query Brave Search for modular design patterns
    3. Use Pinecone to find structural twins
    4. Generate pre-emptive fission strategies
    5. Create GitKraken refactor proposal branches
    

### Methods

#### __init__
**Parameters**: self, McpRouterAgent, line_threshold
**Description**: 
        Initialize Proactive Fission Scanner.

        Args:
            McpRouterAgent: MCPRouter instance for MCP calls
            line_threshold: Line count threshold for bloat detection
        

#### get_line_count
**Parameters**: self, file_path
**Returns**: int
**Description**: 
        Get line count for a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines in file
        

#### _calculate_severity
**Parameters**: self, line_count
**Returns**: str
**Description**: 
        Calculate Severity level based on line count.

        Args:
            line_count: Number of lines

        Returns:
            Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        

#### _recommend_split
**Parameters**: self, file_path
**Returns**: dict[str, str]
**Description**: 
        Recommend split pattern based on file name and content.

        Args:
            file_path: Path to file

        Returns:
            Dictionary of recommended file splits
        



## Function: get_proactive_scanner

**Parameters**: McpRouterAgent, line_threshold
**Returns**: ProactiveFissionScanner
**Description**: 
    Factory function to create ProactiveFissionScanner instance.

    Args:
        McpRouterAgent: MCPRouter instance
        line_threshold: Line count threshold

    Returns:
        ProactiveFissionScanner instance
    



## Function: __init__

**Parameters**: self, McpRouterAgent, line_threshold
**Description**: 
        Initialize Proactive Fission Scanner.

        Args:
            McpRouterAgent: MCPRouter instance for MCP calls
            line_threshold: Line count threshold for bloat detection
        



## Function: get_line_count

**Parameters**: self, file_path
**Returns**: int
**Description**: 
        Get line count for a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines in file
        



## Function: _calculate_severity

**Parameters**: self, line_count
**Returns**: str
**Description**: 
        Calculate Severity level based on line count.

        Args:
            line_count: Number of lines

        Returns:
            Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        



## Function: _recommend_split

**Parameters**: self, file_path
**Returns**: dict[str, str]
**Description**: 
        Recommend split pattern based on file name and content.

        Args:
            file_path: Path to file

        Returns:
            Dictionary of recommended file splits
        



## Usage Examples

### Class Usage

```python
# Using ProactiveFissionScanner
proactivefissionscanner = ProactiveFissionScanner()
proactivefissionscanner.get_line_count()
```

### Function Usage

```python
# Using get_proactive_scanner
result = get_proactive_scanner(McpRouterAgent, line_threshold)
```

```python
# Using __init__
result = __init__(McpRouterAgent, line_threshold)
```

```python
# Using get_line_count
result = get_line_count(file_path)
```



---
**Generated**: 2026-03-26T09:39:04.188754
**Type**: api_reference
**Quality**: comprehensive
