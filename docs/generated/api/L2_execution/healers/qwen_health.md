# API Documentation: qwen_health

**Target Audience**: developers, api_users

# qwen_health API Documentation

**File**: `qwen_health.py`
**Classes**: 1
**Functions**: 4

## Classes

- **MockVLLMProcessManager**

## Functions

- **get_qwen_health_status** -> dict[str, Any]
- **get_gpu_memory_usage** -> int
- **get_pid** -> int | None
- **is_running** -> bool


## Class: MockVLLMProcessManager

**Description**: Mock vLLM process manager for health endpoint.

### Methods

#### get_pid
**Parameters**: self
**Returns**: int | None
**Description**: Get vLLM process ID.

#### is_running
**Parameters**: self
**Returns**: bool
**Description**: Check if vLLM process is running.



## Function: get_qwen_health_status

**Returns**: dict[str, Any]
**Description**: Comprehensive health endpoint with determinism visibility.



## Function: get_gpu_memory_usage

**Returns**: int
**Description**: Get current GPU memory usage in MB.



## Function: get_pid

**Parameters**: self
**Returns**: int | None
**Description**: Get vLLM process ID.



## Function: is_running

**Parameters**: self
**Returns**: bool
**Description**: Check if vLLM process is running.



## Usage Examples

### Class Usage

```python
# Using MockVLLMProcessManager
mockvllmprocessmanager = MockVLLMProcessManager()
mockvllmprocessmanager.get_pid()
mockvllmprocessmanager.is_running()
```

### Function Usage

```python
# Using get_qwen_health_status
result = get_qwen_health_status()
```

```python
# Using get_gpu_memory_usage
result = get_gpu_memory_usage()
```

```python
# Using get_pid
result = get_pid()
```



---
**Generated**: 2026-03-26T09:39:03.840596
**Type**: api_reference
**Quality**: comprehensive
