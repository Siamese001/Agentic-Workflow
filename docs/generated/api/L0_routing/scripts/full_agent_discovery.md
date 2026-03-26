# API Documentation: full_agent_discovery

**Target Audience**: developers, api_users

# full_agent_discovery API Documentation

**File**: `full_agent_discovery.py`
**Classes**: 2
**Functions**: 14

## Classes

- **AgentIntegrityReport**
- **DiscoveryError** (inherits from Exception)

## Functions

- **_get_safe_subprocess_check_output**
- **setup_logging** -> None
- **sha256_file** -> str
- **get_git_commit** -> str
- **main** -> bool
- **analyze_agent_integrity** -> AgentIntegrityReport
- **perform_deep_integrity_scan** -> tuple[list[dict[str, Any]], dict[str, int]]
- **check_compliance_gate** -> bool
- **discover_all_agents** -> list[dict[str, Any]]
- **get_agent_discovery_summary** -> dict[str, Any]
- **refresh_discovery_cache** -> bool
- **get_structured_agent_paths** -> list[str]
- **cli_interface** -> None
- **extract_mro_signature** -> list[str]


## Class: AgentIntegrityReport

**Description**: Detailed AST analysis result for a single agent file.



## Class: DiscoveryError

**Description**: Custom exception for agent discovery operations.

**Inherits from**: Exception



## Function: _get_safe_subprocess_check_output



## Function: setup_logging

**Parameters**: verbose
**Returns**: None
**Description**: 
    Standard logging configuration wrapper.
    



## Function: sha256_file

**Parameters**: path
**Returns**: str


## Function: get_git_commit

**Parameters**: root
**Returns**: str


## Function: main

**Returns**: bool
**Description**: 
    Main entry point for agent discovery operations.
    Performs comprehensive agent discovery and strict integrity validation.
    



## Function: analyze_agent_integrity

**Parameters**: file_path
**Returns**: AgentIntegrityReport
**Description**: 
    Performs deep AST analysis on a file to verify it is a legitimate Agent.

    [REFACTORED 2026-02-08] Classification decision now delegated to the
    zero-dependency kernel (agentic_core.L5_safety.core_kernel.classification_kernel).
    This function still extracts metadata (inheritance, decorators, methods)
    for the integrity report but no longer uses bespoke class_score() logic.

    Steps:
    1. Kernel classification (AGENT vs other FileType)
    2. AST metadata extraction (inheritance, decorators, methods)
    3. Integrity report generation
    



## Function: perform_deep_integrity_scan

**Parameters**: agents, project_root
**Returns**: tuple[list[dict[str, Any]], dict[str, int]]
**Description**: 
    Iterates over discovered agents and validates them using AST analysis.
    Returns:
        tuple: (List of verified agents, Statistics Dictionary)
    



## Function: check_compliance_gate

**Parameters**: scan_stats
**Returns**: bool
**Description**: 
    Check compliance gate using SSOT validation AND Integrity Stats.

    Args:
        scan_stats: Optional dict from perform_deep_integrity_scan.
                    If provided, enforces thresholds on invalid agents.

    Returns:
        bool: True if compliance checks pass, False otherwise.
    



## Function: discover_all_agents

**Parameters**: strict_mode
**Returns**: list[dict[str, Any]]
**Description**: 
    Discover all agents in the repository using SSOT and AST Validation.

    Args:
        strict_mode: If True, filters out agents that fail AST validation.

    Returns:
        List[Dict[str, Any]]: List of verified agent discovery entries.
    



## Function: get_agent_discovery_summary

**Returns**: dict[str, Any]
**Description**: 
    Generate comprehensive agent discovery summary with Integrity Stats.
    



## Function: refresh_discovery_cache

**Returns**: bool
**Description**: 
    Refresh the agent discovery cache.
    Forces cache invalidation and reload to ensure latest data.
    



## Function: get_structured_agent_paths

**Returns**: list[str]
**Description**: 
    Return structured list of verified agent file paths.
    



## Function: cli_interface

**Returns**: None
**Description**: Command-line interface for discovery operations.



## Function: extract_mro_signature

**Parameters**: cls
**Returns**: list[str]


## Usage Examples

### Class Usage

```python
# Using AgentIntegrityReport
agentintegrityreport = AgentIntegrityReport()
```

```python
# Using DiscoveryError
discoveryerror = DiscoveryError()
```

### Function Usage

```python
# Using _get_safe_subprocess_check_output
result = _get_safe_subprocess_check_output()
```

```python
# Using setup_logging
result = setup_logging(verbose)
```

```python
# Using sha256_file
result = sha256_file(path)
```



---
**Generated**: 2026-03-26T09:39:03.150970
**Type**: api_reference
**Quality**: comprehensive
