# API Documentation: healing_provider_adapters

**Target Audience**: developers, api_users

# healing_provider_adapters API Documentation

**File**: `healing_provider_adapters.py`
**Classes**: 5
**Functions**: 14

## Classes

- **OOMRetryableError** (inherits from Exception)
- **OOMEscalatedError** (inherits from Exception)
- **QwenInvokerAdapter**
- **GeminiInvokerAdapter**
- **LocalAgentAdapter**

## Functions

- **__init__** -> None
- **invoke_qwen_vllm** -> InvocationRecord
- **_build_prompt** -> str
- **invoke_local** -> InvocationRecord
- **invoke_gemini** -> InvocationRecord
- **__init__** -> None
- **invoke_gemini** -> InvocationRecord
- **_build_prompt** -> str
- **invoke_local** -> InvocationRecord
- **invoke_qwen_vllm** -> InvocationRecord
- **invoke_local** -> InvocationRecord
- **invoke_qwen_vllm** -> InvocationRecord
- **invoke_gemini** -> InvocationRecord
- **_call_vllm**


## Class: OOMRetryableError

**Description**: Raised when OOM occurs but retry is possible through router escalation.

**Inherits from**: Exception



## Class: OOMEscalatedError

**Description**: Raised when OOM has been escalated to another tier.

**Inherits from**: Exception



## Class: QwenInvokerAdapter

**Description**: Qwen/vLLM provider adapter with explicit configuration - no environment access.

### Methods

#### __init__
**Parameters**: self, base_url, api_key
**Returns**: None
**Description**: Initialize Qwen adapter with explicit configuration.

        Args:
            base_url: vLLM endpoint URL (explicit, no environment variable)
            api_key: API key (explicit, no environment variable)
        

#### invoke_qwen_vllm
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Invoke Qwen model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        

#### _build_prompt
**Parameters**: self, healing_input, decision, agent_name
**Returns**: str
**Description**: Build structured prompt from healing context.

#### invoke_local
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Local agent not supported by Qwen adapter.

#### invoke_gemini
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Gemini not supported by Qwen adapter.



## Class: GeminiInvokerAdapter

**Description**: Gemini 2.5 Pro provider adapter with explicit configuration - no environment access.

### Methods

#### __init__
**Parameters**: self, api_key
**Returns**: None
**Description**: Initialize Gemini adapter with explicit configuration.

        Args:
            api_key: Google API key (explicit, no environment variable)
        

#### invoke_gemini
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Invoke Gemini model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        

#### _build_prompt
**Parameters**: self, healing_input, decision, agent_name
**Returns**: str
**Description**: Build structured prompt from healing context.

#### invoke_local
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Local agent not supported by Gemini adapter.

#### invoke_qwen_vllm
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Qwen not supported by Gemini adapter.



## Class: LocalAgentAdapter

**Description**: Local agent adapter for simple, deterministic healing without LLM calls.

### Methods

#### invoke_local
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Invoke local agent with deterministic record.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig (unused for local agent)
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        

#### invoke_qwen_vllm
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Qwen not supported by local adapter.

#### invoke_gemini
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Gemini not supported by local adapter.



## Function: __init__

**Parameters**: self, base_url, api_key
**Returns**: None
**Description**: Initialize Qwen adapter with explicit configuration.

        Args:
            base_url: vLLM endpoint URL (explicit, no environment variable)
            api_key: API key (explicit, no environment variable)
        



## Function: invoke_qwen_vllm

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Invoke Qwen model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        



## Function: _build_prompt

**Parameters**: self, healing_input, decision, agent_name
**Returns**: str
**Description**: Build structured prompt from healing context.



## Function: invoke_local

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Local agent not supported by Qwen adapter.



## Function: invoke_gemini

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Gemini not supported by Qwen adapter.



## Function: __init__

**Parameters**: self, api_key
**Returns**: None
**Description**: Initialize Gemini adapter with explicit configuration.

        Args:
            api_key: Google API key (explicit, no environment variable)
        



## Function: invoke_gemini

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Invoke Gemini model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        



## Function: _build_prompt

**Parameters**: self, healing_input, decision, agent_name
**Returns**: str
**Description**: Build structured prompt from healing context.



## Function: invoke_local

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Local agent not supported by Gemini adapter.



## Function: invoke_qwen_vllm

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Qwen not supported by Gemini adapter.



## Function: invoke_local

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Invoke local agent with deterministic record.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig (unused for local agent)
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        



## Function: invoke_qwen_vllm

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Qwen not supported by local adapter.



## Function: invoke_gemini

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Gemini not supported by local adapter.



## Function: _call_vllm



## Usage Examples

### Class Usage

```python
# Using OOMRetryableError
oomretryableerror = OOMRetryableError()
```

```python
# Using OOMEscalatedError
oomescalatederror = OOMEscalatedError()
```

```python
# Using QwenInvokerAdapter
qweninvokeradapter = QwenInvokerAdapter()
qweninvokeradapter.invoke_qwen_vllm()
qweninvokeradapter.invoke_local()
```

### Function Usage

```python
# Using __init__
result = __init__(base_url, api_key)
```

```python
# Using invoke_qwen_vllm
result = invoke_qwen_vllm(healing_input, decision)
```

```python
# Using _build_prompt
result = _build_prompt(healing_input, decision)
```



---
**Generated**: 2026-03-26T09:39:03.813489
**Type**: api_reference
**Quality**: comprehensive
