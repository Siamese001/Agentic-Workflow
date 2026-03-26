# API Documentation: HumanReviewAdapter

**Target Audience**: developers, api_users

# HumanReviewAdapter API Documentation

**File**: `HumanReviewAdapter.py`
**Classes**: 3
**Functions**: 12

## Classes

- **ReviewStatus** (inherits from Enum)
- **ReviewRequest**
- **HumanReviewAdapter**

## Functions

- **to_dict** -> dict[str, Any]
- **__init__**
- **submit_for_review** -> str
- **check_status** -> ReviewStatus | None
- **get_pending_reviews** -> list[ReviewRequest]
- **is_available** -> bool
- **get_queue_depth** -> int
- **approve** -> bool
- **reject** -> bool
- **clear_expired** -> int
- **_expire_if_stale** -> None
- **_expire_stale_requests** -> None


## Class: ReviewStatus

**Description**: Status of a human review request.

**Inherits from**: Enum



## Class: ReviewRequest

**Description**: A request for human review.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Class: HumanReviewAdapter

**Description**: 
    Adapter for human-in-the-loop review of proposed code changes.

    Maintains an in-memory queue of review requests. In production this
    would integrate with an external review system (e.g., GitHub PRs, Slack).
    

### Methods

#### __init__
**Parameters**: self, ttl_hours
**Description**: 
        Initialize the adapter.

        Args:
            ttl_hours: Hours before a pending review request expires.
        

#### submit_for_review
**Parameters**: self, agent_name, file_path, change_description, proposed_change, metadata
**Returns**: str
**Description**: 
        Submit a change for human review.

        Returns:
            review_id string
        

#### check_status
**Parameters**: self, review_id
**Returns**: ReviewStatus | None
**Description**: 
        Check the status of a review request.

        Returns:
            ReviewStatus or None if not found
        

#### get_pending_reviews
**Parameters**: self
**Returns**: list[ReviewRequest]
**Description**: Return all pending (non-expired) review requests.

#### is_available
**Parameters**: self
**Returns**: bool
**Description**: Return True — the in-memory adapter is always available.

#### get_queue_depth
**Parameters**: self
**Returns**: int
**Description**: Return the number of pending review requests.

#### approve
**Parameters**: self, review_id, reviewer_notes
**Returns**: bool
**Description**: 
        Approve a review request.

        Returns:
            True if the request was found and approved, False otherwise.
        

#### reject
**Parameters**: self, review_id, reviewer_notes
**Returns**: bool
**Description**: 
        Reject a review request.

        Returns:
            True if the request was found and rejected, False otherwise.
        

#### clear_expired
**Parameters**: self
**Returns**: int
**Description**: 
        Remove all expired review requests from the queue.

        Returns:
            Number of requests removed.
        

#### _expire_if_stale
**Parameters**: self, request
**Returns**: None
**Description**: Mark a single request as expired if its TTL has passed.

#### _expire_stale_requests
**Parameters**: self
**Returns**: None
**Description**: Mark all stale pending requests as expired.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Function: __init__

**Parameters**: self, ttl_hours
**Description**: 
        Initialize the adapter.

        Args:
            ttl_hours: Hours before a pending review request expires.
        



## Function: submit_for_review

**Parameters**: self, agent_name, file_path, change_description, proposed_change, metadata
**Returns**: str
**Description**: 
        Submit a change for human review.

        Returns:
            review_id string
        



## Function: check_status

**Parameters**: self, review_id
**Returns**: ReviewStatus | None
**Description**: 
        Check the status of a review request.

        Returns:
            ReviewStatus or None if not found
        



## Function: get_pending_reviews

**Parameters**: self
**Returns**: list[ReviewRequest]
**Description**: Return all pending (non-expired) review requests.



## Function: is_available

**Parameters**: self
**Returns**: bool
**Description**: Return True — the in-memory adapter is always available.



## Function: get_queue_depth

**Parameters**: self
**Returns**: int
**Description**: Return the number of pending review requests.



## Function: approve

**Parameters**: self, review_id, reviewer_notes
**Returns**: bool
**Description**: 
        Approve a review request.

        Returns:
            True if the request was found and approved, False otherwise.
        



## Function: reject

**Parameters**: self, review_id, reviewer_notes
**Returns**: bool
**Description**: 
        Reject a review request.

        Returns:
            True if the request was found and rejected, False otherwise.
        



## Function: clear_expired

**Parameters**: self
**Returns**: int
**Description**: 
        Remove all expired review requests from the queue.

        Returns:
            Number of requests removed.
        



## Function: _expire_if_stale

**Parameters**: self, request
**Returns**: None
**Description**: Mark a single request as expired if its TTL has passed.



## Function: _expire_stale_requests

**Parameters**: self
**Returns**: None
**Description**: Mark all stale pending requests as expired.



## Usage Examples

### Class Usage

```python
# Using ReviewStatus
reviewstatus = ReviewStatus()
```

```python
# Using ReviewRequest
reviewrequest = ReviewRequest()
reviewrequest.to_dict()
```

```python
# Using HumanReviewAdapter
humanreviewadapter = HumanReviewAdapter()
humanreviewadapter.submit_for_review()
humanreviewadapter.check_status()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using __init__
result = __init__(ttl_hours)
```

```python
# Using submit_for_review
result = submit_for_review(agent_name, file_path)
```



---
**Generated**: 2026-03-26T09:39:04.845931
**Type**: api_reference
**Quality**: comprehensive
