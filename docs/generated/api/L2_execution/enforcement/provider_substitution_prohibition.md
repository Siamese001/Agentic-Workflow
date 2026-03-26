# API Documentation: provider_substitution_prohibition

**Target Audience**: developers, api_users

# provider_substitution_prohibition API Documentation

**File**: `provider_substitution_prohibition.py`
**Classes**: 3
**Functions**: 9

## Classes

- **ProviderRequest**
- **ProviderSubstitutionViolation** (inherits from Exception)
- **ProviderSubstitutionGuard**

## Functions

- **validate_provider_request** -> None
- **enforce_fail_closed_on_failure** -> None
- **get_substitution_guard** -> ProviderSubstitutionGuard
- **test_provider_substitution_prohibition** -> bool
- **__init__**
- **register_request** -> None
- **validate_response** -> None
- **handle_failure** -> None
- **clear_request** -> None


## Class: ProviderRequest

**Description**: Immutable record of original provider request.



## Class: ProviderSubstitutionViolation

**Description**: Raised when provider substitution is attempted.

**Inherits from**: Exception



## Class: ProviderSubstitutionGuard

**Description**: Guard to prevent provider/model substitution in SovereignLLMGateway.

### Methods

#### __init__
**Parameters**: self

#### register_request
**Parameters**: self, request_id, provider_request
**Returns**: None
**Description**: Register a provider request for tracking.

        Args:
            request_id: Unique request identifier
            provider_request: The provider request details
        

#### validate_response
**Parameters**: self, request_id, actual_provider, actual_model
**Returns**: None
**Description**: Validate that the response matches the original request.

        Args:
            request_id: Request identifier
            actual_provider: Provider that actually responded
            actual_model: Model that actually responded

        Raises:
            ProviderSubstitutionViolation: If substitution is detected
        

#### handle_failure
**Parameters**: self, request_id, error, attempted_substitution
**Returns**: None
**Description**: Handle provider failure with fail-closed enforcement.

        Args:
            request_id: Request identifier
            error: The error that occurred
            attempted_substitution: Any attempted substitution

        Raises:
            ProviderSubstitutionViolation: Always raises to ensure fail-closed
        

#### clear_request
**Parameters**: self, request_id
**Returns**: None
**Description**: Clear a completed request.

        Args:
            request_id: Request identifier to clear
        



## Function: validate_provider_request

**Parameters**: original_request, actual_provider, actual_model, context
**Returns**: None
**Description**: Validate that no provider/model substitution occurred (REQ-415).

    Args:
        original_request: The original request made by the agent
        actual_provider: The provider actually used
        actual_model: The model actually used
        context: Optional context for logging

    Raises:
        ProviderSubstitutionViolation: If substitution is detected
    



## Function: enforce_fail_closed_on_failure

**Parameters**: original_request, error, attempted_substitution
**Returns**: None
**Description**: Ensure fail-closed behavior on provider failure (REQ-415).

    Args:
        original_request: The original request that failed
        error: The error that occurred
        attempted_substitution: Any attempted substitution (for logging)

    Raises:
        ProviderSubstitutionViolation: Always raises to ensure fail-closed
    



## Function: get_substitution_guard

**Returns**: ProviderSubstitutionGuard
**Description**: Get the global provider substitution guard.

    Returns:
        The global ProviderSubstitutionGuard instance
    



## Function: test_provider_substitution_prohibition

**Returns**: bool
**Description**: Test that provider substitution prohibition is working.

    Returns:
        True if prohibition is enforced, False otherwise
    



## Function: __init__

**Parameters**: self


## Function: register_request

**Parameters**: self, request_id, provider_request
**Returns**: None
**Description**: Register a provider request for tracking.

        Args:
            request_id: Unique request identifier
            provider_request: The provider request details
        



## Function: validate_response

**Parameters**: self, request_id, actual_provider, actual_model
**Returns**: None
**Description**: Validate that the response matches the original request.

        Args:
            request_id: Request identifier
            actual_provider: Provider that actually responded
            actual_model: Model that actually responded

        Raises:
            ProviderSubstitutionViolation: If substitution is detected
        



## Function: handle_failure

**Parameters**: self, request_id, error, attempted_substitution
**Returns**: None
**Description**: Handle provider failure with fail-closed enforcement.

        Args:
            request_id: Request identifier
            error: The error that occurred
            attempted_substitution: Any attempted substitution

        Raises:
            ProviderSubstitutionViolation: Always raises to ensure fail-closed
        



## Function: clear_request

**Parameters**: self, request_id
**Returns**: None
**Description**: Clear a completed request.

        Args:
            request_id: Request identifier to clear
        



## Usage Examples

### Class Usage

```python
# Using ProviderRequest
providerrequest = ProviderRequest()
```

```python
# Using ProviderSubstitutionViolation
providersubstitutionviolation = ProviderSubstitutionViolation()
```

```python
# Using ProviderSubstitutionGuard
providersubstitutionguard = ProviderSubstitutionGuard()
providersubstitutionguard.register_request()
providersubstitutionguard.validate_response()
```

### Function Usage

```python
# Using validate_provider_request
result = validate_provider_request(original_request, actual_provider)
```

```python
# Using enforce_fail_closed_on_failure
result = enforce_fail_closed_on_failure(original_request, error)
```

```python
# Using get_substitution_guard
result = get_substitution_guard()
```



---
**Generated**: 2026-03-26T09:39:03.723486
**Type**: api_reference
**Quality**: comprehensive
