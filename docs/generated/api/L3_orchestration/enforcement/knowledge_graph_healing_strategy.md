# API Documentation: knowledge_graph_healing_strategy

**Target Audience**: developers, api_users

# knowledge_graph_healing_strategy API Documentation

**File**: `knowledge_graph_healing_strategy.py`
**Classes**: 1
**Functions**: 2

## Classes

- **KnowledgeGraphHealingStrategy**

## Functions

- **__init__**
- **reset_daily_counter** -> Any


## Class: KnowledgeGraphHealingStrategy

**Description**: 
    Autonomous healing for knowledge graph drift.

    Detects and corrects KG inconsistencies by:
    - Re-extracting entities and relations from source content
    - Applying confidence thresholds for quality control
    - Using Memory MCP for all KG operations
    - Enforcing daily healing limits to prevent runaway operations
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize knowledge graph healing strategy with MCP clients.

#### reset_daily_counter
**Parameters**: self
**Returns**: Any
**Description**: Reset the daily processing counter (should be called at midnight).



## Function: __init__

**Parameters**: self
**Description**: Initialize knowledge graph healing strategy with MCP clients.



## Function: reset_daily_counter

**Parameters**: self
**Returns**: Any
**Description**: Reset the daily processing counter (should be called at midnight).



## Usage Examples

### Class Usage

```python
# Using KnowledgeGraphHealingStrategy
knowledgegraphhealingstrategy = KnowledgeGraphHealingStrategy()
knowledgegraphhealingstrategy.reset_daily_counter()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using reset_daily_counter
result = reset_daily_counter()
```



---
**Generated**: 2026-03-26T09:39:04.114801
**Type**: api_reference
**Quality**: comprehensive
