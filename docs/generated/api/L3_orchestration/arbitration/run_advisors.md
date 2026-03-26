# API Documentation: run_advisors

**Target Audience**: developers, api_users

# run_advisors API Documentation

**File**: `run_advisors.py`
**Classes**: 0
**Functions**: 3


## Functions

- **run_advisors** -> list[AdvisorProposal]
- **_validate_proposal** -> None
- **run_all_advisors** -> list[AdvisorProposal]


## Function: run_advisors

**Parameters**: task_dict, advisor_ids
**Returns**: list[AdvisorProposal]
**Description**: Run multiple advisors and return their proposals.

    Args:
        task_dict: Task description dictionary
        advisor_ids: List of advisor IDs to run

    Returns:
        List of AdvisorProposal objects

    Raises:
        ValueError: If any advisor_id is invalid
    



## Function: _validate_proposal

**Parameters**: proposal
**Returns**: None
**Description**: Validate proposal meets contract requirements.

    Args:
        proposal: Proposal to validate

    Raises:
        ValueError: If proposal violates contract
    



## Function: run_all_advisors

**Parameters**: task_dict
**Returns**: list[AdvisorProposal]
**Description**: Run all available advisors.

    Args:
        task_dict: Task description dictionary

    Returns:
        List of AdvisorProposal objects from all advisors
    



## Usage Examples

### Function Usage

```python
# Using run_advisors
result = run_advisors(task_dict, advisor_ids)
```

```python
# Using _validate_proposal
result = _validate_proposal(proposal)
```

```python
# Using run_all_advisors
result = run_all_advisors(task_dict)
```



---
**Generated**: 2026-03-26T09:39:04.085194
**Type**: api_reference
**Quality**: comprehensive
