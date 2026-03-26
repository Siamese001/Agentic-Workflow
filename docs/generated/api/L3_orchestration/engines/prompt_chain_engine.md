# API Documentation: prompt_chain_engine

**Target Audience**: developers, api_users

# prompt_chain_engine API Documentation

**File**: `prompt_chain_engine.py`
**Classes**: 3
**Functions**: 3

## Classes

- **ChainStep**
- **ChainResult**
- **PromptChainEngine**

## Functions

- **__init__** -> None
- **add_step** -> PromptChainEngine
- **from_rg_orchestrator** -> PromptChainEngine


## Class: ChainStep

**Description**: A single step in the prompt chain.



## Class: ChainResult

**Description**: Result of running the full prompt chain.



## Class: PromptChainEngine

**Description**: Sequential prompt chain with per-step Gate nodes.

    Usage::

        chain = PromptChainEngine()
        chain.add_step("enrich",    enrich_fn,    gate=quality_gate)
        chain.add_step("optimise",  optimise_fn)
        chain.add_step("finalise",  finalise_fn,  gate=final_gate, fail_branch=fallback_fn)
        result = await chain.run(initial_context={"resume": raw_resume})

    Args:
        stop_on_gate_failure: If True, abort chain when a gate returns False and
                              no fail_branch is configured (default True).
    

### Methods

#### __init__
**Parameters**: self, stop_on_gate_failure
**Returns**: None

#### add_step
**Parameters**: self, name, fn, gate, fail_branch, description
**Returns**: PromptChainEngine
**Description**: Append a step to the chain.

        Args:
            name:        Unique step identifier.
            fn:          Async step function: (context) -> updated_context
            gate:        Optional async gate: (output) -> bool.  True = proceed.
            fail_branch: Async fallback used when gate returns False.
            description: Human-readable step description.

        Returns:
            self (fluent API).
        

#### from_rg_orchestrator
**Parameters**: cls, ctx
**Returns**: PromptChainEngine
**Description**: Factory that wires the standard apps_rg resume pipeline as a chain.

        Extracts the implicit chaining from ResumeOrchestratorEngine into
        explicit steps with quality gates.
        



## Function: __init__

**Parameters**: self, stop_on_gate_failure
**Returns**: None


## Function: add_step

**Parameters**: self, name, fn, gate, fail_branch, description
**Returns**: PromptChainEngine
**Description**: Append a step to the chain.

        Args:
            name:        Unique step identifier.
            fn:          Async step function: (context) -> updated_context
            gate:        Optional async gate: (output) -> bool.  True = proceed.
            fail_branch: Async fallback used when gate returns False.
            description: Human-readable step description.

        Returns:
            self (fluent API).
        



## Function: from_rg_orchestrator

**Parameters**: cls, ctx
**Returns**: PromptChainEngine
**Description**: Factory that wires the standard apps_rg resume pipeline as a chain.

        Extracts the implicit chaining from ResumeOrchestratorEngine into
        explicit steps with quality gates.
        



## Usage Examples

### Class Usage

```python
# Using ChainStep
chainstep = ChainStep()
```

```python
# Using ChainResult
chainresult = ChainResult()
```

```python
# Using PromptChainEngine
promptchainengine = PromptChainEngine()
promptchainengine.add_step()
promptchainengine.from_rg_orchestrator()
```

### Function Usage

```python
# Using __init__
result = __init__(stop_on_gate_failure)
```

```python
# Using add_step
result = add_step(name, fn)
```

```python
# Using from_rg_orchestrator
result = from_rg_orchestrator(cls, ctx)
```



---
**Generated**: 2026-03-26T09:39:04.194195
**Type**: api_reference
**Quality**: comprehensive
