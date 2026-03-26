# API Documentation: advisors

**Target Audience**: developers, api_users

# advisors API Documentation

**File**: `advisors.py`
**Classes**: 0
**Functions**: 4


## Functions

- **risk_averse_advisor** -> AdvisorProposal
- **throughput_advisor** -> AdvisorProposal
- **get_available_advisors** -> list[str]
- **run_advisor** -> AdvisorProposal


## Function: risk_averse_advisor

**Parameters**: task
**Returns**: AdvisorProposal
**Description**: Risk-averse advisor that prioritizes safety.

    Args:
        task: Task dictionary with task details

    Returns:
        AdvisorProposal with risk-averse recommendation
    



## Function: throughput_advisor

**Parameters**: task
**Returns**: AdvisorProposal
**Description**: Throughput advisor that prioritizes speed and efficiency.

    Args:
        task: Task dictionary with task details

    Returns:
        AdvisorProposal with throughput-focused recommendation
    



## Function: get_available_advisors

**Returns**: list[str]
**Description**: Get list of available advisor IDs.

    Returns:
        List of advisor IDs in deterministic order
    



## Function: run_advisor

**Parameters**: advisor_id, task
**Returns**: AdvisorProposal
**Description**: Run a single advisor and return its proposal.

    Args:
        advisor_id: ID of advisor to run
        task: Task dictionary

    Returns:
        AdvisorProposal from the advisor

    Raises:
        ValueError: If advisor_id is not recognized
    



## Usage Examples

### Function Usage

```python
# Using risk_averse_advisor
result = risk_averse_advisor(task)
```

```python
# Using throughput_advisor
result = throughput_advisor(task)
```

```python
# Using get_available_advisors
result = get_available_advisors()
```



---
**Generated**: 2026-03-26T09:39:04.078791
**Type**: api_reference
**Quality**: comprehensive
