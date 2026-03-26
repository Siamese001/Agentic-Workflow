# API Documentation: readonly_retrieval_orchestrator

**Target Audience**: developers, api_users

# readonly_retrieval_orchestrator API Documentation

**File**: `readonly_retrieval_orchestrator.py`
**Classes**: 0
**Functions**: 1


## Functions

- **retrieve_with_readonly_guarantee** -> tuple[list[AnchoredResult], RetrievalBoundarySnapshot]


## Function: retrieve_with_readonly_guarantee

**Parameters**: mission_id, query, top_k, domain, active_config_hashes, created_at_utc
**Returns**: tuple[list[AnchoredResult], RetrievalBoundarySnapshot]
**Description**: 
    Execute a retrieval inside a read-only scope and return results + snapshot.

    Parameters
    ----------
    mission_id           : str  — mission identifier
    query                : str  — retrieval query text
    top_k                : int  — maximum results to return
    domain               : str  — retrieval domain
    active_config_hashes : dict — L4 active config hashes (policy/routing/model/budget)
    created_at_utc       : str  — stable UTC timestamp for the snapshot
    _query_fn            : callable | None
        Injected query function (for testing / real L4 backend).
        Signature: (query: str, top_k: int, domain: str) -> list[AnchoredResult]
        If None, returns an empty result list (safe default for wiring tests).

    Returns
    -------
    (results, snapshot)
        results  : list[AnchoredResult]
        snapshot : RetrievalBoundarySnapshot  (non-mutating, stable hash)
    



## Usage Examples

### Function Usage

```python
# Using retrieve_with_readonly_guarantee
result = retrieve_with_readonly_guarantee(mission_id, query)
```



---
**Generated**: 2026-03-26T09:39:04.540719
**Type**: api_reference
**Quality**: comprehensive
