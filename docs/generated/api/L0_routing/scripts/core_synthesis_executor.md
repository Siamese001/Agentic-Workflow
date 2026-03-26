# API Documentation: core_synthesis_executor

**Target Audience**: developers, api_users

# core_synthesis_executor API Documentation

**File**: `core_synthesis_executor.py`
**Classes**: 1
**Functions**: 11

## Classes

- **CoreSynthesisExecutor**

## Functions

- **main**
- **__init__**
- **_load_synthesis_plan** -> dict
- **execute_synthesis** -> bool
- **_execute_archival** -> bool
- **_execute_synthesis_merging** -> bool
- **_extract_synthesis_logic** -> str | None
- **_merge_logic_into_target** -> bool
- **_execute_stateless_eviction** -> bool
- **_verify_circular_dependency_purge** -> bool
- **generate_synthesis_report** -> str


## Class: CoreSynthesisExecutor

**Description**: Executes zero-loss synthesis and restructure operations.

### Methods

#### __init__
**Parameters**: self

#### _load_synthesis_plan
**Parameters**: self
**Returns**: dict
**Description**: Load the synthesis plan from analysis results.

#### execute_synthesis
**Parameters**: self
**Returns**: bool
**Description**: Execute the complete synthesis and restructure plan.

#### _execute_archival
**Parameters**: self
**Returns**: bool
**Description**: Archive files marked for archival.

#### _execute_synthesis_merging
**Parameters**: self
**Returns**: bool
**Description**: Execute atomic logic merging for synthesis files.

#### _extract_synthesis_logic
**Parameters**: self, content, file_info
**Returns**: str | None
**Description**: Extract unique logic from source file for synthesis.

#### _merge_logic_into_target
**Parameters**: self, target_path, logic, file_info
**Returns**: bool
**Description**: Merge extracted logic into target file.

#### _execute_stateless_eviction
**Parameters**: self
**Returns**: bool
**Description**: Move stateless utility functions to utils/.

#### _verify_circular_dependency_purge
**Parameters**: self
**Returns**: bool
**Description**: Verify no circular dependencies remain.

#### generate_synthesis_report
**Parameters**: self
**Returns**: str
**Description**: Generate synthesis execution report.



## Function: main

**Description**: Execute the synthesis and restructure.



## Function: __init__

**Parameters**: self


## Function: _load_synthesis_plan

**Parameters**: self
**Returns**: dict
**Description**: Load the synthesis plan from analysis results.



## Function: execute_synthesis

**Parameters**: self
**Returns**: bool
**Description**: Execute the complete synthesis and restructure plan.



## Function: _execute_archival

**Parameters**: self
**Returns**: bool
**Description**: Archive files marked for archival.



## Function: _execute_synthesis_merging

**Parameters**: self
**Returns**: bool
**Description**: Execute atomic logic merging for synthesis files.



## Function: _extract_synthesis_logic

**Parameters**: self, content, file_info
**Returns**: str | None
**Description**: Extract unique logic from source file for synthesis.



## Function: _merge_logic_into_target

**Parameters**: self, target_path, logic, file_info
**Returns**: bool
**Description**: Merge extracted logic into target file.



## Function: _execute_stateless_eviction

**Parameters**: self
**Returns**: bool
**Description**: Move stateless utility functions to utils/.



## Function: _verify_circular_dependency_purge

**Parameters**: self
**Returns**: bool
**Description**: Verify no circular dependencies remain.



## Function: generate_synthesis_report

**Parameters**: self
**Returns**: str
**Description**: Generate synthesis execution report.



## Usage Examples

### Class Usage

```python
# Using CoreSynthesisExecutor
coresynthesisexecutor = CoreSynthesisExecutor()
coresynthesisexecutor.execute_synthesis()
coresynthesisexecutor.generate_synthesis_report()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__()
```

```python
# Using _load_synthesis_plan
result = _load_synthesis_plan()
```



---
**Generated**: 2026-03-26T09:39:02.836771
**Type**: api_reference
**Quality**: comprehensive
