# API Documentation: protocol

**Target Audience**: developers, api_users

# protocol API Documentation

**File**: `protocol.py`
**Classes**: 3
**Functions**: 6

## Classes

- **SubphaseResult**
- **AgentRunResult**
- **L2AgentProtocol** (inherits from Protocol)

## Functions

- **compute_pipeline_digest** -> str
- **emit_pipeline_digest** -> str
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult


## Class: SubphaseResult

**Description**: Result from a single subphase execution.



## Class: AgentRunResult

**Description**: Aggregated result for one agent across all four subphases.



## Class: L2AgentProtocol

**Description**: Protocol every pipeline adapter must satisfy.

**Inherits from**: Protocol

### Methods

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Read-only fast gate. Must never mutate filesystem.

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Deep read-only scan. Must never mutate filesystem.

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Confidence-gated mutations.

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Confidence-gated residual repair.



## Function: compute_pipeline_digest

**Parameters**: pipeline_order, adapter_keys, territory, heal, enable_llm, tamper_token
**Returns**: str
**Description**: Compute a stable SHA-256 digest from pipeline configuration.

    Args:
        pipeline_order: Ordered list of agent_id strings (AGENT_PIPELINE).
        adapter_keys:   Sorted list of keys present in adapters dict.
        territory:      The target territory string.
        heal:           ctx.heal flag.
        enable_llm:     ctx.enable_llm flag.
        tamper_token:   When SSOT_ORCH_NEGCTRL_TAMPER=1, contains "1"; else "0".

    Returns:
        64-char lowercase hex SHA-256 digest.
    



## Function: emit_pipeline_digest

**Parameters**: pipeline_order, adapter_keys, territory, heal, enable_llm
**Returns**: str
**Description**: Compute digest, print the canonical line, and return the digest string.

    Printed line format (exactly once per run):
        EXECUTE_SSOT_PIPELINE_DIGEST: <64-hex>

    When env var SSOT_ORCH_NEGCTRL_TAMPER=1, the tamper token is included
    in the payload so the digest differs from a clean run — used by the
    negative-control test.
    



## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Read-only fast gate. Must never mutate filesystem.



## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Deep read-only scan. Must never mutate filesystem.



## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Confidence-gated mutations.



## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult
**Description**: Confidence-gated residual repair.



## Usage Examples

### Class Usage

```python
# Using SubphaseResult
subphaseresult = SubphaseResult()
```

```python
# Using AgentRunResult
agentrunresult = AgentRunResult()
```

```python
# Using L2AgentProtocol
l2agentprotocol = L2AgentProtocol()
l2agentprotocol.pre_commit()
l2agentprotocol.validate()
```

### Function Usage

```python
# Using compute_pipeline_digest
result = compute_pipeline_digest(pipeline_order, adapter_keys)
```

```python
# Using emit_pipeline_digest
result = emit_pipeline_digest(pipeline_order, adapter_keys)
```

```python
# Using pre_commit
result = pre_commit(territory, ctx)
```



---
**Generated**: 2026-03-26T09:39:03.578787
**Type**: api_reference
**Quality**: comprehensive
