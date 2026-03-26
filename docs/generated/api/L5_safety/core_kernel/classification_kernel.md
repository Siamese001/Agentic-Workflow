# API Documentation: classification_kernel

**Target Audience**: developers, api_users

# classification_kernel API Documentation

**File**: `classification_kernel.py`
**Classes**: 0
**Functions**: 11


## Functions

- **get_classification_conflicts** -> list[dict]
- **clear_classification_conflicts** -> None
- **classify_file_standalone** -> FileType
- **_classify_impl** -> FileType
- **is_agent_file** -> bool
- **is_agent_or_orchestrator** -> bool
- **classify_execution_mode** -> tuple[str, list[str]]
- **clear_classification_cache** -> None
- **classification_cache_info**
- **classification_cache_context**
- **_base_names** -> list[str]


## Function: get_classification_conflicts

**Returns**: list[dict]
**Description**: Return list of dual-tag/ambiguity conflicts detected during classification.



## Function: clear_classification_conflicts

**Returns**: None
**Description**: Clear the conflict tracking list.



## Function: classify_file_standalone

**Parameters**: path
**Returns**: FileType
**Description**: 
    Classify a Python file's architectural role using AST analysis.

    This is the CANONICAL, zero-dependency classification function.
    It mirrors the priority ordering of FileClassificationAgent.classify_file()
    but requires NO internal repo imports.

    Results are cached (LRU, maxsize=1024) keyed on resolved absolute path
    for high performance during batch scans.

    Priority Queue (first match wins):
        0. IGNORE  — Critical infrastructure files (__init__.py, conftest.py, etc.)
        1. CLASS   — Files in base_agents/ directory (foundational classes)
        2. STUB    — Files containing NOT_AN_AGENT marker
        3. TEST    — Files in tests/ or starting with test_
        4. SCRIPT  — No-class files with __main__ guard
        5. UTILITY — No-class files without __main__
        6. EXCEPTION — Primary class inherits from Exception/Error
        7. MIXIN   — Primary class name ends with 'Mixin'
        8. PROTOCOL — Primary class inherits from Protocol or file starts with I
        9. ORCHESTRATOR — Primary class name contains Orchestrator/Coordinator/Pipeline
       10. AGENT   — Primary class name ends with 'Agent' or inherits from *Agent
       11. STRATEGY — Primary class name ends with 'Strategy'
       12. ADAPTER  — Primary class name ends with Adapter/Wrapper/Bridge
       13. SERVICE  — Singleton pattern (_instance attribute)
       14. CONFIG   — Name/path contains config/settings/blueprint
       15. VALIDATOR — Name/path contains validator
       16. FACTORY  — Primary class name ends with 'Factory'
       17. TYPES   — TypedDict/Protocol/Enum/dataclass heavy files
       18. CLASS   — Fallback for files with classes
       19. UTILITY — Fallback for files without classes

    Args:
        path: Absolute or relative Path to a .py file.

    Returns:
        A FileType string literal.
    



## Function: _classify_impl

**Parameters**: path
**Returns**: FileType
**Description**: Cached implementation of classify_file_standalone.



## Function: is_agent_file

**Parameters**: path
**Returns**: bool
**Description**: 
    SSOT predicate: Is this file classified as AGENT?

    This is the ONE function all consumers should call to answer
    "is this an agent?" — replacing all bespoke _is_agent_class() methods.
    Inherits LRU cache from classify_file_standalone.

    Args:
        path: Path to a .py file.

    Returns:
        True if classify_file_standalone(path) == "AGENT".
    



## Function: is_agent_or_orchestrator

**Parameters**: path
**Returns**: bool
**Description**: 
    SSOT predicate: Is this file an AGENT or ORCHESTRATOR?

    Used by agent discovery scripts that treat orchestrators as a
    specialized form of agent for manifest purposes.
    Inherits LRU cache from classify_file_standalone.

    Args:
        path: Path to a .py file.

    Returns:
        True if classification is AGENT or ORCHESTRATOR.
    



## Function: classify_execution_mode

**Parameters**: path
**Returns**: tuple[str, list[str]]
**Description**: Detect whether a file requires LLM reasoning or is purely deterministic.

    Pure AST analysis — zero I/O side effects beyond reading the file.
    Only reads content once; safe to call on any .py file.

    Reasoning signals detected:
        weighted_scoring      — sum(score * weight ...) multi-axis accumulator
        prompt_construction   — FunctionDef with 'prompt' in name
        plan_only_fallback    — AST Constant 'plan_only' present (deferred-execution marker)
        meta_learning         — calls to recall_*/store_*/ml_enhanced* methods
        multi_agent_orch      — ≥2 distinct *Agent class instantiations
        async_external_call   — AsyncFunctionDef present (implies external system wait)

    Returns:
        tuple of (ExecutionMode, list[triggered_signal_names])
        ExecutionMode is "REASONING" when any signal fires, else "DETERMINISTIC".
    



## Function: clear_classification_cache

**Returns**: None
**Description**: Clear the LRU cache. Useful in tests or after file mutations.



## Function: classification_cache_info

**Description**: Return cache statistics (hits, misses, maxsize, currsize).



## Function: classification_cache_context

**Description**: Context manager that clears the cache on entry and exit.

    Useful for batch operations (Discovery, CI scans) where files won't
    change mid-operation, ensuring no stale state carries into the next
    operation.

    Usage::

        with classification_cache_context():
            # Run heavy discovery / scan here
            ...
    



## Function: _base_names

**Parameters**: node
**Returns**: list[str]


## Usage Examples

### Function Usage

```python
# Using get_classification_conflicts
result = get_classification_conflicts()
```

```python
# Using clear_classification_conflicts
result = clear_classification_conflicts()
```

```python
# Using classify_file_standalone
result = classify_file_standalone(path)
```



---
**Generated**: 2026-03-26T09:39:04.752205
**Type**: api_reference
**Quality**: comprehensive
