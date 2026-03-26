# API Documentation: provider_binding_determinism

**Target Audience**: developers, api_users

# provider_binding_determinism API Documentation

**File**: `provider_binding_determinism.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ProviderBindingContext**

## Functions

- **compute_provider_binding_digest** -> str
- **verify_provider_binding_determinism** -> bool
- **extract_provider_context_from_request** -> ProviderBindingContext


## Class: ProviderBindingContext

**Description**: Context for provider binding determinism.



## Function: compute_provider_binding_digest

**Parameters**: provider_id, model_id, gateway_version, semantic_clock, additional_context
**Returns**: str
**Description**: Compute deterministic digest for provider binding (REQ-413).

    Args:
        provider_id: LLM provider identifier (e.g., "openai", "anthropic", "google")
        model_id: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context for determinism

    Returns:
        SHA-256 hex digest of provider binding information
    



## Function: verify_provider_binding_determinism

**Parameters**: expected_digest, provider_id, model_id, gateway_version, semantic_clock, additional_context
**Returns**: bool
**Description**: Verify provider binding determinism (REQ-413).

    Args:
        expected_digest: Previously computed digest to verify against
        provider_id: LLM provider identifier
        model_id: Model identifier
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context

    Returns:
        True if digest matches, False otherwise
    



## Function: extract_provider_context_from_request

**Parameters**: request
**Returns**: ProviderBindingContext
**Description**: Extract provider binding context from LLM request.

    Args:
        request: LLM request dictionary

    Returns:
        ProviderBindingContext with extracted information
    



## Usage Examples

### Class Usage

```python
# Using ProviderBindingContext
providerbindingcontext = ProviderBindingContext()
```

### Function Usage

```python
# Using compute_provider_binding_digest
result = compute_provider_binding_digest(provider_id, model_id)
```

```python
# Using verify_provider_binding_determinism
result = verify_provider_binding_determinism(expected_digest, provider_id)
```

```python
# Using extract_provider_context_from_request
result = extract_provider_context_from_request(request)
```



---
**Generated**: 2026-03-26T09:39:03.720627
**Type**: api_reference
**Quality**: comprehensive
