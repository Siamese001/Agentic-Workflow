# API Documentation: SubAtomicRegistryAgent

**Target Audience**: developers, api_users

# SubAtomicRegistryAgent API Documentation

**File**: `SubAtomicRegistryAgent.py`
**Classes**: 2
**Functions**: 22

## Classes

- **SubAtomicRegistryAgent** (inherits from SovereignBaseAgent)
- **CodeValidatorAgentWrapper**

## Functions

- **_get_RedisSovereignAgent**
- **_get_UnifiedAgent_mapping** -> dict[str, type]
- **_get_phase3_manager_enforcer_mapping** -> dict[str, type]
- **_get_phase4_detector_healer_router_executor_mapping** -> dict[str, type]
- **_get_phase2_validator_mapping** -> dict[str, type]
- **get_UnifiedAgent_class** -> type
- **is_legacy_agent** -> bool
- **__init__** -> None
- **_run_self_tests** -> bool
- **extract_methods** -> list[dict]
- **rebuild_registry** -> Any
- **find_method** -> list[dict]
- **find_and_invoke** -> Any
- **invoke_method** -> Any
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **adg_discover_agents** -> list[str]
- **timeout**
- **__init__**
- **validate_repository**
- **heal_repository**
- **wrapper**


## Class: SubAtomicRegistryAgent

**Description**: 

    Sovereign method registry — live, hybrid-indexed, eternal.

    Now with Redis sovereign caching for instant method discovery.

    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L4 compliance.

#### extract_methods
**Parameters**: self
**Returns**: list[dict]
**Description**: Deep crawl of all .py files to find callables

#### rebuild_registry
**Parameters**: self
**Returns**: Any
**Description**: Rebuild — full method index + Redis cache warm

#### find_method
**Parameters**: self, Task, top_k
**Returns**: list[dict]
**Description**: Cache-first method search — Redis then local index keyword match

#### find_and_invoke
**Parameters**: self, task_description
**Returns**: Any
**Description**: The ultimate sovereign loop: Find it, then do it.

#### invoke_method
**Parameters**: self, method_meta
**Returns**: Any
**Description**: Dynamically invoke a method by metadata

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L4 state agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 

        Heal violations detected by SubAtomicRegistryAgent.



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

        

#### adg_discover_agents
**Parameters**: self, base_class
**Returns**: list[str]
**Description**: R4: O(1) ADG-backed agent discovery by inheritance graph.

        Replaces O(n) filesystem scan in extract_methods for base-class queries.
        Speedup: 100-1000x over full extract_methods() scan.

        Returns list of ADG module names for all known subclasses.
        



## Class: CodeValidatorAgentWrapper

**Description**: Wrapper that delegates to CodeValidatorAgent via subprocess.

### Methods

#### __init__
**Parameters**: self, project_root

#### validate_repository
**Parameters**: self
**Description**: Delegate validation to subprocess.

#### heal_repository
**Parameters**: self, directory
**Description**: Delegate healing to subprocess.



## Function: _get_RedisSovereignAgent

**Description**: Lazy load RedisSovereignAgent to avoid upward import.



## Function: _get_UnifiedAgent_mapping

**Returns**: dict[str, type]
**Description**: 

    Lazy-load unified agent mapping to avoid circular imports.



    Returns:

        Dictionary mapping legacy agent IDs to unified agent classes.

    



## Function: _get_phase3_manager_enforcer_mapping

**Returns**: dict[str, type]
**Description**: 

    Phase 3 Manager & Enforcer Consolidation: Hard Migration mappings.



    Returns:

        Dictionary mapping legacy manager/enforcer names to unified classes.

    



## Function: _get_phase4_detector_healer_router_executor_mapping

**Returns**: dict[str, type]
**Description**: 

    Phase 4 Detector/Healer/router/Executor Consolidation: Hard Migration mappings.



    Returns:

        Dictionary mapping legacy detector/healer/router/executor names to unified classes.

    



## Function: _get_phase2_validator_mapping

**Returns**: dict[str, type]
**Description**: 

    Phase 2 Validator Consolidation: Maps legacy validators to unified agents.



    Returns:

        Dictionary mapping legacy validator names to unified validator classes.

    



## Function: get_UnifiedAgent_class

**Parameters**: agent_id
**Returns**: type
**Description**: 

    Returns the unified agent class for a given legacy agent ID.

    Ensures backward compatibility for dynamic agent instantiation.



    Args:

        agent_id: Legacy agent identifier (e.g., "BareExceptValidator")



    Returns:

        Unified agent class that handles the legacy agent's functionality



    Raises:

        ValueError: If agent_id is not found in the mapping

    



## Function: is_legacy_agent

**Parameters**: agent_id
**Returns**: bool
**Description**: Check if an agent ID refers to a deprecated legacy agent.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L4 compliance.



## Function: extract_methods

**Parameters**: self
**Returns**: list[dict]
**Description**: Deep crawl of all .py files to find callables



## Function: rebuild_registry

**Parameters**: self
**Returns**: Any
**Description**: Rebuild — full method index + Redis cache warm



## Function: find_method

**Parameters**: self, Task, top_k
**Returns**: list[dict]
**Description**: Cache-first method search — Redis then local index keyword match



## Function: find_and_invoke

**Parameters**: self, task_description
**Returns**: Any
**Description**: The ultimate sovereign loop: Find it, then do it.



## Function: invoke_method

**Parameters**: self, method_meta
**Returns**: Any
**Description**: Dynamically invoke a method by metadata



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L4 state agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 

        Heal violations detected by SubAtomicRegistryAgent.



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

        



## Function: adg_discover_agents

**Parameters**: self, base_class
**Returns**: list[str]
**Description**: R4: O(1) ADG-backed agent discovery by inheritance graph.

        Replaces O(n) filesystem scan in extract_methods for base-class queries.
        Speedup: 100-1000x over full extract_methods() scan.

        Returns list of ADG module names for all known subclasses.
        



## Function: timeout

**Parameters**: seconds
**Description**: Stub timeout decorator.



## Function: __init__

**Parameters**: self, project_root


## Function: validate_repository

**Parameters**: self
**Description**: Delegate validation to subprocess.



## Function: heal_repository

**Parameters**: self, directory
**Description**: Delegate healing to subprocess.



## Function: wrapper

**Parameters**: f


## Usage Examples

### Class Usage

```python
# Using SubAtomicRegistryAgent
subatomicregistryagent = SubAtomicRegistryAgent()
subatomicregistryagent.extract_methods()
subatomicregistryagent.rebuild_registry()
```

```python
# Using CodeValidatorAgentWrapper
codevalidatoragentwrapper = CodeValidatorAgentWrapper()
codevalidatoragentwrapper.validate_repository()
codevalidatoragentwrapper.heal_repository()
```

### Function Usage

```python
# Using _get_RedisSovereignAgent
result = _get_RedisSovereignAgent()
```

```python
# Using _get_UnifiedAgent_mapping
result = _get_UnifiedAgent_mapping()
```

```python
# Using _get_phase3_manager_enforcer_mapping
result = _get_phase3_manager_enforcer_mapping()
```



---
**Generated**: 2026-03-26T09:39:03.881099
**Type**: api_reference
**Quality**: comprehensive
