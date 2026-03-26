# API Documentation: ssot_scanner_enforcer

**Target Audience**: developers, api_users

# ssot_scanner_enforcer API Documentation

**File**: `ssot_scanner_enforcer.py`
**Classes**: 2
**Functions**: 11

## Classes

- **AgentMetadata**
- **SSOTScanner**

## Functions

- **has_gravity_violation** -> bool
- **is_compliant** -> bool
- **__init__**
- **scan_agents** -> list[AgentMetadata]
- **get_layer_assignment** -> str
- **get_actual_layer** -> str
- **find_gravity_violations** -> list[AgentMetadata]
- **get_compliance_stats** -> dict[str, any]
- **_should_exclude** -> bool
- **_parse_agent_file** -> AgentMetadata | None
- **_extract_signals** -> set[str]


## Class: AgentMetadata

**Description**: Metadata for a single agent file.

### Methods

#### has_gravity_violation
**Parameters**: self
**Returns**: bool
**Description**: 
        Check if agent is in wrong layer (gravity violation).

        Only L0-L5 layers can have violations. APP and UNKNOWN are not violations.
        

#### is_compliant
**Parameters**: self
**Returns**: bool
**Description**: Check if agent is in correct Gospel-assigned layer.



## Class: SSOTScanner

**Description**: 
    Direct filesystem scanner for SSOT enforcement.

    Replaces agent_discovery_full.json with instant, always-current scanning.
    Uses on-demand AST parsing to minimize overhead.
    

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: 
        Initialize SSOT scanner.

        Args:
            project_root: Root directory of the project
        

#### scan_agents
**Parameters**: self, use_cache
**Returns**: list[AgentMetadata]
**Description**: 
        Scan filesystem for all agent files.

        Args:
            use_cache: If True, return cached results (for performance)

        Returns:
            List of agent metadata
        

#### get_layer_assignment
**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Derive layer assignment from file path.

        Args:
            file_path: Path to agent file

        Returns:
            Layer assignment (L0-L5)
        

#### get_actual_layer
**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Get actual layer from file path (where file currently is).

        Args:
            file_path: Path to agent file

        Returns:
            Actual layer (L0-L5)
        

#### find_gravity_violations
**Parameters**: self
**Returns**: list[AgentMetadata]
**Description**: 
        Find all agents with gravity violations (wrong layer).

        Checks agentic_core and apps_* folders.

        Returns:
            List of agents in wrong layers
        

#### get_compliance_stats
**Parameters**: self
**Returns**: dict[str, any]
**Description**: 
        Get compliance statistics.

        Returns:
            Dictionary with compliance metrics
        

#### _should_exclude
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file should be excluded from scanning.

#### _parse_agent_file
**Parameters**: self, file_path
**Returns**: AgentMetadata | None
**Description**: 
        Parse agent file to extract metadata.

        Args:
            file_path: Path to agent file

        Returns:
            Agent metadata or None if not a valid agent
        

#### _extract_signals
**Parameters**: self, content
**Returns**: set[str]
**Description**: 
        Extract canonical signals from agent code.

        Args:
            content: File content

        Returns:
            Set of detected signals
        



## Function: has_gravity_violation

**Parameters**: self
**Returns**: bool
**Description**: 
        Check if agent is in wrong layer (gravity violation).

        Only L0-L5 layers can have violations. APP and UNKNOWN are not violations.
        



## Function: is_compliant

**Parameters**: self
**Returns**: bool
**Description**: Check if agent is in correct Gospel-assigned layer.



## Function: __init__

**Parameters**: self, project_root
**Description**: 
        Initialize SSOT scanner.

        Args:
            project_root: Root directory of the project
        



## Function: scan_agents

**Parameters**: self, use_cache
**Returns**: list[AgentMetadata]
**Description**: 
        Scan filesystem for all agent files.

        Args:
            use_cache: If True, return cached results (for performance)

        Returns:
            List of agent metadata
        



## Function: get_layer_assignment

**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Derive layer assignment from file path.

        Args:
            file_path: Path to agent file

        Returns:
            Layer assignment (L0-L5)
        



## Function: get_actual_layer

**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Get actual layer from file path (where file currently is).

        Args:
            file_path: Path to agent file

        Returns:
            Actual layer (L0-L5)
        



## Function: find_gravity_violations

**Parameters**: self
**Returns**: list[AgentMetadata]
**Description**: 
        Find all agents with gravity violations (wrong layer).

        Checks agentic_core and apps_* folders.

        Returns:
            List of agents in wrong layers
        



## Function: get_compliance_stats

**Parameters**: self
**Returns**: dict[str, any]
**Description**: 
        Get compliance statistics.

        Returns:
            Dictionary with compliance metrics
        



## Function: _should_exclude

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file should be excluded from scanning.



## Function: _parse_agent_file

**Parameters**: self, file_path
**Returns**: AgentMetadata | None
**Description**: 
        Parse agent file to extract metadata.

        Args:
            file_path: Path to agent file

        Returns:
            Agent metadata or None if not a valid agent
        



## Function: _extract_signals

**Parameters**: self, content
**Returns**: set[str]
**Description**: 
        Extract canonical signals from agent code.

        Args:
            content: File content

        Returns:
            Set of detected signals
        



## Usage Examples

### Class Usage

```python
# Using AgentMetadata
agentmetadata = AgentMetadata()
agentmetadata.has_gravity_violation()
agentmetadata.is_compliant()
```

```python
# Using SSOTScanner
ssotscanner = SSOTScanner()
ssotscanner.scan_agents()
ssotscanner.get_layer_assignment()
```

### Function Usage

```python
# Using has_gravity_violation
result = has_gravity_violation()
```

```python
# Using is_compliant
result = is_compliant()
```

```python
# Using __init__
result = __init__(project_root)
```



---
**Generated**: 2026-03-26T09:39:04.949051
**Type**: api_reference
**Quality**: comprehensive
