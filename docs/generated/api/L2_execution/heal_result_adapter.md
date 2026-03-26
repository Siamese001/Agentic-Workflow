# API Documentation: heal_result_adapter

**Target Audience**: developers, api_users

# heal_result_adapter API Documentation

**File**: `heal_result_adapter.py`
**Classes**: 0
**Functions**: 7


## Functions

- **adapt_heal_result** -> HealCheckResult
- **_extract_status** -> HealStatus
- **_to_relative** -> str
- **_extract_changes_made** -> list[str]
- **_determine_llm_escalation** -> bool
- **_build_escalation_hint** -> str
- **_add_paths** -> None


## Function: adapt_heal_result

**Parameters**: agent_name, raw_result, repo_root
**Returns**: HealCheckResult
**Description**: Adapt unstructured agent result to canonical HealCheckResult.

    Args:
        agent_name: Name of the agent that produced the result.
        raw_result: Raw output from agent.heal_repository() — dict, str, or None.
        repo_root: Repository root used to convert absolute paths to relative.
                   When None the current working directory is used as fallback.

    Returns:
        Canonical HealCheckResult with contract-compliant field values.

    Raises:
        ValueError: Only if agent_name is empty (programming error).
    



## Function: _extract_status

**Parameters**: d
**Returns**: HealStatus
**Description**: Map common result dict patterns to HealStatus.



## Function: _to_relative

**Parameters**: path_str, root
**Returns**: str
**Description**: Convert path_str to repo-relative POSIX string if it looks absolute.

    Uses the same pattern as HealCheckResult.__post_init__ so the sanitised
    string always passes the contract validator.
    



## Function: _extract_changes_made

**Parameters**: d, agent_name, root
**Returns**: list[str]
**Description**: Extract and sanitise list of changes from result dict.



## Function: _determine_llm_escalation

**Parameters**: d, status, changes_made
**Returns**: bool
**Description**: Return True iff LLM escalation is required.



## Function: _build_escalation_hint

**Parameters**: d, agent_name, status
**Returns**: str
**Description**: Build space-delimited structured hint string for tier routing.



## Function: _add_paths

**Parameters**: value
**Returns**: None


## Usage Examples

### Function Usage

```python
# Using adapt_heal_result
result = adapt_heal_result(agent_name, raw_result)
```

```python
# Using _extract_status
result = _extract_status(d)
```

```python
# Using _to_relative
result = _to_relative(path_str, root)
```



---
**Generated**: 2026-03-26T09:39:03.576718
**Type**: api_reference
**Quality**: comprehensive
