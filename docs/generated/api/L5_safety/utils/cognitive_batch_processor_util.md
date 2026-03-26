# API Documentation: cognitive_batch_processor_util

**Target Audience**: developers, api_users

# cognitive_batch_processor_util API Documentation

**File**: `cognitive_batch_processor_util.py`
**Classes**: 1
**Functions**: 10

## Classes

- **CognitiveBatchProcessor**

## Functions

- **__init__**
- **_load_checkpoint** -> dict[str, Any]
- **_save_checkpoint** -> None
- **process_batch** -> dict[str, int]
- **_get_file_path** -> Path | None
- **_process_single_violation** -> bool
- **_get_violation_type** -> str
- **get_results** -> dict[str, Any]
- **get_statistics** -> dict[str, Any]
- **clear_checkpoint** -> None


## Class: CognitiveBatchProcessor

**Description**: 
    Batch processor for high-volume cognitive disposition analysis.

    Manages rate limiting, checkpointing, and resumable execution for
    processing large numbers of architectural violations.

    Attributes:
        agent: CognitiveDispositionAgent instance
        checkpoint_file: Path to checkpoint file for progress tracking
        rate_limit_delay: Seconds to wait between API calls
        checkpoint_interval: Save checkpoint every N items
        max_retries: Maximum retry attempts for failed items
    

### Methods

#### __init__
**Parameters**: self, agent, checkpoint_file, rate_limit_delay, checkpoint_interval, max_retries
**Description**: 
        Initialize the Cognitive Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            checkpoint_file: Path to checkpoint file
            rate_limit_delay: Seconds between API calls
            checkpoint_interval: Save progress every N items
            max_retries: Maximum retry attempts per item
        

#### _load_checkpoint
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Load checkpoint from file if it exists.

        Returns:
            Dictionary of file_path -> disposition results
        

#### _save_checkpoint
**Parameters**: self
**Returns**: None
**Description**: Save current progress to checkpoint file.

#### process_batch
**Parameters**: self, violations, auto_execute
**Returns**: dict[str, int]
**Description**: 
        Process a batch of violations with rate limiting and checkpointing.

        Args:
            violations: List of violation objects to process
            auto_execute: If True, execute disposition actions (not just analyze)

        Returns:
            Statistics dictionary with counts
        

#### _get_file_path
**Parameters**: self, violation
**Returns**: Path | None
**Description**: 
        Extract file path from violation object.

        Args:
            violation: Violation object (dict or object with attributes)

        Returns:
            Path to file or None
        

#### _process_single_violation
**Parameters**: self, violation, file_path_str
**Returns**: bool
**Description**: 
        Process a single violation with retry logic.

        Args:
            violation: Violation object
            file_path_str: String path to file

        Returns:
            True if successful, False otherwise
        

#### _get_violation_type
**Parameters**: self, violation
**Returns**: str
**Description**: 
        Extract violation type from violation object.

        Args:
            violation: Violation object

        Returns:
            Violation type string
        

#### get_results
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get all processed results.

        Returns:
            Dictionary of file_path -> disposition results
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get processing statistics.

        Returns:
            Statistics dictionary
        

#### clear_checkpoint
**Parameters**: self
**Returns**: None
**Description**: Clear the checkpoint file and reset results.



## Function: __init__

**Parameters**: self, agent, checkpoint_file, rate_limit_delay, checkpoint_interval, max_retries
**Description**: 
        Initialize the Cognitive Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            checkpoint_file: Path to checkpoint file
            rate_limit_delay: Seconds between API calls
            checkpoint_interval: Save progress every N items
            max_retries: Maximum retry attempts per item
        



## Function: _load_checkpoint

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Load checkpoint from file if it exists.

        Returns:
            Dictionary of file_path -> disposition results
        



## Function: _save_checkpoint

**Parameters**: self
**Returns**: None
**Description**: Save current progress to checkpoint file.



## Function: process_batch

**Parameters**: self, violations, auto_execute
**Returns**: dict[str, int]
**Description**: 
        Process a batch of violations with rate limiting and checkpointing.

        Args:
            violations: List of violation objects to process
            auto_execute: If True, execute disposition actions (not just analyze)

        Returns:
            Statistics dictionary with counts
        



## Function: _get_file_path

**Parameters**: self, violation
**Returns**: Path | None
**Description**: 
        Extract file path from violation object.

        Args:
            violation: Violation object (dict or object with attributes)

        Returns:
            Path to file or None
        



## Function: _process_single_violation

**Parameters**: self, violation, file_path_str
**Returns**: bool
**Description**: 
        Process a single violation with retry logic.

        Args:
            violation: Violation object
            file_path_str: String path to file

        Returns:
            True if successful, False otherwise
        



## Function: _get_violation_type

**Parameters**: self, violation
**Returns**: str
**Description**: 
        Extract violation type from violation object.

        Args:
            violation: Violation object

        Returns:
            Violation type string
        



## Function: get_results

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get all processed results.

        Returns:
            Dictionary of file_path -> disposition results
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get processing statistics.

        Returns:
            Statistics dictionary
        



## Function: clear_checkpoint

**Parameters**: self
**Returns**: None
**Description**: Clear the checkpoint file and reset results.



## Usage Examples

### Class Usage

```python
# Using CognitiveBatchProcessor
cognitivebatchprocessor = CognitiveBatchProcessor()
cognitivebatchprocessor.process_batch()
cognitivebatchprocessor.get_results()
```

### Function Usage

```python
# Using __init__
result = __init__(agent, checkpoint_file)
```

```python
# Using _load_checkpoint
result = _load_checkpoint()
```

```python
# Using _save_checkpoint
result = _save_checkpoint()
```



---
**Generated**: 2026-03-26T09:39:05.623052
**Type**: api_reference
**Quality**: comprehensive
