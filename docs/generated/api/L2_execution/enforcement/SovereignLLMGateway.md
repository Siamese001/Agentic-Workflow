# API Documentation: SovereignLLMGateway

**Target Audience**: developers, api_users

# SovereignLLMGateway API Documentation

**File**: `SovereignLLMGateway.py`
**Classes**: 3
**Functions**: 21

## Classes

- **ProviderHealthState**
- **SovereigntyViolation** (inherits from Exception)
- **SovereignLLMGateway**

## Functions

- **_get_injection_detector_class**
- **get_llm_gateway** -> SovereignLLMGateway
- **is_degraded** -> bool
- **should_degrade** -> bool
- **__new__**
- **__init__**
- **reset_instance**
- **config**
- **_is_policy_approved_model** -> bool
- **_audit** -> None
- **openai**
- **anthropic**
- **google**
- **_update_provider_health** -> None
- **_is_provider_available** -> bool
- **get_provider_health** -> ProviderHealthState
- **_get_default_model** -> str
- **_emit_token_artifact** -> None
- **_build_replay_envelope** -> ReplayEnvelope
- **_get_agent_registry_hash** -> str
- **get_profile**


## Class: ProviderHealthState

**Description**: Health state for LLM providers with degraded mode support.

    Attributes:
        provider: The provider name.
        is_healthy: Whether the provider is healthy.
        error_rate: Recent error rate (0.0 to 1.0).
        last_check: Unix timestamp of last health check.
        degraded_until: Unix timestamp until which provider is in degraded mode.
        consecutive_failures: Number of consecutive failures.
    

### Methods

#### is_degraded
**Parameters**: self, current_time
**Returns**: bool
**Description**: Check if provider is in degraded mode.

        Args:
            current_time: Current Unix timestamp.

        Returns:
            True if provider is in degraded mode.
        

#### should_degrade
**Parameters**: self, error_threshold, failure_threshold
**Returns**: bool
**Description**: Check if provider should be degraded.

        Args:
            error_threshold: Error rate threshold for degradation.
            failure_threshold: Consecutive failures threshold.

        Returns:
            True if provider should be degraded.
        



## Class: SovereigntyViolation

**Description**: Raised when an agent violates its execution policy.

**Inherits from**: Exception



## Class: SovereignLLMGateway

**Description**: 
    Unified LLM Gateway - Single point of truth for all LLM operations.

    Enforces AgentProfile-based policy: every request must carry a registered
    agent_id with a frozen AgentExecutionProfile from the compile-time registry.
    

### Methods

#### __new__
**Parameters**: cls

#### __init__
**Parameters**: self

#### reset_instance
**Parameters**: cls

#### config
**Parameters**: self

#### _is_policy_approved_model
**Parameters**: self, model, provider
**Returns**: bool
**Description**: Check if model override is policy-approved.

        Currently only allows environment-based overrides for Google provider.
        All other providers must use config defaults.
        

#### _audit
**Parameters**: self, provider, model, success, latency_ms, tokens
**Returns**: None

#### openai
**Parameters**: self

#### anthropic
**Parameters**: self

#### google
**Parameters**: self

#### _update_provider_health
**Parameters**: self, provider, success
**Returns**: None
**Description**: Update provider health state based on operation result.

        Args:
            provider: The provider that was used.
            success: Whether the operation was successful.
        

#### _is_provider_available
**Parameters**: self, provider
**Returns**: bool
**Description**: Check if provider is available (not in degraded mode).

        Args:
            provider: The provider to check.

        Returns:
            True if provider is available.
        

#### get_provider_health
**Parameters**: self, provider
**Returns**: ProviderHealthState
**Description**: Get the current health state of a provider.

        Args:
            provider: The provider to query.

        Returns:
            The provider's health state.
        

#### _get_default_model
**Parameters**: self, provider
**Returns**: str

#### _emit_token_artifact
**Parameters**: self, artifact
**Returns**: None
**Description**: §Wave1.8 — Emit TokenEnforcementArtifact via TelemetryEmitter.

#### _build_replay_envelope
**Parameters**: self, request, model, temperature
**Returns**: ReplayEnvelope
**Description**: Build canonical ReplayEnvelope for deterministic tracking.

#### _get_agent_registry_hash
**Parameters**: self
**Returns**: str
**Description**: Get hash of current agent registry state.



## Function: _get_injection_detector_class



## Function: get_llm_gateway

**Returns**: SovereignLLMGateway
**Description**: Factory function to get the singleton instance of the gateway.



## Function: is_degraded

**Parameters**: self, current_time
**Returns**: bool
**Description**: Check if provider is in degraded mode.

        Args:
            current_time: Current Unix timestamp.

        Returns:
            True if provider is in degraded mode.
        



## Function: should_degrade

**Parameters**: self, error_threshold, failure_threshold
**Returns**: bool
**Description**: Check if provider should be degraded.

        Args:
            error_threshold: Error rate threshold for degradation.
            failure_threshold: Consecutive failures threshold.

        Returns:
            True if provider should be degraded.
        



## Function: __new__

**Parameters**: cls


## Function: __init__

**Parameters**: self


## Function: reset_instance

**Parameters**: cls


## Function: config

**Parameters**: self


## Function: _is_policy_approved_model

**Parameters**: self, model, provider
**Returns**: bool
**Description**: Check if model override is policy-approved.

        Currently only allows environment-based overrides for Google provider.
        All other providers must use config defaults.
        



## Function: _audit

**Parameters**: self, provider, model, success, latency_ms, tokens
**Returns**: None


## Function: openai

**Parameters**: self


## Function: anthropic

**Parameters**: self


## Function: google

**Parameters**: self


## Function: _update_provider_health

**Parameters**: self, provider, success
**Returns**: None
**Description**: Update provider health state based on operation result.

        Args:
            provider: The provider that was used.
            success: Whether the operation was successful.
        



## Function: _is_provider_available

**Parameters**: self, provider
**Returns**: bool
**Description**: Check if provider is available (not in degraded mode).

        Args:
            provider: The provider to check.

        Returns:
            True if provider is available.
        



## Function: get_provider_health

**Parameters**: self, provider
**Returns**: ProviderHealthState
**Description**: Get the current health state of a provider.

        Args:
            provider: The provider to query.

        Returns:
            The provider's health state.
        



## Function: _get_default_model

**Parameters**: self, provider
**Returns**: str


## Function: _emit_token_artifact

**Parameters**: self, artifact
**Returns**: None
**Description**: §Wave1.8 — Emit TokenEnforcementArtifact via TelemetryEmitter.



## Function: _build_replay_envelope

**Parameters**: self, request, model, temperature
**Returns**: ReplayEnvelope
**Description**: Build canonical ReplayEnvelope for deterministic tracking.



## Function: _get_agent_registry_hash

**Parameters**: self
**Returns**: str
**Description**: Get hash of current agent registry state.



## Function: get_profile

**Parameters**: agent_id


## Usage Examples

### Class Usage

```python
# Using ProviderHealthState
providerhealthstate = ProviderHealthState()
providerhealthstate.is_degraded()
providerhealthstate.should_degrade()
```

```python
# Using SovereigntyViolation
sovereigntyviolation = SovereigntyViolation()
```

```python
# Using SovereignLLMGateway
sovereignllmgateway = SovereignLLMGateway()
sovereignllmgateway.reset_instance()
sovereignllmgateway.config()
```

### Function Usage

```python
# Using _get_injection_detector_class
result = _get_injection_detector_class()
```

```python
# Using get_llm_gateway
result = get_llm_gateway()
```

```python
# Using is_degraded
result = is_degraded(current_time)
```



---
**Generated**: 2026-03-26T09:39:03.731170
**Type**: api_reference
**Quality**: comprehensive
