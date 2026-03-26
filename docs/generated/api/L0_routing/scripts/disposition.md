# API Documentation: disposition

**Target Audience**: developers, api_users

# disposition API Documentation

**File**: `disposition.py`
**Classes**: 3
**Functions**: 12

## Classes

- **Disposition** (inherits from Enum)
- **CoreAnalysisResult**
- **CoreSynthesisAnalyzer**

## Functions

- **main**
- **__init__**
- **analyze_file** -> CoreAnalysisResult
- **_analyze_cfg_complexity** -> int
- **_analyze_data_flow** -> int
- **_extract_imports** -> list[str]
- **_detect_circular_dependencies** -> list[str]
- **_verify_contract_compliance** -> bool
- **_analyze_sovereign_requirements** -> list[str]
- **_determine_disposition** -> tuple[Disposition, str | None, float, str]
- **execute_analysis** -> list[CoreAnalysisResult]
- **generate_report** -> str


## Class: Disposition

**Description**: File disposition for synthesis analysis.

**Inherits from**: Enum



## Class: CoreAnalysisResult

**Description**: Result of core analysis for a single file.



## Class: CoreSynthesisAnalyzer

**Description**: Advanced analyzer for sovereign core logic synthesis.

### Methods

#### __init__
**Parameters**: self, base_path

#### analyze_file
**Parameters**: self, file_path
**Returns**: CoreAnalysisResult
**Description**: Perform comprehensive analysis of a single file.

#### _analyze_cfg_complexity
**Parameters**: self, tree
**Returns**: int
**Description**: Analyze Control Flow Graph complexity.

#### _analyze_data_flow
**Parameters**: self, tree
**Returns**: int
**Description**: Analyze data flow nodes.

#### _extract_imports
**Parameters**: self, tree
**Returns**: list[str]
**Description**: Extract import statements.

#### _detect_circular_dependencies
**Parameters**: self, file_path, imports
**Returns**: list[str]
**Description**: Detect circular dependencies with app zones.

#### _verify_contract_compliance
**Parameters**: self, tree
**Returns**: bool
**Description**: Verify CanonBaseAgentInterface contract compliance.

#### _analyze_sovereign_requirements
**Parameters**: self, tree
**Returns**: list[str]
**Description**: Analyze V2.5 Sovereign Requirements compliance.

#### _determine_disposition
**Parameters**: self, file_path, tree, cfg_complexity, data_flow_nodes, circular_deps, contract_compliance, sovereign_requirements
**Returns**: tuple[Disposition, str | None, float, str]
**Description**: Determine file disposition and synthesis target.

#### execute_analysis
**Parameters**: self
**Returns**: list[CoreAnalysisResult]
**Description**: Execute comprehensive analysis of all files.

#### generate_report
**Parameters**: self
**Returns**: str
**Description**: Generate comprehensive analysis report.



## Function: main

**Description**: Execute the core synthesis analysis.



## Function: __init__

**Parameters**: self, base_path


## Function: analyze_file

**Parameters**: self, file_path
**Returns**: CoreAnalysisResult
**Description**: Perform comprehensive analysis of a single file.



## Function: _analyze_cfg_complexity

**Parameters**: self, tree
**Returns**: int
**Description**: Analyze Control Flow Graph complexity.



## Function: _analyze_data_flow

**Parameters**: self, tree
**Returns**: int
**Description**: Analyze data flow nodes.



## Function: _extract_imports

**Parameters**: self, tree
**Returns**: list[str]
**Description**: Extract import statements.



## Function: _detect_circular_dependencies

**Parameters**: self, file_path, imports
**Returns**: list[str]
**Description**: Detect circular dependencies with app zones.



## Function: _verify_contract_compliance

**Parameters**: self, tree
**Returns**: bool
**Description**: Verify CanonBaseAgentInterface contract compliance.



## Function: _analyze_sovereign_requirements

**Parameters**: self, tree
**Returns**: list[str]
**Description**: Analyze V2.5 Sovereign Requirements compliance.



## Function: _determine_disposition

**Parameters**: self, file_path, tree, cfg_complexity, data_flow_nodes, circular_deps, contract_compliance, sovereign_requirements
**Returns**: tuple[Disposition, str | None, float, str]
**Description**: Determine file disposition and synthesis target.



## Function: execute_analysis

**Parameters**: self
**Returns**: list[CoreAnalysisResult]
**Description**: Execute comprehensive analysis of all files.



## Function: generate_report

**Parameters**: self
**Returns**: str
**Description**: Generate comprehensive analysis report.



## Usage Examples

### Class Usage

```python
# Using Disposition
disposition = Disposition()
```

```python
# Using CoreAnalysisResult
coreanalysisresult = CoreAnalysisResult()
```

```python
# Using CoreSynthesisAnalyzer
coresynthesisanalyzer = CoreSynthesisAnalyzer()
coresynthesisanalyzer.analyze_file()
coresynthesisanalyzer.execute_analysis()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(base_path)
```

```python
# Using analyze_file
result = analyze_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:02.865015
**Type**: api_reference
**Quality**: comprehensive
