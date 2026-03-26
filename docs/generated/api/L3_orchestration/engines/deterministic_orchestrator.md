# API Documentation: deterministic_orchestrator

**Target Audience**: developers, api_users

# deterministic_orchestrator API Documentation

**File**: `deterministic_orchestrator.py`
**Classes**: 3
**Functions**: 12

## Classes

- **RouteMode** (inherits from Enum)
- **OrchestrationConfig**
- **DeterministicOrchestrator**

## Functions

- **canonical_json** -> str
- **compute_plan_hash** -> str
- **compute_determinism_digest** -> str
- **__init__**
- **_compute_agent_registry_hash** -> str
- **_compute_tool_key_hash** -> str
- **orchestrate** -> OrchestrationResult
- **_orchestrate_path_b** -> OrchestrationResult
- **_orchestrate_path_c** -> OrchestrationResult
- **_orchestrate_path_d** -> OrchestrationResult
- **_create_deterministic_plan** -> dict[str, Any]
- **_detect_tool_execution_intent** -> bool


## Class: RouteMode

**Description**: Route modes for L3 orchestration.

**Inherits from**: Enum



## Class: OrchestrationConfig

**Description**: Configuration for deterministic orchestration.



## Class: DeterministicOrchestrator

**Description**: 
    Unified deterministic L3 orchestration kernel.

    Implements route_mode-aware orchestration with sequential handshake.
    No direct provider SDK imports, no embedding instantiation, no L4 mutation.
    

### Methods

#### __init__
**Parameters**: self, project_root, run_id

#### _compute_agent_registry_hash
**Parameters**: self
**Returns**: str
**Description**: Compute hash of agent execution profile registry.

#### _compute_tool_key_hash
**Parameters**: self, allowed_tools
**Returns**: str
**Description**: Compute hash of sorted tool keys.

#### orchestrate
**Parameters**: self, governed_payload, route_mode, trace_id, policy_hash, allowed_tools
**Returns**: OrchestrationResult
**Description**: 
        Main orchestration entry point.

        Args:
            governed_payload: The assembled payload from L0
            route_mode: Route mode (B/C/D)
            trace_id: Unique trace identifier
            policy_hash: Policy validation hash
            allowed_tools: Tuple of allowed tool names

        Returns:
            OrchestrationResult with deterministic outcome
        

#### _orchestrate_path_b
**Parameters**: self, config
**Returns**: OrchestrationResult
**Description**: 
        Path B: Policy Check First

        1. Require L5 pre-clear
        2. Handshake: INIT → PRECLEAR_REQUESTED → CERTIFIED
        3. No seal before CERTIFIED
        4. Only after certification may plan be sealed
        

#### _orchestrate_path_c
**Parameters**: self, config
**Returns**: OrchestrationResult
**Description**: 
        Path C: Execute Script Directly

        1. If tool execution intent detected, require L5 certification first
        2. Same handshake enforcement as Path B
        3. Seal only after CERTIFIED
        

#### _orchestrate_path_d
**Parameters**: self, config
**Returns**: OrchestrationResult
**Description**: 
        Path D: Human Review First

        1. DO NOT dispatch to L2
        2. Emit HumanDecisionArtifact draft
        3. Stop
        4. Any MODIFY_DIFF must reference original_plan_hash and re-enter L5
        

#### _create_deterministic_plan
**Parameters**: self, config
**Returns**: dict[str, Any]
**Description**: 
        Create deterministic plan from governed payload.

        Stable sort, canonical structure, no heuristic logic.
        

#### _detect_tool_execution_intent
**Parameters**: self, payload
**Returns**: bool
**Description**: 
        Detect if payload contains tool execution intent.

        Deterministic detection - no ML or fuzzy matching.
        



## Function: canonical_json

**Parameters**: data
**Returns**: str
**Description**: 
    Convert dictionary to canonical JSON string.

    Alphabetical key sort, UTF-8, no whitespace variance.
    



## Function: compute_plan_hash

**Parameters**: plan
**Returns**: str
**Description**: 
    Compute SHA256 hash of canonical plan JSON.
    



## Function: compute_determinism_digest

**Parameters**: plan_hash, agent_registry_hash, tool_key_hash, handshake_sequence_hash
**Returns**: str
**Description**: 
    Compute W5-DETERMINISM-DIGEST.

    Exactly one per run - printed to stdout.
    When W5_NEGCTRL_TAMPER=1 the sort order is reversed to prove tamper detection.
    



## Function: __init__

**Parameters**: self, project_root, run_id


## Function: _compute_agent_registry_hash

**Parameters**: self
**Returns**: str
**Description**: Compute hash of agent execution profile registry.



## Function: _compute_tool_key_hash

**Parameters**: self, allowed_tools
**Returns**: str
**Description**: Compute hash of sorted tool keys.



## Function: orchestrate

**Parameters**: self, governed_payload, route_mode, trace_id, policy_hash, allowed_tools
**Returns**: OrchestrationResult
**Description**: 
        Main orchestration entry point.

        Args:
            governed_payload: The assembled payload from L0
            route_mode: Route mode (B/C/D)
            trace_id: Unique trace identifier
            policy_hash: Policy validation hash
            allowed_tools: Tuple of allowed tool names

        Returns:
            OrchestrationResult with deterministic outcome
        



## Function: _orchestrate_path_b

**Parameters**: self, config
**Returns**: OrchestrationResult
**Description**: 
        Path B: Policy Check First

        1. Require L5 pre-clear
        2. Handshake: INIT → PRECLEAR_REQUESTED → CERTIFIED
        3. No seal before CERTIFIED
        4. Only after certification may plan be sealed
        



## Function: _orchestrate_path_c

**Parameters**: self, config
**Returns**: OrchestrationResult
**Description**: 
        Path C: Execute Script Directly

        1. If tool execution intent detected, require L5 certification first
        2. Same handshake enforcement as Path B
        3. Seal only after CERTIFIED
        



## Function: _orchestrate_path_d

**Parameters**: self, config
**Returns**: OrchestrationResult
**Description**: 
        Path D: Human Review First

        1. DO NOT dispatch to L2
        2. Emit HumanDecisionArtifact draft
        3. Stop
        4. Any MODIFY_DIFF must reference original_plan_hash and re-enter L5
        



## Function: _create_deterministic_plan

**Parameters**: self, config
**Returns**: dict[str, Any]
**Description**: 
        Create deterministic plan from governed payload.

        Stable sort, canonical structure, no heuristic logic.
        



## Function: _detect_tool_execution_intent

**Parameters**: self, payload
**Returns**: bool
**Description**: 
        Detect if payload contains tool execution intent.

        Deterministic detection - no ML or fuzzy matching.
        



## Usage Examples

### Class Usage

```python
# Using RouteMode
routemode = RouteMode()
```

```python
# Using OrchestrationConfig
orchestrationconfig = OrchestrationConfig()
```

```python
# Using DeterministicOrchestrator
deterministicorchestrator = DeterministicOrchestrator()
deterministicorchestrator.orchestrate()
```

### Function Usage

```python
# Using canonical_json
result = canonical_json(data)
```

```python
# Using compute_plan_hash
result = compute_plan_hash(plan)
```

```python
# Using compute_determinism_digest
result = compute_determinism_digest(plan_hash, agent_registry_hash)
```



---
**Generated**: 2026-03-26T09:39:04.164965
**Type**: api_reference
**Quality**: comprehensive
