# API Documentation: healing_tier_config

**Target Audience**: developers, api_users

# healing_tier_config API Documentation

**File**: `healing_tier_config.py`
**Classes**: 1
**Functions**: 4

## Classes

- **HealingTierConfig**

## Functions

- **load_default_healing_tier_config** -> HealingTierConfig
- **validate_qwen_startup_state** -> None
- **is_vllm_process_running** -> bool
- **__post_init__** -> None


## Class: HealingTierConfig

**Description**: Immutable, validated configuration for the L2.3 healing tier router.

    Attributes:
        heal_confidence_x: Upper threshold. heal_confidence >= X → LOCAL_AGENT.
        heal_confidence_y: Lower threshold. Y <= heal_confidence < X → QWEN_VLLM.
                           heal_confidence < Y → GEMINI_2_5_PRO.
        max_heal_retries: Maximum heal attempts before forcing GEMINI_2_5_PRO.
        model_qwen_vllm_id: Model identifier for the Qwen 7B vLLM backend.
        model_qwen_14b_vllm_id: Model identifier for the Qwen 14B vLLM backend (RTX 5090).
        model_gemini_2_5_pro_id: Model identifier for the Gemini 2.5 Pro backend.
        enable_bmg_embeddings: When True the decision engine uses BMG cosine
            similarity instead of Jaccard for semantic scoring.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: load_default_healing_tier_config

**Returns**: HealingTierConfig
**Description**: Load the canonical default healing tier config.

    In production, these values would be loaded from L4 state store.
    This function provides the explicit, auditable defaults.

    BGE embeddings are mandatory for deterministic failure classification.

    Returns:
        Validated HealingTierConfig instance.
    



## Function: validate_qwen_startup_state

**Returns**: None
**Description**: Hard validate kill switch at startup.



## Function: is_vllm_process_running

**Returns**: bool
**Description**: Cross-platform detection of vLLM processes using psutil.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using HealingTierConfig
healingtierconfig = HealingTierConfig()
```

### Function Usage

```python
# Using load_default_healing_tier_config
result = load_default_healing_tier_config()
```

```python
# Using validate_qwen_startup_state
result = validate_qwen_startup_state()
```

```python
# Using is_vllm_process_running
result = is_vllm_process_running()
```



---
**Generated**: 2026-03-26T09:39:03.814523
**Type**: api_reference
**Quality**: comprehensive
