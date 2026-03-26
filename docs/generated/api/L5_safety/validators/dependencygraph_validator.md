# API Documentation: dependencygraph_validator

**Target Audience**: developers, api_users

# dependencygraph_validator API Documentation

**File**: `dependencygraph_validator.py`
**Classes**: 3
**Functions**: 27

## Classes

- **DependencyGraph**
- **BudgetManager**
- **ValidationContext**

## Functions

- **_get_python_files** -> list[str]
- **_clean_llm_code** -> str
- **_rate_limited_retry**
- **decorator**
- **__init__**
- **get_impact_radius** -> list[str]
- **__init__**
- **check_budget** -> bool
- **get_status** -> str
- **__post_init__**
- **init**
- **_init_intelligence**
- **_load_memory**
- **_save_memory**
- **report**
- **get_file_content** -> str
- **write_compliant_file** -> bool
- **client**
- **signal_healing_cycle**
- **signal_convergence**
- **signal_critical_failure**
- **signal_ast_valid**
- **signal_deps_valid**
- **signal_secure**
- **signal_llm_failure**
- **rollback_changes**
- **refresh_graph**


## Class: DependencyGraph

**Description**: Builds a directed graph of imports and class hierarchies.

### Methods

#### __init__
**Parameters**: self

#### get_impact_radius
**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Calculates which files depend on the given path.



## Class: BudgetManager

**Description**: Tracks estimated token usage and financial safety limits.

### Methods

#### __init__
**Parameters**: self, limit_usd

#### check_budget
**Parameters**: self
**Returns**: bool
**Description**: Verifies if the session is within financial safety constraints.

#### get_status
**Parameters**: self
**Returns**: str
**Description**: Returns a formatted budget status string.



## Class: ValidationContext

**Description**: Shared memory and infrastructure state for all agents.

### Methods

#### __post_init__
**Parameters**: self

#### init
**Parameters**: self
**Description**: Explicit initialization - call this when ready to use the context.

#### _init_intelligence
**Parameters**: self

#### _load_memory
**Parameters**: self

#### _save_memory
**Parameters**: self

#### report
**Parameters**: self, agent, key, passed, details

#### get_file_content
**Parameters**: self, file_path
**Returns**: str

#### write_compliant_file
**Parameters**: self, path, content
**Returns**: bool
**Description**: 
        Writes content to a file, ensuring directory exists.
        

#### client
**Parameters**: self

#### signal_healing_cycle
**Parameters**: self, cycle_number, max_cycles
**Description**: Signal the start of a healing cycle.

#### signal_convergence
**Parameters**: self
**Description**: Signal that the validation has converged.

#### signal_critical_failure
**Parameters**: self, message
**Description**: Signal a critical failure.

#### signal_ast_valid
**Parameters**: self
**Description**: Signal that AST checks passed.

#### signal_deps_valid
**Parameters**: self
**Description**: Signal that dependency checks passed.

#### signal_secure
**Parameters**: self
**Description**: Signal that security checks passed.

#### signal_llm_failure
**Parameters**: self, error
**Description**: Signal an LLM failure.

#### rollback_changes
**Parameters**: self
**Description**: Rollback changes from file backups.

#### refresh_graph
**Parameters**: self
**Description**: Rebuilds graph after mutations (sync wrapper).



## Function: _get_python_files

**Parameters**: base_path
**Returns**: list[str]
**Description**: 
    Recursively finds all Python files in the given base path.
    



## Function: _clean_llm_code

**Parameters**: text
**Returns**: str
**Description**: 
    Cleans LLM generated code by removing common markdown fences.
    



## Function: _rate_limited_retry

**Parameters**: max_attempts, delay_seconds
**Description**: 
    A simple retry decorator for async functions with a delay.
    



## Function: decorator

**Parameters**: func


## Function: __init__

**Parameters**: self


## Function: get_impact_radius

**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Calculates which files depend on the given path.



## Function: __init__

**Parameters**: self, limit_usd


## Function: check_budget

**Parameters**: self
**Returns**: bool
**Description**: Verifies if the session is within financial safety constraints.



## Function: get_status

**Parameters**: self
**Returns**: str
**Description**: Returns a formatted budget status string.



## Function: __post_init__

**Parameters**: self


## Function: init

**Parameters**: self
**Description**: Explicit initialization - call this when ready to use the context.



## Function: _init_intelligence

**Parameters**: self


## Function: _load_memory

**Parameters**: self


## Function: _save_memory

**Parameters**: self


## Function: report

**Parameters**: self, agent, key, passed, details


## Function: get_file_content

**Parameters**: self, file_path
**Returns**: str


## Function: write_compliant_file

**Parameters**: self, path, content
**Returns**: bool
**Description**: 
        Writes content to a file, ensuring directory exists.
        



## Function: client

**Parameters**: self


## Function: signal_healing_cycle

**Parameters**: self, cycle_number, max_cycles
**Description**: Signal the start of a healing cycle.



## Function: signal_convergence

**Parameters**: self
**Description**: Signal that the validation has converged.



## Function: signal_critical_failure

**Parameters**: self, message
**Description**: Signal a critical failure.



## Function: signal_ast_valid

**Parameters**: self
**Description**: Signal that AST checks passed.



## Function: signal_deps_valid

**Parameters**: self
**Description**: Signal that dependency checks passed.



## Function: signal_secure

**Parameters**: self
**Description**: Signal that security checks passed.



## Function: signal_llm_failure

**Parameters**: self, error
**Description**: Signal an LLM failure.



## Function: rollback_changes

**Parameters**: self
**Description**: Rollback changes from file backups.



## Function: refresh_graph

**Parameters**: self
**Description**: Rebuilds graph after mutations (sync wrapper).



## Usage Examples

### Class Usage

```python
# Using DependencyGraph
dependencygraph = DependencyGraph()
dependencygraph.get_impact_radius()
```

```python
# Using BudgetManager
budgetmanager = BudgetManager()
budgetmanager.check_budget()
budgetmanager.get_status()
```

```python
# Using ValidationContext
validationcontext = ValidationContext()
validationcontext.init()
validationcontext.report()
```

### Function Usage

```python
# Using _get_python_files
result = _get_python_files(base_path)
```

```python
# Using _clean_llm_code
result = _clean_llm_code(text)
```

```python
# Using _rate_limited_retry
result = _rate_limited_retry(max_attempts, delay_seconds)
```



---
**Generated**: 2026-03-26T09:39:05.780783
**Type**: api_reference
**Quality**: comprehensive
