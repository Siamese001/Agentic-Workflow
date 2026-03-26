# API Documentation: sovereign_healing_engine_enforcer

**Target Audience**: developers, api_users

# sovereign_healing_engine_enforcer API Documentation

**File**: `sovereign_healing_engine_enforcer.py`
**Classes**: 2
**Functions**: 4

## Classes

- **HealingTransaction**
- **SovereignHealingEngine**

## Functions

- **get_filesystem_client**
- **get_git_client**
- **__init__**
- **__init__**


## Class: HealingTransaction

### Methods

#### __init__
**Parameters**: self



## Class: SovereignHealingEngine

**Description**: 
    The brain of L0: Detects and transactionally repairs constitutional breaches.

    Features:
    - Autonomous Violation detection and correction
    - Transactional safety with rollback capability
    - MCP-routed file operations (Filesystem MCP)
    - MCP-routed version control (GitKraken MCP)
    - Configurable auto-apply, auto-commit, auto-PR
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize the healing engine with MCP clients.



## Function: get_filesystem_client



## Function: get_git_client



## Function: __init__

**Parameters**: self


## Function: __init__

**Parameters**: self
**Description**: Initialize the healing engine with MCP clients.



## Usage Examples

### Class Usage

```python
# Using HealingTransaction
healingtransaction = HealingTransaction()
```

```python
# Using SovereignHealingEngine
sovereignhealingengine = SovereignHealingEngine()
```

### Function Usage

```python
# Using get_filesystem_client
result = get_filesystem_client()
```

```python
# Using get_git_client
result = get_git_client()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:04.937886
**Type**: api_reference
**Quality**: comprehensive
