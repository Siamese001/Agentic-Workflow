# API Documentation: layer_sovereignty_enforcer

**Target Audience**: developers, api_users

# layer_sovereignty_enforcer API Documentation

**File**: `layer_sovereignty_enforcer.py`
**Classes**: 3
**Functions**: 14

## Classes

- **SovereigntyViolation**
- **EnforcementReport**
- **LayerSovereigntyEnforcer**

## Functions

- **main** -> int
- **__str__** -> str
- **passed** -> bool
- **summary** -> str
- **__init__** -> None
- **run** -> EnforcementReport
- **_scan_file** -> None
- **_path_to_module** -> str
- **_collect_imports** -> list[str]
- **_is_allowed_exception** -> bool
- **extract_layer_from_module** -> int | None
- **check_upward_mutation** -> bool
- **analyze_file_imports** -> list[SovereigntyViolation]
- **detect_circular_imports** -> list[tuple[str, str]]


## Class: SovereigntyViolation

**Description**: A single detected upward-import violation.

### Methods

#### __str__
**Parameters**: self
**Returns**: str



## Class: EnforcementReport

**Description**: Aggregated result of a sovereignty scan.

### Methods

#### passed
**Parameters**: self
**Returns**: bool

#### summary
**Parameters**: self
**Returns**: str



## Class: LayerSovereigntyEnforcer

**Description**: 
    AST-based layer sovereignty enforcer.

    Scans Python source files and detects any import from a layer with a
    higher authority number than the importing file's own layer.
    

### Methods

#### __init__
**Parameters**: self, repo_root, scan_roots, allowed_exceptions
**Returns**: None

#### run
**Parameters**: self
**Returns**: EnforcementReport
**Description**: Run the full sovereignty scan and return an EnforcementReport.

#### _scan_file
**Parameters**: self, file_path, report
**Returns**: None
**Description**: Parse one file and append any violations to report.

#### _path_to_module
**Parameters**: self, file_path
**Returns**: str
**Description**: Convert a filesystem path to a dotted module name.

#### _collect_imports
**Parameters**: self, tree
**Returns**: list[str]
**Description**: Return all imported module names from an AST tree.

#### _is_allowed_exception
**Parameters**: self, importer, imported
**Returns**: bool
**Description**: Return True if this upward import pair is explicitly whitelisted.

#### extract_layer_from_module
**Parameters**: module_path
**Returns**: int | None
**Description**: 
        Return the layer number for a dotted module path, or None if not
        part of the layer hierarchy.

        Examples
        --------
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.L2_execution.foo")
        2
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.base_agents.Foo") is None
        True
        

#### check_upward_mutation
**Parameters**: importer_layer, imported_layer
**Returns**: bool
**Description**: 
        Return True if importing ``imported_layer`` from ``importer_layer``
        is an upward mutation (violation).

        A violation occurs when ``imported_layer > importer_layer``.
        

#### analyze_file_imports
**Parameters**: self, file_path
**Returns**: list[SovereigntyViolation]
**Description**: 
        Analyse a single file and return any violations found.
        Does NOT mutate any shared state.
        

#### detect_circular_imports
**Parameters**: self
**Returns**: list[tuple[str, str]]
**Description**: 
        Detect mutually circular imports between any two modules in scan roots.
        Returns a list of (module_a, module_b) pairs that import each other.
        



## Function: main

**Returns**: int


## Function: __str__

**Parameters**: self
**Returns**: str


## Function: passed

**Parameters**: self
**Returns**: bool


## Function: summary

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, repo_root, scan_roots, allowed_exceptions
**Returns**: None


## Function: run

**Parameters**: self
**Returns**: EnforcementReport
**Description**: Run the full sovereignty scan and return an EnforcementReport.



## Function: _scan_file

**Parameters**: self, file_path, report
**Returns**: None
**Description**: Parse one file and append any violations to report.



## Function: _path_to_module

**Parameters**: self, file_path
**Returns**: str
**Description**: Convert a filesystem path to a dotted module name.



## Function: _collect_imports

**Parameters**: self, tree
**Returns**: list[str]
**Description**: Return all imported module names from an AST tree.



## Function: _is_allowed_exception

**Parameters**: self, importer, imported
**Returns**: bool
**Description**: Return True if this upward import pair is explicitly whitelisted.



## Function: extract_layer_from_module

**Parameters**: module_path
**Returns**: int | None
**Description**: 
        Return the layer number for a dotted module path, or None if not
        part of the layer hierarchy.

        Examples
        --------
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.L2_execution.foo")
        2
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.base_agents.Foo") is None
        True
        



## Function: check_upward_mutation

**Parameters**: importer_layer, imported_layer
**Returns**: bool
**Description**: 
        Return True if importing ``imported_layer`` from ``importer_layer``
        is an upward mutation (violation).

        A violation occurs when ``imported_layer > importer_layer``.
        



## Function: analyze_file_imports

**Parameters**: self, file_path
**Returns**: list[SovereigntyViolation]
**Description**: 
        Analyse a single file and return any violations found.
        Does NOT mutate any shared state.
        



## Function: detect_circular_imports

**Parameters**: self
**Returns**: list[tuple[str, str]]
**Description**: 
        Detect mutually circular imports between any two modules in scan roots.
        Returns a list of (module_a, module_b) pairs that import each other.
        



## Usage Examples

### Class Usage

```python
# Using SovereigntyViolation
sovereigntyviolation = SovereigntyViolation()
```

```python
# Using EnforcementReport
enforcementreport = EnforcementReport()
enforcementreport.passed()
enforcementreport.summary()
```

```python
# Using LayerSovereigntyEnforcer
layersovereigntyenforcer = LayerSovereigntyEnforcer()
layersovereigntyenforcer.run()
layersovereigntyenforcer.extract_layer_from_module()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __str__
result = __str__()
```

```python
# Using passed
result = passed()
```



---
**Generated**: 2026-03-26T09:39:04.866710
**Type**: api_reference
**Quality**: comprehensive
