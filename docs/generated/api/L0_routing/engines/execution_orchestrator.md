# API Documentation: execution_orchestrator

**Target Audience**: developers, api_users

# execution_orchestrator API Documentation

**File**: `execution_orchestrator.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ExecutionOrchestrator**

## Functions

- **_get_routing_gateway**
- **__init__**
- **_delegate_to_l3** -> dict[str, Any]
- **execute** -> dict[str, Any]
- **plan_execution_with_impact_analysis** -> dict[str, Any]


## Class: ExecutionOrchestrator

**Description**: 
    Deterministic execution orchestrator binding all layers.

    Uses injected seams only, no direct dependencies.
    No wall-clock usage, no side effects beyond injected functions.
    

### Methods

#### __init__
**Parameters**: self, assembler, path_router, d0_engine, risk_gate, cid_registry, reentry_loop, vigilance_dispatcher, meta_bus, l3_orchestrator
**Description**: 
        Initialize orchestrator with injected dependencies.

        Args:
            assembler: Assembly Stage instance
            path_router: PathRouter instance
            d0_engine: D0InjectionEngine instance
            risk_gate: ConfCalibRiskGate instance
            cid_registry: CIDRegistry instance
            reentry_loop: ReEntryLoop instance
            vigilance_dispatcher: VigilanceDispatcher instance
            meta_bus: MetaLearningBus instance
            l3_orchestrator: Optional L3 orchestrator for Paths B/C/D delegation.
                Must implement orchestrate(payload, route_mode, trace_id, ...) or
                a compatible synchronous interface.  When None, Paths B/C/D return
                without delegation (backwards-compatible default).
        

#### _delegate_to_l3
**Parameters**: self, path, payload, cycle, risk
**Returns**: dict[str, Any]
**Description**: 
        Delegate execution to L3 orchestrator for Paths B/C/D.

        Calls l3_orchestrator.orchestrate() when available.  Any exception is
        caught and returned as an error key so L0 routing remains unaffected.

        Returns:
            Result dict including orchestration sub-result or error metadata.
        

#### execute
**Parameters**: self, intent_input
**Returns**: dict[str, Any]
**Description**: 
        Execute intent through all layers deterministically.

        Flow (no hidden state):
        1) Assemble → payload
        2) Route → path
        3) Render D0
        4) Evaluate risk
        5) Start ExecutionCycle
        6) Handle re-entry if risk disallowed
        7) Delegate to L3 for Paths B/C/D (when l3_orchestrator injected)
        8) Return structured result dict

        Args:
            intent_input: Input intent dictionary

        Returns:
            Structured result dict with path, risk, cycle, and state
        

#### plan_execution_with_impact_analysis
**Parameters**: self, changed_files
**Returns**: dict[str, Any]
**Description**: R6: Plan execution order based on ADG blast radius.

        Uses pre-built reverse dependency index instead of full codebase scan.
        Speedup: 50-500x over full scan.
        



## Function: _get_routing_gateway



## Function: __init__

**Parameters**: self, assembler, path_router, d0_engine, risk_gate, cid_registry, reentry_loop, vigilance_dispatcher, meta_bus, l3_orchestrator
**Description**: 
        Initialize orchestrator with injected dependencies.

        Args:
            assembler: Assembly Stage instance
            path_router: PathRouter instance
            d0_engine: D0InjectionEngine instance
            risk_gate: ConfCalibRiskGate instance
            cid_registry: CIDRegistry instance
            reentry_loop: ReEntryLoop instance
            vigilance_dispatcher: VigilanceDispatcher instance
            meta_bus: MetaLearningBus instance
            l3_orchestrator: Optional L3 orchestrator for Paths B/C/D delegation.
                Must implement orchestrate(payload, route_mode, trace_id, ...) or
                a compatible synchronous interface.  When None, Paths B/C/D return
                without delegation (backwards-compatible default).
        



## Function: _delegate_to_l3

**Parameters**: self, path, payload, cycle, risk
**Returns**: dict[str, Any]
**Description**: 
        Delegate execution to L3 orchestrator for Paths B/C/D.

        Calls l3_orchestrator.orchestrate() when available.  Any exception is
        caught and returned as an error key so L0 routing remains unaffected.

        Returns:
            Result dict including orchestration sub-result or error metadata.
        



## Function: execute

**Parameters**: self, intent_input
**Returns**: dict[str, Any]
**Description**: 
        Execute intent through all layers deterministically.

        Flow (no hidden state):
        1) Assemble → payload
        2) Route → path
        3) Render D0
        4) Evaluate risk
        5) Start ExecutionCycle
        6) Handle re-entry if risk disallowed
        7) Delegate to L3 for Paths B/C/D (when l3_orchestrator injected)
        8) Return structured result dict

        Args:
            intent_input: Input intent dictionary

        Returns:
            Structured result dict with path, risk, cycle, and state
        



## Function: plan_execution_with_impact_analysis

**Parameters**: self, changed_files
**Returns**: dict[str, Any]
**Description**: R6: Plan execution order based on ADG blast radius.

        Uses pre-built reverse dependency index instead of full codebase scan.
        Speedup: 50-500x over full scan.
        



## Usage Examples

### Class Usage

```python
# Using ExecutionOrchestrator
executionorchestrator = ExecutionOrchestrator()
executionorchestrator.execute()
executionorchestrator.plan_execution_with_impact_analysis()
```

### Function Usage

```python
# Using _get_routing_gateway
result = _get_routing_gateway()
```

```python
# Using __init__
result = __init__(assembler, path_router)
```

```python
# Using _delegate_to_l3
result = _delegate_to_l3(path, payload)
```



---
**Generated**: 2026-03-26T09:39:02.656608
**Type**: api_reference
**Quality**: comprehensive
