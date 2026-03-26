# API Documentation: RootCustomsAgent

**Target Audience**: developers, api_users

# RootCustomsAgent API Documentation

**File**: `RootCustomsAgent.py`
**Classes**: 3
**Functions**: 23

## Classes

- **RoutingDecision**
- **ASTAnalyzer**
- **RootCustomsAgent** (inherits from SovereignBaseAgent)

## Functions

- **main**
- **__init__**
- **analyze_file** -> dict[str, Any]
- **_extract_signals**
- **__init__**
- **scan_root_directory** -> list[Path]
- **check_allowed_patterns** -> bool
- **analyze_content_signatures** -> dict[str, Any]
- **analyze_ast_signals** -> dict[str, Any]
- **_analyze_markdown** -> dict[str, Any]
- **_analyze_json** -> dict[str, Any]
- **_analyze_text** -> dict[str, Any]
- **determine_routing** -> RoutingDecision
- **_determine_test_routing** -> RoutingDecision | None
- **_determine_legacy_routing** -> RoutingDecision | None
- **_determine_ast_placement_routing** -> RoutingDecision | None
- **_calculate_routing_score** -> float
- **execute_routing** -> bool
- **run_inspection** -> dict[str, Any]
- **_print_summary**
- **heal** -> dict[str, Any]
- **heal_repository** -> dict
- **extract_keys**


## Class: RoutingDecision

**Description**: Represents a routing decision for a file.



## Class: ASTAnalyzer

**Description**: Analyzes Python files for AST-based routing signals.

### Methods

#### __init__
**Parameters**: self

#### analyze_file
**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze Python file for AST signals.

#### _extract_signals
**Parameters**: self, tree
**Description**: Extract AST signals from parsed tree.



## Class: RootCustomsAgent

**Description**: 
    Enhanced "Customs Agent" with AST-based Test Taxonomy and Zombie Code detection.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, dry_run

#### scan_root_directory
**Parameters**: self
**Returns**: list[Path]
**Description**: Scan the project root for files to analyze.

#### check_allowed_patterns
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file matches any allowed root patterns.

#### analyze_content_signatures
**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze file content for routing signatures.

#### analyze_ast_signals
**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze Python files for AST-based routing signals.

#### _analyze_markdown
**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: Analyze markdown content for headers and keywords.

#### _analyze_json
**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: Analyze JSON content for key signatures.

#### _analyze_text
**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: Analyze plain text content for keywords.

#### determine_routing
**Parameters**: self, file_path, content_matches, ast_matches
**Returns**: RoutingDecision
**Description**: Determine where a file should be routed using enhanced analysis.

#### _determine_test_routing
**Parameters**: self, file_path, ast_matches
**Returns**: RoutingDecision | None
**Description**: Determine test routing based on AST signals.

#### _determine_legacy_routing
**Parameters**: self, file_path, ast_matches
**Returns**: RoutingDecision | None
**Description**: Determine legacy routing based on AST signals.

#### _determine_ast_placement_routing
**Parameters**: self, file_path, ast_matches
**Returns**: RoutingDecision | None
**Description**: Determine AST placement routing.

#### _calculate_routing_score
**Parameters**: self, file_path, content_matches, config
**Returns**: float
**Description**: Calculate routing score for a destination configuration.

#### execute_routing
**Parameters**: self, decision
**Returns**: bool
**Description**: Execute a routing decision.

#### run_inspection
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Run complete enhanced root inspection and routing.

#### _print_summary
**Parameters**: self
**Description**: Print enhanced inspection summary.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RootCustomsAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for RootCustomsAgent.



## Function: main

**Description**: Main entry point for the Enhanced Root Customs Agent.



## Function: __init__

**Parameters**: self


## Function: analyze_file

**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze Python file for AST signals.



## Function: _extract_signals

**Parameters**: self, tree
**Description**: Extract AST signals from parsed tree.



## Function: __init__

**Parameters**: self, project_root, dry_run


## Function: scan_root_directory

**Parameters**: self
**Returns**: list[Path]
**Description**: Scan the project root for files to analyze.



## Function: check_allowed_patterns

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file matches any allowed root patterns.



## Function: analyze_content_signatures

**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze file content for routing signatures.



## Function: analyze_ast_signals

**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze Python files for AST-based routing signals.



## Function: _analyze_markdown

**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: Analyze markdown content for headers and keywords.



## Function: _analyze_json

**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: Analyze JSON content for key signatures.



## Function: _analyze_text

**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: Analyze plain text content for keywords.



## Function: determine_routing

**Parameters**: self, file_path, content_matches, ast_matches
**Returns**: RoutingDecision
**Description**: Determine where a file should be routed using enhanced analysis.



## Function: _determine_test_routing

**Parameters**: self, file_path, ast_matches
**Returns**: RoutingDecision | None
**Description**: Determine test routing based on AST signals.



## Function: _determine_legacy_routing

**Parameters**: self, file_path, ast_matches
**Returns**: RoutingDecision | None
**Description**: Determine legacy routing based on AST signals.



## Function: _determine_ast_placement_routing

**Parameters**: self, file_path, ast_matches
**Returns**: RoutingDecision | None
**Description**: Determine AST placement routing.



## Function: _calculate_routing_score

**Parameters**: self, file_path, content_matches, config
**Returns**: float
**Description**: Calculate routing score for a destination configuration.



## Function: execute_routing

**Parameters**: self, decision
**Returns**: bool
**Description**: Execute a routing decision.



## Function: run_inspection

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Run complete enhanced root inspection and routing.



## Function: _print_summary

**Parameters**: self
**Description**: Print enhanced inspection summary.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RootCustomsAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for RootCustomsAgent.



## Function: extract_keys

**Parameters**: obj, prefix


## Usage Examples

### Class Usage

```python
# Using RoutingDecision
routingdecision = RoutingDecision()
```

```python
# Using ASTAnalyzer
astanalyzer = ASTAnalyzer()
astanalyzer.analyze_file()
```

```python
# Using RootCustomsAgent
rootcustomsagent = RootCustomsAgent()
rootcustomsagent.scan_root_directory()
rootcustomsagent.check_allowed_patterns()
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
# Using analyze_file
result = analyze_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:02.716022
**Type**: api_reference
**Quality**: comprehensive
