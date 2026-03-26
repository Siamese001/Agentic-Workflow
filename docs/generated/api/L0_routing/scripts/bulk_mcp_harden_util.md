# API Documentation: bulk_mcp_harden_util

**Target Audience**: developers, api_users

# bulk_mcp_harden_util API Documentation

**File**: `bulk_mcp_harden_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **load_discovery**
- **get_unhardened_external_agents**
- **add_mcp_mixin_to_file** -> bool
- **add_import** -> str
- **main**


## Function: load_discovery

**Description**: Load agent discovery data.



## Function: get_unhardened_external_agents

**Parameters**: data
**Description**: Get list of external agents that aren't MCP hardened.



## Function: add_mcp_mixin_to_file

**Parameters**: file_path, class_name
**Returns**: bool
**Description**: Add MCPHardenedMixin to a class in a file.



## Function: add_import

**Parameters**: content
**Returns**: str
**Description**: Add MCPHardenedMixin import to content.



## Function: main



## Usage Examples

### Function Usage

```python
# Using load_discovery
result = load_discovery()
```

```python
# Using get_unhardened_external_agents
result = get_unhardened_external_agents(data)
```

```python
# Using add_mcp_mixin_to_file
result = add_mcp_mixin_to_file(file_path, class_name)
```



---
**Generated**: 2026-03-26T09:39:02.770877
**Type**: api_reference
**Quality**: comprehensive
