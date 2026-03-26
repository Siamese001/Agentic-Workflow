# API Documentation: vllm_invariant_verifier_types

**Target Audience**: developers, api_users

# vllm_invariant_verifier_types API Documentation

**File**: `vllm_invariant_verifier_types.py`
**Classes**: 0
**Functions**: 1


## Functions

- **verify_gateway_invariants** -> list[InvariantViolation]


## Function: verify_gateway_invariants

**Returns**: list[InvariantViolation]
**Description**: 
    Verify architectural invariants at the gateway execution boundary.

    Args:
        provider_selected: Selected provider (e.g., "Qwen2.5-7B-Instruct" or "gemini-2.5-pro").
        local_request: Shaped local request (None if routed to Gemini).
        telemetry_dict: Telemetry dictionary with stable key ordering.
        fingerprint: Infrastructure fingerprint (None if not provided).
        replay_hash_enabled: If True, enforce replay_hash presence in telemetry (FAIL if missing).
        gpu_import_policy_ok: If False, report GPU import policy violation (FAIL).

    Returns:
        List of InvariantViolation objects, sorted by invariant_id then severity.
    



## Usage Examples

### Function Usage

```python
# Using verify_gateway_invariants
result = verify_gateway_invariants()
```



---
**Generated**: 2026-03-26T09:39:04.034169
**Type**: api_reference
**Quality**: comprehensive
