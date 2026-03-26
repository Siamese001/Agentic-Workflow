# API Documentation: vllm_process_manager

**Target Audience**: developers, api_users

# vllm_process_manager API Documentation

**File**: `vllm_process_manager.py`
**Classes**: 1
**Functions**: 9

## Classes

- **VLLMProcessManager**

## Functions

- **get_model_config** -> dict
- **__init__**
- **start_server** -> int
- **stop_server** -> None
- **health_check** -> bool
- **get_memory_usage** -> dict
- **get_pid** -> int | None
- **is_running** -> bool
- **get_uptime** -> float


## Class: VLLMProcessManager

**Description**: Manage isolated vLLM server process.

### Methods

#### __init__
**Parameters**: self

#### start_server
**Parameters**: self, model_config
**Returns**: int
**Description**: Start vLLM server with specified model configuration.

#### stop_server
**Parameters**: self
**Returns**: None
**Description**: Stop vLLM server gracefully.

#### health_check
**Parameters**: self
**Returns**: bool
**Description**: Check if vLLM server is healthy and responding.

#### get_memory_usage
**Parameters**: self
**Returns**: dict
**Description**: Get GPU memory usage statistics.

#### get_pid
**Parameters**: self
**Returns**: int | None
**Description**: Get vLLM process ID.

#### is_running
**Parameters**: self
**Returns**: bool
**Description**: Check if vLLM process is running.

#### get_uptime
**Parameters**: self
**Returns**: float
**Description**: Get server uptime in seconds.



## Function: get_model_config

**Parameters**: model_size
**Returns**: dict
**Description**: Get model configuration for specified model size.



## Function: __init__

**Parameters**: self


## Function: start_server

**Parameters**: self, model_config
**Returns**: int
**Description**: Start vLLM server with specified model configuration.



## Function: stop_server

**Parameters**: self
**Returns**: None
**Description**: Stop vLLM server gracefully.



## Function: health_check

**Parameters**: self
**Returns**: bool
**Description**: Check if vLLM server is healthy and responding.



## Function: get_memory_usage

**Parameters**: self
**Returns**: dict
**Description**: Get GPU memory usage statistics.



## Function: get_pid

**Parameters**: self
**Returns**: int | None
**Description**: Get vLLM process ID.



## Function: is_running

**Parameters**: self
**Returns**: bool
**Description**: Check if vLLM process is running.



## Function: get_uptime

**Parameters**: self
**Returns**: float
**Description**: Get server uptime in seconds.



## Usage Examples

### Class Usage

```python
# Using VLLMProcessManager
vllmprocessmanager = VLLMProcessManager()
vllmprocessmanager.start_server()
vllmprocessmanager.stop_server()
```

### Function Usage

```python
# Using get_model_config
result = get_model_config(model_size)
```

```python
# Using __init__
result = __init__()
```

```python
# Using start_server
result = start_server(model_config)
```



---
**Generated**: 2026-03-26T09:39:03.852369
**Type**: api_reference
**Quality**: comprehensive
