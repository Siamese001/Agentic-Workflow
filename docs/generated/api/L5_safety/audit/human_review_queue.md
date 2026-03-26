# API Documentation: human_review_queue

**Target Audience**: developers, api_users

# human_review_queue API Documentation

**File**: `human_review_queue.py`
**Classes**: 2
**Functions**: 10

## Classes

- **PendingVerdict**
- **HumanReviewQueue**

## Functions

- **get_review_queue** -> HumanReviewQueue
- **__init__** -> None
- **enqueue** -> None
- **approve** -> bool
- **reject** -> bool
- **is_approved** -> bool
- **is_blocked** -> bool
- **pending_count** -> int
- **all_pending** -> list[PendingVerdict]
- **size** -> int


## Class: PendingVerdict

**Description**: A verdict awaiting human review.



## Class: HumanReviewQueue

**Description**: Thread-safe queue for AI verdicts requiring human review.

    Verdicts are blocked from routing until `approve()` or `reject()` is called.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### enqueue
**Parameters**: self, verdict
**Returns**: None
**Description**: Add a verdict to the review queue.

#### approve
**Parameters**: self, verdict_id, reviewer_notes
**Returns**: bool
**Description**: Mark a verdict as approved. Returns True if found.

#### reject
**Parameters**: self, verdict_id, reviewer_notes
**Returns**: bool
**Description**: Mark a verdict as rejected. Returns True if found.

#### is_approved
**Parameters**: self, verdict_id
**Returns**: bool
**Description**: Return True only if the verdict has been reviewed and approved.

#### is_blocked
**Parameters**: self, verdict_id
**Returns**: bool
**Description**: Return True if the verdict exists and has not yet been reviewed.

#### pending_count
**Parameters**: self
**Returns**: int
**Description**: Return number of unreviewed verdicts.

#### all_pending
**Parameters**: self
**Returns**: list[PendingVerdict]
**Description**: Return all unreviewed verdicts.

#### size
**Parameters**: self
**Returns**: int



## Function: get_review_queue

**Returns**: HumanReviewQueue
**Description**: Return the module-level singleton review queue.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: enqueue

**Parameters**: self, verdict
**Returns**: None
**Description**: Add a verdict to the review queue.



## Function: approve

**Parameters**: self, verdict_id, reviewer_notes
**Returns**: bool
**Description**: Mark a verdict as approved. Returns True if found.



## Function: reject

**Parameters**: self, verdict_id, reviewer_notes
**Returns**: bool
**Description**: Mark a verdict as rejected. Returns True if found.



## Function: is_approved

**Parameters**: self, verdict_id
**Returns**: bool
**Description**: Return True only if the verdict has been reviewed and approved.



## Function: is_blocked

**Parameters**: self, verdict_id
**Returns**: bool
**Description**: Return True if the verdict exists and has not yet been reviewed.



## Function: pending_count

**Parameters**: self
**Returns**: int
**Description**: Return number of unreviewed verdicts.



## Function: all_pending

**Parameters**: self
**Returns**: list[PendingVerdict]
**Description**: Return all unreviewed verdicts.



## Function: size

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using PendingVerdict
pendingverdict = PendingVerdict()
```

```python
# Using HumanReviewQueue
humanreviewqueue = HumanReviewQueue()
humanreviewqueue.enqueue()
humanreviewqueue.approve()
```

### Function Usage

```python
# Using get_review_queue
result = get_review_queue()
```

```python
# Using __init__
result = __init__()
```

```python
# Using enqueue
result = enqueue(verdict)
```



---
**Generated**: 2026-03-26T09:39:04.723098
**Type**: api_reference
**Quality**: comprehensive
