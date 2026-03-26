# API Documentation: qwen_gpu_validator

**Target Audience**: developers, api_users

# qwen_gpu_validator API Documentation

**File**: `qwen_gpu_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **QwenGPUCapabilityError** (inherits from RuntimeError)

## Functions

- **get_gpu_memory_gb** -> float
- **get_cuda_version** -> str
- **get_compute_capability** -> float
- **get_nvidia_driver_version** -> str
- **version_parse** -> tuple[int, ...]
- **validate_qwen_gpu_capabilities** -> None
- **start_qwen_server_safely** -> None
- **__init__**


## Class: QwenGPUCapabilityError

**Description**: Raised when GPU capabilities are insufficient for Qwen model.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, requirement, current, model



## Function: get_gpu_memory_gb

**Returns**: float
**Description**: Get available GPU memory in GB.



## Function: get_cuda_version

**Returns**: str
**Description**: Get CUDA version from nvcc or nvidia-smi.



## Function: get_compute_capability

**Returns**: float
**Description**: Get GPU compute capability.



## Function: get_nvidia_driver_version

**Returns**: str
**Description**: Get NVIDIA driver version.



## Function: version_parse

**Parameters**: version
**Returns**: tuple[int, ...]
**Description**: Parse version string into comparable tuple.



## Function: validate_qwen_gpu_capabilities

**Parameters**: model_size
**Returns**: None
**Description**: Hard fail on GPU capability mismatch BEFORE model load.



## Function: start_qwen_server_safely

**Parameters**: model_size
**Returns**: None
**Description**: Enforce validation order: validate BEFORE start.



## Function: __init__

**Parameters**: self, requirement, current, model


## Usage Examples

### Class Usage

```python
# Using QwenGPUCapabilityError
qwengpucapabilityerror = QwenGPUCapabilityError()
```

### Function Usage

```python
# Using get_gpu_memory_gb
result = get_gpu_memory_gb()
```

```python
# Using get_cuda_version
result = get_cuda_version()
```

```python
# Using get_compute_capability
result = get_compute_capability()
```



---
**Generated**: 2026-03-26T09:39:03.837800
**Type**: api_reference
**Quality**: comprehensive
