# API Documentation: qwen_determinism

**Target Audience**: developers, api_users

# qwen_determinism API Documentation

**File**: `qwen_determinism.py`
**Classes**: 0
**Functions**: 3


## Functions

- **compute_qwen_determinism_digest** -> str
- **canonicalize_qwen_output** -> str
- **compute_current_determinism_digest** -> str


## Function: compute_qwen_determinism_digest

**Parameters**: model_id, model_revision, tokenizer_revision, inference_params, vllm_version, cuda_version, torch_version
**Returns**: str
**Description**: Compute W-QWEN-DETERMINISM-DIGEST with full SHA-256.



## Function: canonicalize_qwen_output

**Parameters**: output
**Returns**: str
**Description**: Enforce Unicode and whitespace canonicalization for replay consistency.



## Function: compute_current_determinism_digest

**Returns**: str
**Description**: Compute determinism digest for current runtime configuration.



## Usage Examples

### Function Usage

```python
# Using compute_qwen_determinism_digest
result = compute_qwen_determinism_digest(model_id, model_revision)
```

```python
# Using canonicalize_qwen_output
result = canonicalize_qwen_output(output)
```

```python
# Using compute_current_determinism_digest
result = compute_current_determinism_digest()
```



---
**Generated**: 2026-03-26T09:39:03.836356
**Type**: api_reference
**Quality**: comprehensive
