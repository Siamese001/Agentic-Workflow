# API Documentation: complexity_visitor_util

**Target Audience**: developers, api_users

# complexity_visitor_util API Documentation

**File**: `complexity_visitor_util.py`
**Classes**: 1
**Functions**: 43

## Classes

- **_CCVisitor** (inherits from <ast.Attribute object at 0x000001CBFCC025D0>)

## Functions

- **should_exclude_path** -> bool
- **should_exclude_file** -> bool
- **validate_agent_count** -> tuple[bool, list[str]]
- **get_previous_agent_count** -> int | None
- **generate_manifest** -> dict
- **safe_parse** -> ast.AST | None
- **extract_bases** -> set[str]
- **extract_decorators** -> list[str]
- **extract_class_attributes** -> list[str]
- **extract_imports** -> tuple[list[str], list[str]]
- **extract_method_signatures** -> list[dict[str, Any]]
- **build_inheritance_map** -> None
- **has_healing_in_chain** -> bool
- **extract_methods** -> list[str]
- **has_method** -> bool
- **get_method** -> ast.FunctionDef | None
- **detect_invocation_status** -> str
- **detect_has_tests** -> bool
- **_check_external_test_file** -> bool
- **calculate_typing_coverage** -> float
- **calculate_docstring_coverage** -> float
- **check_proper_base** -> bool
- **calculate_schema_strictness** -> float
- **get_base_name** -> str
- **detect_agent_metadata** -> bool
- **detect_observability** -> dict
- **calculate_cyclomatic_complexity** -> int
- **count_loc** -> int
- **is_sovereign_agent** -> bool
- **is_agent_class** -> bool
- **get_docstring** -> str
- **main**
- **check_compliance_gate** -> int
- **__init__**
- **visit_If**
- **visit_For**
- **visit_While**
- **visit_ExceptHandler**
- **visit_With**
- **visit_BoolOp**
- **visit_comprehension**
- **get_territory_from_path**
- **refine_territory_by_ast**


## Class: _CCVisitor

**Description**: Visitor to calculate cyclomatic complexity.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self

#### visit_If
**Parameters**: self, node

#### visit_For
**Parameters**: self, node

#### visit_While
**Parameters**: self, node

#### visit_ExceptHandler
**Parameters**: self, node

#### visit_With
**Parameters**: self, node

#### visit_BoolOp
**Parameters**: self, node

#### visit_comprehension
**Parameters**: self, node



## Function: should_exclude_path

**Parameters**: path
**Returns**: bool
**Description**: Return True if path should be excluded from scanning/hashing.

    Multi-factor exclusion (ANY match → exclude):
    1. Directory name in EXCLUDED_DIRS
    2. Filename matches EXCLUDED_FILENAME_PATTERNS
    3. Path contains EXCLUDED_PATH_PATTERNS
    



## Function: should_exclude_file

**Parameters**: py_file
**Returns**: bool
**Description**: Return True if file should not be scanned for agent discovery.

    HARDENED multi-factor exclusion for agent discovery:
    1. Directory-based: file in excluded directory
    2. Filename-based: filename contains mixin/utility patterns
    3. Extension-based: must be .py file
    4. Path-based: in test/example/generated directories

    Returns:
        True if ANY exclusion factor matches (aggressive OR for safety)
    



## Function: validate_agent_count

**Parameters**: agent_count, previous_count
**Returns**: tuple[bool, list[str]]
**Description**: 
    HARDENING: Validate agent count against safety thresholds.

    Returns:
        (is_valid, errors) - is_valid=False means ABORT discovery
    



## Function: get_previous_agent_count

**Returns**: int | None
**Description**: Get agent count from previous discovery run (from manifest or JSON).



## Function: generate_manifest

**Parameters**: agents, scan_duration, parse_errors
**Returns**: dict
**Description**: Generate manifest with metadata for staleness detection and validation.



## Function: safe_parse

**Parameters**: code, file_path
**Returns**: ast.AST | None
**Description**: Parse code with error tolerance.



## Function: extract_bases

**Parameters**: class_node
**Returns**: set[str]
**Description**: Extract base class names from class definition.



## Function: extract_decorators

**Parameters**: node
**Returns**: list[str]
**Description**: Extract decorator names from class definition.



## Function: extract_class_attributes

**Parameters**: node
**Returns**: list[str]
**Description**: Extract class-level attribute assignments.



## Function: extract_imports

**Parameters**: tree
**Returns**: tuple[list[str], list[str]]
**Description**: Extract all imports from a module.



## Function: extract_method_signatures

**Parameters**: node
**Returns**: list[dict[str, Any]]
**Description**: Extract method signatures with parameters.



## Function: build_inheritance_map

**Parameters**: tree
**Returns**: None
**Description**: Build map of class -> bases for MRO traversal.



## Function: has_healing_in_chain

**Parameters**: class_name, bases, visited
**Returns**: bool
**Description**: Check if class has healing capability through inheritance chain.



## Function: extract_methods

**Parameters**: class_node
**Returns**: list[str]
**Description**: Extract method names from class definition.



## Function: has_method

**Parameters**: class_node, method_name
**Returns**: bool
**Description**: Check if class has a specific method.



## Function: get_method

**Parameters**: class_node, method_name
**Returns**: ast.FunctionDef | None
**Description**: Get a specific method from a class, or None if not found.



## Function: detect_invocation_status

**Parameters**: class_node
**Returns**: str
**Description**: 
    Detect heal_repository invocation status for a CLASS.

    Returns:
        'Yes' - Class defines heal_repository with super().heal_repository() call
        'No (missing super)' - Class defines heal_repository but no super() call
        'Inherited' - Class does not define heal_repository (inherits from base)

    IMPORTANT: This checks the CLASS's heal_repository method specifically,
    not standalone module-level functions. This is the SSOT for invocation.
    



## Function: detect_has_tests

**Parameters**: class_node, source, class_name
**Returns**: bool
**Description**: Detect if class has ACTUAL test coverage (not inherited infrastructure).

    Checks:
    1. External test file exists (test_<ClassName>.py in tests/ subdirs)
    2. _run_self_tests method defined in the class
    3. SubatomicTestingMixin in direct inheritance
    4. pytest/unittest imports with test_ methods
    



## Function: _check_external_test_file

**Parameters**: agent_name
**Returns**: bool
**Description**: Check if an external test file exists for the given agent.



## Function: calculate_typing_coverage

**Parameters**: class_node
**Returns**: float
**Description**: Calculate percentage of methods with type annotations.

    Computes actual typing coverage by checking:
    - Parameter annotations on methods
    - Return type annotations on methods
    



## Function: calculate_docstring_coverage

**Parameters**: class_node
**Returns**: float
**Description**: Calculate percentage of methods with docstrings.

    Computes actual docstring coverage by checking for docstrings on methods.
    



## Function: check_proper_base

**Parameters**: class_node, layer
**Returns**: bool
**Description**: Phase 4: Verify agent has proper architectural inheritance.

    Proper base class means the agent follows the canonical architecture:
    - Inherits from SovereignBaseAgent (directly or transitively)
    - OR inherits from a layer-specific base agent
    - OR uses canonical mixins (HealerMixin, MCPHardenedMixin)

    This is a permissive check - we want to identify poorly structured agents,
    not penalize agents that follow alternative but valid patterns.
    



## Function: calculate_schema_strictness

**Parameters**: class_node, source
**Returns**: float
**Description**: Phase 4: schema Strictness - % with strict Pydantic/dataclass schema validation.

    Checks for:
    1. @dataclass decorator on the class
    2. Pydantic BaseModel inheritance
    3. Field definitions with type annotations
    4. Pydantic Field() or dataclass field() usage

    Returns 100% if agent uses Pydantic or dataclass, 0% otherwise.
    



## Function: get_base_name

**Parameters**: base_node
**Returns**: str
**Description**: Extract base class name from AST node.



## Function: detect_agent_metadata

**Parameters**: class_node
**Returns**: bool
**Description**: Phase 3: Detect if agent class has sufficient metadata (Finding #2).

    Checks for the presence of a class-level docstring.
    Agents with comprehensive docstrings enable better discovery and understanding.
    



## Function: detect_observability

**Parameters**: class_node, source
**Returns**: dict
**Description**: Detect observability indicators (logging, metrics, tracing).



## Function: calculate_cyclomatic_complexity

**Parameters**: class_node
**Returns**: int
**Description**: 
    Calculate total cyclomatic complexity for class.

    Complexity health % = 100 - (CC * 2)
    This penalizes complex classes to encourage refactoring.
    



## Function: count_loc

**Parameters**: source
**Returns**: int
**Description**: Count non-blank, non-comment lines.



## Function: is_sovereign_agent

**Parameters**: class_node, bases, rel_path
**Returns**: bool
**Description**: 
    STRICT SOVEREIGN AGENT TYPING — DELEGATES TO CLASSIFICATION KERNEL (SSOT).

    [REFACTORED 2026-02-08] All bespoke scoring logic removed.
    Now delegates to the zero-dependency classification kernel for the
    canonical "is this an agent?" decision.

    The kernel uses the same priority ordering as FileClassificationAgent:
    AST-based primary class detection, suffix matching, inheritance checks,
    with proper exclusions for MIXIN, PROTOCOL, STRATEGY, ORCHESTRATOR, etc.

    Args:
        class_node: AST ClassDef node (used for class name fallback only).
        bases: Set of base class names (unused — kernel does its own AST parse).
        rel_path: Relative path to the file.

    Returns:
        True if the file is classified as AGENT by the kernel.
    



## Function: is_agent_class

**Parameters**: class_node, bases, rel_path
**Returns**: bool
**Description**: 
    DEPRECATED — Delegates to classification kernel (SSOT).

    [REFACTORED 2026-02-08] All 200+ lines of bespoke scoring logic removed.
    Now delegates to is_sovereign_agent() which uses the kernel.

    Kept as a shim for any internal callers. All new code should use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    



## Function: get_docstring

**Parameters**: class_node
**Returns**: str
**Description**: Extract class docstring.



## Function: main



## Function: check_compliance_gate

**Parameters**: agents, parse_errors
**Returns**: int
**Description**: 
    Phase 3.3 Compliance Gate: Validate agent discovery for critical issues.
    Returns 0 if compliant, 1 if issues found.
    



## Function: __init__

**Parameters**: self


## Function: visit_If

**Parameters**: self, node


## Function: visit_For

**Parameters**: self, node


## Function: visit_While

**Parameters**: self, node


## Function: visit_ExceptHandler

**Parameters**: self, node


## Function: visit_With

**Parameters**: self, node


## Function: visit_BoolOp

**Parameters**: self, node


## Function: visit_comprehension

**Parameters**: self, node


## Function: get_territory_from_path

**Parameters**: path


## Function: refine_territory_by_ast

**Parameters**: path, territory


## Usage Examples

### Class Usage

```python
# Using _CCVisitor
_ccvisitor = _CCVisitor()
_ccvisitor.visit_If()
_ccvisitor.visit_For()
```

### Function Usage

```python
# Using should_exclude_path
result = should_exclude_path(path)
```

```python
# Using should_exclude_file
result = should_exclude_file(py_file)
```

```python
# Using validate_agent_count
result = validate_agent_count(agent_count, previous_count)
```



---
**Generated**: 2026-03-26T09:39:03.508124
**Type**: api_reference
**Quality**: comprehensive
