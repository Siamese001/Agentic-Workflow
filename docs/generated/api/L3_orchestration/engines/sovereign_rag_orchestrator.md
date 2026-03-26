# API Documentation: sovereign_rag_orchestrator

**Target Audience**: developers, api_users

# sovereign_rag_orchestrator API Documentation

**File**: `sovereign_rag_orchestrator.py`
**Classes**: 1
**Functions**: 14

## Classes

- **SovereignRagOrchestrator** (inherits from SovereignBaseAgent, IRagProvider)

## Functions

- **_get_active_configs**
- **_get_retrieval_anchor_types**
- **get_sovereign_rag_orchestrator** -> SovereignRagOrchestrator
- **__init__** -> None
- **_init_titanium_pipeline** -> None
- **_load_sovereign_config** -> None
- **_save_sovereign_config** -> None
- **get_health** -> dict[str, Any]
- **set_rerank_engine** -> None
- **get_config** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **_parse_critique** -> Any
- **_cosine** -> float


## Class: SovereignRagOrchestrator

**Description**: 
    Sovereign RAG Orchestrator - L3 Self-Optimizing RAG System.

    Adapts parameters based on performance with persistent configuration.
    Implements IRagProvider for unified RAG interface.
    

**Inherits from**: SovereignBaseAgent, IRagProvider

### Methods

#### __init__
**Parameters**: self, retriever, query_planner, guardrail, engine
**Returns**: None
**Description**: 
        Initialize sovereign RAG orchestrator.

        Args:
            retriever: Optional retriever instance
            query_planner: Optional query planner instance
            guardrail: Optional guardrail instance
            engine: Optional engine instance
        

#### _init_titanium_pipeline
**Parameters**: self
**Returns**: None
**Description**: Initialize Titanium RAG Pipeline for SOTA features with strict lazy-loading.

#### _load_sovereign_config
**Parameters**: self
**Returns**: None
**Description**: 
        L4: Persist the 'learned intelligence' of the system.

        Loads configuration from persistent storage or uses defaults.
        

#### _save_sovereign_config
**Parameters**: self
**Returns**: None
**Description**: 
        L4: Write learned parameters back to the Canon.

        Persists learned configuration to disk.
        

#### get_health
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get RAG system health status.

#### set_rerank_engine
**Parameters**: self, rerank_engine
**Returns**: None
**Description**: Inject a RerankEngine implementation.

        The engine must implement:
            async rerank(query: str, candidates: list[Any]) -> list[Any]

        When set, _llm_rerank() routes through this engine instead of
        falling back to score-sorted truncation.
        Fail-closed: any exception in reranking returns candidates[:top_k] unchanged.
        

#### get_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current configuration

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration/workflow_engines - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SovereignRagOrchestrator.

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
        



## Function: _get_active_configs



## Function: _get_retrieval_anchor_types



## Function: get_sovereign_rag_orchestrator

**Returns**: SovereignRagOrchestrator
**Description**: 
    Get singleton instance of Sovereign RAG Orchestrator.

    Returns:
        SovereignRagOrchestrator instance
    



## Function: __init__

**Parameters**: self, retriever, query_planner, guardrail, engine
**Returns**: None
**Description**: 
        Initialize sovereign RAG orchestrator.

        Args:
            retriever: Optional retriever instance
            query_planner: Optional query planner instance
            guardrail: Optional guardrail instance
            engine: Optional engine instance
        



## Function: _init_titanium_pipeline

**Parameters**: self
**Returns**: None
**Description**: Initialize Titanium RAG Pipeline for SOTA features with strict lazy-loading.



## Function: _load_sovereign_config

**Parameters**: self
**Returns**: None
**Description**: 
        L4: Persist the 'learned intelligence' of the system.

        Loads configuration from persistent storage or uses defaults.
        



## Function: _save_sovereign_config

**Parameters**: self
**Returns**: None
**Description**: 
        L4: Write learned parameters back to the Canon.

        Persists learned configuration to disk.
        



## Function: get_health

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get RAG system health status.



## Function: set_rerank_engine

**Parameters**: self, rerank_engine
**Returns**: None
**Description**: Inject a RerankEngine implementation.

        The engine must implement:
            async rerank(query: str, candidates: list[Any]) -> list[Any]

        When set, _llm_rerank() routes through this engine instead of
        falling back to score-sorted truncation.
        Fail-closed: any exception in reranking returns candidates[:top_k] unchanged.
        



## Function: get_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current configuration



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration/workflow_engines - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SovereignRagOrchestrator.

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
        



## Function: _parse_critique

**Parameters**: raw
**Returns**: Any
**Description**: Parse critique.



## Function: _cosine

**Parameters**: a, b
**Returns**: float


## Usage Examples

### Class Usage

```python
# Using SovereignRagOrchestrator
sovereignragorchestrator = SovereignRagOrchestrator()
sovereignragorchestrator.get_health()
sovereignragorchestrator.set_rerank_engine()
```

### Function Usage

```python
# Using _get_active_configs
result = _get_active_configs()
```

```python
# Using _get_retrieval_anchor_types
result = _get_retrieval_anchor_types()
```

```python
# Using get_sovereign_rag_orchestrator
result = get_sovereign_rag_orchestrator()
```



---
**Generated**: 2026-03-26T09:39:04.228634
**Type**: api_reference
**Quality**: comprehensive
